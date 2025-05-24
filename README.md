
# 📊 Projeto: Sistema Local de Análise de Entrevistas de Desligamento

## 🎯 Objetivo
Desenvolver um sistema web local para análise automatizada de entrevistas de desligamento, permitindo diagnósticos estratégicos com base em dados de múltiplos períodos. O sistema funcionará inteiramente offline, com interface em navegador, processamento local e geração de relatórios PDF, gráficos interativos, comparações temporais e exportações para uso externo.

---

## 🧱 Estrutura Geral do Projeto

```
projeto-desligamentos/
│
├── app/                         # Lógica da aplicação
│   ├── main.py                  # Backend principal com Flask
│   ├── analytics.py             # Funções de análise de dados
│   ├── visualizations.py        # Geração de gráficos
│   ├── comparatives.py          # Comparações entre períodos
│   └── report_generator.py      # Geração de relatório PDF com insights
│
├── database/                    # Pasta para arrastar arquivos CSV
│   └── desligamentos_*.csv
│
├── static/
│   └── charts/                  # Gráficos gerados para visualização
│
├── templates/
│   ├── index.html               # Interface do usuário
│   ├── compare.html             # Página de comparações
│   └── report_template.html     # Template para PDF
│
├── requirements.txt             # Bibliotecas necessárias
├── README.md                    # Documentação de uso
└── run.py                       # Script principal para rodar o app
```

---

## ⚙️ Funcionalidades

- Upload simples via pasta local (`/database`)
- Leitura automática de múltiplos arquivos CSV
- Análise de dados quantitativos e qualitativos
- Filtros por períodos: mês, trimestre, semestre, ano, geral
- Comparações entre períodos distintos
- Detecção de palavras-chave em comentários abertos
- Geração de gráficos:
  - Barras, radar, pizza, linha do tempo, wordcloud
- Geração de alertas automáticos por variação negativa
- Exportação dos resultados em:
  - `.pdf` com visual profissional e insights automáticos
  - `.xlsx` com tabelas comparativas
  - `.csv` para uso em Excel ou Power BI

---

## 🔁 Sessão de Comparações

Permite ao gestor comparar dois recortes temporais (ex: Semestre 1 vs Semestre 2), gerando:
- Comparações visuais lado a lado
- Alertas de piora ou melhora
- Texto automático de diagnóstico por área

---

## 📌 Tecnologias e Especialidades Necessárias

### 🔹 Backend Python (Dev Python)
- Flask
- Pandas
- Plotly / Matplotlib / Seaborn
- Wordcloud
- WeasyPrint (PDF via HTML)
- Jinja2 (templating)

### 🔹 Frontend Web (Dev Front-End)
- HTML5 / CSS3
- Bootstrap 5
- JavaScript básico (eventos, DOM)

### 🔹 Análise de Dados
- Estruturação de base de dados tabular (CSV)
- Tratamento de textos (NLP local)
- Construção de dashboards com indicadores visuais

---

## 📦 Requisitos Técnicos

- Python 3.9+
- Rodar localmente sem conexão com internet
- Compatível com máquinas de uso corporativo (Windows/Linux)
- Instalação simples via `pip install -r requirements.txt`
- Abrir via navegador local (`http://localhost:5000`)

---

## 📝 Insights Automáticos

Geração automática de frases como:

> "A liderança apresentou melhora de 15% no segundo semestre."
> 
> "Remuneração foi o ponto mais crítico, com score abaixo de 3 nos últimos dois trimestres."

Esses textos serão inseridos:
- No dashboard
- Nos relatórios PDF
- Na aba comparativa

---

## 🔒 Segurança

- Totalmente offline
- Sem upload para nuvem
- Seguro para dados sensíveis de RH

---

## 🚀 Pronto para Iniciar

Este escopo pode ser entregue para as equipes de desenvolvimento, análise de dados e design visual. A arquitetura modular permite que diferentes partes sejam desenvolvidas em paralelo.


---

## 🧠 Frases de Insights Automáticos por Área de Análise

Durante a geração de relatórios e comparações, o sistema utilizará as seguintes frases automáticas com base na variação percentual entre os períodos analisados. A variável `{var:.1f}` será substituída pelo valor real calculado.

### Liderança
- Houve uma melhora significativa na percepção da liderança no período analisado, com aumento de {var:.1f}% na média de satisfação.
- A liderança apresentou queda de {var:.1f}% na avaliação dos colaboradores, indicando possível falha de comunicação ou gestão.
- Liderança manteve estabilidade no período, sem variações expressivas nos indicadores de satisfação.

### Remuneração
- Remuneração foi um dos principais pontos positivos, com um crescimento de {var:.1f}% na avaliação média.
- Remuneração foi apontada como o ponto mais crítico, com queda de {var:.1f}% na média de satisfação.
- A percepção sobre remuneração se manteve estável, sem sinais de piora ou melhora relevantes.

### Comunicação
- Houve avanço na clareza e transparência da comunicação interna, com melhora de {var:.1f}% na avaliação.
- A comunicação foi uma área sensível, com queda de {var:.1f}% nos indicadores — possível foco de intervenção.
- Os dados apontam estabilidade na avaliação da comunicação corporativa.

### Benefícios
- Os benefícios oferecidos foram mais bem avaliados neste período, com ganho de {var:.1f}% no score médio.
- A avaliação dos benefícios caiu em {var:.1f}%, o que pode indicar insatisfação com mudanças ou percepção de perda de valor.
- Benefícios permaneceram com percepção estável, sem grandes alterações.

### Cultura Organizacional
- A cultura organizacional foi percebida de forma mais positiva, com crescimento de {var:.1f}% na avaliação geral.
- A percepção sobre a cultura organizacional apresentou queda de {var:.1f}%, indicando possível desalinhamento de valores.
- Cultura organizacional foi avaliada de forma estável, mantendo o mesmo nível de percepção anterior.

### Relacionamento com colegas
- O relacionamento interpessoal entre colegas foi melhor avaliado neste período, com aumento de {var:.1f}%.
- Houve queda de {var:.1f}% na avaliação do relacionamento com colegas, o que pode sinalizar tensões internas.
- O relacionamento com colegas manteve-se em linha com períodos anteriores, sem grandes oscilações.
