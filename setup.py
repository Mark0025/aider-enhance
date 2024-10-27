from setuptools import setup, find_packages

setup(
    name="aider-config",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich>=10.0.0",
        "inquirer>=3.1.3",
        "pyyaml>=6.0.1",
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "anthropic>=0.8.0",
        "playwright>=1.42.0",
    ],
    entry_points={
        "console_scripts": [
            "aider-config=aider_config.core.config_manager:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered configuration manager for Aider",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aider-config",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)
