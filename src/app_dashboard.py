import dash
from dash import dcc, html
import pandas as pd
import os
import urllib.parse
from sqlalchemy import create_engine
import plotly.express as px
from dotenv import load_dotenv

# --- INICIALIZAÇÃO ---
load_dotenv()

# --- CONFIGURAÇÃO DA CONEXÃO ---
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

SENHA_ENCODED = urllib.parse.quote_plus(DB_PASS)
STRING_CONEXAO = f'postgresql://{DB_USER}:{SENHA_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(STRING_CONEXAO)

# --- IDENTIDADE VISUAL (ESTILO ARIAL / AZUL) ---
def aplicar_estilo_tcc(fig, eixo_x_titulo, eixo_y_titulo):
    fig.update_layout(
        font=dict(family="Arial", color="black"),
        plot_bgcolor='white', paper_bgcolor='white',
        title_font=dict(family="Arial", size=18, color="black"), title_x=0.5,
        xaxis=dict(title=f'<b>{eixo_x_titulo}</b>', showgrid=False, showline=True, linecolor='black'),
        yaxis=dict(title=f'<b>{eixo_y_titulo}</b>', showgrid=True, gridcolor='#E5E7EB', griddash='dash', showline=True, linecolor='black')
    )
    fig.update_traces(textfont=dict(family="Arial", color="black", size=12))
    return fig

# --- GERAÇÃO DOS GRÁFICOS ---
print("Consultando DW e gerando visualizações...")

# G1: Evolução
df_ano = pd.read_sql("SELECT t.ano, COUNT(f.sk_sinistro) as qtd FROM ft_sinistros f JOIN dm_tempo t ON f.sk_tempo = t.sk_tempo GROUP BY t.ano ORDER BY t.ano", engine)
fig1 = px.line(df_ano, x='ano', y='qtd', title='<b>Evolução Anual de Acidentes</b>', markers=True, text='qtd', color_discrete_sequence=['#154360'])
fig1.update_traces(textposition="top center", cliponaxis=False, line=dict(width=3), marker=dict(size=12, color='#3498DB', line=dict(color='black', width=1)))
fig1 = aplicar_estilo_tcc(fig1, "Ano", "Quantidade")
fig1.update_layout(xaxis=dict(dtick=1, range=[2014.5, 2025.5]), yaxis=dict(range=[0, df_ano['qtd'].max() * 1.15]))

# G2: Top BRs
df_br = pd.read_sql("SELECT l.br, COUNT(f.sk_sinistro) as qtd FROM ft_sinistros f JOIN dm_local l ON f.sk_local = l.sk_local GROUP BY l.br ORDER BY qtd DESC LIMIT 5", engine)
df_br['br'] = 'BR-' + df_br['br'].astype(str)
fig2 = px.bar(df_br, x='br', y='qtd', color='qtd', title='<b>Top 5 Rodovias Federais (BA)</b>', text='qtd', color_continuous_scale='Blues', range_color=[0, df_br['qtd'].max()])
fig2.update_traces(textposition="outside", cliponaxis=False)
fig2 = aplicar_estilo_tcc(fig2, "Rodovia", "Quantidade")
fig2.update_layout(coloraxis_showscale=False, bargap=0.4, yaxis=dict(range=[0, df_br['qtd'].max() * 1.15]))

# G3: Causas
df_causa = pd.read_sql("SELECT c.causa_base, COUNT(f.sk_sinistro) as qtd FROM ft_sinistros f JOIN dm_causa c ON f.sk_causa = c.sk_causa GROUP BY c.causa_base ORDER BY qtd DESC LIMIT 10", engine)
fig3 = px.bar(df_causa, x='qtd', y='causa_base', orientation='h', title='<b>Top 10 Causas de Acidentes</b>', text='qtd', color_discrete_sequence=['#5DADE2'])
fig3.update_traces(textposition="outside", cliponaxis=False)
fig3 = aplicar_estilo_tcc(fig3, "Quantidade", "Causa")
fig3.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis=dict(range=[0, df_causa['qtd'].max() * 1.15]))

# G4: Carnaval
df_carnaval = pd.read_sql("SELECT CASE WHEN t.flag_carnaval = TRUE THEN 'Carnaval' ELSE 'Resto do Ano' END as periodo, COUNT(f.sk_sinistro) as total, COUNT(DISTINCT t.data_completa) as dias FROM ft_sinistros f JOIN dm_tempo t ON f.sk_tempo = t.sk_tempo GROUP BY t.flag_carnaval", engine)
df_carnaval['media'] = round(df_carnaval['total'] / df_carnaval['dias'], 2)
fig4 = px.bar(df_carnaval, x='periodo', y='media', color='periodo', title='<b>Média Diária: Carnaval vs Ano</b>', text='media', color_discrete_sequence=['#A9CCE3', '#154360'])
fig4.update_traces(textposition='outside', cliponaxis=False)
fig4 = aplicar_estilo_tcc(fig4, "Período", "Média Acidentes/Dia")
fig4.update_layout(showlegend=False, bargap=0.5, yaxis=dict(range=[0, df_carnaval['media'].max() * 1.15]))

# --- LAYOUT DO DASHBOARD (CSS FLEXBOX) ---
app = dash.Dash(__name__)

app.layout = html.Div(style={'fontFamily': 'Arial', 'backgroundColor': '#F3F4F6', 'padding': '20px'}, children=[
    html.Div(style={'backgroundColor': '#154360', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px', 'color': 'white', 'textAlign': 'center'}, children=[
        html.H1("Painel Analítico de Sinistralidade Viária - Bahia", style={'margin': '0'}),
        html.P("Projeto de Engenharia de Software | Fonte: Dados Abertos PRF", style={'margin': '5px 0 0 0'})
    ]),
    
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}, children=[
        html.Div(dcc.Graph(figure=fig1), style={'width': '48%', 'minWidth': '400px', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
        html.Div(dcc.Graph(figure=fig2), style={'width': '48%', 'minWidth': '400px', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
        html.Div(dcc.Graph(figure=fig3), style={'width': '48%', 'minWidth': '400px', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
        html.Div(dcc.Graph(figure=fig4), style={'width': '48%', 'minWidth': '400px', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'marginBottom': '20px'})
    ])
])

if __name__ == '__main__':
    print("Servidor rodando em http://127.0.0.1:8050/")
    app.run(debug=True)