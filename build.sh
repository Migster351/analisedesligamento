#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala dependências do sistema
apt-get update
apt-get install -y wkhtmltopdf
apt-get install -y python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 libffi-dev libjpeg-dev libopenjp2-7-dev

# Instala as dependências Python
pip install -r requirements.txt 