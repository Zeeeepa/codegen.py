#!/usr/bin/env python3
"""
Setup script for CodegenAPI
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codegenapi",
    version="1.0.0",
    author="Codegen Team",
    author_email="support@codegen.com",
    description="Python SDK and CLI for Codegen Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zeeeepa/codegen.py",
    py_modules=["codegen_api", "cli"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "codegenapi=cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Zeeeepa/codegen.py/issues",
        "Source": "https://github.com/Zeeeepa/codegen.py",
        "Documentation": "https://docs.codegen.com",
    },
)
