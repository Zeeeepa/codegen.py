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
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.7.4",
    ],
    entry_points={
        "console_scripts": [
            "codegen-mcp=mcp.server:main",
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

