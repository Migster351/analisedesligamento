#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala wkhtmltopdf
apt-get update
apt-get install -y wkhtmltopdf

# Instala as dependências Python
pip install -r requirements.txt 