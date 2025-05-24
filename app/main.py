#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Backend principal da aplicação utilizando Flask
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, send_from_directory, flash
import pandas as pd
from . import analytics, visualizations, comparatives, report_generator
import glob
from werkzeug.utils import secure_filename
import os.path
from datetime import datetime

# Configuração da aplicação Flask
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Definir uma chave secreta para o aplicativo
app.config['SECRET_KEY'] = 'analise_software_2025_desligamentos_key'

# Definição dos períodos disponíveis
PERIODS = {
    'month': 'Mensal',
    'quarter': 'Trimestral',
    'semester': 'Semestral',
    'year': 'Anual',
    'all': 'Todos os Períodos'
}

# Inicialização dos dados ao carregar o aplicativo
@app.before_request
def initialize_if_needed():
    """Inicializa o aplicativo carregando os dados disponíveis se ainda não estiverem carregados"""
    if not hasattr(app, 'initialized'):
        analytics.load_data()
        app.initialized = True

@app.route('/')
def index():
    # Obter os períodos disponíveis
    available_periods = analytics.get_available_periods()
    
    # Obter os parâmetros da requisição
    period_name = request.args.get('period_type', 'year')
    
    # Verificar se o tipo de período solicitado está disponível
    if period_name not in available_periods or not available_periods[period_name]:
        # Tentar usar um período alternativo se o solicitado não estiver disponível
        for p_type in ['year', 'month', 'week']:
            if p_type in available_periods and available_periods[p_type]:
                period_name = p_type
                break
        else:
            # Se nenhum período estiver disponível
            return render_template('index.html', 
                                  analysis=None, 
                                  charts=None, 
                                  available_periods=available_periods,
                                  period_name=None,
                                  period_value=None)
    
    # Obter o valor do período selecionado
    period_value = request.args.get('period_value', available_periods[period_name][0])
    
    # Verificar se o valor do período está disponível
    if period_value not in available_periods[period_name]:
        period_value = available_periods[period_name][0]
    
    # Gerar dados de análise para o período selecionado
    analysis_data = analytics.analyze_period(period_name, period_value)
    
    # Gerar gráficos para o período selecionado
    charts = visualizations.generate_charts(analysis_data, period_name, period_value)
    
    return render_template('index.html', 
                          analysis=analysis_data, 
                          charts=charts, 
                          available_periods=available_periods,
                          period_name=period_name,
                          period_value=period_value)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Rota para analisar dados com base no período selecionado"""
    # Obter os períodos disponíveis
    available_periods = analytics.get_available_periods()
    
    if request.method == 'POST':
        period_type = request.form.get('period_type', 'all')
        period_value = request.form.get('period_value', 'all')
    else:  # GET
        # Usar parâmetros da URL ou valores padrão
        period_type = request.args.get('period_type', 'year')
        
        # Verificar se o tipo de período solicitado está disponível
        if period_type not in available_periods or not available_periods[period_type]:
            # Tentar usar um período alternativo se o solicitado não estiver disponível
            for p_type in ['year', 'month', 'week']:
                if p_type in available_periods and available_periods[p_type]:
                    period_type = p_type
                    break
        
        # Obter o valor do período
        period_value = request.args.get('period_value')
        if not period_value or period_value not in available_periods.get(period_type, []):
            # Usar o primeiro valor disponível como padrão
            period_value = available_periods.get(period_type, ['all'])[0]
    
    # Gera análises para o período selecionado
    analysis_data = analytics.analyze_period(period_type, period_value)
    
    # Gera visualizações para o período
    charts_paths = visualizations.generate_charts(analysis_data, period_type, period_value)
    
    # Gera insights automáticos
    insights = analytics.generate_insights(analysis_data)
    
    # Verifica se há alertas baseados nos dados
    alerts = analytics.generate_alerts(analysis_data)
    
    return render_template('analysis.html',
                          period_type=period_type,
                          period_value=period_value,
                          periods=PERIODS,
                          available_periods=available_periods,
                          analysis=analysis_data,
                          charts=charts_paths,
                          insights=insights,
                          alerts=alerts)

@app.route('/compare')
def compare():
    """Rota para página de comparação entre períodos"""
    available_periods = analytics.get_available_periods()
    return render_template('compare.html', 
                          periods=PERIODS,
                          available_periods=available_periods)

@app.route('/compare_periods', methods=['POST'])
def compare_periods():
    """Rota para executar a comparação entre dois períodos"""
    period1_type = request.form.get('period1_type')
    period1_value = request.form.get('period1_value')
    period2_type = request.form.get('period2_type')
    period2_value = request.form.get('period2_value')
    
    # Realiza a comparação entre os períodos selecionados
    comparison_data = comparatives.compare_periods(
        period1_type, period1_value, 
        period2_type, period2_value
    )
    
    # Gera visualizações comparativas
    charts_paths = visualizations.generate_comparison_charts(comparison_data)
    
    # Gera insights para comparação
    insights = comparatives.generate_comparison_insights(comparison_data)
    
    return render_template('comparison_results.html',
                          period1=(period1_type, period1_value),
                          period2=(period2_type, period2_value),
                          periods=PERIODS,
                          comparison=comparison_data,
                          charts=charts_paths,
                          insights=insights)

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Rota para gerar relatório PDF"""
    try:
        period_type = request.form.get('period_type', 'all')
        period_value = request.form.get('period_value', 'all')
        
        # Gera o relatório
        file_path = report_generator.generate_pdf_report(period_type, period_value)
        
        if file_path is None:
            flash('Não foi possível gerar o relatório. Tente novamente.', 'error')
            return redirect(url_for('analyze', period_type=period_type, period_value=period_value))
        
        # Determina o tipo MIME com base na extensão
        is_pdf = file_path.lower().endswith('.pdf')
        mimetype = 'application/pdf' if is_pdf else 'text/html'
        
        # Define o nome do arquivo para download
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extension = 'pdf' if is_pdf else 'html'
        download_name = f'relatorio_desligamentos_{period_type}_{period_value}_{timestamp}.{extension}'
        
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        flash(f'Erro ao gerar relatório: {str(e)}', 'error')
        return redirect(url_for('analyze', period_type=period_type, period_value=period_value))

