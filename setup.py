#!/usr/bin/env python

import setuptools

if __name__ == "__main__":
    setuptools.setup(name = "unity",
                     version = "0.1.1-alpha.2",
                     description = "",
                     author = ["Benjamin Rose", "David Rubin"],
                     author_email = ["benjamin.rose@duke.edu", "drubin@hawaii.edu"],
                     license = "MIT",
                    #  readme = "README.rst",
                     url = "https://github.com/rubind/host_unity",
                     # homepage
                     # documentation
                     classifiers = ["Develoment Status :: 4 - Beta",
	                                "Environment :: Console",
	                                "Operating System :: MacOS :: MacOS X",
	                                "Operating System :: POSIX"],
                    #  entry_points = {'unity': ["unity.cli:cli"]}
                    entry_points = '''[console_scripts]
                                   unity=unity.cli:cli
                                   ''',
    )