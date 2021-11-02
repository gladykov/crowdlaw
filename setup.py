"""Package PyPI package"""
import os
import pathlib

from setuptools import find_packages, setup

from crowdlaw.model.common import BaseModel


# The directory containing this file
HERE = pathlib.Path(__file__).parent
REPO = HERE / "crowdlaw"

# The text of the README file
README = (HERE / "README.md").read_text()

with open("requirements.txt", "r") as f:
    required = f.readlines()

required = [x for x in required if x]  # Filter empty lines


def package_files(directories):
    """Add extra directories to the package"""
    all_paths = []
    for directory in directories:
        paths = []
        for (path, directories, filenames) in os.walk(directory):
            for filename in filenames:
                paths.append(os.path.join("..", path, filename))

        all_paths = all_paths + paths

    return all_paths


setup(
    name="crowdlaw",
    version=BaseModel.get_version(),
    description="Create and edit law collaboratively",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/gladykov/crowdlaw/",
    author="Jakub Gładykowski",
    author_email="gladykov@gmail.com",
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(),
    package_data={"crowdlaw": package_files([REPO / "locale", REPO / "resources"])},
    include_package_data=True,
    install_requires=required,
    entry_points={
        "console_scripts": [
            "crowdlaw=crowdlaw.main:main",
        ]
    },
    platforms="any",
)
