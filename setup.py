from setuptools import setup, find_packages

setup(
    name="codegen-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "typer>=0.4.0",
        "rich>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "mypy>=0.812",
            "flake8>=3.9.2",
        ],
        "async": [
            "aiohttp>=3.7.0",
        ],
        "ui": [
            # tkinter is part of the standard library, but we list it here for clarity
            # It needs to be installed separately on some systems
        ],
    },
    entry_points={
        "console_scripts": [
            "codegen=cli:app",
        ],
    },
    python_requires=">=3.7",
    author="Codegen Team",
    author_email="info@codegen.com",
    description="Python client for the Codegen Agent API",
    keywords="codegen, api, client",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)

