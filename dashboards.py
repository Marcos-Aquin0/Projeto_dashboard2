import streamlit as st 
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go 
import openpyxl
import xlrd
import copy
import numpy as np

#função para categorizar os dados: direção do vento em graus na rosa dos ventos
def categorizar_direcao_16(dict_direcoes, graus, velocidade, indice):
    # Lista de direções com seus intervalos de graus
    direcoes = [
        ('N', (0, 11.25)), ('N', (348.75, 360)), ('NNE', (11.25, 33.75)), ('NE', (33.75, 56.25)),
        ('ENE', (56.25, 78.75)), ('E', (78.75, 101.25)), ('ESE', (101.25, 123.75)),
        ('SE', (123.75, 146.25)), ('SSE', (146.25, 168.75)), ('S', (168.75, 191.25)),
        ('SSO', (191.25, 213.75)), ('SO', (213.75, 236.25)), ('OSO', (236.25, 258.75)),
        ('O', (258.75, 281.25)), ('ONO', (281.25, 303.75)), ('NO', (303.75, 326.25)),
        ('NNO', (326.25, 348.75))]

    # Itera sobre a lista de direções e verifica o intervalo correspondente aos graus
    for direcao, (min_graus, max_graus) in direcoes:
        if min_graus <= graus < max_graus:
            dict_direcoes[direcao]['Frequencia'] += 1
            if indice not in dict_direcoes[direcao]['Indices']:
                dict_direcoes[direcao]['Indices'].append(indice)
            categorizar_velocidade(dict_direcoes[direcao], velocidade)
            break  # Sai do loop ao encontrar a direção correta

#função para categorizar a velocidade do vento de acordo com a direção
def categorizar_velocidade(dict_velocidade, velocidade):
    if 0 <= velocidade < 0.5:
        dict_velocidade['Calmaria'] += 1
    elif 0.5 <= velocidade < 2.1:
        dict_velocidade['0.5 - 2.1'] += 1
    elif 2.1 <= velocidade < 3.6:
        dict_velocidade['2.1 - 3.6'] += 1
    elif 3.6 <= velocidade < 5.7:
        dict_velocidade['3.6 - 5.7'] += 1
    elif 5.7 <= velocidade < 8.8:
        dict_velocidade['5.7 - 8.8'] += 1
    elif 8.8 <= velocidade < 11.1:
        dict_velocidade['8.8 - 11.1'] += 1
    elif velocidade >= 11.1:
        dict_velocidade['>= 11.1'] += 1

#funções para encontrar maximos e minimos
def encontrar_max(lista_valores):
    vmax = 1
    for item in lista_valores:
        if item > vmax:
            vmax = item
    return vmax

def encontrar_min(lista_valores):
    vmin = 10000000
    for item in lista_valores:
        if item < vmin:
            vmin = item
    return vmin

def plotar_rosa(dict_direcoes, total, titulo_grafico):
    #separando as informações de direção, velocidade e frequência para tratar como dataframe
        evitar = ['Frequencia', 'Indices']
        data = []
        for direcao, info in dict_direcoes.items():
            for velocidade, frequencia in info.items():
                if velocidade not in evitar:
                    data.append({'Direção': direcao, 'Velocidade': velocidade, 'Frequencia': frequencia})

        df1_rosa = pd.DataFrame(data)
        # #normalização em porcentagem da frequencia obtida de cada direção e velocidade
        df1_rosa['Frequencia: '] = (round((df1_rosa['Frequencia'] / total) * 100, 2))

        #cores para a legenda de velocidades
        colors = ['lightblue', 'blue', 'purple', 'green', 'yellow', 'orange', 'red']
        #rosa dos ventos é um gráfico polar, com barras
        fig = px.bar_polar(df1_rosa, r="Frequencia: ", theta="Direção",
                color="Velocidade",
                color_discrete_sequence=colors,
                template="plotly_white",
                title=titulo_grafico,
                barmode='stack')

        st.plotly_chart(fig, use_container_width=True)
            

#definição inicial do layout da página
st.set_page_config(layout="wide")

#pede para o usuário escolher o arquivo excel. Válido adicionar o formato csv depois
st.title("Análise de dados metereológicos diários - Ponta Praia Santos")
tipo = st.selectbox("Escolha o tipo do arquivo excel: ", ['xls', 'xlsx'])
upload_file = st.file_uploader(f"Escolha o arquivo excel {tipo}: ", type = [tipo])

