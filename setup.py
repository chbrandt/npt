from setuptools import setup

setup(entry_points = {
        'console_scripts': ['gpt=gpt.cli:main'],
    })
