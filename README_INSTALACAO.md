# Sistema Local de Análise de Entrevistas de Desligamento

Este sistema permite a análise automatizada de entrevistas de desligamento, gerando insights estratégicos, gráficos, comparações entre períodos e relatórios em PDF.

## Requisitos

- Python 3.9 ou superior
- Navegador web moderno (Chrome, Firefox, Edge, etc.)
- Ambiente Linux, Windows ou macOS

## Instalação

1. Clone ou faça download deste repositório para o seu computador.

2. Instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

3. Se estiver utilizando Linux ou macOS, talvez seja necessário instalar algumas dependências adicionais para o WeasyPrint (gerador de PDF):

```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# macOS (com Homebrew)
brew install cairo pango gdk-pixbuf libffi
```

Para mais detalhes sobre a instalação do WeasyPrint em diferentes sistemas, consulte a [documentação oficial](https://weasyprint.readthedocs.io/en/stable/install.html).

## Executando o sistema

1. Navegue até a pasta do projeto e execute:

```bash
python run.py
```

2. Acesse o sistema em seu navegador através do endereço:

```
http://localhost:5000
```

## Utilização

### Preparando os dados

1. Coloque os arquivos CSV com os dados das entrevistas de desligamento na pasta `database/`.
2. O formato esperado dos arquivos CSV é:

```
data_desligamento,lideranca,remuneracao,comunicacao,beneficios,cultura,relacionamento,comentarios
2023-01-15,4,3,4,3,5,4,"Comentário do colaborador aqui"
```

Onde:
- `data_desligamento`: Data no formato YYYY-MM-DD
- `lideranca`, `remuneracao`, `comunicacao`, `beneficios`, `cultura`, `relacionamento`: Avaliações numéricas de 1 a 5
- `comentarios`: Texto livre com feedback do colaborador

### Funcionalidades principais

1. **Análise por período**: Selecione o tipo de período (mês, trimestre, semestre, ano) e visualize análises, gráficos e insights.

2. **Comparação entre períodos**: Compare dois períodos distintos para identificar tendências, melhorias ou deteriorações nas diferentes áreas.

3. **Exportação**: Exporte os dados analisados em CSV ou Excel, ou gere relatórios em PDF com todos os insights e gráficos.

## Estrutura do projeto

```
/
├── app/                       # Backend da aplicação
│   ├── __init__.py
│   ├── main.py                # Rotas e configurações Flask
│   ├── analytics.py           # Análise de dados
│   ├── visualizations.py      # Geração de gráficos
│   ├── comparatives.py        # Comparação entre períodos
│   └── report_generator.py    # Geração de relatórios PDF
│
├── database/                  # Diretório para armazenar os arquivos CSV
│
├── static/                    # Arquivos estáticos
│   ├── charts/                # Gráficos gerados
│   ├── exports/               # Exportações CSV/Excel
│   └── reports/               # Relatórios PDF gerados
│
├── templates/                 # Templates HTML
│   ├── index.html             # Página inicial
│   ├── analysis.html          # Página de análise
│   ├── compare.html           # Página de seleção para comparação
│   ├── comparison_results.html # Resultados da comparação
│   └── report_template.html   # Template para geração de PDF
│
├── requirements.txt           # Dependências Python
├── run.py                     # Script para iniciar o aplicativo
└── README_INSTALACAO.md       # Este arquivo
```

## Solução de problemas

Se encontrar problemas ao gerar gráficos ou PDFs:

1. Certifique-se de que todas as dependências estão instaladas corretamente.
2. Verifique se a pasta `database/` contém pelo menos um arquivo CSV válido.
3. Confira se as pastas `static/charts/`, `static/exports/` e `static/reports/` existem e têm permissões de escrita.

## Personalização

Você pode personalizar o sistema editando os templates HTML em `templates/` ou ajustando os parâmetros de análise nos arquivos Python em `app/`. 