"""
setup.py
- 프로젝트 설치 설정
"""

from setuptools import setup, find_packages

setup(
    name="ai_dev_tool",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "faiss-cpu",
        "pymongo",
        "redis",
        "python-dotenv",
        "motor",
        "tenacity",
        "openai",
        "PyQt5",
        "requests",
        "aiohttp",
        "asyncio",
        "tqdm",
        "colorama",
        "rich",
        "loguru"
    ],
    python_requires=">=3.8",
    author="AI Dev Tool Team",
    author_email="your.email@example.com",
    description="AI Development Tool with EORA System",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai_dev_tool",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 