from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.adoc')) as f:
    readme = f.read()

setup(
    name             = 'pl-heudiconv',
    version          = '0.1',
    description      = 'An app to ...',
    long_description = readme,
    author           = 'grdryn',
    author_email     = 'gerard@ryan.lt',
    url              = 'http://wiki',
    packages         = ['pl_heudiconv'],
    install_requires = ['chrisapp', 'heudiconv'],
    test_suite       = 'nose.collector',
    tests_require    = ['nose'],
    license          = 'MIT',
    zip_safe         = False,
    python_requires  = '>=3.6',
    entry_points     = {
        'console_scripts': [
            'pl-heudiconv = pl_heudiconv.__main__:main'
            ]
        }
)
