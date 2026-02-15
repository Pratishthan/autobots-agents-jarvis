#!/bin/bash

# Get the project name from the command line
PROJECT_NAME="$1"
DOMAIN_NAME="$2"

if [ -z "$PROJECT_NAME" ]; then
    echo "Error: Project name is required"
    exit 1
fi

if [ -z "$DOMAIN_NAME" ]; then
    echo "Error: Domain name is required"
    exit 1
fi

echo "Cleaning up existing virtual environment..."
rm -rf .venv

echo "Setting up virtual environment..."
python3.12 -m venv .venv
source .venv/bin/activate

echo "Scaffolding project structure... for $PROJECT_NAME and domain: $DOMAIN_NAME"
.venv/bin/python sbin/scaffold.py "$PROJECT_NAME" --primary-domain "$DOMAIN_NAME"

echo "Running Poetry lock to update $PROJECT_NAME"
poetry lock

echo "Installing dependencies..."
make install
make install-dev
make install-hooks

echo "Running quality checks..."
make pre-commit


echo "Setup complete for project: $PROJECT_NAME"
