import pybind11
from setuptools import setup, Extension

ext_modules = [
    Extension(
        'Extension',
        ['Extension.cpp'],
        include_dirs=[pybind11.get_include()],
        language='c++',
    ),
]

setup(
    name='Extension',
    ext_modules=ext_modules,
)
