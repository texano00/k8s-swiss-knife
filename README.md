# k8s-swiss-knife
k8s-swiss-knife is the k8s plugin you ever wanted.

<img src=asset/k8s-swiss-knife-removebg.png width=300>

# Usage
## help
`kubectl swissknife -h `
<img src=asset/helper.png>

`kubectl swissknife root_less_checker -h`
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

# Install
```
LATEST_TAG=$(curl https://api.github.com/repos/texano00/k8s-swiss-knife/tags | jq -r '.[0].name') && wget -O kubectl-swissknife "https://github.com/texano00/k8s-swiss-knife/releases/download/$LATEST_TAG/kubectl-swissknife" && sudo install kubectl-swissknife /usr/bin
```

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