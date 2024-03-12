from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="a_MlOps",
    version="0.1",
    packages=find_packages(where='.'),
    python_requires=">=3.11.5",
    install_requires=requirements,
    package_dir={"":"."},
    description="L'objectif est de concevoir et développer MLOps",
    author="sofiane OULD AMARA",
    author_email="sofiane_ouldamara@outlook.fr"
)
