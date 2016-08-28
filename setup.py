# -*- encoding: UTF-8 -*-

import os
from setuptools import setup, find_packages



# here = path.abspath(path.dirname(__file__))
# with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
#     long_description = f.read()


setup(
    name='serf_client2',
    version='1.0.0',
    description='Python RPC client for the Serf with streaming support',
    # long_description=long_description,
    url='https://github.com/wix/serf-client2',
    download_url='https://github.com/wix/serf-client2/archive/master.zip',
    author='WIX',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable

    # packages=find_packages(),
    packages=['serf_client2'],
    install_requires=[
        'msgpack-python >= 0.4.0',
    ],
)

# pip install -e .
# pip install --user --upgrade .

