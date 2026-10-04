"""Sphinx configuration for PiperG2P's Markdown documentation."""

import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
ROOT_DIR = DOCS_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

project = "PiperG2P"
author = "Holger Nahrstaedt"
try:
    release = version("piperg2p")
except PackageNotFoundError:
    release = "0+unknown"
version = release

master_doc = "index"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
]
source_suffix = {".md": "markdown"}
myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 4

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
}
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.md"]
html_theme = "sphinx_rtd_theme"
html_theme_options = {"navigation_depth": 4, "titles_only": False}
