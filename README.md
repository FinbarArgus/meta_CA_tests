# meta_CA_tests

Coordinator test suite for private circulatory_autogen model repositories.

Use this when developing **circulatory_autogen** to confirm that changes do not
break downstream private models before merging or releasing.

## Covered repositories

- `sympathetic_neuron` — SN_full CellML generation and simulation
- `lung_CPAP_model` — lung_dev pre_calib CellML generation and simulation
- `lymph_CA_user` — Lymphatic CellML generation and simulation

## Prerequisites

- `circulatory_autogen` checked out as a sibling directory, or set explicitly:
  ```bash
  export CIRCULATORY_AUTOGEN_DIR=/path/to/circulatory_autogen
  ```
- Python environment with circulatory_autogen dependencies installed
  (the meta runner prefers `sympathetic_neuron/SN_full/venv/bin/python` when present)
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
and `sys.path` stay isolated between projects.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `CIRCULATORY_AUTOGEN_DIR` | Path to circulatory_autogen repo (default: sibling `../circulatory_autogen`) |
| `SYMPATHETIC_NEURON_DIR` | Override path to sympathetic_neuron repo |
| `LUNG_CPAP_MODEL_DIR` | Override path to lung_CPAP_model repo |
| `LYMPH_CA_USER_DIR` | Override path to lymph_CA_user repo |
