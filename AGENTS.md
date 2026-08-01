# AGENTS.md

## Cursor Cloud specific instructions

`systemd-dbus` is a Python library (supporting Python 2.7 and 3) providing thin
bindings over systemd via `sd-bus`, implemented as a C extension
(`systemd_dbus._sdbus`), plus pure-Python helpers to generate systemd unit files
(`UnitFile`) and Polkit rules (`PolkitRule`) using Jinja2. There is no server or
GUI — it is a library exercised from Python/terminal.

### Environment / tooling

- System build dependencies are baked into the environment snapshot (do not add
  these to the update script): `libsystemd-dev` (headers + `pkg-config
  libsystemd` for the C extension), `python3-dev` (Python headers /
  `python3-config`), and `cppcheck` (optional C static analysis).
- The startup update script provisions a virtualenv at `.venv` and runs
  `pip install -e ".[dev]" ruff`, which compiles the C extension in place
  (`src/systemd_dbus/_sdbus.*.so`). Always run tooling via `.venv/bin/...`
  (e.g. `.venv/bin/python`, `.venv/bin/pytest`, `.venv/bin/ruff`).
- Editing the C sources under `src/systemd_dbus/c/` requires a rebuild:
  re-run `.venv/bin/python -m pip install -e ".[dev]"` to recompile the extension.

### Lint / test / build (see `README.md` and `pyproject.toml` for details)

- Lint: `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .`. Note the
  repo currently reports pre-existing lint (`F841`) and formatting diffs; that is
  the existing state, not a broken environment.
- Tests: the default `pytest` invocation deselects everything because
  `addopts = "-m not-integration"` in `pyproject.toml` uses a stray hyphen. Run
  unit tests with `.venv/bin/python -m pytest -m "not integration"` and the full
  set with `-m ""` (as the README documents).
- Integration tests (`-m integration`) require a live D-Bus + systemd running as
  PID 1. In this container `SystemdManager` detects the container and disables
  D-Bus, so those tests **skip** by design — this is expected, not a failure.
- C static analysis: `./cppcheck_script.sh` (the `unusedFunction` /
  `Unmatched suppression` notes are expected per the README).
- Packaging: `./build_deb.sh` (needs `dpkg-buildpackage`, present) and
  `./build_rpm.sh` (needs `rpmdevtools`, not installed by default).
