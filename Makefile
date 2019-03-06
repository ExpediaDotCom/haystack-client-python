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
	python -m flake8 ./haystack --exclude *_pb2* && echo "Flake8 passed without any issues!"
	
.PHONY: integration_tests
integration_tests:
	docker-compose -f tests/integration/docker-compose.yml -p sandbox up -d
	sleep 15
	docker run -it
	    --rm \
		--network=sandbox_default \
		-v $(pwd):/ws \
		-w /ws \
		python:3.6 \
		/bin/sh -c 'python setup.py install && pip install kafka-python && python tests/integration/integration.py'
	docker-compose -f tests/integration/docker-compose.yml -p sandbox stop

.PHONY: set_version
set_version:
	pip install semver
	pip install requests
	python ./scripts/version.py
	
.PHONY: proto_compile
proto_compile:
	git submodule init -- ./haystack-idl
	git submodule update
	pip install grpcio-tools
	python -m grpc_tools.protoc -I haystack-idl/ --python_out=./haystack  haystack-idl/proto/span.proto
	python -m grpc_tools.protoc -I haystack-idl/proto --python_out=./haystack/proto --grpc_python_out=./haystack/proto agent/spanAgent.proto
