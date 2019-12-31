from setuptools import setup, find_packages

setup(
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.6, <4',
    install_requires=['numpy>=1.17'],
)