@app.route('/export_data', methods=['POST'])
def export_data():
    """Rota para exportar dados em formatos CSV e XLSX"""
    try:
        period_type = request.form.get('period_type', 'all')
        period_value = request.form.get('period_value', 'all')
        export_format = request.form.get('format', 'csv')
        
        if export_format == 'csv':
            file_path = analytics.export_to_csv(period_type, period_value)
            mimetype = 'text/csv'
            extension = 'csv'
        else:
            file_path = analytics.export_to_excel(period_type, period_value)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            extension = 'xlsx'
        
        if file_path is None or not os.path.exists(file_path):
            flash(f'Não foi possível exportar os dados para {export_format.upper()}. Tente novamente.', 'error')
            return redirect(url_for('analyze', period_type=period_type, period_value=period_value))
        
        # Define o nome do arquivo para download
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        download_name = f'desligamentos_{period_type}_{period_value}_{timestamp}.{extension}'
        
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        flash(f'Erro ao exportar dados: {str(e)}', 'error')
        return redirect(url_for('analyze', period_type=period_type, period_value=period_value))

@app.route('/refresh_data')
def refresh_data():
    """Rota para atualizar os dados quando novos arquivos são adicionados"""
    analytics.load_data(force_reload=True)
    return redirect(request.referrer or url_for('index'))

@app.route('/comments')
def comments():
    # Obter os períodos disponíveis
    available_periods = analytics.get_available_periods()
    
    # Obter os parâmetros da requisição
    period_name = request.args.get('period_type', 'year')
    
    # Verificar se o tipo de período solicitado está disponível
    if period_name not in available_periods or not available_periods[period_name]:
        # Tentar usar um período alternativo se o solicitado não estiver disponível
        for p_type in ['year', 'month', 'week']:
            if p_type in available_periods and available_periods[p_type]:
                period_name = p_type
                break
        else:
            # Se nenhum período estiver disponível
            return render_template('comments.html', 
                                  analysis=None, 
                                  available_periods=available_periods,
                                  period_name=None,
                                  period_value=None)
    
    # Obter o valor do período selecionado
    period_value = request.args.get('period_value', available_periods[period_name][0])
    
    # Verificar se o valor do período está disponível
    if period_value not in available_periods[period_name]:
        period_value = available_periods[period_name][0]
    
    # Gerar dados de análise para o período selecionado
    analysis_data = analytics.analyze_period(period_name, period_value)
    
    return render_template('comments.html', 
                          analysis=analysis_data, 
                          available_periods=available_periods,
                          period_name=period_name,
                          period_value=period_value)

@app.route('/export')
def export_report():
    # Obter os períodos disponíveis
    available_periods = analytics.get_available_periods()
    
    # Obter os parâmetros da requisição
    period_name = request.args.get('period_type', 'year')
    
    # Verificar se o tipo de período solicitado está disponível
    if period_name not in available_periods or not available_periods[period_name]:
        # Tentar usar um período alternativo se o solicitado não estiver disponível
        for p_type in ['year', 'month', 'week']:
            if p_type in available_periods and available_periods[p_type]:
                period_name = p_type
                break
        else:
            # Se nenhum período estiver disponível
            return redirect(url_for('index'))
    
    # Obter o valor do período selecionado
    period_value = request.args.get('period_value', available_periods[period_name][0])
    
    # Verificar se o valor do período está disponível
    if period_value not in available_periods[period_name]:
        period_value = available_periods[period_name][0]
    
    # Gerar dados de análise para o período selecionado
    analysis_data = analytics.analyze_period(period_name, period_value)
    
    # Gerar gráficos para o período selecionado
    charts = visualizations.generate_charts(analysis_data, period_name, period_value)
    
    # Gerar relatório em PDF
    report_file = visualizations.generate_report(analysis_data, charts, period_name, period_value)
    
    if report_file and os.path.exists(report_file):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"relatorio_{period_name}_{period_value}_{timestamp}.pdf"
        return send_file(report_file, 
                        as_attachment=True, 
                        download_name=filename, 
                        mimetype='application/pdf')
    
    # Se falhar, redirecionar para a página inicial
    return redirect(url_for('index'))

