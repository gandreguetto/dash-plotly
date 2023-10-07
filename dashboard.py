######## Dashboard com os dados de criminalidade da cidade de Ottawa - Canada


#### Importação das bibliotecas principais

# Importando dash e seus pacotes para a construção do bashboard
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Importando o plotly para a contrução dos gráficos
import plotly.graph_objects as go

# Importando o pandas
import pandas as pd

# Importando o numpy
import numpy as np


#### Carregamento dos dados e primeiras manipulções

# Lendo o arquivo csv com os dados
# (os dados foram obtidos do site https://open.ottawa.ca/datasets/criminal-offences-map/explore?location=45.177489%2C-75.455252%2C4.79)
df = pd.read_csv('Criminal_Offences_Map.csv')

# Selecionando apenas as colunas de interesse
df = df[["Occurrence", "Criminal_O", "Primary_Of"]]

# Selecionando apenas a data da ocorrência, sem o horário
df['Occurrence'] = df['Occurrence'].apply(lambda x: x[:10])

# Criando uma nova coluna contendo o ano da ocorrência
df['Year'] = df['Occurrence'].apply(lambda x: int(x[:4]))

# Selecionando os dados apenas a partir de 2016 para as análises (os dados anteriores não estão bons)
df = df[df['Year']>2015]




#### Figura 1: número de crimes por ano

# Cria um novo dataframe contendo o ano e número de crimes
crime_year = df['Year'].value_counts().sort_index().reset_index()

# Define o gráfico de barras com os anos no eixo x e quantidade de crimes no eixo y
fig1 = go.Figure(go.Bar(
            x=crime_year['Year'],
            y=crime_year['count'],
            base = "yellow",
            textposition = "inside",
            text = crime_year['count'],
            marker={'color': "#4f6cf0"},
            orientation='v',
))

# Ajustes no eixo y
fig1.update_yaxes(showticklabels=False) # retira os valores do eixo y

# Determina alguns ajustes adicionais na figura
fig1.update_layout(
    height=250,
    width = 500,
    showlegend = False,
    template = "plotly_white",
    margin=dict(l=25, r=25, t=0, b=45)
)



#### Figura 2: evolução percentual nos crimes de 2016 a 2022

# Grava na variável "types" os nomes dos tipos de crime
types = df['Primary_Of'].unique()

# Renomeando alguns tipos de crime para melhorar a exibição
titles = types.copy()

titles = ['Violence', 'Break in', 'Mischief', 'Under $5000', 'Theft Vehicles', 'Assaults', 'Sexual Violations', 'Fraud', 'Over $5000',
          'Other Crim. Code', 'Poss./Traffic. Stolen Goods', 'Offensive Weapons', 'Arson', 'Attempt. Capital Crime', 
          'Deprivation of Freedom', 'Causing Death', 'Commodif. of Sex. Activity', 'Prostitution', 'Gaming']


# Dataframe com a quantidade de crimes por ano e tipo
crime_year_primary = df[["Year", "Primary_Of"]].value_counts().sort_index().reset_index()

# Listas para serem gravados os números de 2016 e 2022
crimes_2016 = []
crimes_2022 = []

# Percorre a lista com os tipos de crime e para cada tipo grava a quantidade de crimes em 2016 e 2022 nas respectivas lstas
for i in range(len(types)):

    if crime_year_primary[(crime_year_primary['Year'] == 2016) & (crime_year_primary['Primary_Of'] == types[i])]['count'].empty:
        crimes_2016.append(0) # adiciona "0" na lista de 2016 se não há crimes para o tipo selecionado

    else:
        crimes_2016.append(
            crime_year_primary[(crime_year_primary['Year'] == 2016) & (crime_year_primary['Primary_Of'] == types[i])]['count'].item()
        ) # adiciona na lista de 2016 a quantidade de crimes correspondente
        
    if crime_year_primary[(crime_year_primary['Year'] == 2022) & (crime_year_primary['Primary_Of'] == types[i])]['count'].empty:#.item())
        crimes_2022.append(0) # adiciona "0" na lista de 2022 se não há crimes para o tipo selecionado

    else:
        crimes_2022.append(
            crime_year_primary[(crime_year_primary['Year'] == 2022) & (crime_year_primary['Primary_Of'] == types[i])]['count'].item()
        ) # adiciona na lista de 2022 a quantidade de crimes correspondente

