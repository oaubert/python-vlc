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
# FIXME: get from the actual vlc.py module
version = "3.0.16"
release = "3.0.16"

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

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"

