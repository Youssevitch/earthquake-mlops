# Contributing

Thanks for contributing!

## Workflow
1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/<short-name>
   ```
2. Code your change with tests.
3. Run quality gates locally:
   ```bash
   make format && make lint && make test
   ```
4. Commit with clear messages (Conventional-style preferred):
   - `feat: ...` new feature
   - `fix: ...` bug fix
   - `docs: ...` docs only
   - `chore: ...` tooling, CI
5. Push branch and open a PR. CI must be green before merge.

## Code Style
- **Black** (line length 100) + **isort** (profile=black)
- **Flake8** with `max-line-length=100`, ignore `E203,W503`
- Tests with **pytest**; avoid brittle assertions.

## PR Checklist
- [ ] Code formatted & linted
- [ ] Tests added/updated
- [ ] Docs updated if behavior changes
- [ ] CI green
