# k8s-swiss-knife
k8s-swiss-knife is the k8s plugin you ever wanted.


# Usage
## root_less_checker
```
kubectl swissknife root_less_checker [-n <namespace>]
```
<img src=asset/root_less_checker.png>

# Install


# Development
```
#! /bin/bash

cd plugin

pyinstaller -F --path venv/lib64/python3.10/site-packages kubectl-swissknife.py

sudo cp dist/kubectl-swissknife /usr/local/bin/kubectl-swissknife
```