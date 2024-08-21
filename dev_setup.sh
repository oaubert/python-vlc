#!/bin/bash

# Setup development environment
PROJECT_ROOT=$(dirname "$(readlink -f $0)")
cd "${PROJECT_ROOT}" || exit

VENV_DIR="${PROJECT_ROOT}/.venv"

# Clone Tree-sitter grammar which is a Git submodule of the project
# See https://git-scm.com/book/en/v2/Git-Tools-Submodules
echo "Updating C Tree-sitter grammar"
git submodule update --init --recursive

if [ ! -d "${PROJECT_ROOT}/.venv" ]
then
    # Create a virtual environment if it doesn't exist
    echo "Creating a virtual environment in .venv"
    python3 -m venv "${VENV_DIR}"
fi

echo "Activating .venv"
# shellcheck source=/dev/null
. "${VENV_DIR}/bin/activate"

echo "Upgrading .venv's pip"
python3 -m pip install --upgrade pip

echo "Installing dependencies"
python3 -m pip install -r requirements.txt

echo "If you want to enable pre-commit hooks (ruff checks), run the command pre-commit install"

echo "Setup done"
