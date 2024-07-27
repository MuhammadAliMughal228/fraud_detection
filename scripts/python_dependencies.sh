#!/usr/bin/env bash

sudo chown -R ubuntu:ubuntu ~/fd_backend
virtualenv /home/ubuntu/fd_backend/venv
source /home/ubuntu/fd_backend/venv/bin/activate
pip install -r /home/ubuntu/fd_backend/requirements.txt
