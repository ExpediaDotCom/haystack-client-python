# Haystack bindings for Python OpenTracing API
This is Haystack's client library for Python that implements [OpenTracing](https://github.com/opentracing/opentracing-python/)

Further information can be found on [opentracing.io](https://opentracing.io/) 

## Using this library
See examples in /examples directory. There is a serverless example representing an AWS Lambda function. 

Also a more generic example in main.py

See opentracing [usage](https://github.com/opentracing/opentracing-python/#usage) for additional information.

## How to configure build environment
Create a virtual environment:
- `pip install virtualenv`
- `python -m virtualenv venv`
- `source venv/bin/activate`

Then `make bootstrap`

## Running the example code
`make example`

## How to release
TBD ` 

### TODO
- integration tests 
- figure out bytes Tags in proto spans

