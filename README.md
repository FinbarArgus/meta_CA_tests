# meta_CA_tests

Coordinator test suite for private circulatory_autogen model repositories.

Use this when developing **circulatory_autogen** to confirm that changes do not
break downstream private models before merging or releasing.

## Covered repositories

- `sympathetic_neuron` — SN_full CellML generation/simulation and cost-check regression
- `lung_CPAP_model` — lung_dev pre_calib CellML generation and simulation
- `lymph_CA_user` — Lymphatic CellML generation and simulation
- `CA_user_volume_control` — PhLynx BVC RAAS5 CellML simulation
- `glucose_dynamics` — ICING glucose model: Myokit-vs-OpenCOR multi-meal solver and calibration-cost comparison (needs both backends; run under the OpenCOR Python shell)

## Prerequisites

- `circulatory_autogen` checked out as a sibling directory, or set explicitly:
  ```bash
  export CIRCULATORY_AUTOGEN_DIR=/path/to/circulatory_autogen
  ```
- Python environment with circulatory_autogen dependencies installed
  (the meta runner prefers `circulatory_autogen/venv/bin/python` when present)
- `pytest` installed in each repo (or install dev extras):
  ```bash
  pip install -e "../sympathetic_neuron[dev]"
  pip install -e "../lung_CPAP_model[dev]"
  pip install -e ".[dev]"
  ```

## Running

From this directory:

```bash
./run_tests.sh
```

Or directly:

```bash
pytest tests/ -v
```

To run only integration tests:

```bash
pytest tests/ -m integration -v
```

Each meta test launches the target repository's pytest in a subprocess so imports
and `sys.path` stay isolated between projects. The subprocess runs **every test**
under that repo's `tests/` directory (`pytest tests/ -v`), including integration,
slow, and cost-check markers (e.g. `sympathetic_neuron/tests/test_cost_check.py`).

## Environment variables

| Variable | Purpose |
|----------|---------|
| `CIRCULATORY_AUTOGEN_DIR` | Path to circulatory_autogen repo (default: sibling `../circulatory_autogen`) |
| `SYMPATHETIC_NEURON_DIR` | Override path to sympathetic_neuron repo |
| `LUNG_CPAP_MODEL_DIR` | Override path to lung_CPAP_model repo |
| `LYMPH_CA_USER_DIR` | Override path to lymph_CA_user repo |
| `CA_USER_VOLUME_CONTROL_DIR` | Override path to CA_user_volume_control repo |
| `GLUCOSE_DYNAMICS_DIR` | Override path to glucose_dynamics repo |
