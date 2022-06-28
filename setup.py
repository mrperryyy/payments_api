from pathlib import Path
from setuptools import find_packages, setup
from typing import List

def parse_requirements_file(file: str) -> List[str]:
    file_path = Path(file)
    with open(file_path, "r") as f:
        return [str(line) for line in f if not line.startswith("#")]

REQUIREMENTS = parse_requirements_file("requirements.txt")
DEV_REQUIREMENTS = parse_requirements_file("requirements-dev.txt")

setup(
    name="example-api",
    version="0.1.0",
    packages=find_packages(exclude=("tests",)),
    install_requires=REQUIREMENTS,
    python_requires=">=3.7",
    extras_require={
        "dev": DEV_REQUIREMENTS,
    },
)