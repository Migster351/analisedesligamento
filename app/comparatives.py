#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para comparação entre períodos
"""

from . import analytics

# Definição das frases de insights por área
INSIGHT_PHRASES = {
    'lideranca': {
        'positive': "Houve uma melhora significativa na percepção da liderança no período analisado, com aumento de {var:.1f}% na média de satisfação.",
        'negative': "A liderança apresentou queda de {var:.1f}% na avaliação dos colaboradores, indicando possível falha de comunicação ou gestão.",
        'neutral': "Liderança manteve estabilidade no período, sem variações expressivas nos indicadores de satisfação."
    },
    'remuneracao': {
        'positive': "Remuneração foi um dos principais pontos positivos, com um crescimento de {var:.1f}% na avaliação média.",
        'negative': "Remuneração foi apontada como o ponto mais crítico, com queda de {var:.1f}% na média de satisfação.",
        'neutral': "A percepção sobre remuneração se manteve estável, sem sinais de piora ou melhora relevantes."
    },
    'comunicacao': {
        'positive': "Houve avanço na clareza e transparência da comunicação interna, com melhora de {var:.1f}% na avaliação.",
        'negative': "A comunicação foi uma área sensível, com queda de {var:.1f}% nos indicadores — possível foco de intervenção.",
        'neutral': "Os dados apontam estabilidade na avaliação da comunicação corporativa."
    },
    'beneficios': {
        'positive': "Os benefícios oferecidos foram mais bem avaliados neste período, com ganho de {var:.1f}% no score médio.",
        'negative': "A avaliação dos benefícios caiu em {var:.1f}%, o que pode indicar insatisfação com mudanças ou percepção de perda de valor.",
        'neutral': "Benefícios permaneceram com percepção estável, sem grandes alterações."
    },
    'cultura': {
        'positive': "A cultura organizacional foi percebida de forma mais positiva, com crescimento de {var:.1f}% na avaliação geral.",
        'negative': "A percepção sobre a cultura organizacional apresentou queda de {var:.1f}%, indicando possível desalinhamento de valores.",
        'neutral': "Cultura organizacional foi avaliada de forma estável, mantendo o mesmo nível de percepção anterior."
    },
    'relacionamento': {
        'positive': "O relacionamento interpessoal entre colegas foi melhor avaliado neste período, com aumento de {var:.1f}%.",
        'negative': "Houve queda de {var:.1f}% na avaliação do relacionamento com colegas, o que pode sinalizar tensões internas.",
        'neutral': "O relacionamento com colegas manteve-se em linha com períodos anteriores, sem grandes oscilações."
    }
}

def compare_periods(period1_type, period1_value, period2_type, period2_value):
    """Compara dois períodos e retorna as diferenças"""
    # Obtém análises dos dois períodos
    analysis1 = analytics.analyze_period(period1_type, period1_value)
    analysis2 = analytics.analyze_period(period2_type, period2_value)
    
    # Verifica se há dados para ambos os períodos
    if analysis1 is None or analysis2 is None:
        return None
    
    # Estrutura para armazenar a comparação
    comparison = {
        'period1': {
            'type': period1_type,
            'value': period1_value,
            'count': analysis1['count']
        },
        'period2': {
            'type': period2_type,
            'value': period2_value,
            'count': analysis2['count']
        },
        'areas': {},
        'alerts': []
    }
    
    # Compara cada área
    for area in analytics.AREAS:
        if area in analysis1['areas'] and area in analysis2['areas']:
            # Extrai médias dos dois períodos
            mean1 = analysis1['areas'][area]['mean']
            mean2 = analysis2['areas'][area]['mean']
            
            # Calcula variação percentual
            if mean1 > 0:
                variation_pct = ((mean2 - mean1) / mean1) * 100
            else:
                variation_pct = 0 if mean2 == 0 else 100
            
            # Determina direção da variação
            variation_direction = 'neutral'
            if abs(variation_pct) < 5:  # Menos de 5% de variação é considerado estável
                variation_direction = 'neutral'
            elif variation_pct > 0:
                variation_direction = 'positive'
            else:
                variation_direction = 'negative'
            
            # Armazena dados da comparação
            comparison['areas'][area] = {
                'period1': analysis1['areas'][area],
                'period2': analysis2['areas'][area],
                'variation_pct': variation_pct,
                'variation_direction': variation_direction
            }
            
            # Gera alerta se variação negativa for maior que 10%
            if variation_pct <= -10:
                comparison['alerts'].append({
                    'area': area,
                    'severity': 'high' if variation_pct <= -20 else 'medium',
                    'message': f"Alerta: {area.capitalize()} apresentou queda de {abs(variation_pct):.1f}% na média de satisfação."
                })
    
    return comparison

def generate_comparison_insights(comparison_data):
    """Gera insights automáticos com base na comparação entre períodos"""
    if comparison_data is None:
        return {}
    
    insights = {}
    
    # Gera um insight para cada área
    for area, data in comparison_data['areas'].items():
        variation_pct = data['variation_pct']
        variation_direction = data['variation_direction']
        
        # Seleciona a frase adequada com base na direção da variação
        if area in INSIGHT_PHRASES:
            insight_template = INSIGHT_PHRASES[area][variation_direction]
            insights[area] = insight_template.format(var=abs(variation_pct))
    
    # Adiciona insight geral
    positive_vars = [d['variation_pct'] for a, d in comparison_data['areas'].items() if d['variation_direction'] == 'positive']
    negative_vars = [d['variation_pct'] for a, d in comparison_data['areas'].items() if d['variation_direction'] == 'negative']
    
    if len(positive_vars) > len(negative_vars):
        insights['geral'] = f"Houve uma tendência geral de melhora nas avaliações, com {len(positive_vars)} áreas apresentando crescimento."
    elif len(negative_vars) > len(positive_vars):
        insights['geral'] = f"Houve uma tendência geral de piora nas avaliações, com {len(negative_vars)} áreas apresentando queda."
    else:
        insights['geral'] = "O período apresentou um balanço equilibrado entre melhorias e pioras nas diferentes áreas."
    
    # Destaca a área com maior melhora e maior piora
    if positive_vars:
        max_positive_var = max(positive_vars)
        max_positive_area = next(a for a, d in comparison_data['areas'].items() if d['variation_pct'] == max_positive_var)
        insights['max_positive'] = f"A área de {max_positive_area.capitalize()} apresentou a maior melhora, com aumento de {max_positive_var:.1f}% na satisfação."
    
    if negative_vars:
        max_negative_var = min(negative_vars)
        max_negative_area = next(a for a, d in comparison_data['areas'].items() if d['variation_pct'] == max_negative_var)
        insights['max_negative'] = f"A área de {max_negative_area.capitalize()} apresentou a maior queda, com redução de {abs(max_negative_var):.1f}% na satisfação."
    
    return insights 