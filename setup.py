"""
Set up the installation via `pip install`
"""

import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="power-forecasting",
    version="1.0.0",
    author="Cooper Sanders",
    author_email="cssande@clemson.edu",
    description="Power forecasting for CEVAC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "pandas",
        "tensorflow",
        "sklearn",
        "numpy",
    ],
)
