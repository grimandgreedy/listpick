import setuptools
import os
# import pip


full_required = [
    "setuptools",
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

required = [
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
# Read the requirements from the requirements.txt file
# with open('requirements.txt') as f:
#     required = f.read().splitlines()

# pip.main(['install'] + requires)

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "listpick",
    version = "0.1.4.12",
    author = "Grim",
    author_email = "grimandgreedy@protonmail.com",
    description = "List Picker is a powerful TUI data tool for creating TUI apps or viewing/comparing tabulated data.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/grimandgreedy/list_picker",
    project_urls = {
        "Bug Tracker": "https://github.com/grimandgreedy/list_picker/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
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
