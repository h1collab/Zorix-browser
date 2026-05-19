#!/usr/bin/env python3
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Zorix-Browser',
    version='1.0.0',
    description='A functional lightweight web browser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='h1collab',
    url='https://github.com/h1collab/Zorix-browser',
    python_requires='>=3.8',
    install_requires=[
        'PyQt5>=5.15.0',
        'PyQtWebEngine>=5.15.0',
    ],
    entry_points={
        'console_scripts': [
            'zorix-browser=zorix_browser:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