if upload_file is None:
    st.write("""Para esse tipo de análise, é necessário separar os parâmetros em planilhas 
             diferentes. Cada planilha deve conter os dados de um parâmetro específico, 
             com a primeira linha contendo o nome do parâmetro e a segunda linha contendo o mês. 
             A partir da terceira linha, os dados devem ser inseridos. O arquivo deve conter 5 planilhas, 
             cada uma com um parâmetro diferente.""")
    #inserir imagem de exemplo
    st.image("exemplo1.png")
    st.markdown("""**Certifique-se de manter a seguinte sequência dos parâmetros nas respectivas planilhas: 
                Temperatura do Ar, Umidade Relativa do Ar, Pressão Atmosférica, Velocidade do Vento e Direção do Vento.**""")
    st.markdown("Escreve o nome do mês por extenso")
    
if tipo == 'xls':
    ferramenta = 'xlrd'
elif tipo == 'xlsx':
    ferramenta = 'openpyxl'
else:
    ferramenta = ''

#se recebeu um arquivo válido e a ferramenta de leitura
if upload_file is not None and ferramenta != '':
    #pela identaçao do arquivo, a primeira linha, com df_aux é o mês, depois essa linha é ignorada para considerar as colunas corretamente no dataframe
    df_aux = pd.read_excel(upload_file, sheet_name = 0, engine=ferramenta, nrows=1) 
    # Substituir "-" por 0 e gerar avisos
    
    mes_analise = df_aux.iloc[0, 0]
    st.sidebar.write(f"Mês: {mes_analise}") #essa linha é referente ao mês
    st.sidebar.write("Você quer ver os gráficos por mês (dia a dia, usando a média diária), por dia (hora a hora) ou o mês por uma hora em específico?")
    
    #definir o limite de dias, de acordo com o mês (se tem 31, 30 ou 28 dias)
    opcoes_31 = ["Janeiro", "jan", "Março", "mar", "Maio", "maio", "Julho", "jul", 
                 "Agosto", "ago", "Outubro", "out", "Dezembro", "dez"]
    opcoes_30 = ["Abril", "abr", "Junho", "jun", "Setembro", "set", "Novembro", "nov"]
    opcoes_28 = ["Fevereiro", "fev"]
    if any(option in mes_analise for option in opcoes_31):
        maximo_dias = 31
    elif any(option in mes_analise for option in opcoes_30):
        maximo_dias = 30
    elif any(option in mes_analise for option in opcoes_28):
        maximo_dias = 28

    #escolher entre uma das 3 opções de análise
    analise = st.sidebar.selectbox("Escolha o tipo de análise: ", ['Mês', 'Dia', 'Hora', 'Média Horas'])
    if analise == 'Dia':
        st.sidebar.write("Esse modo de análise é para cada dia do mês, pegando todos os valores de 0 a 24 horas")
        day = st.sidebar.number_input("Escolha o dia", 1, maximo_dias, 1)
    elif analise == 'Mês':
        st.sidebar.write("Esse modo de análise é para o mês inteiro, pegando a média diária e os valores máximos e mínimos")
        st.sidebar.write("Escolha o intervalo de dias para a análise mensal")
        dia_inicial = st.sidebar.number_input("Dia inicial", 1, maximo_dias, 1)
        dia_final = st.sidebar.number_input("Dia final", 1, maximo_dias, maximo_dias) #por padrão, o dia final é o último dia possível
    elif analise == 'Hora':
        st.sidebar.write("""Esse modo de análise apresenta os valores para um horário específico de cada dia do mês. 
                         Por exemplo, ao escolher a hora 3, serão avaliados todos os dados referentes à hora 3 de cada dia""")
        horario = st.sidebar.number_input("Horário para análise", 1, 24, 1)
    elif analise == 'Média Horas':
        st.sidebar.write("Esse modo de análise é para o mês inteiro, pegando a média de cada hora do dia (média dos valores por colunas)")
    
    #lista com as unidades de medida de cada parâmetro a ser inserida no gráfico
    medida = ['(ºC)', '(%)', 'Hectopascal (hPa)', '(graus)', '(m/s)']   
    #primeiro a plotagem será feita para temperatura, umidade e pressão atmosférica. Direção e Velocidade serão plotados juntos
    for i in range(3):
        df_aux = pd.read_excel(upload_file, sheet_name = i, engine=ferramenta, nrows=1) 
        #transformar as colunas em strings para poder manipular
        df_aux.columns = df_aux.columns.astype(str)

        #manipular e corrigir o nome do parâmetro
        coluna = df_aux.columns[0]
        pos = df_aux[coluna].name.find(")")
        df_aux[coluna].name = df_aux[coluna].name[:pos+1]
        st.write(f'{df_aux[coluna].name} - {medida[i]} - {df_aux[coluna][0]}')
        
        #limpeza dos dados, retirando as colunas e linhas que não serão utilizadas,  
        # quero apenas as linhas e colunas referentes a dias e horas
        df1 = pd.read_excel(upload_file, sheet_name = i, engine=ferramenta, skiprows=2)
        df1.columns = df1.columns.astype(str)
        df1 = df1.drop(df1.columns[25:], axis=1)
        df1 = df1.drop(df1.index[maximo_dias:])
        

        # Substituir "-" por NaN e gerar avisos
        for index, row in df1.iterrows():
            dia = index + 1
            for col in df1.columns:
                if row[col] == "-":
                    horario_ = col
                    st.warning(f"No dia {dia} e horário {horario_} não haviam dados devido a erros de medição.")
        # Converter para numérico, com valores "-" tornando-se NaN
        df1 = df1.apply(pd.to_numeric, errors='coerce')
        st.dataframe(df1)
        if analise == 'Dia':  
            #realizar uma filtragem para pegar apenas os valores do dia escolhido e as 24 horas
            df_dia = df1.iloc[day-1:day, 1:25]                
            valores_y = df_dia.iloc[0, :].values # pega todos os valores da linha do dia escolhido
            horas = list(range(1, 25))  # Colunas de 1 a 25, referente as horas
            
            # Plotar o gráfico de linha usando plotly
            fig = px.line(x=horas, y=valores_y, labels={'x': 'Hora', 'y': f'{df_aux[coluna].name} - {medida[i]}'}, title=f'Gráfico para {df_aux[coluna].name} - {medida[i]} - dia {day} de {mes_analise} ', markers=True)
            fig.update_layout(
                    xaxis=dict(range=[1, 24],
                        tickmode='linear',
                        tick0=1,
                        dtick=1 
                    ) #arruma o eixo x para mostrar todas as horas
            )
            fig.update_traces(hovertemplate=f'Hora: %{{x}}<br>{df_aux[coluna].name}: %{{y}}') #arruma o hover
            st.plotly_chart(fig, use_container_width=True) #plota o gráfico
    
        elif analise == "Mês":
            #serão plotados 3 linhas, com os valores médios, máximos e mínimos de cada dia, de acordo com o intervalo escolhido
            lista_valores_media = []
            lista_valores_maximo = []
            lista_valores_minimo = []
            #pega os valores de cada dia e calcula a média, máximo e mínimo, adicionando a respectiva lista
            for day in range(dia_inicial, dia_final+1):
                df_dia = df1.iloc[day-1:day, 1:25]                
                valores_y = df_dia.iloc[0, :].values
                lista_valores_media.append(valores_y.mean())
                lista_valores_maximo.append(valores_y.max())
                lista_valores_minimo.append(valores_y.min())

            dias = list(range(dia_inicial, dia_final+1)) #lista com os dias escolhidos no intervalo
            
            # plotagem com as três linhas
            fig = go.Figure()

            #valores médios
            fig.add_trace(
                go.Scatter(
                    x=dias, y=lista_valores_media, mode='lines+markers',
                    name=f'Valores médios de {df_aux[coluna].name}',
                    hovertemplate=f'Dia: %{{x}}<br>Média diária de {df_aux[coluna].name}: %{{y:.2f}}',
                    yaxis='y1', hoverinfo='text'
                )
            )
            #valores máximos
            fig.add_trace(
                go.Scatter(
                    x=dias, y=lista_valores_maximo, mode='lines+markers',
                    name=f'Valores máximos de {df_aux[coluna].name}',
                    hovertemplate=f'Dia: %{{x}}<br>Máxima diária de {df_aux[coluna].name}: %{{y:.2f}}',
                    yaxis='y2', hoverinfo='text'
                )
            )
            #valores mínimos
            fig.add_trace(
                go.Scatter(
                    x=dias, y=lista_valores_minimo, mode='lines+markers',
                    name=f'Valores mínimos de {df_aux[coluna].name}',
                    hovertemplate=f'Dia: %{{x}}<br>Mínima diária de {df_aux[coluna].name}: %{{y:.2f}}',
                    yaxis='y3', hoverinfo='text'
                )
            )   
            #encontrar o valor máximo e mínimo para ajustar a escala do gráfico e facilitar a visualização
            maximo = encontrar_max(lista_valores_maximo)
            minimo = encontrar_min(lista_valores_minimo)
            # Atualizar o layout para adicionar o eixo y2 e y3 sobre y1
            fig.update_layout(
                title=f'Gráfico para {df_aux[coluna].name} - {medida[i]} - {mes_analise}',
                xaxis=dict(title='Dia', range=[dia_inicial, dia_final], tickmode='linear', tick0=1, dtick=1), 
                yaxis=dict(range=[minimo, maximo]),  # Escala para velocidade
                yaxis2=dict(range=[minimo, maximo], overlaying='y', side='right'),  # Eixo secundário
                yaxis3=dict(range=[minimo, maximo], overlaying='y', side='right'),  # Eixo terciário
                legend=dict(x=0.5, y=1.01, xanchor='center', yanchor='bottom', orientation='h')
            )
            
            st.plotly_chart(fig, use_container_width=True) #plotagem

        elif analise == "Hora":
            coluna_indice = int(horario)
            df1_dia = df1.iloc[:maximo_dias, coluna_indice]
            valores_y = df1_dia.values
            dias = list(range(1, maximo_dias+1)) #lista com os dias do mês
            
            fig = px.line(x=dias, y=valores_y, labels={'x': 'Dia', 'y': f'{df_aux[coluna].name}'}, 
                          title=f'Gráfico para {df_aux[coluna].name} - {medida[i]} - Hora {horario} - {mes_analise} ', markers=True)
            fig.update_layout(
                xaxis=dict(range=[1, maximo_dias],
                    tickmode='linear',
                    tick0=1,
                    dtick=1 
                )
            )
            fig.update_traces(hovertemplate=f'Dia: %{{x}} Hora: {horario}<br>{df_aux[coluna].name}: %{{y}}')
            st.plotly_chart(fig, use_container_width=True)

        elif analise == "Média Horas":
            lista_valores_media = []
            for hora in range(1, 25):
                df_dia = df1.iloc[:maximo_dias, hora]                
                valores_y = df_dia.values
                lista_valores_media.append(valores_y.mean())

            horas = list(range(1, 25)) #lista com os dias escolhidos no intervalo
            
            fig = px.line(x=horas, y=lista_valores_media, labels={'x': 'Horas', 'y': f'{df_aux[coluna].name}'}, 
                          title=f'Gráfico para {df_aux[coluna].name} - {medida[i]} - Média dos horários no mês inteiro de {mes_analise} ', markers=True)
            fig.update_layout(
                xaxis=dict(range=[1, 24],
                    tickmode='linear',
                    tick0=1,
                    dtick=1 
                )
            ) 
            fig.update_traces(hovertemplate=f'Hora: %{{x}} <br>{df_aux[coluna].name}: %{{y:.2f}}')
            st.plotly_chart(fig, use_container_width=True)

    #analise direcao e velocidade
    df_aux1 = pd.read_excel(upload_file, sheet_name = 3, engine=ferramenta, nrows=1) 
    df_aux1.columns = df_aux1.columns.astype(str)
    df1 = pd.read_excel(upload_file, sheet_name = 3, engine=ferramenta, skiprows=2)
    df1.columns = df1.columns.astype(str)
    df1 = df1.drop(df1.columns[25:], axis=1)
    df1 = df1.drop(df1.index[maximo_dias:])

    coluna = df_aux1.columns[0]
    pos = df_aux1[coluna].name.find(")")
    df_aux1[coluna].name = df_aux1[coluna].name[:pos+1]
    st.write(f'{df_aux1[coluna].name} - {medida[3]} - {df_aux1[coluna][0]}')
    
    for index, row in df1.iterrows():
        dia = index + 1
        for col in df1.columns:
            if row[col] == "-":
                horario_ = col
                st.warning(f"No dia {dia} e horário {horario_} não haviam dados devido a erros de medição.")
    # Converter para numérico, com valores "-" tornando-se NaN
    df1 = df1.apply(pd.to_numeric, errors='coerce')
    st.dataframe(df1)
           
    df_aux2 = pd.read_excel(upload_file, sheet_name = 4, engine=ferramenta, nrows=1) 
    df_aux2.columns = df_aux2.columns.astype(str)
    df2 = pd.read_excel(upload_file, sheet_name = 4, engine=ferramenta, skiprows=2)
    df2.columns = df2.columns.astype(str)
    df2 = df2.drop(df2.columns[25:], axis=1)
    df2 = df2.drop(df2.index[maximo_dias:])
    
    coluna = df_aux2.columns[0]
    pos = df_aux2[coluna].name.find(")")
    df_aux2[coluna].name = df_aux2[coluna].name[:pos+1]
    st.write(f'{df_aux2[coluna].name} - {medida[3]} - {df_aux2[coluna][0]}')
    
    for index, row in df2.iterrows():
        dia = index + 1
        for col in df2.columns:
            if row[col] == "-":
                horario_ = col
                st.warning(f"No dia {dia} e horário {horario_} não haviam dados devido a erros de medição.")
    # Converter para numérico, com valores "-" tornando-se NaN
    df2 = df2.apply(pd.to_numeric, errors='coerce')
    st.dataframe(df2)
    
    if analise == 'Dia':
        df1_dia = df1.iloc[day-1:day, 1:25]                
        valores_y1 = df1_dia.iloc[0, :].values

        df2_dia = df2.iloc[day-1:day, 1:25]                
        valores_y2 = df2_dia.iloc[0, :].values
        horas = list(range(1, 25))  # Colunas de 1 a 25

        fig = go.Figure()
        #direção e velocidade são plotados juntos, mas com escalas diferentes
        fig.add_trace(
            go.Scatter(
                x=horas, y=valores_y1, mode='lines+markers',
                name='Direção do Vento',
                hovertemplate='Hora: %{x}<br>Direção (graus): %{y:.2f}',
                yaxis='y1', hoverinfo='text'
            )
        )

        fig.add_trace(
            go.Scatter(
                x=horas, y=valores_y2, mode='lines+markers',
                name='Velocidade do Vento',
                hovertemplate='Hora: %{x}<br> Velocidade (m/s): %{y:.2f}',
                yaxis='y2', hoverinfo='text'
            )
        )   
        #encontra o máximo da direção e da velocidade
        maximo1 = encontrar_max(valores_y1)
        maximo2 = encontrar_max(valores_y2)
        # Atualizar o layout para adicionar o eixo y2 sobre y1
        fig.update_layout(
            title=f'Gráfico para Direção e Velocidade do Vento - {mes_analise} - Dia {day}',
            xaxis=dict(title='Hora', range=[1, 24], tickmode='linear', tick0=1, dtick=1), 
            yaxis=dict(range=[0, 360]), # Escala para direção
            yaxis2=dict(range=[0, maximo2], overlaying='y', side='right'),  # Escala para velocidade
            legend=dict(x=0.5, y=1.01, xanchor='center', yanchor='bottom', orientation='h')
        )
            
        st.plotly_chart(fig, use_container_width=True)  

        #rosa dos ventos
        #cada direção recebe um dicionário de velocidades
        #deepcopy é recomendado para elementos mais complexos, pois garante que todos os níveis da estrutura sejam copiados de forma independente.
        dict_vel = {'Frequencia': 0, 'Calmaria': 0, '0.5 - 2.1': 0, '2.1 - 3.6': 0, '3.6 - 5.7': 0, '5.7 - 8.8': 0, '8.8 - 11.1': 0, '>= 11.1': 0, 'Indices':[]}
        dict_direcoes = {'N': copy.deepcopy(dict_vel), 'NNE': copy.deepcopy(dict_vel), 'NE': copy.deepcopy(dict_vel), 'ENE': copy.deepcopy(dict_vel), 'E': copy.deepcopy(dict_vel), 'ESE': copy.deepcopy(dict_vel), 'SE': copy.deepcopy(dict_vel), 'SSE': copy.deepcopy(dict_vel),
                        'S': copy.deepcopy(dict_vel), 'SSO': copy.deepcopy(dict_vel), 'SO': copy.deepcopy(dict_vel), 'OSO': copy.deepcopy(dict_vel), 'O': copy.deepcopy(dict_vel), 'ONO': copy.deepcopy(dict_vel), 'NO': copy.deepcopy(dict_vel), 'NNO': copy.deepcopy(dict_vel)}
        total = 0  
        #para cada coluna, categorizar a direção e a velocidade
        for indice, coluna in enumerate(df1_dia):
            valor1 = df1_dia[coluna][day-1].astype(float)
            valor2 = df2_dia[coluna][day-1].astype(float)
            # Verificar se algum dos valores é NaN
            if not (np.isnan(valor1) or np.isnan(valor2)):
                categorizar_direcao_16(dict_direcoes, valor1, valor2, indice)
                total += 1
          
        #separando as informações de direção, velocidade e frequência para tratar como dataframe
        titulo_grafico = f"Rosa dos Ventos - {mes_analise} - Dia {day}"
        plotar_rosa(dict_direcoes, total, titulo_grafico)
        # Multiselect para escolher múltiplas opções
        options_dir = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
        selected_options = st.multiselect("Filtro de Direções para Rosa dos Ventos de Velocidade e Direção do Vento", options_dir, placeholder="Escolha uma ou mais direções")

        #mudar indices para filtrar o dataframe
        if selected_options:
            todos_indices = []
            for direcao in selected_options:
                todos_indices.extend(dict_direcoes[direcao]["Indices"])

            final_filtered_df = df1_dia.iloc[:, todos_indices]            
            #adicionar um filtro por intervalo (ou por direção) e mostrar em um dataframe todos os resultados com dias e horas em que apareceu aquela direção    
            st.write(f"Tabela Filtro por Direção - {mes_analise} - Dia {day}")
            final_filtered_df.index = final_filtered_df.index + 1
            final_filtered_df.index.name = 'Dia/Hora'
            st.dataframe(final_filtered_df) # mostra data, hora e coluna do laço 

    elif analise == "Mês":
        lista1_valores_media = []
        lista2_valores_media = []
        for day in range(dia_inicial, dia_final+1):
            df1_dia = df1.iloc[day-1:day, 1:25]                
            valores_y1 = df1_dia.iloc[0, :].values
            lista1_valores_media.append(valores_y1.mean())
            df2_dia = df2.iloc[day-1:day, 1:25]                
            valores_y2 = df2_dia.iloc[0, :].values
            lista2_valores_media.append(valores_y2.mean())

        dias = list(range(dia_inicial, dia_final+1))
        # um gráfico com os valores de média, um com minima e um com maxima
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=dias, y=lista1_valores_media, mode='lines+markers',
                name='Direção do Vento',
                hovertemplate='Dia: %{x}<br>Direção (graus): %{y:.2f}',
                yaxis='y1', hoverinfo='text'
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dias, y=lista2_valores_media, mode='lines+markers',
                name='Velocidade do Vento',
                hovertemplate='Dia: %{x}<br> Velocidade (m/s): %{y:.2f}',
                yaxis='y2', hoverinfo='text'
            )
        )   
           
        maximo1 = encontrar_max(valores_y1)
        maximo2 = encontrar_max(valores_y2)
            
        fig.update_layout(
            title=f'Gráfico para Direção e Velocidade do Vento - {mes_analise} - {dia_inicial} à {dia_final}',
            xaxis=dict(title='Dia', range=[dia_inicial, dia_final], tickmode='linear', tick0=1, dtick=1), 
            yaxis=dict(range=[0, 360]), # Escala para direção
            yaxis2=dict(range=[0, maximo2], overlaying='y', side='right'),  # Escala para velocidade
            legend=dict(x=0.5, y=1.01, xanchor='center', yanchor='bottom', orientation='h')
        )
            
        st.plotly_chart(fig, use_container_width=True) 

        dict_vel = {'Frequencia': 0, 'Calmaria': 0, '0.5 - 2.1': 0, '2.1 - 3.6': 0, '3.6 - 5.7': 0, '5.7 - 8.8': 0, '8.8 - 11.1': 0, '>= 11.1': 0, 'Indices':[]}
        dict_direcoes = {'N': copy.deepcopy(dict_vel), 'NNE': copy.deepcopy(dict_vel), 'NE': copy.deepcopy(dict_vel), 'ENE': copy.deepcopy(dict_vel), 'E': copy.deepcopy(dict_vel), 'ESE': copy.deepcopy(dict_vel), 'SE': copy.deepcopy(dict_vel), 'SSE': copy.deepcopy(dict_vel),
                        'S': copy.deepcopy(dict_vel), 'SSO': copy.deepcopy(dict_vel), 'SO': copy.deepcopy(dict_vel), 'OSO': copy.deepcopy(dict_vel), 'O': copy.deepcopy(dict_vel), 'ONO': copy.deepcopy(dict_vel), 'NO': copy.deepcopy(dict_vel), 'NNO': copy.deepcopy(dict_vel)}
        total = 0  

        for indice, coluna in enumerate(lista1_valores_media):
            valor1 = lista1_valores_media[indice].astype(float)
            valor2 = lista2_valores_media[indice].astype(float)
            # Verificar se algum dos valores é NaN
            if not (np.isnan(valor1) or np.isnan(valor2)):
                categorizar_direcao_16(dict_direcoes, valor1, valor2, indice)
                total += 1
                           
        titulo_grafico = f"Rosa dos Ventos - {mes_analise} - {dia_inicial} à {dia_final}"
        plotar_rosa(dict_direcoes, total, titulo_grafico)
        # Multiselect para escolher múltiplas opções
        options_dir = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
        selected_options = st.multiselect("Filtro de Direções para Rosa dos Ventos de Velocidade e Direção do Vento", options_dir, placeholder="Escolha uma ou mais direções")

        #mudar indices para filtrar o dataframe
        if selected_options:
            todos_indices = []
            for direcao in selected_options:
                todos_indices.extend(dict_direcoes[direcao]["Indices"])
            df_lista1 = pd.DataFrame(lista1_valores_media)
            
            final_filtered_df = df_lista1.iloc[todos_indices]            
            
            #adicionar um filtro por intervalo (ou por direção) e mostrar em um dataframe todos os resultados com dias e horas em que apareceu aquela direção    
            st.write(f"Tabela Filtro por Direção - {mes_analise} - {dia_inicial} à {dia_final}")
            final_filtered_df.index = final_filtered_df.index + 1
            final_filtered_df.index.name = 'Dia'
            final_filtered_df = final_filtered_df.rename(columns={0: 'Valores diários médios'})
            st.dataframe(final_filtered_df) # mostra data, hora e coluna do laço 
            

    elif analise == "Hora":
        coluna_indice = int(horario)
        df1_dia = df1.iloc[:maximo_dias, coluna_indice]
        valores_y1 = df1_dia.values

        df2_dia = df2.iloc[:maximo_dias, coluna_indice]
        valores_y2 = df2_dia.values
        dias = list(range(1, maximo_dias+1))
        
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=dias, y=valores_y1, mode='lines+markers',
                name='Direção do Vento',
                hovertemplate='Dia: %{x}<br>Direção (graus): %{y:.2f}',
                yaxis='y1', hoverinfo='text'
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dias, y=valores_y2, mode='lines+markers',
                name='Velocidade do Vento',
                hovertemplate='Dia: %{x}<br> Velocidade (m/s): %{y:.2f}',
                yaxis='y2', hoverinfo='text'
            )
        )   

        maximo1 = encontrar_max(valores_y1)
        maximo2 = encontrar_max(valores_y2)
            
        fig.update_layout(
            title=f'Gráfico para Direção e Velocidade do Vento - {mes_analise} - Hora {horario}',
            xaxis=dict(title='Dia', range=[1, maximo_dias], tickmode='linear', tick0=1, dtick=1), 
            yaxis=dict(range=[0, 360]), # Escala para direção
            yaxis2=dict(range=[0, maximo2], overlaying='y', side='right'),  # Escala para velocidade
            legend=dict(x=0.5, y=1.01, xanchor='center', yanchor='bottom', orientation='h')
        )
            
        st.plotly_chart(fig, use_container_width=True) 


        dict_vel = {'Frequencia': 0, 'Calmaria': 0, '0.5 - 2.1': 0, '2.1 - 3.6': 0, '3.6 - 5.7': 0, '5.7 - 8.8': 0, '8.8 - 11.1': 0, '>= 11.1': 0, 'Indices':[]}
        dict_direcoes = {'N': copy.deepcopy(dict_vel), 'NNE': copy.deepcopy(dict_vel), 'NE': copy.deepcopy(dict_vel), 'ENE': copy.deepcopy(dict_vel), 'E': copy.deepcopy(dict_vel), 'ESE': copy.deepcopy(dict_vel), 'SE': copy.deepcopy(dict_vel), 'SSE': copy.deepcopy(dict_vel),
                        'S': copy.deepcopy(dict_vel), 'SSO': copy.deepcopy(dict_vel), 'SO': copy.deepcopy(dict_vel), 'OSO': copy.deepcopy(dict_vel), 'O': copy.deepcopy(dict_vel), 'ONO': copy.deepcopy(dict_vel), 'NO': copy.deepcopy(dict_vel), 'NNO': copy.deepcopy(dict_vel)}
        total = 0  

        for indice, coluna in enumerate(valores_y1):
            valor1 = valores_y1[indice].astype(float)
            valor2 = valores_y2[indice].astype(float)
            # Verificar se algum dos valores é NaN
            if not (np.isnan(valor1) or np.isnan(valor2)):
                categorizar_direcao_16(dict_direcoes, valor1, valor2, indice)
                total += 1
                           
        #separando as informações de direção, velocidade e frequência para tratar como dataframe
        titulo_grafico = f"Rosa dos Ventos - {mes_analise} - Hora {horario}"
        plotar_rosa(dict_direcoes, total, titulo_grafico)
        # Multiselect para escolher múltiplas opções
        options_dir = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
        selected_options = st.multiselect("Filtro de Direções para Rosa dos Ventos de Velocidade e Direção do Vento", options_dir, placeholder="Escolha uma ou mais direções")

        #mudar indices para filtrar o dataframe
        if selected_options:
            todos_indices = []
            for direcao in selected_options:
                todos_indices.extend(dict_direcoes[direcao]["Indices"])
            
            
            df_lista1 = pd.DataFrame(valores_y1)
            
            final_filtered_df = df_lista1.iloc[todos_indices]            
            
            #adicionar um filtro por intervalo (ou por direção) e mostrar em um dataframe todos os resultados com dias e horas em que apareceu aquela direção    
            st.write(f"Tabela Filtro por Direção - {mes_analise} - Hora {horario}")
            final_filtered_df.index = final_filtered_df.index + 1
            final_filtered_df.index.name = 'Dia'
            final_filtered_df = final_filtered_df.rename(columns={0: f'Valores diários hora {horario}'})
            st.dataframe(final_filtered_df) # mostra data, hora e coluna do laço 
      
      
    elif analise == "Média Horas":
        lista1_valores_media = []
        lista2_valores_media = []
        for hora in range(1, 25):
            df1_dia = df1.iloc[:maximo_dias, hora]                
            valores_y1 = df1_dia.values
            lista1_valores_media.append(valores_y1.mean())
            df2_dia = df2.iloc[:maximo_dias, hora]                
            valores_y2 = df2_dia.values
            lista2_valores_media.append(valores_y2.mean())

        horas = list(range(1, 25)) #lista com os dias escolhidos no intervalo

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=horas, y=lista1_valores_media, mode='lines+markers',
                name='Direção do Vento',
                hovertemplate='Hora: %{x}<br>Direção (graus): %{y:.2f}',
                yaxis='y1', hoverinfo='text'
            )
        )

        fig.add_trace(
            go.Scatter(
                x=horas, y=lista2_valores_media, mode='lines+markers',
                name='Velocidade do Vento',
                hovertemplate='Hora: %{x}<br> Velocidade (m/s): %{y:.2f}',
                yaxis='y2', hoverinfo='text'
            )
        )   

        maximo1 = encontrar_max(lista1_valores_media)
        maximo2 = encontrar_max(lista2_valores_media)

        fig.update_layout(
            title=f'Gráfico para Direção e Velocidade do Vento - Média dos horários no mês inteiro de {mes_analise} ',
            xaxis=dict(title='Hora', range=[1, 24], tickmode='linear', tick0=1, dtick=1), 
            yaxis=dict(range=[0, 360]), # Escala para direção
            yaxis2=dict(range=[0, maximo2], overlaying='y', side='right'),  # Escala para velocidade
            legend=dict(x=0.5, y=1.01, xanchor='center', yanchor='bottom', orientation='h')
        )
            
        st.plotly_chart(fig, use_container_width=True) 

        dict_vel = {'Frequencia': 0, 'Calmaria': 0, '0.5 - 2.1': 0, '2.1 - 3.6': 0, '3.6 - 5.7': 0, '5.7 - 8.8': 0, '8.8 - 11.1': 0, '>= 11.1': 0, 'Indices':[]}
        dict_direcoes = {'N': copy.deepcopy(dict_vel), 'NNE': copy.deepcopy(dict_vel), 'NE': copy.deepcopy(dict_vel), 'ENE': copy.deepcopy(dict_vel), 'E': copy.deepcopy(dict_vel), 'ESE': copy.deepcopy(dict_vel), 'SE': copy.deepcopy(dict_vel), 'SSE': copy.deepcopy(dict_vel),
                        'S': copy.deepcopy(dict_vel), 'SSO': copy.deepcopy(dict_vel), 'SO': copy.deepcopy(dict_vel), 'OSO': copy.deepcopy(dict_vel), 'O': copy.deepcopy(dict_vel), 'ONO': copy.deepcopy(dict_vel), 'NO': copy.deepcopy(dict_vel), 'NNO': copy.deepcopy(dict_vel)}
        total = 0  

        for indice, coluna in enumerate(lista1_valores_media):
            valor1 = lista1_valores_media[indice].astype(float)
            valor2 = lista2_valores_media[indice].astype(float)
            # Verificar se algum dos valores é NaN
            if not (np.isnan(valor1) or np.isnan(valor2)):
                categorizar_direcao_16(dict_direcoes, valor1, valor2, indice)
                total += 1
                           
        titulo_grafico = f"Rosa dos Ventos - {mes_analise} - Média das horas"
        plotar_rosa(dict_direcoes, total, titulo_grafico)
        # Multiselect para escolher múltiplas opções
        options_dir = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
        selected_options = st.multiselect("Filtro de Direções para Rosa dos Ventos de Velocidade e Direção do Vento", options_dir, placeholder="Escolha uma ou mais direções")

        #mudar indices para filtrar o dataframe
        if selected_options:
            todos_indices = []
            for direcao in selected_options:
                todos_indices.extend(dict_direcoes[direcao]["Indices"])
            df_lista1 = pd.DataFrame(lista1_valores_media)
            
            final_filtered_df = df_lista1.iloc[todos_indices]            
            
            #adicionar um filtro por intervalo (ou por direção) e mostrar em um dataframe todos os resultados com dias e horas em que apareceu aquela direção    
            st.write(f"Tabela Filtro por Direção - {mes_analise} - Média das horas")
            final_filtered_df.index = final_filtered_df.index + 1
            final_filtered_df.index.name = 'Hora'
            final_filtered_df = final_filtered_df.rename(columns={0: 'Valores médios das horas'})
            st.dataframe(final_filtered_df) # mostra data, hora e coluna do laço 
        
      
else:
    st.write("Aguardando a sua planilha!")