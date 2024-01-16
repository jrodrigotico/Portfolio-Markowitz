[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://portfolio-markowitz.streamlit.app)
[![Python Version](https://img.shields.io/badge/python-3.11.6-blue.svg)](https://www.python.org/downloads/)
![GitHub License](https://img.shields.io/github/license/jrodrigotico/python)
![Em desenvolvimento](https://img.shields.io/badge/status%20:%20em%20desenvolvimento%20-8A2BE2)


## 	:school: Teoria Moderna do Portfolio - Markowitz
A Teoria Moderna do Portfólio, desenvolvida por Harry Markowitz em meados de 1950, postula que diferentes ativos podem compor 'n' carteiras de investimentos com o intuito de encontrar uma relação ótima entre risco e retorno. 
Markowitz é o principal responsável por introduzir conceitos de diversificação de ativos, contribuindo significativamente para o aprimoramento das estratégias de investimentos.


## 	:books: Estrutura do repositório
| **Arquivo** | **Conteúdo** |
| ------------- | ------------- |
| app_streamlit.py | Script da aplicação web |
| arquivos_csv | Arquivos no formato '.csv' que são utilizados em 'app_streamlit.py' |
| arquivos_pdf | Trabalho original de Harry Markowitz |
| imagens | Arquivos em '.jpg' utilizados no script 'app_streamlit.py' |
| requirements.txt | Dependências do projeto |


## 	:scissors: Tratamento dos dados
A taxa **SELIC** foi selecionada como a taxa livre de risco para calcular o **Índice de Sharpe**. Os dados estão disponíveis para o período entre 16/01/2013 e 31/11/2023 em 'selic.csv' na pasta 'arquivos'.

Ações brasilerias precisam estar com **'.SA'** para servirem como símbolo no 'Yahoo Finance' e assim extrair informações.

A ação da empresa **Allos (ALOS3)** está no subsetor **'Outros'**.

No arquivo **'base_acoes.csv'**, localizado na pasta 'arquivos_csv', consta uma lista de todas as ações listadas na B3, conforme base do **Economatica** em 14/12/2023. Ações com tickers de seis caracteres foram retiradas, pois não são acessíveis via API do Yahoo Finance.

Algumas ações apresentaram problemas durante a extração de dados da API do Yahoo Finance, então essas empresas foram excluídas da lista de tickers. Os detalhes dessas ações estão no arquivo **'erro_acoes.csv'**, na pasta 'arquivos_csv'.


## :bar_chart: Demonstração da aplicação

![Teoria Moderna de Portfólio - Markowitz](https://youtu.be/xDNOIRyIDgw)

Para a plotagem dos gráficos foi utilizado o pacote 'Plotly' (https://plotly.com) por possuir recursos interativos que auxiliam a visualização dos dados.


## 	:desktop_computer: Acesso ao aplicativo
Clone do repositório:

```
git clone https://github.com/jrodrigotico/Portfolio-Markowitz.git
```

Instalação das depedências:

```
pip install -r requirements.txt
```

Rodar o script 'app_streamlit.py' e aplicar o seguinte comando no terminal:
```
streamlit run app_streamlit.py
```

Alternativamente, pode-se acessar o aplicativo por qualquer navegador pelo link:
https://portfolio-markowitz.streamlit.app.    


## :mag_right: Tecnologias utilizadas
- ``Python - 3.11.6``
- ``API Yahoo Finance (yfinance - v0.2.33)``
- ``Streamlit``
- ``Visual Studio Code``


## 	:email: Contato
Para feedbacks, sugestão de melhorias ou relato de problemas, sinta-se à vontade para entrar em contato comigo através do meu perfil no Linkedin:

[![LinkedIn Badge](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/joão-rodrigo-lemes-5603a6154/)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jrodrigo)

