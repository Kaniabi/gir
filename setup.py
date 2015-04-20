from __future__ import unicode_literals
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys



#===================================================================================================
# PyTest
#===================================================================================================
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)



#===================================================================================================
# setup
#===================================================================================================
setup(
    name='gir',
    provides=['gir'],
    version='0.1',

    packages=find_packages(exclude=['tests']),
    install_requires=[
        # Portability (python 2 and 3)
        'six',
        # Code
        'requests',
        'jsonpath-rw',
        'rq',
        'redis',
        # App framework
        'flask',
        'uwsgi',
        # TODO: Find out how to use github urls on setup.py
        # 'git+https://github.com/ESSS/python-slackclient.git@python3',
        # Apps
        'Flask-Debug',
        'rq-dashboard',
    ],
    tests_require=[
        'pytest',
        'mock',
        # TODO: Find out how to use github urls on setup.py
        # 'git+https://github.com/ESSS/datatree.git@esss-master',
    ],

    cmdclass = {'test': PyTest},


    #===============================================================================================
    # Project description
    #===============================================================================================
    author='Alexandre Motta de Andrade',
    author_email='ama@esss.com.br',
    url='https://github.com/Kaniabi/gir',
    license='LGPL v3+',
    description='XMl Factory is a simple XMl writer that uses dict syntax to write files.',
    keywords='gir slack stash jira jenkins chatbot chatops',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development',
    ],
)
