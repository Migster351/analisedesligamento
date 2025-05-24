#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema Local de Análise de Entrevistas de Desligamento
Arquivo principal para iniciar o aplicativo Flask
"""

from app.main import app

if __name__ == '__main__':
    print("Iniciando Sistema de Análise de Entrevistas de Desligamento...")
    print("Acesse http://localhost:5001 no seu navegador")
    app.run(debug=True, host='0.0.0.0', port=5001) 