"""Shared fixtures for meta_CA_tests."""

import os
from pathlib import Path

import pytest

META_TESTS_ROOT = Path(__file__).resolve().parents[1]
GIT_PROJECTS = META_TESTS_ROOT.parent


@pytest.fixture(scope="session")
def circulatory_autogen_dir():
    env = os.environ.get("CIRCULATORY_AUTOGEN_DIR")
    if env:
        path = Path(env).resolve()
    else:
        path = (GIT_PROJECTS / "circulatory_autogen").resolve()
    if not path.is_dir():
        pytest.skip(f"circulatory_autogen not found: {path}")
    return path


@pytest.fixture(scope="session")
def sympathetic_neuron_dir():
    env = os.environ.get("SYMPATHETIC_NEURON_DIR")
    if env:
        return Path(env).resolve()
    return (GIT_PROJECTS / "sympathetic_neuron").resolve()


@pytest.fixture(scope="session")
def lung_cpap_model_dir():
    env = os.environ.get("LUNG_CPAP_MODEL_DIR")
    if env:
        return Path(env).resolve()
    return (GIT_PROJECTS / "lung_CPAP_model").resolve()


@pytest.fixture(scope="session")
def lymph_ca_user_dir():
    env = os.environ.get("LYMPH_CA_USER_DIR")
    if env:
        return Path(env).resolve()
    return (GIT_PROJECTS / "lymph_CA_user").resolve()


@pytest.fixture(scope="session")
def subprocess_env(circulatory_autogen_dir):
    env = os.environ.copy()
    env["CIRCULATORY_AUTOGEN_DIR"] = str(circulatory_autogen_dir)
    return env
