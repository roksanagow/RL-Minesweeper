from setuptools import setup, find_packages

setup(
    name="minesweeper_rl",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        "pyyaml",
        "numpy"
    ],
    entry_points={
        "console_scripts": [
            "minesweeper-ui=frontend.app:main"
        ]
    },
)
