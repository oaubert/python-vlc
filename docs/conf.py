# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Relative to conf.py location
MODULE_DIR = '../generated/3.0/'

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "python-vlc"
copyright = "2024, Olivier Aubert"
author = "Olivier Aubert"

version = "Unknown"
with open(f"{MODULE_DIR}/vlc.py", "r") as f:
    for l in f.readlines():
        if l.startswith('__version__'):
            items = l.split('"')
            if len(items) == 3:
                version = items[1]
            break
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(0, os.path.abspath(MODULE_DIR))

extensions = [
    'sphinx_rtd_theme',
    'autoapi.extension',
    'sphinx_mdinclude',
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autoapi_dirs = [ MODULE_DIR ]
# We only want to include vlc.py, not example files
autoapi_file_patterns = [ 'vlc.py' ]
autoapi_root = 'api'
autoapi_member_order = 'alphabetical'
autoapi_own_page_level = 'class'
autoapi_python_class_content = 'both'
autoapi_options = [ 'members', 'undoc-members', 'private-members', 'show-inheritance', 'show-module-summary' ]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"

