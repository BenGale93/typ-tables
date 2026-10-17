set dotenv-required

default: lint type_check test

alias t := test

@test *FLAGS:
    uv run pytest tests/ {{ FLAGS }}
    uv run coverage report --fail-under=100

alias cov := coverage

@coverage:
    uv run coverage html --skip-covered --skip-empty
    uv run coverage report --format=markdown

alias tc := type_check

@type_check:
    uv run pyrefly check src/ tests/ --config pyproject.toml

alias l := lint

@lint:
    uv run ruff format .
    uv run ruff check . --fix

alias lc := lint_check

@lint_check:
    uv run ruff format --check .
    uv run ruff check .

alias cc := check

check: lint_check type_check test

@docs:
    just sync_changelog
    uv run --group docs zensical serve

@docs_build:
    just sync_changelog
    uv run --group docs zensical build --clean

@sync_changelog:
    cp CHANGELOG.md docs/changelog.md

@sync:
    uv sync --all-groups

@update:
    uv lock --upgrade

@clean:
    rm -rf dist site htmlcov .coverage .pytest_cache .ruff_cache

release version:
    uv run scripts/bump_changelog.py {{ version }}
    just sync_changelog
    git add CHANGELOG.md docs/changelog.md
    git commit -m "Update changelog for {{ version }}"
    git tag {{ version }}
    git push origin HEAD {{ version }}
