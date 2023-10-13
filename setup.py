import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="sense-hat",
    version="2.6.0",
    author="Dave Honess",
    author_email="dave@raspberrypi.org",
    description="Python module to control the Raspberry Pi Sense HAT, originally used in the Astro Pi mission",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    license="BSD",
    keywords=[
        "sense hat",
        "raspberrypi",
        "astro pi",
    ],
    url="https://github.com/astro-pi/python-sense-hat",
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
