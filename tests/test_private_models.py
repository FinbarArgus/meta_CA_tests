"""Run private model integration tests as isolated subprocesses."""

import subprocess
import sys

import pytest


def _run_repo_pytest(repo_dir, env, marker="integration"):
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-m",
        marker,
        "-v",
    ]
    result = subprocess.run(
        cmd,
        cwd=str(repo_dir),
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail(
            f"pytest failed in {repo_dir}\n"
            f"--- stdout ---\n{result.stdout}\n"
            f"--- stderr ---\n{result.stderr}"
        )


@pytest.mark.integration
@pytest.mark.slow
def test_sympathetic_neuron_integration(sympathetic_neuron_dir, subprocess_env):
    """Run sympathetic_neuron integration tests against circulatory_autogen."""
    if not sympathetic_neuron_dir.is_dir():
        pytest.skip(f"sympathetic_neuron repo not found: {sympathetic_neuron_dir}")
    _run_repo_pytest(sympathetic_neuron_dir, subprocess_env)


@pytest.mark.integration
@pytest.mark.slow
def test_lung_cpap_model_integration(lung_cpap_model_dir, subprocess_env):
    """Run lung_CPAP_model integration tests against circulatory_autogen."""
    if not lung_cpap_model_dir.is_dir():
        pytest.skip(f"lung_CPAP_model repo not found: {lung_cpap_model_dir}")
    _run_repo_pytest(lung_cpap_model_dir, subprocess_env)
