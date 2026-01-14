from setuptools import setup, find_packages

setup(
    name='EtradePythonClient',
    version='1.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    long_description=open('README.md').read(),
)

