from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(
    name='Orphan',
    version='0.1.0',
    author='David Eyk',
    author_email='david.eyk@gmail.com',
    packages=['orphan'],
    # scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='http://github.com/eykd/orphan',
    license='LICENSE.txt',
    description='A Dickensian roguelike.',
    long_description=open('README.rst').read(),
    install_requires=[
        name for name in
        open('requirements.txt').read().splitlines()
        if not name.startswith('-')
        and not name.startswith('#')
        ],
    entry_points={
        'console_scripts': [
            'orphan = orphan.main:main',
            ],
        },
    )
