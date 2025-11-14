from setuptools import setup, find_packages

setup(
    name="four_d_chess",
    version="1.0.0",
    description="A fully playable four-dimensional chess engine with special pieces",
    author="Codex",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "4d-chess=cli.main:main",
        ]
    },
)
