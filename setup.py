from setuptools import setup, find_packages

setup(
    name="gui_constructor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "tkinter",  # обычно входит в стандартную библиотеку Python
    ],
    author="Khushvakht799",
    description="GUI Constructor with AI capabilities",
    python_requires=">=3.7",
)
