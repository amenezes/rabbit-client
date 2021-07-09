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
    license="Apache-2.0",
    url="https://github.com/amenezes/rabbit-client",
    packages=setuptools.find_packages(include=["rabbit", "rabbit.*"]),
    entry_points={
        "console_scripts": ["rabbit-client=rabbit.__main__:application.run [cli]"]
    },
    include_package_data=True,
    python_requires=">=3.7.*",
    project_urls=OrderedDict(
        (
            ("Documentation", "https://rabbit-client.amenezes.net"),
            ("Code", "https://github.com/amenezes/rabbit-client"),
            ("Issue tracker", "https://github.com/amenezes/rabbit-client/issues"),
        )
    ),
    install_requires=[
        "aioamqp>=0.13.0",
        "attrs>=19.1.0",
    ],
    tests_require=[
        "isort",
        "black",
        "portray",
        "flake8",
        "flake8-blind-except",
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "codecov",
        "coverage",
        "mypy",
        "tox",
        "tox-asdf",
    ],
    extras_require={
        "cli": ["cleo>=0.8.0", "tqdm"],
        "all": ["cleo>=0.8.0"],
    },
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
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
