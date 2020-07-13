import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="power-forecasting",
    version="0.0.1",
    author="Cooper Sanders",
    author_email="cssande@clemson.edu",
    description="Power forecasting for CEVAC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
)
