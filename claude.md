# meta_CA_tests — guide for adding private model tests

This document explains how **meta_CA_tests** is structured and how to add integration
tests for a new private circulatory_autogen model repository. Use it when prompting
an assistant to extend the test suite.

## Purpose

**meta_CA_tests** is a thin coordinator repo. It does **not** contain model logic.
Instead it runs each private model repo's own pytest suite as a **subprocess**, so:

- `sys.path` and imports stay isolated between projects
- circulatory_autogen changes can be validated against all private models in one command
- each model repo owns its own smoke tests (generation + short simulation)

Typical workflow when developing **circulatory_autogen**:

```bash
cd meta_CA_tests
./run_tests.sh -m integration
```

Run this before merging CA changes that might affect autogeneration, parsers, or solvers.

## Architecture

```
git_projects/
├── circulatory_autogen/          # framework under test (sibling, or CIRCULATORY_AUTOGEN_DIR)
├── meta_CA_tests/                # this repo — subprocess runner only
│   └── tests/test_private_models.py
├── sympathetic_neuron/           # private model repo #1
│   └── tests/                    # actual SN_full tests live here
└── lung_CPAP_model/              # private model repo #2
    └── tests/                    # actual lung_dev tests live here
```

**Two layers:**

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Meta | `meta_CA_tests/tests/` | Discover repo path, set env, `subprocess` → `pytest -m integration` |
| Model | `<model_repo>/tests/` | Generate CellML via CA, run short simulation, assert outputs |

Meta tests never import circulatory_autogen or model code directly.

## Currently registered repositories

| Repo | Env override | Meta test function | Model smoke tests |
|------|--------------|-------------------|-------------------|
| `sympathetic_neuron` | `SYMPATHETIC_NEURON_DIR` | `test_sympathetic_neuron_integration` | `tests/test_sn_full.py` |
| `lung_CPAP_model` | `LUNG_CPAP_MODEL_DIR` | `test_lung_cpap_model_integration` | `tests/test_lung_dev.py` |
| `lymph_CA_user` | `LYMPH_CA_USER_DIR` | `test_lymph_ca_user_integration` | `tests/test_lymphatic.py` |
| `CA_user_volume_control` | `CA_USER_VOLUME_CONTROL_DIR` | `test_ca_user_volume_control_integration` | `tests/test_bvc_raas5.py` |

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CIRCULATORY_AUTOGEN_DIR` | `../circulatory_autogen` (sibling of meta_CA_tests) | Passed to child pytest; each model repo adds `src/` to `sys.path` |
| `SYMPATHETIC_NEURON_DIR` | `../sympathetic_neuron` | Override path to sympathetic_neuron |
| `LUNG_CPAP_MODEL_DIR` | `../lung_CPAP_model` | Override path to lung_CPAP_model |
| `PYTHON` | auto-detect | Python executable for `run_tests.sh` |

When adding a new repo, follow the naming pattern:

```
<REPO_NAME_UPPER>_DIR   e.g. MY_NEW_MODEL_DIR=/path/to/my_new_model
```

## How to add tests for a new model repository

Complete **both** parts below. Meta registration alone is useless without tests
inside the model repo.

### Part A — Add smoke tests inside the model repo

Create a `tests/` directory in the new private repo with this layout:

```
my_new_model/
├── pyproject.toml
├── .gitignore          # exclude generated_models/, data/, venv/, .pytest_cache/
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_<model_name>.py
```

#### A1. `pyproject.toml` (minimal)

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-new-model"
version = "0.1.0"
requires-python = ">=3.8"

[project.optional-dependencies]
dev = ["pytest>=7.0.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "integration: integration tests that require circulatory_autogen",
    "slow: long-running tests",
]
```

#### A2. `tests/conftest.py` — required fixtures

Every model repo conftest should include:

1. **`ca_src_dir`** — resolve `CIRCULATORY_AUTOGEN_DIR`, insert `src/` into `sys.path`
   at import time (so test modules can import CA before fixtures run)
2. **`tmp_generated_models_dir`** — pytest `tmp_path` subdir; **never** write into the
   repo's tracked `generated_models/`
3. **Model config fixture** — dict passed to `generate_with_new_architecture`
4. **`cellml_solver`** — prefer `CVODE_myokit`, fall back to `CVODE_opencor`, skip if neither available
5. **Optional: `<model>_cellml_path`** — generate once per test, return path to `.cellml`

**Circulatory autogen path setup** (copy this pattern):

