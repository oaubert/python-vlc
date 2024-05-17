#!/usr/bin/env python3

"""Script to get going after having cloned the repository."""

import os
import sys
from pathlib import Path
from subprocess import PIPE, STDOUT, CalledProcessError, run

PROJECT_ROOT = Path(__file__).parent
cwd = Path.cwd()
assert (
    cwd.resolve() == PROJECT_ROOT.resolve()
), f"You should run that script from {PROJECT_ROOT}, but current working directory is {cwd}."

# See https://stackoverflow.com/questions/1854/how-to-identify-which-os-python-is-running-on
on_windows = os.name == "nt"

python = "python3"
venv_bin = ".venv/Scripts" if on_windows else ".venv/bin"
venv_python = f"{venv_bin}/python3"
pre_commit = f"{venv_bin}/pre-commit"
cmds = [
    # See https://git-scm.com/book/en/v2/Git-Tools-Submodules
    (
        "Clone vendored C Tree-sitter grammar",
        ["git", "submodule", "update", "--init", "--recursive"],
    ),
    ("Create a virtual environment in .venv", [python, "-m", "venv", ".venv"]),
    ("Upgrade pip", [venv_python, "-m", "pip", "install", "--upgrade", "pip"]),
    (
        "Install dependencies",
        [venv_python, "-m", "pip", "install", "-r", "requirements.txt"],
    ),
    ("Install pre-commit hooks", [pre_commit, "install"]),
]

for mess, cmd in cmds:
    print(f"{mess}...", end=" ", flush=True)
    try:
        proc = run(cmd, stdout=PIPE, stderr=STDOUT, check=True)
    except CalledProcessError as e:
        print()
        print(f"Oops! Command '{" ".join(e.cmd)}' failed.")
        print(f"Got return code {e.returncode}.")
        print("Here is the command output:")
        print(e.output.decode(), end="", flush=True)
        sys.exit(e.returncode)
    print("Done.", flush=True)

print("Setup successfull!")
