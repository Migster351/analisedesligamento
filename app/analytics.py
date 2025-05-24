#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para análise de dados das entrevistas de desligamento
"""

import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import re
import json

# Variável global para armazenar os dados carregados
_data_cache = None

# Diretório onde os arquivos CSV serão armazenados
DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
# Diretório para salvar exportações
EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'exports')

# Certifica-se que o diretório de exportação existe
os.makedirs(EXPORT_DIR, exist_ok=True)

# Definição das áreas de análise
AREAS = [
    'lideranca', 'remuneracao', 'comunicacao', 
    'beneficios', 'cultura', 'relacionamento'
]

def load_data(force_reload=False):
    """Carrega os dados de todos os arquivos CSV na pasta database"""
    global _data_cache
    
    # Se já temos dados carregados e não é forçada a recarga, retorna os dados em cache
    if _data_cache is not None and not force_reload:
        return _data_cache
    
    # Lista todos os arquivos CSV na pasta database
    csv_files = glob.glob(os.path.join(DATABASE_DIR, '*.csv'))
    
    if not csv_files:
        print("Nenhum arquivo CSV encontrado na pasta 'database'")
        return None
    
    # Lista para armazenar os DataFrames de cada arquivo
    dfs = []
    
    # Processa cada arquivo CSV
    for file_path in csv_files:
        try:
            # Lê o arquivo CSV assumindo que a primeira linha é o cabeçalho
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # Verifica se temos uma coluna de data no DataFrame
            if 'data_desligamento' in df.columns:
                # Converte para formato de data
                df['data_desligamento'] = pd.to_datetime(df['data_desligamento'])
                
                # Adiciona colunas para facilitar filtragem por período
                df['ano'] = df['data_desligamento'].dt.year
                df['mes'] = df['data_desligamento'].dt.month
                df['trimestre'] = df['data_desligamento'].dt.quarter
                df['semestre'] = (df['data_desligamento'].dt.month > 6).astype(int) + 1
                
                # Adiciona o DataFrame à lista
                dfs.append(df)
            else:
                print(f"Arquivo {file_path} não contém a coluna 'data_desligamento'")
        except Exception as e:
            print(f"Erro ao processar arquivo {file_path}: {str(e)}")
    
    # Se não há DataFrames válidos, retorna None
    if not dfs:
        return None
    
    # Concatena todos os DataFrames em um único
    _data_cache = pd.concat(dfs, ignore_index=True)
    
    # Ordena por data de desligamento
    _data_cache = _data_cache.sort_values('data_desligamento')
    
    return _data_cache

def get_available_periods():
    """Retorna os períodos disponíveis nos dados"""
    df = load_data()
    if df is None:
        return {}
    
    # Obtém períodos disponíveis
    result = {
        'month': sorted(df['mes'].unique().tolist()),
        'quarter': sorted(df['trimestre'].unique().tolist()),
        'semester': sorted(df['semestre'].unique().tolist()),
        'year': sorted(df['ano'].unique().tolist()),
        'all': ['Todos']
    }
    
    return result

def filter_by_period(df, period_type, period_value):
    """Filtra os dados de acordo com o período selecionado"""
    if df is None:
        return None
    
    # Se o período for 'all', retorna todos os dados
    if period_type == 'all' or period_value == 'all':
        return df
    
    # Converte period_value para inteiro se não for 'all'
    period_value = int(period_value)
    
    # Filtra de acordo com o tipo de período
    if period_type == 'month':
        return df[df['mes'] == period_value]
    elif period_type == 'quarter':
        return df[df['trimestre'] == period_value]
    elif period_type == 'semester':
        return df[df['semestre'] == period_value]
    elif period_type == 'year':
        return df[df['ano'] == period_value]
    
    # Caso nenhum dos tipos acima, retorna None
    return None

def analyze_period(period_type, period_value):
    """Analisa os dados para o período especificado"""
    df = load_data()
    
    # Filtra os dados para o período específico
    filtered_df = filter_by_period(df, period_type, period_value)
    
    if filtered_df is None or filtered_df.empty:
        return None
    
    # Resultados da análise
    analysis = {
        'count': len(filtered_df),
        'period': {
            'type': period_type,
            'value': period_value
        },
        'areas': {},
        'keywords': extract_keywords(filtered_df),
        'comments': process_comments(filtered_df),
        'overall_mean': 0.0  # Inicializa a média geral
    }
    
    # Analisa cada área
    for area in AREAS:
        if area in filtered_df.columns:
            area_data = {
                'name': area.capitalize(),
                'mean': filtered_df[area].mean(),
                'median': filtered_df[area].median(),
                'mode': filtered_df[area].mode()[0],
                'std': filtered_df[area].std(),
                'min': filtered_df[area].min(),
                'max': filtered_df[area].max(),
                'distribution': filtered_df[area].value_counts().to_dict()
            }
            analysis['areas'][area] = area_data
    
    # Calcula a média geral se houver áreas analisadas
    if analysis['areas']:
        analysis['overall_mean'] = sum(data['mean'] for data in analysis['areas'].values()) / len(analysis['areas'])
    
    # Adiciona categorias ordenadas por média (melhores e piores)
    if analysis['areas']:
        # Converte para lista para poder ordenar
        areas_list = [{'name': k.capitalize(), 'mean': v['mean']} for k, v in analysis['areas'].items()]
        # Ordena por média (decrescente para melhores, crescente para piores)
        analysis['best_categories'] = sorted(areas_list, key=lambda x: x['mean'], reverse=True)
        analysis['worst_categories'] = sorted(areas_list, key=lambda x: x['mean'])
    
    return analysis

def extract_keywords(df, comment_column='comentarios', min_freq=2):
    """Extrai palavras-chave dos comentários dos desligados"""
    if df is None or df.empty or comment_column not in df.columns:
        return {}
    
    # Filtra apenas comentários não vazios
    comments = df[comment_column].dropna().astype(str).tolist()
    
    if not comments:
        return {}
    
    # Pré-processamento de texto
    processed_comments = []
    for comment in comments:
        # Converte para minúsculas
        comment = comment.lower()
        # Remove pontuação
        comment = re.sub(r'[^\w\s]', '', comment)
        # Remove números
        comment = re.sub(r'\d+', '', comment)
        processed_comments.append(comment)
    
    # Lista de stopwords em português
    stopwords = [
        'a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo', 'as', 'até',
        'com', 'como', 'da', 'das', 'de', 'dela', 'delas', 'dele', 'deles', 'depois',
        'do', 'dos', 'e', 'ela', 'elas', 'ele', 'eles', 'em', 'entre', 'era',
        'eram', 'éramos', 'essa', 'essas', 'esse', 'esses', 'esta', 'estas', 'este',
        'estes', 'eu', 'foi', 'fomos', 'for', 'foram', 'fui', 'há', 'isso',
        'isto', 'já', 'lhe', 'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu',
        'meus', 'minha', 'minhas', 'muito', 'muitos', 'na', 'não', 'nas', 'nem',
        'no', 'nos', 'nós', 'nossa', 'nossas', 'nosso', 'nossos', 'num', 'numa',
        'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos', 'por',
        'qual', 'quando', 'que', 'quem', 'são', 'se', 'seja', 'sem', 'seu',
        'seus', 'só', 'somos', 'sou', 'sua', 'suas', 'também', 'te', 'tem',
        'tém', 'temos', 'tenho', 'teu', 'teus', 'tu', 'tua', 'tuas', 'um',
        'uma', 'você', 'vocês', 'vos'
    ]
    
    # Usando CountVectorizer para extrair as palavras-chave
    vectorizer = CountVectorizer(
        stop_words=stopwords,
        min_df=min_freq,  # Frequência mínima
        ngram_range=(1, 2)  # Unigrams e bigrams
    )
    
    # Treina o vetorizador
    X = vectorizer.fit_transform(processed_comments)
    
    # Obtém as palavras e suas contagens
    words = vectorizer.get_feature_names_out()
    counts = X.sum(axis=0).A1
    
    # Cria um dicionário de palavras-chave e suas contagens
    keywords = dict(zip(words, counts))
    
    # Ordena por contagem (mais frequentes primeiro)
    keywords = dict(sorted(keywords.items(), key=lambda item: item[1], reverse=True))
    
    return keywords

def process_comments(df, comment_column='comentarios'):
    """Processa os comentários dos desligados"""
    if df is None or df.empty or comment_column not in df.columns:
        return []
    
    # Filtra apenas comentários não vazios
    comments = df[comment_column].dropna().astype(str).tolist()
    
    # Processa os comentários (simplificado para exemplo)
    processed = []
    for comment in comments:
        processed.append({
            'text': comment,
            'length': len(comment),
            'sentiment': _simple_sentiment_analysis(comment)
        })
    
    return processed

def _simple_sentiment_analysis(text):
    """Análise de sentimento simples baseada em palavras-chave"""
    # Lista de palavras positivas e negativas em português
    positive_words = [
        'bom', 'ótimo', 'excelente', 'incrível', 'maravilhoso', 'fantástico',
        'adorei', 'gostei', 'satisfeito', 'feliz', 'contente', 'positivo',
        'recomendo', 'aprovado', 'agradável', 'melhor', 'tranquilo'
    ]
    
    negative_words = [
        'ruim', 'péssimo', 'terrível', 'horrível', 'detestei', 'odiei',
        'decepcionado', 'insatisfeito', 'triste', 'infeliz', 'negativo',
        'não recomendo', 'reprovado', 'desagradável', 'pior', 'estressante',
        'problema', 'difícil', 'complicado', 'fraco', 'errado'
    ]
    
    text_lower = text.lower()
    
    # Conta palavras positivas e negativas no texto
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Define o sentimento com base na contagem
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'

def generate_insights(analysis_data):
    """Gera insights com base nos dados analisados"""
    if analysis_data is None:
        return {}
    
    insights = {}
    
    # Gera um insight para cada área
    for area, data in analysis_data['areas'].items():
        mean_score = data['mean']
        
        # Determina o tipo de insight com base na média
        if mean_score >= 4:
            insights[area] = f"A área de {area} apresenta alto nível de satisfação, com média {mean_score:.1f}."
        elif mean_score >= 3:
            insights[area] = f"A área de {area} apresenta nível de satisfação moderado, com média {mean_score:.1f}."
        else:
            insights[area] = f"A área de {area} apresenta baixo nível de satisfação, com média {mean_score:.1f}. Requer atenção."
    
    # Adiciona insight sobre comentários
    sentiment_counts = Counter([c['sentiment'] for c in analysis_data['comments']])
    total_comments = len(analysis_data['comments'])
    
    if total_comments > 0:
        positive_percent = (sentiment_counts.get('positive', 0) / total_comments) * 100
        negative_percent = (sentiment_counts.get('negative', 0) / total_comments) * 100
        
        if positive_percent > 50:
            insights['comments'] = f"{positive_percent:.1f}% dos comentários são positivos, indicando uma percepção geral boa."
        elif negative_percent > 50:
            insights['comments'] = f"{negative_percent:.1f}% dos comentários são negativos, indicando necessidade de melhorias."
        else:
            insights['comments'] = "Os comentários apresentam um balanço entre percepções positivas e negativas."
    
    return insights

def generate_alerts(analysis_data, threshold=3.0):
    """Gera alertas baseados nos dados analisados"""
    if analysis_data is None:
        return []
    
    alerts = []
    
    # Verifica áreas com média abaixo do threshold
    for area, data in analysis_data['areas'].items():
        if data['mean'] < threshold:
            alerts.append({
                'area': area,
                'severity': 'high' if data['mean'] < 2.5 else 'medium',
                'message': f"Alerta: {area.capitalize()} apresenta média de satisfação baixa ({data['mean']:.1f})."
            })
    
    # Verifica comentários negativos
    sentiment_counts = Counter([c['sentiment'] for c in analysis_data['comments']])
    total_comments = len(analysis_data['comments'])
    
    if total_comments > 0:
        negative_percent = (sentiment_counts.get('negative', 0) / total_comments) * 100
        
        if negative_percent > 60:
            alerts.append({
                'area': 'comentários',
                'severity': 'high',
                'message': f"Alerta: {negative_percent:.1f}% dos comentários são negativos."
            })
        elif negative_percent > 40:
            alerts.append({
                'area': 'comentários',
                'severity': 'medium',
                'message': f"Alerta: {negative_percent:.1f}% dos comentários são negativos."
            })
    
    return alerts

def export_to_csv(period_type, period_value):
    """Exporta os dados para um arquivo CSV"""
    try:
        df = load_data()
        
        # Filtra os dados para o período específico
        filtered_df = filter_by_period(df, period_type, period_value)
        
        if filtered_df is None or filtered_df.empty:
            return None
        
        # Define o caminho do arquivo de saída
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(EXPORT_DIR, f'desligamentos_{period_type}_{period_value}_{timestamp}.csv')
        
        # Cria o diretório de exportação se não existir
        os.makedirs(EXPORT_DIR, exist_ok=True)
        
        # Exporta para CSV
        filtered_df.to_csv(file_path, index=False, encoding='utf-8')
        
        # Retorna o caminho absoluto do arquivo
        return os.path.abspath(file_path)
    except Exception as e:
        print(f"Erro ao exportar para CSV: {e}")
        return None

def export_to_excel(period_type, period_value):
    """Exporta os dados para um arquivo XLSX com múltiplas abas"""
    try:
        df = load_data()
        
        # Filtra os dados para o período específico
        filtered_df = filter_by_period(df, period_type, period_value)
        
        if filtered_df is None or filtered_df.empty:
            return None
        
        # Define o caminho do arquivo de saída
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(EXPORT_DIR, f'desligamentos_{period_type}_{period_value}_{timestamp}.xlsx')
        
        # Cria o diretório de exportação se não existir
        os.makedirs(EXPORT_DIR, exist_ok=True)
        
        # Cria um escritor Excel
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Aba principal com todos os dados
            filtered_df.to_excel(writer, sheet_name='Dados Gerais', index=False)
            
            # Aba com estatísticas por área
            stats_df = pd.DataFrame({
                'Area': AREAS,
                'Media': [filtered_df[area].mean() if area in filtered_df.columns else None for area in AREAS],
                'Mediana': [filtered_df[area].median() if area in filtered_df.columns else None for area in AREAS],
                'Desvio Padrao': [filtered_df[area].std() if area in filtered_df.columns else None for area in AREAS],
                'Minimo': [filtered_df[area].min() if area in filtered_df.columns else None for area in AREAS],
                'Maximo': [filtered_df[area].max() if area in filtered_df.columns else None for area in AREAS]
            })
            stats_df.to_excel(writer, sheet_name='Estatisticas', index=False)
            
            # Aba com comentários
            if 'comentarios' in filtered_df.columns:
                comments_df = filtered_df[['data_desligamento', 'comentarios']].dropna(subset=['comentarios'])
                comments_df.to_excel(writer, sheet_name='Comentarios', index=False)
            
            # Aba com palavras-chave
            keywords = extract_keywords(filtered_df)
            keywords_df = pd.DataFrame(list(keywords.items()), columns=['Palavra', 'Frequencia'])
            keywords_df.to_excel(writer, sheet_name='Palavras-Chave', index=False)
        
        # Retorna o caminho absoluto do arquivo
        return os.path.abspath(file_path)
    except Exception as e:
        print(f"Erro ao exportar para Excel: {e}")
        return None 