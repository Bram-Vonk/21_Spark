# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# #
import os
import sys

sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------

project = '`Spark project`'
copyright = 'Bram Vonk 2021'
author = 'Bram Vonk'

# The full version, including alpha/beta/rc tags
release = '0.0.1'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # 'sphinxcontrib.fulltoc',
    'sphinx.ext.autodoc',  # Core library for html generation from docstrings
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "numpydoc",  # handle NumPy documentation formatted docstrings
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'nbsphinx',
    'recommonmark',
    'autoapi.extension',
]

autoapi_dirs = ['../../src']

# autoapi_ignore = ['*/]

autoapi_options = ['members', 'undoc-members', 'special-members', 'show-inheritance', 'imported-members']
autoapi_python_class_content = 'both'
autodoc_typehints = 'none'
nbsphinx_allow_errors = True

# # Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = ['.rst', '.md']

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'sphinx_rtd_theme'
html_theme = "pydata_sphinx_theme"

# # Add any paths that contain custom static files (such as style sheets) here,
# # relative to this directory. They are copied after the builtin static files,
# # so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

htmlhelp_basename = 'spark-doc'

# html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'] }

# html_logo = '_static/img/dst.jpg'
# html_favion = '_static/img/dst.jpg'

# # numpydoc
numpydoc_attributes_as_param_list = False
numpydoc_xref_param_type = True
numpydoc_xref_ignore = {'optional', 'type_without_description', 'BadException'}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    # "mne": ("https://mne.tools/dev", None),
    "numpy": ("https://www.numpy.org/devdocs", None),
    "scipy": ("https://scipy.github.io/devdocs", None),
    # "matplotlib": ("https://matplotlib.org", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    # "scikit-learn": ('https://scikit-learn.org/stable/', None),
    # "plotly": ("https://plot.ly/python-api-reference/", None),
}