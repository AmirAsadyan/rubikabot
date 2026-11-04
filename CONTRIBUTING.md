# Contributing

Thanks for helping rubikabot grow.

## Ground rules

- Field names and payload shapes follow the official docs at
  https://rubika.ir/botapi. The methods page wins where the docs
  contradict themselves, and the disagreement should be noted in the
  code or the changelog.
- Zero runtime dependencies is a feature. Pull requests that add one
  need a strong reason.
- Every behaviour change needs a test, and the tests must keep running
  fully offline against a fake transport.

## Running the tests

```bash
python -m unittest discover -s tests -v
```

## Style

- Python 3.10+, standard library only, type hints on public APIs.
- Keep the public API in `rubikabot/__init__.py` in sync with new
  modules, and update both READMEs when behaviour changes.
