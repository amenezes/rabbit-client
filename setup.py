from collections import OrderedDict

import setuptools

from rabbit import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rabbit-client",
    version=f"{__version__}",
    author="alexandre menezes",
    author_email="alexandre.fmenezes@gmail.com",
    description="async rabbit client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache-2.0',
    url="https://github.com/amenezes/rabbit-client",
    packages=setuptools.find_packages(include=["rabbit", "rabbit.*"]),
    entry_points={"console_scripts": ["rabbit-client=rabbit.__main__:application.run [cli]"]},
    package_data={
        '': ['rabbit/alembic.ini']
    },
    include_package_data=True,
    python_requires='>=3.6.0',
    project_urls=OrderedDict((
        ('Documentation', 'https://rabbit-client.amenezes.net'),
        ('Code', 'https://github.com/amenezes/rabbit-client'),
        ('Issue tracker', 'https://github.com/amenezes/rabbit-client/issues')
    )),
    install_requires=[
        "aioamqp>=0.13.0",
        "attrs>=19.1.0",
        "sqlalchemy>=1.3.15",
        "alembic>=1.4.2",
    ],
    tests_require=[
        "isort==4.3.21",
        "black==19.10b0",
        "portray==1.3.1",
        "flake8==3.7.8",
        "flake8-blind-except==0.1.1",
        "flake8-polyfill==1.0.2",
        "pytest==5.3.4",
        "pytest-asyncio==0.10.0",
        "pytest-cov==2.8.1",
        "codecov==2.0.22",
        "coverage==5.0.4",
        "mypy",
        "tox==3.14.6",
        "tox-asdf==0.1.0",
        "psycopg2-binary==2.8.4",
    ],
    extras_require={
        "cli": ["cleo>=0.8.0"],
        "all": ["cleo>=0.8.0"],
    },
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Framework :: AsyncIO",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Object Brokering",
        "Topic :: System :: Distributed Computing",
    ],
)
