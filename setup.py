
from distutils.core import setup
setup(name='djonet',
    version='0.1',
    description='MonetDB backend for Django',
    author='Gijs Molenaar',
    author_email='gijsmolenaar@gmail.com',
    url='https://github.com/gijzelaerr/djonet',
    packages=['djonet'],
    requires=['monetdb', 'django']
)
