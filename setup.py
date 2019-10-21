from collections import OrderedDict

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rabbit-client",
    version="0.2.0",
    author="alexandre menezes",
    author_email="alexandre.fmenezes@gmail.com",
    description="rabbit message queue client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache-2.0',
    url="https://github.com/amenezes/rabbit-client",
    packages=setuptools.find_packages(),
    python_requires='>=3.6.0',
    project_urls=OrderedDict((
        ('Documentation', 'https://github.com/amenezes/rabbit-client'),
        ('Code', 'https://github.com/amenezes/rabbit-client'),
        ('Issue tracker', 'https://github.com/amenezes/rabbit-client/issues')
    )),
    install_requires=[
        'attrs>=19.1.0',
        'aioamqp>=0.13.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: AsyncIO",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Object Brokering",
        "Topic :: System :: Distributed Computing",
    ],
)
