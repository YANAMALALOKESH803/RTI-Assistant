from pathlib import Path
import re


def test_required_top_level_files_exist():
    required_files = [
        "README.md",
        "requirements.txt",
        "requirements-dev.txt",
        "LICENSE",
        "Makefile",
        ".gitlab-ci.yml",
        ".coveragerc",
        ".flake8",
        ".pre-commit-config.yaml",
        ".gitleaks.toml",
        ".env.example",
        "Dockerfile",
    ]

    for file_name in required_files:
        assert Path(file_name).is_file()


def test_requirements_include_runtime_and_test_dependencies():
    requirements = Path("requirements.txt").read_text(encoding="utf-8").splitlines()
    dev_requirements = Path("requirements-dev.txt").read_text(encoding="utf-8").splitlines()

    expected_packages = [
        "streamlit",
        "langchain",
        "langchain-community",
        "langchain-huggingface",
        "faiss-cpu",
        "transformers",
        "pytest",
        "pytest-cov",
        "pre-commit",
        "black",
        "mypy",
        "bandit",
        "vulture",
        "pylint",
        "flake8",
        "pyupgrade",
        "ruff",
    ]

    for package in expected_packages:
        assert package in requirements

    assert "-r requirements.txt" in dev_requirements
    assert "semgrep" in dev_requirements


def test_pytest_coverage_configuration_is_present():
    pytest_config = Path("pyproject.toml").read_text(encoding="utf-8")
    fail_under_match = re.search(r"--cov-fail-under=(\d+)", pytest_config)

    assert "[tool.pytest.ini_options]" in pytest_config
    assert 'testpaths = ["tests"]' in pytest_config
    assert "--cov=." in pytest_config
    assert "--cov-report=term-missing" in pytest_config
    assert "--cov-report=xml" in pytest_config
    assert fail_under_match is not None
    assert int(fail_under_match.group(1)) > 50


def test_coverage_reporting_configuration_is_present():
    coverage_config = Path(".coveragerc").read_text(encoding="utf-8")
    pyproject_config = Path("pyproject.toml").read_text(encoding="utf-8")

    assert "[report]" in coverage_config
    assert "show_missing = True" in coverage_config
    assert "fail_under = 51" in coverage_config
    assert "[xml]" in coverage_config
    assert "output = coverage.xml" in coverage_config

    assert "[tool.coverage.report]" in pyproject_config
    assert "fail_under = 51" in pyproject_config


def test_pre_commit_hooks_cover_lint_format_types_security_and_quality():
    pre_commit_config = Path(".pre-commit-config.yaml").read_text(encoding="utf-8")

    expected_hooks = [
        "id: ruff",
        "id: ruff-format",
        "id: black",
        "id: mypy",
        "id: bandit",
        "id: pyupgrade",
        "id: flake8",
        "id: pylint",
        "id: vulture",
        "id: semgrep",
        "id: gitleaks",
        "id: trailing-whitespace",
        "id: end-of-file-fixer",
        "id: check-yaml",
        "id: check-toml",
        "id: check-added-large-files",
    ]

    for hook in expected_hooks:
        assert hook in pre_commit_config

    assert "--config=.gitleaks.toml" in pre_commit_config


def test_ci_pipeline_covers_quality_tests_and_security():
    ci_config = Path(".gitlab-ci.yml").read_text(encoding="utf-8")

    expected_ci_entries = [
        "stages:",
        "- lint",
        "- format",
        "- type_check",
        "- test",
        "- coverage",
        "- security",
        "stage: lint",
        "stage: format",
        "stage: type_check",
        "stage: coverage",
        "ruff check .",
        "flake8 --config=.flake8 .",
        "pylint --errors-only --rcfile=pyproject.toml tests",
        "vulture app.py ingest.py tests --min-confidence=80",
        "black --check .",
        "pyupgrade --py311-plus --exit-zero-even-if-changed app.py ingest.py tests/*.py",
        "mypy --follow-imports=skip app.py ingest.py",
        "pytest --no-cov",
        "pytest --cov=. --cov-report=term-missing --cov-report=xml --cov-fail-under=51",
        "coverage_report:",
        "bandit -r app.py ingest.py -ll",
        "semgrep --config=auto --error app.py ingest.py",
        "pip install -r requirements-dev.txt",
    ]

    for entry in expected_ci_entries:
        assert entry in ci_config


def test_tooling_configuration_is_declared_in_pyproject():
    pyproject_config = Path("pyproject.toml").read_text(encoding="utf-8")

    expected_sections = [
        "[tool.ruff]",
        "[tool.black]",
        "[tool.mypy]",
        "[tool.bandit]",
        "[tool.pylint.main]",
        "[tool.vulture]",
        "[tool.flake8]",
        "[tool.pytest.ini_options]",
        "[tool.coverage.report]",
    ]

    for section in expected_sections:
        assert section in pyproject_config
