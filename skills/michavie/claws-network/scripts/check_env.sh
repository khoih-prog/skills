#!/bin/bash

# Check if mxpy is installed
if ! command -v mxpy &> /dev/null
then
    echo "❌ mxpy could not be found. Please install it using 'pipx install multiversx-sdk-cli'"
    exit 1
fi

echo "✅ mxpy is installed"
mxpy --version

# Check python version
if ! command -v python3 &> /dev/null
then
    echo "❌ python3 could not be found."
    exit 1
fi

echo "✅ python3 is installed"
python3 --version

echo "Environment check passed for Claws Network interactions."
