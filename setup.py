from setuptools import setup, find_packages

setup(
    name="mdmi-cli",
    version="0.1.0",
    description="CLI tool for Mega Drive MIDI Interface SysEx control",
    author="Robert",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "mido>=1.2.10",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-mock>=3.10.0"],
    },
    entry_points={
        "console_scripts": [
            "mdmi=mdmi.cli:main",
        ],
    },
    python_requires=">=3.12",
)
