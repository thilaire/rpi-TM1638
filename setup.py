# coding=utf-8

""" setup.py file for the rpi-TM1638 package
this package provides a Raspberry Pi driver for (chained) TM1638 boards

see https://github.com/thilaire/rpi-TM1638
"""

from setuptools import setup


def readme():
	"""Returns the content of the file README.md"""
	with open('README.md') as f:
		return f.read()


setup(name='rpi_TM1638',
      version='0.1',
      description='A Raspberry Pi driver for (chained) TM1638 boards',
      long_description=readme(),
      classifiers=[
		'Development Status :: 4 - Beta',
		'Operating System :: POSIX :: Linux',
		'Environment :: Other Environment',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Programming Language :: Python :: 2.7',
		'Topic :: System :: Hardware :: Hardware Drivers',
		'Topic :: Software Development',
		'Topic :: System :: Hardware'
	],
	keywords='TM1638 driver chained raspberry pi',
	url='https://github.com/thilaire/rpi_TM1638',
	author='Thibault Hilaire',
	author_email='thibault@docmatic.fr',
	license='GPL3',
	packages=['rpi_TM1638'],
	install_requires=['RPi.GPIO'],
	include_package_data=True,
	zip_safe=False)
