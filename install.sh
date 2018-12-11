#!/usr/bin/env bash
echo "Install required packages"

case `uname` in
    Linux )
        sudo apt-get update
        sudo apt-get install build-essential python-pip libffi-dev python-dev python3-dev libpq-dev
        ;;
    Darwin )
        brew update
        brew install postgres
        ;;
    *)
    exit 1
    ;;
esac


rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt