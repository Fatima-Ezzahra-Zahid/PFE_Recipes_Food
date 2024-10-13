#!/bin/bash

# Ensure pip is installed
python3.12 -m ensurepip --upgrade

# Install dependencies
python3.12 -m pip install -r requirements.txt

# Run Django management commands
python3.12 manage.py collectstatic --noinput
