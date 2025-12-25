from setuptools import setup, find_packages

setup(
    name="zenpad",
    version="0.1.0",
    description="A lightweight text editor (Mousepad clone) with extra features.",
    author="Zenpad Team",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "zenpad=zenpad.main:main",
        ],
    },
    install_requires=[
        "PyGObject",
    ],
    data_files=[
        ("share/applications", ["data/zenpad.desktop"]),
    ],
)
