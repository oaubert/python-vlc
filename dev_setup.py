#!/usr/bin/env python3

"""Script to get going after having cloned the repository."""

import os
from pathlib import Path
from subprocess import run

PROJECT_ROOT = Path(__file__).parent
cwd = Path.cwd()
assert (
    cwd.resolve() == PROJECT_ROOT.resolve()
), f"You should run that script from {PROJECT_ROOT}, but current working directory is {cwd}."

# See https://stackoverflow.com/questions/1854/how-to-identify-which-os-python-is-running-on
on_windows = os.name == "nt"

cmds = []
if on_windows:
    cmds = [
        # See https://git-scm.com/book/en/v2/Git-Tools-Submodules
        (
            "Clone vendored C Tree-sitter grammar",
            ["git", "submodule", "update", "--init", "--recursive"],
        ),
        ("Create a virtual environment in .venv", ["python", "-m", "venv", ".venv"]),
        # A common cause of failure is the Powershell Execution Policy
        # blocking the execution of the activation script.
        # In this case, see https://stackoverflow.com/questions/18713086/virtualenv-wont-activate-on-windows
        # ----------------
        # Also, assumes the script is executed from Powershell.
        (
            "Activate the virtual environment",
            [r".\.venv\Scripts\Activate.ps1"],
        ),
        ("Upgrade pip", ["pip", "install", "--upgrade", "pip"]),
        ("Install dependencies", ["pip", "install", "-r", "requirements.txt"]),
        ("Install pre-commit hooks", ["pre-commit", "install"]),
    ]
else:  # on posix
    cmds = [
        # See https://git-scm.com/book/en/v2/Git-Tools-Submodules
        (
            "Clone vendored C Tree-sitter grammar",
            ["git", "submodule", "update", "--init", "--recursive"],
        ),
        ("Create a virtual environment in .venv", ["python3", "-m", "venv", ".venv"]),
        # A common cause of failure is the Powershell Execution Policy
        # blocking the execution of the activation script.
        # In this case, see https://stackoverflow.com/questions/18713086/virtualenv-wont-activate-on-windows
        (
            "Activate the virtual environment",
            ["/bin/sh", ".venv/bin/activate"],
        ),
        ("Upgrade pip", ["pip3", "install", "--upgrade", "pip"]),
        ("Install dependencies", ["pip3", "install", "-r", "requirements.txt"]),
        ("Install pre-commit hooks", ["pre-commit", "install"]),
    ]

for mess, cmd in cmds:
    print(f"{mess}...", end=" ", flush=True)
    proc = run(cmd, capture_output=True, check=True)
    print("Done.", flush=True)

print("Setup successfull!")
