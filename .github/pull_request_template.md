## What does this PR do?
<!-- One or two sentences. What phase/module does this touch? -->

## Why
<!-- Link to the roadmap phase or issue this addresses -->
Closes #

## How was this tested?
<!-- pytest output, manual curl commands, screenshots of Grafana/API docs, etc. -->

## Checklist
- [ ] Tests pass locally (`pytest tests/ --cov=src --cov=api`)
- [ ] Bandit/Pylint run clean (`bandit -r src api -ll`, `pylint src api`)
- [ ] Updated README/docs if this changes how the project runs
- [ ] No secrets, API keys, or `.env` values committed
- [ ] Ran against a small local dataset (not just unit tests) if this touches the data/model pipeline
