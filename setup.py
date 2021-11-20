#!/usr/bin/env python3
from cartuli import __version__
from setuptools import setup


setup(
    name='cartuli',
    version=__version__,
    description="A tool to create print and play board games",
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Topic :: Games/Entertainment :: Board Games',
        'Typing :: Typed'
    ],
    keywords='PnP board game',
    author='Pablo Muñoz',
    author_email='pablerass@gmail.com',
    url='https://github.com/pablerass/cartuli',
    license='LGPLv3',
    entry_points={
        'console_scripts': [
            'carturli=cartuli.__main__:main',
        ],
    },
    packages=['cartuli'],
    install_requires=[line for line in open('requirements.txt')],
    python_requires='>=3.10'
)