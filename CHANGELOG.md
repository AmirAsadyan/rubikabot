# Changelog

## 0.1.0 - 2026-11-04

First public release.

- Typed models for the full Rubika Bot API v3 (messages, updates, keypads,
  buttons, polls, files, metadata and every documented enum).
- `Bot` client covering all 19 API methods, with a pluggable transport
  and zero runtime dependencies.
- `Dispatcher` and `Router` with decorators per update kind, composable
  filters (Command, Text, ButtonId, StateFilter and the magic filter `F`),
  middleware and error handlers.
- FSM with states groups, per chat and user context, in memory or JSON
  file storage.
- `KeyboardBuilder` for chat and inline keypads.
- `FormattedText` builder with UTF-16 aware metadata validation.
- Long polling runner with a persisted offset cursor, plus a standard
  library webhook server and framework agnostic webhook feeding.
- Test suite that runs fully offline, and examples for echo, keypads,
  FSM forms and webhooks.
