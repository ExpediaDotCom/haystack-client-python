# Haystack bindings for Python OpenTracing API
This is Haystack's client library for Python that implements [OpenTracing](https://github.com/opentracing/opentracing-python/)

Further information can be found on [opentracing.io](https://opentracing.io/) 

## Using this library
See examples in /examples directory. 

First initialize the tracer at the application level by supplying a service name and recorder
```python
opentracing.tracer = HaystackTracer("a_service", recorder)
```

**If there is a Scope, it will act as the parent to any newly started Span** unless the programmer passes 
`ignore_active_span=True` at `start_span()/start_active_span()` time or specified parent context explicitly using 
`childOf=parent_context`

Starting a span can be done as a managed resource using `start_active_span()`
```python
with opentracing.tracer.start_active_span("span-name") as scope:
    do_stuff()
```

or finish the span on your own terms with
```python
span = opentracing.tracer.start_span("span-name")
do_stuff()
span.finish()
```

See opentracing [usage](https://github.com/opentracing/opentracing-python/#usage) for additional information.

#### Logging
All modules define their logger via `logging.getLogger(__name__)`

So in order to define specific logging format or level for this library use `getLogger('haystack')` or configure the
root logger.

## How to configure build environment
Create a python3 virtual environment, activate it and then `make bootstrap`

## Running the example code
`make example`

## How to Release this library
TBD