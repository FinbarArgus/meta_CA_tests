"""Run private model integration tests as isolated subprocesses."""

import subprocess
import sys

import pytest


def _run_repo_pytest(repo_dir, env, extra_pytest_args=None):
    """Run the full pytest suite under ``<repo>/tests/`` (all test modules)."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
    ]
    if extra_pytest_args:
        cmd.extend(extra_pytest_args)
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
    """Run all sympathetic_neuron tests/ (SN_full smoke + cost_check regression)."""
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


@pytest.mark.integration
@pytest.mark.slow
def test_lymph_ca_user_integration(lymph_ca_user_dir, subprocess_env):
    """Run lymph_CA_user integration tests against circulatory_autogen."""
    if not lymph_ca_user_dir.is_dir():
        pytest.skip(f"lymph_CA_user repo not found: {lymph_ca_user_dir}")
    _run_repo_pytest(lymph_ca_user_dir, subprocess_env)


@pytest.mark.integration
@pytest.mark.slow
def test_ca_user_volume_control_integration(ca_user_volume_control_dir, subprocess_env):
    """Run CA_user_volume_control integration tests against circulatory_autogen."""
    if not ca_user_volume_control_dir.is_dir():
        pytest.skip(
            f"CA_user_volume_control repo not found: {ca_user_volume_control_dir}"
        )
    _run_repo_pytest(ca_user_volume_control_dir, subprocess_env)
