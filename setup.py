import setuptools
import os
from pathlib import Path
root_path = Path(__file__).parent
version_file = f"{root_path}/VERSION"





with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().split("\n")

setuptools.setup(
    name="kbc-jinjamator-public-tasks",
    author="K-Businesscom",
    author_email="kbc-ns-github@aci.guru",
    description="Publicly available jinjamator tasks of K-Businesscom",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/kbc-network-solutions/kbc-jinjamator-public-tasks",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={"": ["*"]},
    install_requires=install_requires,
    license="ASL V2",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    zip_safe=False,
    setup_requires=["setuptools-git-versioning<2"],
    setuptools_git_versioning={
        "enabled": True,
    },

)

from setuptools_git_versioning import version_from_git
with open(version_file,"w") as fh:
    fh.write(version_from_git())
