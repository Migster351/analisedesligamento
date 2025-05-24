#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para geração de relatórios em PDF
"""

import os
from datetime import datetime
import jinja2
import pdfkit
import tempfile
from weasyprint import HTML
from . import analytics, visualizations

# Diretório para armazenar os relatórios gerados
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'reports')
# Diretório para templates de relatórios
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

# Certifica-se que o diretório de relatórios existe
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_pdf_report(period_type, period_value):
    """Gera um relatório PDF para o período especificado"""
    try:
        # Obtém os dados analisados para o período
        analysis_data = analytics.analyze_period(period_type, period_value)
        
        if analysis_data is None:
            raise ValueError("Não há dados disponíveis para o período especificado")
        
        # Gera gráficos para o relatório
        charts = visualizations.generate_charts(analysis_data, period_type, period_value)
        
        # Converte caminhos relativos para absolutos
        base_dir = os.path.dirname(os.path.dirname(__file__))
        absolute_charts = {}
        for key, path in charts.items():
            if path.startswith('../static/'):
                # Remove '../static/' e usa o caminho absoluto
                img_path = os.path.join(base_dir, 'static', path.replace('../static/', ''))
                absolute_charts[key] = img_path
            else:
                absolute_charts[key] = os.path.join(base_dir, path)
        
        # Gera insights e alertas
        insights = analytics.generate_insights(analysis_data)
        alerts = analytics.generate_alerts(analysis_data)
        
        # Define o nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'relatorio_desligamentos_{period_type}_{period_value}_{timestamp}.pdf'
        filepath = os.path.join(REPORTS_DIR, filename)
        
        # Dados para o template
        template_data = {
            'title': f'Relatório de Entrevistas de Desligamento - {period_type} {period_value}',
            'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'period': {'type': period_type, 'value': period_value},
            'analysis': analysis_data,
            'charts': absolute_charts,  # Usa os caminhos absolutos
            'insights': insights,
            'alerts': alerts
        }
        
        # Cria um arquivo temporário para o HTML
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.html', encoding='utf-8', delete=False) as temp_html:
            # Lê o template HTML
            template_path = os.path.join(TEMPLATES_DIR, 'report_template.html')
            if not os.path.exists(template_path):
                html_content = _generate_default_template(template_data)
            else:
                with open(template_path, 'r', encoding='utf-8') as file:
                    template_str = file.read()
                template = jinja2.Template(template_str)
                html_content = template.render(**template_data)
            
            # Escreve o HTML no arquivo temporário
            temp_html.write(html_content)
            temp_html_path = temp_html.name
        
        try:
            # Tenta gerar o PDF usando pdfkit com configurações ajustadas
            options = {
                'quiet': '',
                'encoding': 'UTF-8',
                'enable-local-file-access': None,  # Permite acesso a arquivos locais
                'allow': [os.path.dirname(base_dir)],  # Permite acesso ao diretório do projeto
                'page-size': 'A4',
                'margin-top': '2.5cm',
                'margin-right': '2cm',
                'margin-bottom': '2.5cm',
                'margin-left': '2cm',
                'image-quality': 100,  # Melhor qualidade de imagem
                'image-dpi': 300,  # DPI mais alto para imagens
                'enable-javascript': True,
                'javascript-delay': 1000,  # Espera 1 segundo para carregar JavaScript
                'no-stop-slow-scripts': True
            }
            
            # Garante que o diretório de relatórios existe
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            pdfkit.from_file(temp_html_path, filepath, options=options)
            return os.path.abspath(filepath)
            
        except Exception as e:
            print(f"Erro ao gerar PDF com pdfkit: {e}")
            
            try:
                # Tenta com WeasyPrint como fallback
                from weasyprint import HTML, CSS
                from weasyprint.fonts import FontConfiguration

                font_config = FontConfiguration()
                css = CSS(string='''
                    @page { size: A4; margin: 2.5cm 2cm; }
                    img { max-width: 100%; height: auto; }
                ''', font_config=font_config)
                
                HTML(filename=temp_html_path).write_pdf(filepath, stylesheets=[css], font_config=font_config)
                return os.path.abspath(filepath)
            except Exception as e:
                print(f"Erro ao gerar PDF com WeasyPrint: {e}")
                # Retorna o arquivo HTML como último recurso
                html_filepath = os.path.join(REPORTS_DIR, f'relatorio_{timestamp}.html')
                os.rename(temp_html_path, html_filepath)
                return os.path.abspath(html_filepath)
        finally:
            # Limpa o arquivo temporário se ainda existir
            if os.path.exists(temp_html_path):
                os.unlink(temp_html_path)
    
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return None

def _generate_default_template(data):
    """Gera um template HTML padrão para o relatório quando não há template personalizado"""
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ title }}</title>
        <style>
            @page {
                size: A4;
                margin: 2.5cm 2cm;
                @top-center {
                    content: "Relatório de Entrevistas de Desligamento";
                    font-family: Arial, sans-serif;
                    font-size: 10pt;
                    color: #666;
                }
                @bottom-center {
                    content: "Página " counter(page) " de " counter(pages);
                    font-family: Arial, sans-serif;
                    font-size: 10pt;
                    color: #666;
                }
            }
            
            body {
                font-family: Arial, Helvetica, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 100%;
                margin: 0;
                padding: 0;
                background-color: white;
            }
            
            .header {
                text-align: center;
                margin-bottom: 3rem;
                padding: 2rem;
                background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
                color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .header h1 {
                margin: 0;
                font-size: 24pt;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .header p {
                margin: 10px 0 0;
                font-size: 12pt;
                opacity: 0.9;
            }
            
            .section {
                margin: 2rem 0;
                padding: 1.5rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .section h2 {
                color: #1a365d;
                font-size: 18pt;
                margin-top: 0;
                margin-bottom: 1.5rem;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #e2e8f0;
            }
            
            .insights {
                background-color: #f8fafc;
                padding: 1.5rem;
                border-radius: 8px;
                border-left: 5px solid #4299e1;
                margin: 1.5rem 0;
            }
            
            .insight-item {
                margin-bottom: 1rem;
                padding: 0.5rem 0;
                border-bottom: 1px solid #e2e8f0;
            }
            
            .insight-item:last-child {
                border-bottom: none;
            }
            
            .alerts {
                background-color: #fff5f5;
                padding: 1.5rem;
                border-radius: 8px;
                border-left: 5px solid #f56565;
                margin: 1.5rem 0;
            }
            
            .alert-item {
                margin-bottom: 1rem;
                padding: 0.5rem 0;
            }
            
            .alert-high {
                color: #c53030;
                font-weight: bold;
            }
            
            .alert-medium {
                color: #dd6b20;
            }
            
            .chart-container {
                text-align: center;
                margin: 2rem 0;
                padding: 1rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .chart-container h3 {
                color: #2d3748;
                font-size: 14pt;
                margin-bottom: 1rem;
            }
            
            .chart-container img {
                max-width: 100%;
                height: auto;
                border-radius: 4px;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1.5rem 0;
                background: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            table th {
                background-color: #2c5282;
                color: white;
                padding: 1rem;
                text-align: left;
                font-weight: bold;
                font-size: 11pt;
            }
            
            table td {
                padding: 1rem;
                border-top: 1px solid #e2e8f0;
                font-size: 10pt;
            }
            
            table tr:nth-child(even) {
                background-color: #f8fafc;
            }
            
            .footer {
                text-align: center;
                margin-top: 3rem;
                padding-top: 1.5rem;
                border-top: 2px solid #e2e8f0;
                color: #718096;
                font-size: 10pt;
            }
            
            .summary-box {
                background: #f8fafc;
                border-radius: 8px;
                padding: 1.5rem;
                margin: 1.5rem 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .summary-box h3 {
                color: #2d3748;
                margin-top: 0;
                font-size: 14pt;
            }
            
            .summary-item {
                display: flex;
                justify-content: space-between;
                padding: 0.5rem 0;
                border-bottom: 1px solid #e2e8f0;
            }
            
            .summary-item:last-child {
                border-bottom: none;
            }
            
            .summary-label {
                font-weight: bold;
                color: #4a5568;
            }
            
            .summary-value {
                color: #2d3748;
            }
            
            @media print {
                .header {
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }
                
                table th {
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }
                
                .chart-container {
                    page-break-inside: avoid;
                }
                
                .section {
                    page-break-inside: avoid;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{{ title }}</h1>
            <p>Gerado em: {{ date }}</p>
        </div>
        
        <div class="section">
            <h2>Resumo Executivo</h2>
            <div class="summary-box">
                <div class="summary-item">
                    <span class="summary-label">Total de Entrevistas:</span>
                    <span class="summary-value">{{ analysis.count }}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Período:</span>
                    <span class="summary-value">{{ period.type|capitalize }} {{ period.value }}</span>
                </div>
            </div>
            
            {% if insights %}
            <div class="insights">
                <h3>Principais Insights</h3>
                {% for area, insight in insights.items() %}
                <div class="insight-item">
                    <strong>{{ area|capitalize }}:</strong> {{ insight }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if alerts %}
            <div class="alerts">
                <h3>Pontos de Atenção</h3>
                {% for alert in alerts %}
                <div class="alert-item alert-{{ alert.severity }}">
                    {{ alert.message }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>Análise por Área</h2>
            {% if charts.bar %}
            <div class="chart-container">
                <h3>Médias por Área</h3>
                <img src="{{ charts.bar }}" alt="Gráfico de médias por área">
            </div>
            {% endif %}
            
            <table>
                <thead>
                    <tr>
                        <th>Área</th>
                        <th>Média</th>
                        <th>Mediana</th>
                        <th>Mínimo</th>
                        <th>Máximo</th>
                    </tr>
                </thead>
                <tbody>
                    {% for area, data in analysis.areas.items() %}
                    <tr>
                        <td>{{ area|capitalize }}</td>
                        <td>{{ "%.2f"|format(data.mean) }}</td>
                        <td>{{ "%.2f"|format(data.median) }}</td>
                        <td>{{ data.min }}</td>
                        <td>{{ data.max }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Visão Geral da Satisfação</h2>
            {% if charts.radar %}
            <div class="chart-container">
                <h3>Radar de Satisfação</h3>
                <img src="{{ charts.radar }}" alt="Radar de satisfação">
            </div>
            {% endif %}
        </div>
        
        {% if charts.pie %}
        <div class="section">
            <h2>Análise de Sentimento</h2>
            <div class="chart-container">
                <h3>Distribuição de Sentimentos nos Comentários</h3>
                <img src="{{ charts.pie }}" alt="Sentimento dos comentários">
            </div>
        </div>
        {% endif %}
        
        {% if charts.wordcloud %}
        <div class="section">
            <h2>Análise de Comentários</h2>
            <div class="chart-container">
                <h3>Palavras-chave mais Frequentes</h3>
                <img src="{{ charts.wordcloud }}" alt="Nuvem de palavras">
            </div>
        </div>
        {% endif %}
        
        <div class="section">
            <h2>Distribuição de Respostas</h2>
            {% for area in analysis.areas %}
                {% if charts['distribution_' + area] %}
                <div class="chart-container">
                    <h3>{{ area|capitalize }}</h3>
                    <img src="{{ charts['distribution_' + area] }}" alt="Distribuição de respostas para {{ area }}">
                </div>
                {% endif %}
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>Sistema Local de Análise de Entrevistas de Desligamento</p>
            <p>&copy; {{ date.split(' ')[0].split('/')[2] }} - Todos os direitos reservados</p>
        </div>
    </body>
    </html>
    """
    
    # Renderiza o template com os dados
    template = jinja2.Template(html_content)
    return template.render(**data) 