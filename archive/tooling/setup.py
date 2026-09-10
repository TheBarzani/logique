#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read README file for long description
def read_readme():
    """Read the README.md file for the long description"""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    return "VCGC: Vertex Coloring Problem with Quantum Computing"

# Read requirements from vcgc/requirements.txt
def read_requirements():
    """Read requirements from vcgc/requirements.txt"""
    req_path = os.path.join(os.path.dirname(__file__), "vcgc", "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

setup(
    name="vcgc",
    version="0.1.0",
    author="Ismael Barzani",
    author_email="i_ridha@live.concordia.ca",
    description="Vertex Coloring Problem with Quantum Computing",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/TheBarzani/vcgc",
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
