.PHONY: build
build:
	echo "nothing to compile"

.PHONY: bootstrap
bootstrap:
	python setup.py install

.PHONY: test
test:
	python setup.py test

.PHONY: example
example: bootstrap
	python examples/main.py
	
.PHONY: lint
lint:
	pip install flake8
	python -m flake8 haystack/*.py
	
.PHONY: integration_tests
integration_tests:
	docker-compose -f tests/integration/docker-compose.yml -p sandbox up -d
	sleep 15
	docker run -it \
	    --rm \
		--network=sandbox_default \
		-v $(PWD):/ws \
		-w /ws \
		python:3.6 \
		/bin/sh -c 'python setup.py install && pip install kafka-python && python tests/integration/integration.py'
	docker-compose -f integration-tests/docker-compose.yml -p sandbox stop
	
.PHONY: dist
dist: bootstrap lint test integration_tests
	pip install wheel
	python setup.py sdist
	python setup.py bdist_wheel
	
.PHONY: publish
publish:
	pip install twine
	python -m twine upload dist/*
	
.PHONY: proto_compile
proto_compile:
	git submodule init -- ./haystack-idl
	git submodule update
	python -m grpc_tools.protoc -I haystack-idl/proto --python_out=./haystack  haystack-idl/proto/span.proto
	python -m grpc_tools.protoc -I haystack-idl/proto --python_out=./haystack --grpc_python_out=./haystack haystack-idl/proto/agent/spanAgent.proto