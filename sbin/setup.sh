#!/bin/bash

rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate

poetry lock
make install
make install-dev
make install-hooks
make pre-commit
