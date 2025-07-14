#!/bin/python
# -*- coding: utf-8 -*-
"""
setup.py

Author: GrimAndGreedy
Created: 2025-06-25
License: MIT
"""

import setuptools


with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "listpick",
    version = "0.1.11.4",
    author = "Grim",
    author_email = "grimandgreedy@protonmail.com",
    description = "Listpick is a powerful TUI data tool for creating TUI apps or viewing/comparing tabulated data.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/grimandgreedy/listpick",
    project_urls = {
        "Bug Tracker": "https://github.com/grimandgreedy/listpick/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.0",

    entry_points={
        'console_scripts': [
            'listpick = listpick:main',
        ]
    },
    install_requires = [
        "wcwidth",
        "pyperclip",
        "toml",
        "dill",
    ],

    extras_require={
        "full": [
            "dill",
            "wcwidth",
            "ipython",
            "msgpack",
            "openpyxl",
            "pandas",
            # "pyarrow",
            "pyperclip",
            "toml",
            "traitlets",
        ]
    },

)
