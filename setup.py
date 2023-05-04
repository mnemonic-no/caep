"""Setup script for the python-act library module"""

from os import path

from setuptools import setup

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), "rb") as f:
    long_description = f.read().decode("utf-8")

setup(
    name="caep",
    version="0.1.8",
    author="mnemonic AS",
    zip_safe=True,
    author_email="opensource@mnemonic.no",
    description="Config Argument Env Parser (CAEP)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="ISC",
    keywords="mnemonic",
    packages=["caep"],
    url="https://github.com/mnemonic-no/caep",
    python_requires=">=3.6, <4",
    package_data={"caep": ["py.typed"]},
    install_requires=[
        "pydantic>=1.8.0,<2.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: ISC License (ISCL)",
    ],
)
