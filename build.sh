#! /bin/bash
pyinstaller -F --path venv/lib64/python3.10/site-packages kubectl-swissknife.py

sudo cp dist/kubectl-swissknife /usr/local/bin/kubectl-swissknife