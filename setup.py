"""
Setup configuration for the Codegen Python SDK and CLI
"""

import os

from setuptools import find_packages, setup


# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Codegen Python SDK and CLI for agent orchestration"


# Read version from __init__.py
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "codegen", "__init__.py")
    with open(version_file, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"


setup(
    name="codegen-py",
    version=get_version(),
    author="Codegen Team",
    author_email="support@codegen.com",
    description="Python SDK and CLI for Codegen agent orchestration",
    long_description=read_readme(),
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
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0; extra == 'async'",
    ],
    extras_require={
        "async": ["aiohttp>=3.8.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "isort>=5.9.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "myst-parser>=0.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "codegen=codegen.cli:main",
            "codegen-cli=codegen.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "codegen": ["*.json", "*.yaml", "*.yml"],
    },
    project_urls={
        "Bug Reports": "https://github.com/Zeeeepa/codegen.py/issues",
        "Source": "https://github.com/Zeeeepa/codegen.py",
        "Documentation": "https://docs.codegen.com",
    },
    keywords="codegen ai agent automation cli sdk api orchestration",
    zip_safe=False,
)