```python
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GIT_PROJECTS = REPO_ROOT.parent

def _circulatory_autogen_dir() -> Path:
    env = os.environ.get("CIRCULATORY_AUTOGEN_DIR")
    if env:
        return Path(env).resolve()
    return (GIT_PROJECTS / "circulatory_autogen").resolve()

_CA_SRC_DIR = _circulatory_autogen_dir() / "src"
if _CA_SRC_DIR.is_dir() and str(_CA_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_CA_SRC_DIR))
```

**Config dict** must include at minimum:

```python
{
    "file_prefix": "<prefix>",              # e.g. "SN_full", "lung_dev"
    "input_param_file": "<prefix>_parameters.csv",
    "solver": "CVODE",
    "model_type": "cellml_only",
    "resources_dir": "<absolute path to parameters CSV dir>",
    "generated_models_dir": "<tmp path>",
    "solver_info": {"MaximumStep": ..., "MaximumNumberOfSteps": ...},
}
```

Add `"external_modules_dir"` when the model uses custom CellML modules (see
`sympathetic_neuron/SN_full/module_config_user/`).

Use **absolute paths** for `resources_dir`, `generated_models_dir`, and
`external_modules_dir` when passing a raw dict (CA's YAML parser resolves relative
paths against an empty base when `inp_data_dict` is passed directly).

#### A3. `tests/test_<model>.py` — two smoke tests

Every model repo should have exactly these two integration tests, both marked
`@pytest.mark.integration` and `@pytest.mark.slow`:

| Test | What it checks |
|------|----------------|
| `test_<model>_model_generation` | `generate_with_new_architecture(False, config)` returns success; `{generated_models_dir}/{file_prefix}/{file_prefix}.cellml` exists |
| `test_<model>_single_simulation` | `get_simulation_helper(...).run()` succeeds; at least one output variable is non-empty and finite |

**Generation:**

```python
from scripts.script_generate_with_new_architecture import generate_with_new_architecture

success = generate_with_new_architecture(False, config.copy())
assert success
model_path = os.path.join(config["generated_models_dir"], "<prefix>", "<prefix>.cellml")
assert os.path.isfile(model_path)
```

**Simulation** (keep times short — this is a smoke test, not calibration):

```python
from solver_wrappers import get_simulation_helper

helper = get_simulation_helper(
    model_path=model_path,
    solver=cellml_solver,       # "CVODE_myokit" or "CVODE_opencor"
    model_type="cellml_only",
    dt=0.01,
    sim_time=0.5,               # keep short; SN_full uses 0.5 s
    pre_time=0.0,
    solver_info={...},
)
assert helper.run()
# assert on known output variables for this model
helper.reset_and_clear()
helper.close_simulation()
```

**Myokit vs OpenCOR variable names:** Myokit uses dot notation (`soma_SN_module.V`);
OpenCOR uses slash notation (`soma_SN_module/V`). When asserting on outputs, check
both suffix forms or use `get_all_results_dict()` and search by substring.

#### A4. What to track in git vs ignore

**Track (source/config):**
- Python scripts, YAML user inputs, shell runners
- `resources/*.csv`, `resources/*.json` (parameters, vessel arrays, obs_data configs)
- `module_config_user/` when present
- `tests/`, `pyproject.toml`

**Do not track (add to `.gitignore`):**
- `generated_models/`, `param_id_output/`, `plots/`, `outputs/`
- Raw experimental data (`data/`, `.wcp`, `.abf`)
- `venv/`, `__pycache__/`, `.pytest_cache/`
- Patient/run-specific artifacts (see `lung_CPAP_model/lung_dev/patient_dirs/`)

#### A5. Verify locally before registering in meta

```bash
cd /path/to/my_new_model
/path/to/python/with/CA/deps -m pytest tests/ -m integration -v
```

Both tests must pass. A working Python env needs circulatory_autogen dependencies
(myokit, libcellml, numpy, etc.). The meta runner defaults to
`sympathetic_neuron/SN_full/venv/bin/python` when present.

---

### Part B — Register the repo in meta_CA_tests

After Part A passes, wire the new repo into meta_CA_tests with three edits:

#### B1. `tests/conftest.py` — add directory fixture

```python
@pytest.fixture(scope="session")
def my_new_model_dir():
    env = os.environ.get("MY_NEW_MODEL_DIR")
    if env:
        return Path(env).resolve()
    return (GIT_PROJECTS / "my_new_model").resolve()
```

Use the repo directory name as the default sibling path under `git_projects/`.

#### B2. `tests/test_private_models.py` — add subprocess test

```python
@pytest.mark.integration
@pytest.mark.slow
def test_my_new_model_integration(my_new_model_dir, subprocess_env):
    """Run my_new_model integration tests against circulatory_autogen."""
    if not my_new_model_dir.is_dir():
        pytest.skip(f"my_new_model repo not found: {my_new_model_dir}")
    _run_repo_pytest(my_new_model_dir, subprocess_env)
```

