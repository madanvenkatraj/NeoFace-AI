#!/bin/bash
echo "Building testing environment..."
docker-compose build api
echo "Running tests..."
docker-compose run --rm api python -m unittest discover -s tests
