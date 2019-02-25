from setuptools import setup, find_packages

setup(
    name="haystack-client",
    version="1.0.0",
    description="Haystack Python OpenTracing Implementation",
    author="Ryan Hilfers, Haystack",
    author_email="haystack@expediagroup.com",
    install_requires=["opentracing==2.0.0",
                      "requests>=2.19,<3.0",
                      "requests-futures==0.9.9,<1.0",
                      "protobuf>=3.6.0,<4.0",
                      "grpcio>=1.18.0,<2.0]"],
    tests_require=["mock",
                   "nose",
                   "flake8",
                   "pytest",
                   "coverage",
                   "kafka-python"],
    test_suite="nose.collector",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords=['opentracing', 'haystack', 'tracing', 'microservices', 'distributed'],
    packages=find_packages()
)
