
#!/bin/bash

set -e
if [ -n "$1" ]; then
    PYTHON_VERSION=$1
else
    echo "Please specify a Python version, e.g. 3.7.1";
    exit 1
fi
set +e

BASE_PATH=$(basename `pwd`) 
pyenv local $1 && \
python --version && \
python -m venv .venv && \
ln -s `pwd`/.venv ~/.pyenv/versions/$BASE_PATH && \
pyenv local $BASE_PATH
echo "Python virtual env created successfully"
