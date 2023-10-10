"""Setup script for the python-act library module"""

from os import path

from setuptools import setup  # type: ignore

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), "rb") as f:
    long_description = f.read().decode("utf-8")

setup(
    name="caep",
    version="1.1.0",
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
        "pydantic",
    ],
    extras_require={
        "dev": [
            "mypy",
            "pytest",
            "types-setuptools",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: ISC License (ISCL)",
    ],
)
