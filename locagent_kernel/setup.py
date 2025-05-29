"""Setup script for LocAgent Kernel."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() for line in f 
            if line.strip() and not line.startswith('#')
        ]
else:
    requirements = [
        "networkx>=2.8.0",
        "pyyaml>=6.0.0",
        "openai>=1.0.0",
        "anthropic>=0.3.0",
        "litellm>=1.0.0"
    ]

setup(
    name="locagent-kernel",
    version="1.0.0",
    author="LocAgent Team",
    author_email="team@locagent.dev",
    description="A modular code localization engine using graph-guided LLM agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/locagent-kernel",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "locagent=locagent_kernel.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "locagent_kernel": [
            "examples/*.py",
            "examples/*.yaml",
        ],
    },
    keywords="code localization, software engineering, llm, graph analysis, bug localization",
    project_urls={
        "Bug Reports": "https://github.com/your-org/locagent-kernel/issues",
        "Source": "https://github.com/your-org/locagent-kernel",
        "Documentation": "https://locagent-kernel.readthedocs.io/",
    },
)