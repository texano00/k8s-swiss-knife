# k8s-swiss-knife

k8s-swiss-knife is the k8s plugin you ever wanted.

<img src=asset/k8s-swiss-knife-removebg.png width=300>

# Install

```
LATEST_TAG=$(curl https://api.github.com/repos/texano00/k8s-swiss-knife/tags | jq -r '.[0].name') && wget -O kubectl-swissknife "https://github.com/texano00/k8s-swiss-knife/releases/download/$LATEST_TAG/kubectl-swissknife" && sudo install kubectl-swissknife /usr/bin
```

# Usage

## help

```
kubectl swissknife -h
```
<img src=asset/helper.png>

```
kubectl swissknife root_less_checker -h
```
<img src=asset/root_less_checker_helper.png>

## root_less_checker

```
kubectl swissknife root_less_checker [-n <namespace>]
```
<img src=asset/root_less_checker.png>

## healthcheck

```
kubectl swissknife healthcheck [-n <namespace>]
```
<img src=asset/oom_checker.png>

## get_resource

```
kubectl swissknife get_resource [-n <namespace>]
```
<img src=asset/get_resource.png>

# Note
Register binary with your shell’s completion framework by running `register-python-argcomplete`:
```
eval "$(register-python-argcomplete kubectl-swissknife)"
```

## optimization_dashboard
```
kubectl swissknife optimization_dashboard [-n <namespace>]
```
<img src=asset/optimization_dashboard.gif>

# Development

```
#! /bin/bash

cd plugin
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

pyinstaller -F --path venv/lib64/python3.10/site-packages kubectl-swissknife.py

sudo cp dist/kubectl-swissknife /usr/local/bin/kubectl-swissknife
```

# License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

# Version

Current version: 0.5.0 - see the [CHANGELOG](CHANGELOG) file for details.