import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fake_transport import FakeTransport

from rubikabot import (Bot, ButtonId, Command, Dispatcher, F, Router,
                       State, StateFilter, StatesGroup, Text)
from rubikabot.fsm import MemoryStorage


def message_update(text, chat_id="c1", sender_id="u1", button_id=None,
                   message_id="m1"):
    return {
        "type": "NewMessage",
        "chat_id": chat_id,
        "new_message": {
            "message_id": message_id,
            "text": text,
            "sender_type": "User",
            "sender_id": sender_id,
            "aux_data": {"start_id": None, "button_id": button_id},
        },
    }


class Form(StatesGroup):
    name = State()
    age = State()


class TestRouting(unittest.TestCase):
    def setUp(self):
        self.transport = FakeTransport()
        self.bot = Bot("T", transport=self.transport)
        self.dp = Dispatcher(self.bot)
        self.seen = []

    def test_command_with_args(self):
        @self.dp.message(Command("start"))
        def start(message, command_args):
            self.seen.append(("start", command_args))

        self.assertTrue(self.dp.feed_update(message_update("/start ref-9")))
        self.assertEqual(self.seen, [("start", "ref-9")])
        self.assertFalse(self.dp.feed_update(message_update("/unknown")))

    def test_first_matching_handler_wins(self):
        @self.dp.message(Text(equals="سلام"))
        def hello(message):
            self.seen.append("hello")

        @self.dp.message()
        def fallback(message):
            self.seen.append("fallback")

        self.dp.feed_update(message_update("سلام"))
        self.dp.feed_update(message_update("چیز دیگر"))
        self.assertEqual(self.seen, ["hello", "fallback"])

    def test_message_answer_is_bound(self):
        @self.dp.message(Command("start"))
        def start(message):
            message.answer("خوش آمدی")

        self.dp.feed_update(message_update("/start"))
        payload = self.transport.calls_for("sendMessage")[-1]
        self.assertEqual(payload["chat_id"], "c1")
        self.assertEqual(payload["text"], "خوش آمدی")

    def test_button_id_filter_and_magic_filter(self):
        @self.dp.message(ButtonId("buy"))
        def buy(message):
            self.seen.append("buy")

        @self.dp.inline_message(F.button_id == "confirm")
        def confirm(inline):
            self.seen.append("confirm")

        self.dp.feed_update(message_update("خرید", button_id="buy"))
        self.dp.feed_inline_message({
            "inline_message": {
                "sender_id": "u1", "chat_id": "c1", "message_id": "m9",
                "aux_data": {"button_id": "confirm"}}})
        self.assertEqual(self.seen, ["buy", "confirm"])

    def test_magic_text_filter(self):
        @self.dp.message(F.text.startswith("قیمت"))
        def price(message):
            self.seen.append(message.text)

        self.dp.feed_update(message_update("قیمت چنده؟"))
        self.dp.feed_update(message_update("سلام"))
        self.assertEqual(self.seen, ["قیمت چنده؟"])

    def test_combined_filters(self):
        @self.dp.message(Text(contains="کتاب") & ~Text(contains="قدیمی"))
        def book(message):
            self.seen.append(message.text)

        self.dp.feed_update(message_update("کتاب تازه"))
        self.dp.feed_update(message_update("کتاب قدیمی"))
        self.assertEqual(self.seen, ["کتاب تازه"])

    def test_router_inclusion(self):
        router = Router("shop")

        @router.message(Command("shop"))
        def shop(message):
            self.seen.append("shop")

        self.dp.include_router(router)
        self.dp.feed_update(message_update("/shop"))
        self.assertEqual(self.seen, ["shop"])

    def test_updated_and_removed_kinds(self):
        @self.dp.edited_message()
        def edited(message):
            self.seen.append(("edited", message.text))

        @self.dp.removed_message()
        def removed(update):
            self.seen.append(("removed", update.removed_message_id))

        edited_update = message_update("ویرایش شد")
        edited_update["type"] = "UpdatedMessage"
        edited_update["updated_message"] = edited_update.pop("new_message")
        self.dp.feed_update(edited_update)
        self.dp.feed_update({"type": "RemovedMessage", "chat_id": "c1",
                             "removed_message_id": "m77"})
        self.assertEqual(self.seen,
                         [("edited", "ویرایش شد"), ("removed", "m77")])

    def test_middleware_wraps_handler(self):
        order = []

        @self.dp.middleware
        def trace(handler, event, data):
            order.append("before")
            result = handler(event, data)
            order.append("after")
            return result

        @self.dp.message(Command("start"))
        def start(message):
            order.append("handler")

        self.dp.feed_update(message_update("/start"))
        self.assertEqual(order, ["before", "handler", "after"])

    def test_error_handler(self):
        @self.dp.errors
        def on_error(event, error):
            self.seen.append(type(error).__name__)
            return True

        @self.dp.message(Command("boom"))
        def boom(message):
            raise RuntimeError("kaput")

        self.assertTrue(self.dp.feed_update(message_update("/boom")))
        self.assertEqual(self.seen, ["RuntimeError"])

    def test_webhook_payload_shapes(self):
        @self.dp.message(Command("start"))
        def start(message):
            self.seen.append("start")

        wrapped = {"update": message_update("/start")}
        self.assertTrue(self.dp.handle_webhook_payload("update", wrapped))


class TestFSMFlow(unittest.TestCase):
    def setUp(self):
        self.transport = FakeTransport()
        self.bot = Bot("T", transport=self.transport)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.answers = []

        dp = self.dp

        @dp.message(Command("register"))
        def begin(message, state):
            state.set_state(Form.name)
            self.answers.append("name?")

        @dp.message(StateFilter(Form.name))
        def got_name(message, state):
            state.update_data(name=message.text)
            state.set_state(Form.age)
            self.answers.append("age?")

        @dp.message(StateFilter(Form.age))
        def got_age(message, state):
            data = state.get_data()
            state.clear()
            self.answers.append(f"done:{data['name']}:{message.text}")

        @dp.message()
        def fallback(message, state):
            self.answers.append(f"free:{state.get_state()}")

    def test_two_step_form(self):
        self.dp.feed_update(message_update("/register"))
        self.dp.feed_update(message_update("امیر"))
        self.dp.feed_update(message_update("۲۴"))
        self.dp.feed_update(message_update("متن آزاد"))
        self.assertEqual(self.answers,
                         ["name?", "age?", "done:امیر:۲۴", "free:None"])

    def test_states_are_per_user(self):
        self.dp.feed_update(message_update("/register", sender_id="u1"))
        self.dp.feed_update(message_update("سلام", sender_id="u2"))
        self.assertEqual(self.answers, ["name?", "free:None"])


if __name__ == "__main__":
    unittest.main()
