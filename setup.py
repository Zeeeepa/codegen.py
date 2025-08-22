#!/usr/bin/env python3
"""
Setup script for the Codegen API client.
"""

from setuptools import setup, find_packages

setup(
    name="codegen-api",
    version="0.1.0",
    description="Python client for the Codegen Agent API",
    author="Codegen Team",
    author_email="support@codegen.com",
    url="https://github.com/Zeeeepa/codegen.py",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "typer>=0.4.0",
        "rich>=10.0.0",
    ],
    extras_require={
        "async": ["aiohttp>=3.7.0"],
        "ui": ["tkinter"],
        "dev": [
            "pytest>=6.0.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "mypy>=0.812",
            "flake8>=3.9.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "codegen=codegen.cli:app",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)

