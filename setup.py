from setuptools import setup, find_packages, Extension
import treeseg

setup(
    name='treeseg',
    version=treeseg.__version__,
    author='Bryce Frank',
    author_email='bfrank70@gmail.com',
    packages=['treeseg', 'treesegtest'],
    url='https://github.com/brycefrank/treeseg',
    license='LICENSE.txt',
    description='Tools for the detection and segmentation of trees.',
    install_requires = [ # Dependencies from pip
    ]
)
