default: lint type_check test

alias t := test

@test *FLAGS:
    uv run pytest tests/ {{FLAGS}}
    uv run coverage report --fail-under=100

alias tc := type_check

@type_check:
    uv run pyrefly check src/ tests/ --config pyproject.toml

alias l := lint

@lint:
    uv run ruff format .
    uv run ruff check . --fix