Do **not** duplicate model logic here. `_run_repo_pytest` already runs:

```
python -m pytest tests/ -m integration -v
```

in the target repo with `CIRCULATORY_AUTOGEN_DIR` set in the environment.

#### B3. `README.md` — add row to "Covered repositories"

Document the new repo, what model it smoke-tests, and its env override variable.

#### B4. Verify meta runner

```bash
cd meta_CA_tests
./run_tests.sh -m integration -k my_new_model
```

---

## Reference implementations

Study these existing repos before adding a new one:

### sympathetic_neuron (custom modules, external_modules_dir)

- Config: `SN_full/resources/SN_full_parameters.csv` + `module_config_user/`
- Tests: `sympathetic_neuron/tests/test_sn_full.py`
- Generated path: `{tmp}/SN_full/SN_full.cellml`
- Simulation check: soma membrane potential (`soma_SN_module.V`)

### lung_CPAP_model (pre_calib resources copied to tmp)

- Config: `lung_dev/patient_dirs/pre_calib/resources/lung_dev_parameters.csv`
- Resources copied to tmp in conftest (generation may modify CSVs)
- Tests: `lung_CPAP_model/tests/test_lung_dev.py`
- Generated path: `{tmp}/lung_dev/lung_dev.cellml`
- Simulation check: `lung/P_A` (OpenCOR-style names work with both backends via `get_results`)

### lymph_CA_user (custom lymph modules, external_modules_dir)

- Config: `resources/Lymphatic_parameters.csv` + `module_config_user/`
- Tests: `lymph_CA_user/tests/test_lymphatic.py`
- Generated path: `{tmp}/Lymphatic/Lymphatic.cellml`
- Simulation check: lymph vessel volume (`Lymph_vessel_1_module.q_m` or similar)

### CA_user_volume_control (PhLynx-exported CellML, simulation-only)

- No circulatory_autogen autogeneration inputs in-repo; uses committed PhLynx export
- Reference model: `version_1/generated_models/phlynx-export-3C-BVC-RAAS5/phlynx-export-3C-BVC-RAAS5.cellml`
- Tests: `CA_user_volume_control/tests/test_bvc_raas5.py`
- Tests: model availability + short simulation via `get_simulation_helper`
- Simulation check: `aortic_root/u`

---

## meta_CA_tests file reference

| File | Role |
|------|------|
| `run_tests.sh` | Sets `CIRCULATORY_AUTOGEN_DIR`, picks Python, runs pytest |
| `pyproject.toml` | pytest markers: `integration`, `slow` |
| `tests/conftest.py` | Repo path fixtures, `subprocess_env` with CA dir |
| `tests/test_private_models.py` | One `@pytest.mark.integration` test per registered repo |
| `README.md` | Human-facing quick start |

---

## Checklist for prompts adding a new model

When asking an assistant to add model `<name>`:

- [ ] Create `tests/` in `<model_repo>` with conftest + two smoke tests
- [ ] Add `pyproject.toml` with pytest markers in `<model_repo>`
- [ ] Use `tmp_path` for generated CellML; never commit generated outputs
- [ ] Mark tests `@pytest.mark.integration` and `@pytest.mark.slow`
- [ ] Verify: `pytest tests/ -m integration -v` passes in `<model_repo>`
- [ ] Add `<model>_dir` fixture to `meta_CA_tests/tests/conftest.py`
- [ ] Add `test_<model>_integration` to `meta_CA_tests/tests/test_private_models.py`
- [ ] Document env var `<MODEL>_DIR` and repo in `meta_CA_tests/README.md`
- [ ] Verify: `./run_tests.sh -m integration` passes in meta_CA_tests

---

## Common pitfalls

1. **Relative paths in config dict** — pass absolute paths when calling
   `generate_with_new_architecture` with a dict (not loaded from YAML in repo root).
2. **Missing `external_modules_dir`** — SN-style models with custom CellML modules
   will fail generation without it.
3. **Writing to repo `generated_models/`** — always use pytest `tmp_path`.
4. **Import errors in test collection** — add CA `src/` to `sys.path` at conftest
   module level, not only inside fixtures.
5. **Solver unavailable** — use the `cellml_solver` fixture pattern; skip rather
   than fail hard when neither Myokit nor OpenCOR is installed.
6. **Meta test imports model code** — don't; keep meta layer subprocess-only.
7. **Committing raw data** — keep `.gitignore` aligned with sympathetic_neuron and
   lung_CPAP_model patterns before pushing to GitHub.
