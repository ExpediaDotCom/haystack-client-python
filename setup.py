from setuptools import setup, find_packages

with open("README.md") as file:
    long_description = file.read()

setup(
    name="haystack-client",
    version="X.X.X",  # do not change, makefile updates this prior to a release
    url="https://github.com/ExpediaDotCom/haystack-client-python",
    description="Haystack Python OpenTracing Implementation",
    author="Ryan Hilfers, Haystack",
    author_email="haystack@expediagroup.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["opentracing==2.0.0",
                      "requests>=2.19,<3.0",
                      "requests-futures==0.9.9,<1.0",
                      "protobuf>=3.6.0,<4.0",
                      "grpcio>=1.18.0,<2.0]"],
    tests_require=["mock",
                   "nose",
                   "pytest",
                   "coverage",],
    test_suite="nose.collector",
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=3.5",
    keywords=["opentracing", "haystack", "tracing", "microservices", "distributed"],
    packages=find_packages()
)