# Vetor que irá guardar as variações percentuais        
var = np.array([])

# Percorre as listas de crimes nos anos de 2016 e 2022 e calcula a variação percentual para cada tipo de crime. Os dois últimos tipos de crime: "Prostitution" e "Gaming" contém muito poucos registros e foram removidos da análise.
for i in range(len(crimes_2022) - 2):
    var = np.append(
        var, (crimes_2022[i] - crimes_2016[i])*100/crimes_2016[i]
    )

# Vetor com os tipos de crime, exceto "Prostitution" e "Gaming"
titles1 = np.array(titles[:-2])

# Indices que ordenam as variações percentuais
idx = np.argsort(var)

# Ordenando pelo valor da variação
var = var[idx]

# Ordenando os tipos de crime para seguirem o ordenamento das variações
titles1 = titles1[idx]

# Novo dataframe com as variações percentuais e tipos de crimes
df_var = pd.DataFrame({
            'Var' : var,        
            'Titles' : titles1
})

# Define as cores para serem usadas no gráfico de acordo com o sinal da variação
df_var['Color'] = np.where(df_var['Var'] > 0, "#f53333", "#4f6cf0")

# Lista que receberá os valores editados dos labels para serem exibidos nas barras
var_labels = []
for i  in range(len(df_var['Var'])): # percorre os valores das variações, transforma em string e adiciona o símbolo de porcentagem
    var_labels.append(str(int(df_var['Var'][i])) + '%')


# Define a Figura 2 como um gráfico de barras horizontais    
fig2 = go.Figure(go.Bar(
            x=df_var['Var'],
            y=df_var['Titles'],
            text = var_labels,
            textposition = "outside",
            cliponaxis = False,
            orientation='h',
            ))

# Altera as cores das barras utilizando o esquema criado na coluna "Color" do dataframe df_var
fig2.update_traces(marker_color=df_var["Color"])

# Remove as informações do eixo x
fig2.update_xaxes(showticklabels=False)


fig2.update_yaxes(
   automargin=True
)
fig2.update_layout(
    height=1050,
    width = 950,
    showlegend = False,
    margin=dict(l=5, r=18, t=8, b=8),
    template = "plotly_white"
)


#### Estruturando o dashboard

app = dash.Dash(
    __name__,
    title='Crimes in Ottawa - Canada',
    external_stylesheets = [
        dbc.themes.DARKLY,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awsome/6.1.1/css/all.min.css',
        'https://fonts.googleapis.com/css2?family=Joan&family=Roboto:ital,wght@0,100;1,300&family=Source+Sans+Pro:'
    ]
)

