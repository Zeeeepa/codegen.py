"""
Setup script for the Codegen application.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codegen-api",
    version="0.1.0",
    author="Codegen",
    author_email="support@codegen.com",
    description="Python client and API for Codegen",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codegen-sh/codegen.py",
    packages=find_packages(include=["backend*", "frontend*"]),
    install_requires=[
        "requests>=2.25.0",
        "typer>=0.4.0",
        "rich>=10.0.0",
    ],
    extras_require={
        "async": ["aiohttp>=3.7.0"],
        # tkinter is part of the standard library, so no need to include it
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
            "codegen=app:main",
            "codegen-api=app:api",
            "codegen-ui=app:ui",
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
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
)
