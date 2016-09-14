from setuptools import setup, find_packages

from teamleader import __prog__, __version__


setup(
    name=__prog__,
    version=__version__,

    description='python-teamleader',
    long_description='Library for accessing the Teamleader API (http://apidocs.teamleader.be/)',

    author='Ruben Van den Bossche, Matteo De Wint',
    author_email='ruben@novemberfive.co, matteo@novemberfive.co',
    url='https://github.com/novemberfiveco/python-teamleader',
    download_url='https://github.com/novemberfiveco/python-teamleader/tarball/' + __version__,

    packages=['teamleader'],
    include_package_data=True,

    install_requires=['requests', 'pycountry']
)
