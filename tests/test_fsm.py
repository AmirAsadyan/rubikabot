import os
import tempfile
import unittest

from rubikabot.fsm import (FSMContext, FileStorage, MemoryStorage, State,
                           StatesGroup, storage_key)


class Profile(StatesGroup):
    name = State()
    age = State()


class TestStates(unittest.TestCase):
    def test_group_binding(self):
        self.assertEqual(Profile.name.full_name, "Profile:name")
        self.assertEqual(Profile.age.full_name, "Profile:age")
        self.assertEqual(
            {state.full_name for state in Profile.all_states()},
            {"Profile:name", "Profile:age"})

    def test_unbound_state_raises(self):
        with self.assertRaises(RuntimeError):
            _ = State().full_name


class TestContext(unittest.TestCase):
    def test_state_and_data_cycle(self):
        ctx = FSMContext(MemoryStorage(), storage_key("c1", "u1"))
        self.assertIsNone(ctx.get_state())
        ctx.set_state(Profile.name)
        self.assertEqual(ctx.get_state(), "Profile:name")
        ctx.update_data(name="امیر")
        ctx.update_data(age=24)
        self.assertEqual(ctx.get_data(), {"name": "امیر", "age": 24})
        ctx.clear()
        self.assertIsNone(ctx.get_state())
        self.assertEqual(ctx.get_data(), {})

    def test_file_storage_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "fsm.json")
            ctx = FSMContext(FileStorage(path), "c1:u1")
            ctx.set_state(Profile.age)
            ctx.update_data(name="امیر")
            reloaded = FSMContext(FileStorage(path), "c1:u1")
            self.assertEqual(reloaded.get_state(), "Profile:age")
            self.assertEqual(reloaded.get_data(), {"name": "امیر"})


if __name__ == "__main__":
    unittest.main()
