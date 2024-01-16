# ---------------- Pacotes ---------------- # 
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import yfinance as yf
import plotly.express as px
import plotly.colors as pcolors
import plotly.graph_objects as go
from scipy.optimize import minimize
import pandas_datareader as pdr
import warnings


# ---------------- Arquivos ---------------- # 
# yf.pdr_override() #corrige problemas da bibliotece do pandas_datareader
acoes = pd.read_csv('https://raw.githubusercontent.com/jrodrigotico/Portfolio-Markowitz/main/arquivos_csv/base_acoes.csv', sep=';')[['Código','Subsetor Bovespa']]
acoes = acoes[acoes['Código'].apply(lambda x: len(str(x))==5)]

selic = pd.read_csv('https://raw.githubusercontent.com/jrodrigotico/Portfolio-Markowitz/main/arquivos_csv/selic.csv', sep=';')
selic['Data'] = pd.to_datetime(selic['Data'], dayfirst=True)


# ---------------- Introducao ---------------- # 
def introducao(): # funcao para exibir a introducao e seus componentes
    introducao = st.container()
    introducao.header('Teoria Moderna do Portfólio - Markowitz')
    introducao.markdown('''A Teoria Moderna do Portfólio, desenvolvida por Harry Markowitz em meados de 1950, 
                    diz que diferentes ativos podem compor 'n' carteiras de investimentos com o intuito de encontrar
                    uma relação ótima entre risco e retorno. Para determinar essa relação, Markowitz não descarta o uso do 
                    julgamento profissional na escolha dos ativos, utilizando critérios específicos que não são contemplados nos cálculos 
                    matemáticos.''')
    st.text('\n')
    introducao.markdown('''A teoria tem como principal objetivo diminuir o 'Risco Diversificável', que consiste 
                    no risco que pode ser eliminado por meio da diversificação da carteira de investimentos. Diferentemente 
                    do 'Risco Não-Diversificável', que não pode ser eliminado pela diversificação, pois suas flutuações dependem 
                    do cenário econômico como um todo.''')
    st.text('\n')
    introducao.markdown('''Markowitz é o principal responsável por introduzir conceitos de diversificação de ativos, 
                    contribuindo significativamente para o aprimoramento das estratégias de investimentos.''')
    
    # Fonte: The Nobel Prize
    introducao.image('https://raw.githubusercontent.com/jrodrigotico/Portfolio-Markowitz/main/imagens/img_introducao.jpg', caption='Fonte: The Nobel Prize')

exibir_introducao = st.session_state.get('exibir_introducao', True)

if exibir_introducao:
    introducao()
    # remove a introdução
    if st.button('Simulação de Carteiras :bar_chart: '):
        st.session_state['exibir_introducao'] = False # transforma a chave que carrega a introducao em falsa
        st.experimental_rerun() # recarrega a página


