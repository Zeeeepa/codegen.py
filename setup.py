#!/usr/bin/env python3
"""
Setup script for CodegenAPI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="codegenapi",
    version="1.0.0",
    author="Codegen Team",
    author_email="support@codegen.com",
    description="A comprehensive Python SDK and CLI tool for agent-to-agent task execution using the Codegen API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zeeeepa/codegen.py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "codegenapi=codegenapi.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "codegenapi": ["*.md", "*.yaml", "*.yml"],
    },
    keywords="codegen ai agents api sdk cli automation development",
    project_urls={
        "Bug Reports": "https://github.com/Zeeeepa/codegen.py/issues",
        "Source": "https://github.com/Zeeeepa/codegen.py",
        "Documentation": "https://docs.codegen.com",
    },
)

