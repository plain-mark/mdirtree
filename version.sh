#!/bin/bash
# Usuń poprzednie pliki
rm -rf *.egg-info
rm -rf dist
rm -rf build

# Zainstaluj w trybie edytowalnym
pip install -e .
python changelog.py
bash git.sh
bash publish.sh


