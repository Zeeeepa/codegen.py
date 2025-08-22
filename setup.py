"""
Setup script for the Codegen API client.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codegen-client",
    version="0.1.0",
    author="Codegen",
    author_email="support@codegen.com",
    description="Python client for the Codegen API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codegen-sh/codegen-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "httpx>=0.23.0",
        "pydantic>=1.9.0",
    ],
)

