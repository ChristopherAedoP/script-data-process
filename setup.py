from setuptools import setup, find_packages

setup(
    name="rag-mvp",
    version="0.1.0",
    description="MVP RAG implementation with local embeddings and FAISS",
    author="RAG MVP Team",
    packages=find_packages(),
    install_requires=[
        "faiss-cpu>=1.8.0",
        "langchain-text-splitters>=0.2.0",
        "langchain-community>=0.2.0",
        "click>=8.1.7",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.24.3",
        "openai>=1.0.0",
        "qdrant-client>=1.7.0",
    ],
    entry_points={
        "console_scripts": [
            "rag-cli=src.cli:main",
        ],
    },
    python_requires=">=3.10",
)