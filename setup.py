# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


with open('README') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='zhihu analysis',
    version='0.0.1',
    description='A tool for zhihu analysis',
    long_description=readme,
    author='Wuhao Chen',
    author_email='wuhao.chen999@gmail.com',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