app.layout = html.Div(
    children=[

        # Banner do título
        
        html.Div(
            className = 'banner',
            style={
                'height' : 'fit-content',
                'background-color' : '#1e2130',
                'display' : 'flex',
                'flex-direction' : 'row',
                'align-itens' : 'center',
                'justify-content' : 'space-between',
                'border-bottom' : '1px solid #4b5460',
                'padding' : '1rem 5rem 1rem 4rem',
                'width' : '100%'
            },
            children=[

                # Título do dashboard
                
                html.Div(
                    className = 'banner-title',
                    children=[
                        html.H4(
                            ['Crime Records'],
                            style = {
                                'font-famly' : 'open sans semi bold, sans-serif',
                                'font-weight' : '500'
                            }
                        ),
                        html.H5('Ottawa - Canada')
                    ]
                ),


                # Filtro de categoria
                
                html.Div(
                    [   html.H6("Select Category"),
                        dcc.Dropdown(
                            np.append(np.array('All'), titles),
                            'All',
                            id='dropdown',
                            placeholder = "Category",
                            style={'color': 'black'}
                        ),
                        html.Div(
                            id='dd-output-container',
                            style={
                                "width": "240px",
                                "height": "50%"
                            },
                        )
                    ]
                ),


                # Imagem na faixa do cabeçalho
                
                html.Div(
                    html.Img(
                        src="assets/flag.png",
                        style={'width':'30%',
                            'align-itens' : 'right',
                        }
                    ),
                    style={'textAlign': 'right'}
                )
            ],
        ),

        # Faixa de conteúdo

        html.Div(
            className = 'app-content',
            style={
                'padding' : '0.5rem 2rem',
                'width' : '100%'
            },

            children=[

                # Bloco da esquerda
                
                html.Div(
                
                    className = 'left-div',
                    style={
                        'background-color' : '#161a28',
                        'display' : 'inline-block',
                        'flex-direction' : 'column',
                        'align-itens' : 'center',
                        'justify-content' : 'space-evenly',
                        'border-bottom' : '1px solid #4b5460',
                        'padding' : '0',
                        'width' : '45%',
                        'margin' : '0',
                        'border' : '#1e2130 solid 0.2rem'
                    },

                    # Título do bloco da esquerda
                    
                    children=[
                        html.Div(
                            className='top',
                            children=[
                                html.H5(
                                    ['Number of crimes per year'],
                                    style={
                                        'line-height' : '1.6',
                                        'box-sizing' : 'border-box',
                                        'margin' : '1rem',
                                        'font-weight' : '500',
                                        'align-self' : 'flex-start'
                                    }
                                ),

                                # Insere a Figura 1
                                
                                html.Div(
                                    html.Div(
                                        html.Div(
                                            dcc.Graph(
                                                id = "figure1",
                                                figure=fig1, 
                                                responsive=True,
                                                style={
                                                    "width": "100%",
                                                    "height": "100%"
                                                }
                                            ),
                                            style={
                                                "width": "100%",
                                                "height": "100%",
                                            },
                                        ),
                                        style={
                                            "width": "100%",
                                            "height": "425px",
                                            "display": "inline-block",
                                            "border": "3px #5c5c5c solid",
                                            "padding-top": "1px",
                                            "padding-left": "1px",
                                            "overflow": "hidden"
                                        }
                                    )
                                )
                            ]    
                        ),    
                    ]
                ),

                # Bloco da direita
                
                html.Div(
                
                    className = 'right-div',
                    style={
                        'background-color' : '#161a28',
                        'display' : 'inline-block',
                        'flex-direction' : 'column',
                        'align-itens' : 'center',
                        'justify-content' : 'space-evenly',
                        'border-bottom' : '1px solid #4b5460',
                        'padding' : '0',
                        'width' : '55%',
                        'margin' : '0',
                        'border' : '#1e2130 solid 0.2rem'
                    },

                    # Título do bloco da direita

                    children=[
                        html.Div(
                            className='top',
                            children=[
                                html.H5(
                                    ['Evolution of crimes - 2016 to 2022'],
                                    style={
                                        'line-height' : '1.6',
                                        'box-sizing' : 'border-box',
                                        'margin' : '1rem',
                                        'font-weight' : '500',
                                        'align-self' : 'flex-start'
                                    }
                                ),

                                # Insere a Figura 2 no bloco
                                                                
                                html.H6(
                                    html.Div(
                                        html.Div(
                                            dcc.Graph(
                                                figure=fig2, 
                                                responsive=True,
                                                style={
                                                    "width": "100%",
                                                    "height": "100%"
                                                }
                                            ),
                                            style={
                                                "width": "100%",
                                                "height": "100%",
                                            },
                                        ),
                                        style={
                                            "width": "100%",
                                            "height": "425px",
                                            "display": "inline-block",
                                            "border": "3px #5c5c5c solid",
                                            "padding-top": "1px",
                                            "padding-left": "1px",
                                            "overflow": "hidden"
                                        }
                                    )
                                )
                            ]    
                        ),    
                    ]
                )
            ]
        )            
    ]
)   


#### Atualizando a Figura 1 conforme a seleção de categoria

@app.callback(
    Output("figure1", "figure"), 
    Input("dropdown", "value"),
    prevent_initial_call = True)
def update_figure(selected_category):
 
    if selected_category != "All" and not not selected_category:
        new_selected_category = types[titles.index(selected_category)]
        crime_year = df[df['Primary_Of'] == new_selected_category]['Year'].value_counts().sort_index().reset_index()

    else:
        crime_year = df['Year'].value_counts().sort_index().reset_index()

        
    fig1 = go.Figure(go.Bar(
        x=crime_year['Year'],
        y=crime_year['count'],
        base = "yellow",
        textposition = "inside",
        text = crime_year['count'],
        marker={'color': "#4f6cf0"},
        orientation='v',
    ))

    fig1.update_yaxes(showticklabels=False)

    fig1.update_layout(
        height=250,
        width = 500,
        showlegend = False,
        template = "plotly_white",
        margin=dict(l=25, r=25, t=0, b=45)
    )

    return fig1

if __name__ == '__main__':
    app.run_server( debug = True )
