"""
Set up the installation via `pip install`
"""

import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="CEVAC-Forecasting-API",
    version="1.0.0",
    author="Cooper Sanders",
    author_email="cssande@clemson.edu",
    description="API for working with models "
                "produced by the CEVAC research team.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "pandas",
        "tensorflow",
        "sklearn",
    ],
)