# --------- Código geral ---------- #
if not exibir_introducao:
    st.markdown(''':calendar: O intervalo de tempo considerado está entre 16/01/2013 e 01/11/2023, 
                sendo possível selecionar a periodicidade dos preços das ações. ''')
    st.text('\n')

    st.markdown(''':grey_question: Utilizou-se o 'Subsetor' em vez do 'Segmento' de cada ação na B3 para simplificar a seleção das ações.''')
    st.text('\n')

    st.markdown(''':heavy_exclamation_mark: Esperar gráfico de preços de uma ação ser plotado antes de selecionar outra ação ''')
    st.text('\n')

    st.markdown('''	:flag-br: A taxa livre de risco (*Risk-Free*) escolhida foi a **SELIC**, que será utilizada no cálculo do Índice de Sharpe. Optou-se por 
            utilizar a média aritmética da **SELIC** durante o intervalo de tempo selecionado.''')
    st.text('\n')

    st.markdown(''':dollar: No que diz respeito à simulação, não há uma regra definida para o número de portfolios a serem simulados, porém
                é necessário no mínimo duas ações para compor um portfólio.''')
    st.write('---')

    st.sidebar.header('Parâmetros')

    data_minima = dt.date(2013,1,16)
    data_maxima = dt.date(2023,11,30)

    data_i = st.sidebar.date_input('Data inicial', format='YYYY-MM-DD', value=None, min_value=data_minima, max_value=data_maxima)
    data_i = pd.Timestamp(data_i)
    data_f = st.sidebar.date_input('Data final',  format='YYYY-MM-DD', value=None, min_value=data_minima, max_value=data_maxima)
    data_f = pd.Timestamp(data_f)
    peridiocidade = st.sidebar.selectbox('Peridiocidade', ('Diário', 'Mensal', 'Anual'))

    # seleção de subsetor da empresa
    subsetor = st.sidebar.multiselect('Subsetor', sorted(acoes['Subsetor Bovespa'].unique()))

    # acoes filtradas pelo subsetor
    filtro_subsetor = acoes.loc[acoes['Subsetor Bovespa'].isin(subsetor)].iloc[:,0] # esse iloc retorna as acoes de determinado subsetor que foi anteriormente selecionado, é zero pq o 0 representa a coluna de códigos que é o que eu desejo que retorne
    filtro_subsetor = pd.DataFrame(filtro_subsetor)

    # retirar tickers que deram problema com o yahoo finance
    acoes_erro = pd.read_csv('https://raw.githubusercontent.com/jrodrigotico/Portfolio-Markowitz/main/arquivos_csv/erro_acao.csv', sep=';') 
    acoes_erro.columns = ['Index', 'Ticker']

    # funcao para retirar '.SA' mantendo apenas os primeiros 5 caracteres
    def retirar_sa(i):
        return i[:5]

    acoes_erro['Ticker'] = acoes_erro['Ticker'].apply(retirar_sa)
    valores_fixos = ~filtro_subsetor['Código'].isin(acoes_erro['Ticker'])
    filtro_subsetor = filtro_subsetor[valores_fixos] # mantem os valores que nao estao em 'acoes_erro'

    # filtro de acoes depois de selecionados os subsetores
    selecionar_acoes = st.sidebar.multiselect('Ações', sorted(filtro_subsetor['Código'] + '.SA'))
    st.set_option('deprecation.showPyplotGlobalUse', False)


    # ---------------- Dados das ações selecionadas ---------------- #
    # objetos vazios a serem populados
    tabelas_acoes = []  
    tabela_norm = pd.DataFrame()
    valores_iniciais = {}
    indices_iniciais = {}

    if selecionar_acoes:
        for i in selecionar_acoes:
            try:
                tabela_acao = round(yf.download(i, start=data_i, end=data_f)["Adj Close"].rename(i), 2)
            except Exception as erro:
                print(f'Erro ao baixar {i}: {erro}')

            if peridiocidade=='Mensal':
                tabela_acao = tabela_acao.resample('M').last()
            elif peridiocidade == 'Anual':
                tabela_acao = tabela_acao.resample('Y').last()
            else:
                tabela_acao = tabela_acao
            tabelas_acoes.append(tabela_acao)

            # primeiro valor e seu índice para cada ação
            primeiro_valor = tabela_acao.first_valid_index()
            if primeiro_valor:
                valores_iniciais[i] = tabela_acao.loc[primeiro_valor]
                indices_iniciais[i] = primeiro_valor

        tabela = pd.concat(tabelas_acoes, axis=1)

        st.subheader(f'Preço das ações - {peridiocidade}')
        
        st.markdown('''Os preços das ações selecionadas ao longo do intervalo de tempo estão normalizados. 
                    Essa normalização garante que o preço de todas as ações comece a partir do mesmo valor, 
                    possibilitando a comparação e sem alterar o comportamento dessas ações.''')
        
        for i in tabela.columns:
            if i in valores_iniciais and i in indices_iniciais: # normaliza usando o primeiro valor válido de cada ação, se disponível
                first_valid_index = indices_iniciais[i]
                tabela_norm[i[:5]] = round(tabela[i] / valores_iniciais[i], 2) # ignora o '.SA'
            else:
                first_valid_index = tabela[i].first_valid_index()
                if first_valid_index:
                    tabela_norm[i[:5]] = round(tabela[i] / tabela[i].loc[first_valid_index], 2)
                else:
                    tabela_norm[i[:5]] = tabela[i]

        # Plotar o gráfico com todas as ações selecionadas considerando intervalo em que determinada ação ainda nao existia e portanto preço igual a zero
        grafico2 = px.line(tabela_norm)
        grafico2.update_layout(width=800, height=500)
        st.plotly_chart(grafico2)

        # Retornos Contínuos e Matriz de Correlação
        st.write('---')
        st.header('Médias dos retornos de cada ação:')
        st.markdown('''Foi utilizado o retorno contínuo para o cálculo do retorno de cada ação, em seguida, 
                    foi-se calculada a média para cada ação.\n''')
        tabela_retorn = tabela_norm.pct_change() # aqui se faz a formula de variacao percentual: 'Valor f/Valor i - 1 '
        retorno_contiuo = np.log(tabela_retorn + 1) # aqui soma-se 1 para ficar apenas a divisao entre 'Valor f/Valor i' e o LN é aplicado nessa divisão

        # funcao para média
        def media(i):
            return i.mean()
        media_retor = retorno_contiuo.apply(media, axis = 0) # compara os valores das linhas
        
        for i, z in zip(media_retor, selecionar_acoes):
            porcent = i * 100
            if porcent > 0:
                st.markdown(f'**{z}** &mdash; {round(i*100,4)} % :white_check_mark:  ')
            else:
                st.markdown(f'**{z}** &mdash; {round(i*100,4)} % :warning:')

        # verificação de '-inf %' e 'inf %'
        acoes_inf = media_retor[np.isinf(media_retor)]
        if np.isinf(media_retor).any():
            st.text('\n')
            st.warning(f'''Ação(ões) com média de retorno contínuo muito próximo de zero: **{acoes_inf.index[0]}**.
                    Recomenda-se tirá-la(s) da simulação :heavy_exclamation_mark:''')

        # tratamento caso exista apenas uma ação
        if len(selecionar_acoes)<=1:
            st.warning('''Para a composição de uma carteira de investimentos 
                    são necessários no mínimo 2 ativos! :heavy_exclamation_mark:''')

        matriz_corr = round(tabela_retorn.corr(),4)

        st.write('---')
        st.header('Matriz de correlação:')
        st.markdown('''A partir dos retornos de cada ativo, é possível calcular a correlação entre eles. A correlação explica
                    o grau de relação entre os ativos.''')
        st.text('\n')
        st.markdown('''Deve-se evitar ativos com grau de correlação próximos de 1 ou -1, pois convergem mais intensamente no mesmo sentido,
                    tanto do lado positivo como do lado negativo.''')
        st.text('\n')
        st.markdown('''Portanto, quanto menor a correlação entre os ativos ou até mesmo quanto mais negativa,
                    menor será o risco dessa carteira se comparada aos ativos individuais ''')
        
        heatmap_retorn = px.imshow(matriz_corr, text_auto=True)
        st.plotly_chart(heatmap_retorn)


    # ---------------- SELIC tratamento ---------------- #
    selic = selic.loc[(selic['Data'] >= data_i) & (selic['Data'] <= data_f)]
    selic['Taxa SELIC'] = selic['Taxa SELIC'].str.replace(',','.').astype(float)    
    ret_livre = selic['Taxa SELIC'].dropna().mean()/100


    # ---------------- Simulação ---------------- #
    fator_periodicidade = []
    numero_portfolios = st.sidebar.number_input('Número de portfolios')
    def parametros_portofolio (numero_portfolios):
        
        #objetos primeiramente zerados que serão usados para simulação de n carteiras
        tabela_retorn_esperados = np.zeros(numero_portfolios)
        tabela_volatilidades_esperadas = np.zeros(numero_portfolios)
        tabela_sharpe = np.zeros(numero_portfolios)
        tabela_pesos = np.zeros((numero_portfolios, len(selecionar_acoes)))
        tabela_retorn_esperados_aritm = np.zeros(numero_portfolios)

        if peridiocidade == 'Mensal':
            fator_periodicidade = 12
        elif peridiocidade == 'Anual':
            fator_periodicidade = 1
        elif peridiocidade == 'Diário':
            fator_periodicidade = 252     
        
        for i in range(numero_portfolios):
            pesos_random = np.random.random(len(selecionar_acoes)) # aleatoriedade
            pesos_random /= np.sum(pesos_random)
            tabela_pesos[i,:] = pesos_random
            tabela_retorn_esperados[i] = np.sum(media_retor * pesos_random * fator_periodicidade)
            tabela_retorn_esperados_aritm[i] = np.exp(tabela_retorn_esperados[i])-1
            tabela_volatilidades_esperadas[i] =  np.sqrt(np.dot(pesos_random.T, np.dot(matriz_corr * fator_periodicidade, pesos_random))) # formula principal para calcular risco da carteira
            tabela_sharpe[i] = (tabela_retorn_esperados[i] - ret_livre) / tabela_volatilidades_esperadas[i] # formula do IS
            
        indice_sharpe_max = tabela_sharpe.argmax() # valor máximo para carteira ótima
        carteira_max_retorno = tabela_pesos[indice_sharpe_max]
        menor_risco = tabela_volatilidades_esperadas.argmin() # valor minimo para carteira de mínimo risco
        carteira_min_variancia= tabela_pesos[menor_risco]

        st.write('---')
        st.header('Carteira de Mínima Variância:')
        st.markdown('''Para uma determinada combinação de pesos de ativos em uma carteira, há um ponto que representa o risco mínimo.
                    Esse ponto representa a Carteira de Mínimo Risco ou Carteira de Mínima Variância.''')
        
        legenda = selecionar_acoes
        valores_cart_min_var = carteira_min_variancia
        graph_pizza2 = go.Figure(data=[go.Pie(labels=legenda, values =valores_cart_min_var )])
        st.plotly_chart(graph_pizza2)

        st.header('Carteira Ótima:')
        st.markdown('''Para a determinação da Carteira Ótima foi utilizado o 'Índice de Sharpe'.''')
        st.text('\n')            
        st.markdown('''O ponto que representa a carteira ótima
                        mostra a combinação de ativos para ter um ganho a partir de uma taxa livre de risco, ou seja, existe uma carteira
                        de ativos com alta chance de ser preferível às demais combinações de carteiras.''')    
        
        legenda = selecionar_acoes
        valores_cart_max_retorno = carteira_max_retorno
        graph_pizza = go.Figure(data=[go.Pie(labels=legenda, values =valores_cart_max_retorno )])
        st.plotly_chart(graph_pizza)

        # restrições PPL para curva de fronteira eficiente
        def pegando_retorno (peso_teste):
            peso_teste = np.array(peso_teste)
            retorno = np.sum(media_retor * peso_teste) * fator_periodicidade
            retorno = np.exp(retorno) - 1 # aqui estou passando os retornos para aritmeticos
            return retorno
        
        # soma dos pesos deve ser igual a 1 (100%)
        def checando_soma_pesos(peso_teste):
            return np.sum(peso_teste)-1
        
        # multiplicacao de matrizes
        def pegando_vol(peso_teste):
            peso_teste = np.array(peso_teste)
            vol = np.sqrt(np.dot(peso_teste.T, np.dot(matriz_corr * fator_periodicidade, peso_teste)))
            return vol
        
        peso_inicial = [1/len(selecionar_acoes)] * len(selecionar_acoes)  # pesos iguais para todas as acoes
        limites = tuple([(0,1) for i in selecionar_acoes])   # aqui nenhuma acao pode ter mais que 100%
        
        # testando as restrições
        eixo_x_fronteira_eficiente = []
        fronteira_eficiente_y = np.linspace(tabela_retorn_esperados_aritm.min(), tabela_retorn_esperados_aritm.max(), 200)

        for retorno_possivel in fronteira_eficiente_y:
            restricoes = ({'type':'eq', 'fun':checando_soma_pesos},
                        {'type':'eq', 'fun' : lambda weight: pegando_retorno(weight) - retorno_possivel}) # é um dicionario de restricoes, quando a igualdade ('eq') for zero é pq a restricao fo satisfeita
            result = minimize(pegando_vol, peso_inicial, method='SLSQP', bounds = limites, constraints = restricoes)
            eixo_x_fronteira_eficiente.append(result['fun'])
        
        st.write('---')

        st.header(f'Gráfico com a simulação de {numero_portfolios} carteiras: ') 
        st.markdown(f'Taxa livre de risco (SELIC) média: {round(ret_livre*100,4)}%')   

        # condições IS
        sharpe_max = ((tabela_retorn_esperados_aritm[indice_sharpe_max] - ret_livre) / tabela_volatilidades_esperadas[indice_sharpe_max])
        if sharpe_max >0:
            st.markdown(f'Índice de Sharpe Máximo: {round(sharpe_max,4)} :white_check_mark:')
        else:
            st.markdown(f'Índice de Sharpe Máximo: {round(sharpe_max,4)} :warning:')
        
        if 0.5>sharpe_max>0:
            st.warning(f'''O índice de Sharpe de {round(sharpe_max,4)} diz que para cada 1 ponto de risco,
                    o investidor obtém um retorno positivo de {round(sharpe_max,4)} pontos de rentabilidade acima da rentabilidade que
                    esse investidor teria caso optasse por investir em um ativo livre de risco, porém ainda é menor do que 0.5, com isso
                    o investimento na carteira não é bom!''')
        if sharpe_max>0.5:
            st.warning(f'''O índice de Sharpe de {round(sharpe_max,4)} diz que para cada 1 ponto de risco,
                    o investidor obtém um retorno positivo de {round(sharpe_max,4)} pontos de rentabilidade acima da rentabilidade que
                    esse investidor teria caso optasse por investir em um ativo livre de risco. Além disso, o Índice de Sharpe é superior
                    a 0.5, com isso o investimento na carteira é bom e compensa o risco.''')
        elif sharpe_max<0:
            st.warning(f'''O índice de Sharpe de {round(sharpe_max,4)} diz que para cada 1 ponto de risco,
                    o investidor obtém um retorno negativo de {round(sharpe_max,4)}. Com isso o investimento na carteira não compensa o risco.''')
        elif sharpe_max=='nan':
            st.warning('Algum ativo escolhido apresenta média de retorno igual a zero ou nan''')


        # ---------------- Gráfico Simulação ---------------- #
        carteiras_simulacao = go.Scatter(x=tabela_volatilidades_esperadas,y=tabela_retorn_esperados_aritm,mode='markers',
            marker=dict(size=8, color=tabela_sharpe, colorscale='Viridis'), name = 'Carteiras Simuladas')

        carteira_max_sharpe = go.Scatter(x=[tabela_volatilidades_esperadas[indice_sharpe_max]], y=[tabela_retorn_esperados_aritm[indice_sharpe_max]],
            mode='markers', marker= dict(size=12, color='red'), name = 'Carteira Ótima')

        carteira_min_variancia = go.Scatter(x=[tabela_volatilidades_esperadas[menor_risco]], y=[tabela_retorn_esperados_aritm[menor_risco]],
            mode='markers', marker= dict(size=12, color='pink'), name = 'Carteira de Mínima Variância') # essa carteira é importante lembrar do ponto de 'inflexão'

        fronteira_eficiente = go.Scatter(x=eixo_x_fronteira_eficiente, y=fronteira_eficiente_y,
                                    mode='lines', line=dict(color='green', width=2),
                                    name='Fronteira Eficiente')
        
        # Criação do gráfico Plotly com todos os dados
        layout = go.Layout(xaxis=dict(title='Risco esperado'), yaxis=dict(title='Retorno esperado'))
        pontos_dispersao = [carteiras_simulacao, carteira_max_sharpe, carteira_min_variancia, fronteira_eficiente]
        fig = go.Figure(data=pontos_dispersao, layout=layout)
        st.plotly_chart(fig)

        st.text('\n')
        st.markdown('''A Hipérbole de Markowitz, ou Fronteira Eficiente, demonstra as várias combinações de carteiras considerando
                    um conjunto de ativos. Matematicamente falando, esse conceito revela a importância da diversificação na construção
                    de uma carteira ao analisar a relação entre retorno e risco.''')
        st.text('\n')
        st.markdown('''Os pares ordenados abaixo do par ordenado da carteira de mínima variância, representam portófilios não eficientes, devido
                    ao fato de que há um aumento do risco e diminuição do retorno''')
        st.text('\n')
        st.markdown('''A teoria de Markowitz evidencia que o desempenho conjunto de ativos dentro de uma carteira
                    é superior ao desempenho desses mesmos ativos quando analisados individualmente. Isso enfatiza a relevância da interação
                    e do equilíbrio entre diferentes investimentos para otimizar tanto o potencial de retorno quanto a redução do risco
                    associado a uma carteira de investimentos. ''')


    # ---------------- Principais fórmulas e referências utilizadas no trabalho ---------------- #   
    if st.sidebar.button('Simular'):
        parametros_portofolio (int(numero_portfolios))
        st.write('---')
        with st.expander('Princpais fórmulas'):
            st.latex(r'''RetornoCarteira =  \sum_{i=1} WiRi''')
            st.write('\n')
            st.latex(r'''RetornoContínuo = \ln{\left(Retorno_t /Retorno_t-1\right) } ''')
            st.write('\n')
            st.latex(r''' IndíceSharpe = \left(\frac{{Retorno-Taxa\quad livre\quad de\quad risco}}{{Risco}} \right)''')
            st.write('\n')
            st.latex(r'''RiscoCarteira =  \sqrt{\left(Wa^2 \cdot \sigma a^2\right) + \left(Wb^2 \cdot \sigma b^2\right) + 2 \cdot \left( Wa \cdot Wb \cdot \rho ab \cdot \sigma a  \cdot \sigma b  \right)}''')
            st.write('\n')
            st.latex(r'''\text{alternativamente pode-se usar a covariância entre os ativos} \\
                \text {multiplicada pelos seus respectivos pesos}''')
            st.latex(r'''RiscoCarteira =  \sqrt{\left(Wa^2 \cdot \sigma a^2\right) + \left(Wb^2 \cdot \sigma b^2\right) + 2 \cdot \left( Wa \cdot Wb \cdot covab\right)}''')
        with st.expander('Referências'):
            st.latex(r'''\text{MARKOWITZ, Harry. Portfolio selection. The Journal of Finance,}\\
                    \text {v. 7, n. 1, p. 77-91, Mar. 1952}''')
            st.latex(r'''\text{Guasti Lima, Fabiano. Análise de Risco. Atlas, 2016}''')
            st.latex(r'''\text{Assaf Neto, Alexandre. Mercado Financeiro. Décima Terceira Edição. Atlas}''')
            st.latex(r'''\text{Canal Brenno Sullivan - VAROS Quant }''')
            st.latex(r'''\text{Streamlit Documentaion - https://docs.streamlit.io}''')