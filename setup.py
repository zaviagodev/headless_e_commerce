from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in headless_e_commerce/__init__.py
from headless_e_commerce import __version__ as version

setup(
	name="headless_e_commerce",
	version=version,
	description="App that provide apis for custom store fronts for ERPNext.",
	author="Zaviago Ltd.",
	author_email="john@zaviago.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
