#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'mpttadmin',
    version = '0.3.1',
    author = 'Mikhail Sakhno',
    author_email = 'pawn13@gmail.com',
    description = """jstree admin for mptt models""",
    license = "BSD",
    keywords = "django admin",
    platforms = "POSIX",
    url = 'http://code.tabed.org/mptt_admin',
    install_requires=['django'],
    packages=['mpttadmin'],#find_packages(),
    package_data = { 'mpttadmin': [
        'media/js/*.js',
        'media/js/lib/*.js',
        'media/js/lib/plugins/*.js',
        'media/js/lib/themes/*/*',
    ]},
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
