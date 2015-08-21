import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="sense-hat",
    version="2.0.0",
    author="Dave Honess",
    author_email="dave@raspberrypi.org",
    description="Python API to control the Sense HAT for Raspberry Pi",
    long_description=read('README.rst'),
    license="BSD",
    keywords=[
        "sense hat",
        "raspberrypi",
        "astro pi",
    ],
    url="https://github.com/astro-pi/astro-pi-hat",
    packages=find_packages(),
    package_data={
        "txt": ['sense_hat_text.txt'],
        "png": ['sense_hat_text.png']
    },
    include_package_data=True,
    install_requires=[
        "pillow",
        "numpy"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Education",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
    ],
)