@app.route('/manage_files', methods=['GET', 'POST', 'DELETE'])
def manage_files():
    """Rota para gerenciar arquivos de dados (listar, fazer upload, excluir)"""
    # Para requisições de exclusão (DELETE)
    if request.method == 'DELETE':
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({"status": "error", "message": "Nome de arquivo não especificado"})
        
        # Garante que não há caracteres maliciosos no nome do arquivo
        filename = secure_filename(filename)
        file_path = os.path.join(analytics.DATABASE_DIR, filename)
        
        # Verifica se o arquivo existe
        if not os.path.isfile(file_path):
            return jsonify({"status": "error", "message": "Arquivo não encontrado"})
        
        try:
            # Tenta excluir o arquivo
            os.remove(file_path)
            # Recarrega os dados para refletir as alterações
            analytics.load_data(force_reload=True)
            return jsonify({"status": "success", "message": f"Arquivo {filename} excluído com sucesso"})
        except Exception as e:
            return jsonify({"status": "error", "message": f"Erro ao excluir arquivo: {str(e)}"})
    
    # Para requisições de upload (POST)
    elif request.method == 'POST':
        # Verifica se o arquivo foi enviado
        if 'csv_file' not in request.files:
            return jsonify({"status": "error", "message": "Nenhum arquivo enviado"})
        
        file = request.files['csv_file']
        
        # Se o usuário não selecionou um arquivo
        if file.filename == '':
            return jsonify({"status": "error", "message": "Nenhum arquivo selecionado"})
        
        # Se o arquivo tem a extensão .csv
        if file and file.filename.endswith('.csv'):
            # Garante que o nome do arquivo é seguro
            filename = secure_filename(file.filename)
            file_path = os.path.join(analytics.DATABASE_DIR, filename)
            
            # Verifica se o diretório existe
            os.makedirs(analytics.DATABASE_DIR, exist_ok=True)
            
            try:
                # Salva o arquivo temporariamente para validação
                file.save(file_path)
                
                # Valida se o arquivo contém as colunas esperadas
                required_columns = ['data_desligamento'] + analytics.AREAS
                df = pd.read_csv(file_path, encoding='utf-8')
                
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    # Remove o arquivo se não for válido
                    os.remove(file_path)
                    return jsonify({
                        "status": "error", 
                        "message": f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}"
                    })
                
                # Recarrega os dados para incluir o novo arquivo
                analytics.load_data(force_reload=True)
                
                return jsonify({
                    "status": "success", 
                    "message": f"Arquivo {filename} carregado com sucesso ({len(df)} registros)"
                })
            except Exception as e:
                # Em caso de erro, tenta remover o arquivo
                if os.path.exists(file_path):
                    os.remove(file_path)
                return jsonify({"status": "error", "message": f"Erro ao processar arquivo: {str(e)}"})
        else:
            return jsonify({"status": "error", "message": "Apenas arquivos CSV são permitidos"})
    
    # Para requisições de listagem (GET)
    else:
        # Lista todos os arquivos CSV no diretório de base de dados
        csv_files = []
        
        # Certifica que o diretório existe
        os.makedirs(analytics.DATABASE_DIR, exist_ok=True)
        
        for file_path in glob.glob(os.path.join(analytics.DATABASE_DIR, '*.csv')):
            filename = os.path.basename(file_path)
            file_info = {
                'name': filename,
                'size': os.path.getsize(file_path) / 1024,  # Tamanho em KB
                'date': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d/%m/%Y %H:%M')
            }
            
            # Tenta ler o arquivo para obter informações adicionais
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
                file_info['records'] = len(df)
                file_info['columns'] = len(df.columns)
                
                # Verifica se o arquivo tem as colunas necessárias
                required_columns = ['data_desligamento'] + analytics.AREAS
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    file_info['valid'] = False
                    file_info['error'] = f"Colunas ausentes: {', '.join(missing_columns)}"
                else:
                    file_info['valid'] = True
            except Exception as e:
                file_info['valid'] = False
                file_info['error'] = str(e)
                file_info['records'] = 0
                file_info['columns'] = 0
            
            csv_files.append(file_info)
        
        # Ordena arquivos por data de modificação (mais recentes primeiro)
        csv_files.sort(key=lambda x: x['date'], reverse=True)
        
        return render_template('manage_files.html', csv_files=csv_files)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 