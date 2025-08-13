#!/usr/bin/env python3
"""
Setup script for the Codegen MCP Server.
"""

from setuptools import setup, find_packages

setup(
    name="codegen-mcp",
    version="0.1.0",
    description="Model Context Protocol (MCP) server for the Codegen API",
    author="Codegen",
    author_email="info@codegen.com",
    url="https://github.com/Zeeeepa/codegen.py",
    packages=find_packages(),
    py_modules=["codegen_api_client", "codegenapi"],
    install_requires=[
        "requests>=2.28.0",
        "aiohttp>=3.8.0",
        "pydantic>=1.8.0",
        "click>=8.0.0",
        "rich>=12.0.0",
        "pyyaml>=6.0",
        "toml>=0.10.0",
    ],
    entry_points={
        "console_scripts": [
            "codegen-mcp=mcp.server:main",
            "codegenapi=codegenapi:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)

