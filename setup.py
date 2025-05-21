import codecs
import os.path
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read() # Assumes README.md exists in the root directory

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

setup(
    name='netbox-aws-resources-plugin',
    version=get_version('netbox_aws_resources_plugin/version.py'),
    description='NetBox plugin for managing AWS Resources',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jordan Keith',
    author_email='jordan@iopc.com.au',
    # install_requires=[], # Add any specific Python dependencies here if needed
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ]
)