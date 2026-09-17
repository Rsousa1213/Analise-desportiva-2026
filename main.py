import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# 1. Configuração da Página
st.set_page_config(
    page_title="Análise Desportiva 26/27",
    layout="wide"
)

def aplicar_fundo_estadio():
    url_imagem = "https://raw.githubusercontent.com/Rsousa1213/Analise-desportiva-2026/main/fundo_estadio.jpg"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.6)), url('{url_imagem}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        [data-testid="stHeader"], [data-testid="stSidebar"] {{
            background-color: transparent !important;
        }}
        .stMainBlockContainer {{
            background-color: rgba(18, 18, 18, 0.65) !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

aplicar_fundo_estadio()

st.title("⚽ Análise Desportiva 26/27")
st.markdown("Análise focada no **Mercado de Golos (Over 1.5 Pré-Live & Over 2.5)** e **Cantos** com Odds Automáticas")

# 2. Dicionário de Ligas com Equipas Reais por Competição
LEAGUES_TEAMS = {
    "🇪🇺 Liga dos Campeões 26/27": [
        "Real Madrid", "Barcelona", "Manchester City", "Arsenal", "Bayern München", 
        "Bayer Leverkusen", "Inter", "Juventus", "PSG", "Benfica", "Sporting CP", 
        "FC Porto", "Atletico Madrid", "Borussia Dortmund", "Atalanta", "RB Leipzig"
    ],
    "🇪🇺 Liga Europa 26/27": [
        "AS Roma", "Lazio", "Manchester United", "Tottenham", "Real Sociedad", 
        "Athletic Bilbao", "Eintracht Frankfurt", "Villarreal", "Braga", "Vitoria Guimarães", 
        "Lyon", "Marseille", "Feyenoord", "AZ Alkmaar"
    ],
    "PT Liga Portugal": [
        "Sporting CP", "SL Benfica", "FC Porto", "SC Braga", "Vitória SC", 
        "Moreirense", "Arouca", "Famalicão", "Casa Pia", "Farense", 
        "Rio Ave", "Gil Vicente", "Estoril", "Boavista", "Estrela Amadora", "AVS", "Nacional", "Santa Clara"
    ],
    "ES La Liga (Espanha)": [
        "Real Madrid", "Barcelona", "Atletico Madrid", "Athletic Bilbao", "Real Sociedad", 
        "Villarreal", "Real Betis", "Sevilla", "Valencia", "Girona", 
        "Celta Vigo", "Osasuna", "Getafe", "Mallorca", "Rayo Vallecano", "Alavés", "Las Palmas", "Leganés", "Valladolid", "Espanyol"
    ],
    "IT Serie A (Itália)": [
        "Inter", "AC Milan", "Juventus", "Napoli", "Atalanta", 
        "AS Roma", "Lazio", "Fiorentina", "Bologna", "Torino", 
        "Monza", "Genoa", "Lecce", "Udinese", "Cagliari", "Empoli", "Verona", "Parma", "Como", "Venezia"
    ],
    "EN Premier League (Inglaterra)": [
        "Manchester City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham", 
        "Chelsea", "Newcastle", "Manchester United", "West Ham", "Crystal Palace", 
        "Brighton", "Bournemouth", "Fulham", "Wolves", "Everton", "Brentford", "Nottingham Forest", "Leicester City", "Ipswich Town", "Southampton"
    ],
    "BR Brasileirão (Brasil)": [
        "Flamengo", "Palmeiras", "Atlético Mineiro", "Fluminense", "São Paulo", 
        "Internacional", "Grêmio", "Botafogo", "Corinthians", "Athletico Paranaense", 
        "Bahia", "Fortaleza", "Cruzeiro", "Vasco da Gama", "Cuiabá", "Red Bull Bragantino", "Juventude", "Criciúma", "Atlético Goianiense", "Vitória"
    ],
    "AR Liga Profesional (Argentina)": [
        "River Plate", "Boca Juniors", "Racing Club", "Independiente", "San Lorenzo", 
        "Estudiantes", "Vélez Sarsfield", "Talleres", "Lanús", "Argentinos Juniors", 
        "Defensa y Justicia", "Belgrano", "Godoy Cruz", "Newell's Old Boys", "Rosario Central"
    ]
}

def generate_league_data(team_list):
    records = []
    np.random.seed(42)
    for i in range(len(team_list)):
        for j in range(len(team_list)):
            if i != j:
                records.append({
                    "HomeTeam": team_list[i],
                    "AwayTeam": team_list[j],
                    "FTHG": np.random.poisson(1.6),
                    "FTAG": np.random.poisson(1.1),
                    "HC": np.random.randint(3, 9),
                    "AC": np.random.randint(2, 7)
                })
    return pd.DataFrame(records)

# 5. Interface da Barra Lateral
selected_league = st.sidebar.selectbox("Selecione a Liga / Competição:", list(LEAGUES_TEAMS.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Gestão de Banca")
banca_inicial = st.sidebar.number_input("Valor da Banca (€)", min_value=1.0, value=100.0, step=10.0)
stake_pct = st.sidebar.slider("Percentagem de Aposta (%)", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
valor_stake = (banca_inicial * stake_pct) / 100
st.sidebar.info(f"Valor recomendado por aposta: **{valor_stake:.2f} €**")

# Processamento e Métricas
if selected_league:
    teams_list = LEAGUES_TEAMS[selected_league]
    df = generate_league_data(teams_list)
    
    if df is not None and not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            home_team = st.selectbox("Equipa da Casa", teams_list, index=0)
        with col2:
            away_options = [t for t in teams_list if t != home_team]
            away_team = st.selectbox("Equipa Visitante", away_options, index=0 if away_options else 0)

        home_games = df[df['HomeTeam'] == home_team]
        away_games = df[df['AwayTeam'] == away_team]

        if not home_games.empty and not away_games.empty:
            avg_home_goals_for = home_games['FTHG'].mean()
            avg_home_goals_against = home_games['FTAG'].mean()
            avg_away_goals_for = away_games['FTAG'].mean()
            avg_away_goals_against = home_games['FTHG'].mean()

            league_avg_home = df['FTHG'].mean()
            league_avg_away = df['FTAG'].mean()

            lambda_home = (avg_home_goals_for / league_avg_home if league_avg_home else 1) * \
                          (avg_away_goals_against / league_avg_home if league_avg_home else 1) * league_avg_home
            lambda_away = (avg_away_goals_for / league_avg_away if league_avg_away else 1) * \
                          (avg_home_goals_against / league_avg_away if league_avg_away else 1) * league_avg_away

            max_g = 7
            prob_matrix = np.zeros((max_g, max_g))
            for i in range(max_g):
                for j in range(max_g):
                    prob_matrix[i, j] = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)

            prob_over_1_5 = (1 - (prob_matrix[0,0] + prob_matrix[1,0] + prob_matrix[0,1])) * 100
            prob_over_2_5 = (1 - np.sum(np.tril(prob_matrix, 2))) * 100

            home_corners = home_games['HC'].mean() + home_games['AC'].mean()
            away_corners = away_games['HC'].mean() + away_games['AC'].mean()
            avg_total_corners = (home_corners + away_corners) / 2

            st.subheader("📊 Análise do Jogo")
            c1, c2, c3 = st.columns(3)
            c1.metric("Probabilidade Over 1.5 Golos", f"{prob_over_1_5:.1f}%")
            c2.metric("Probabilidade Over 2.5 Golos", f"{prob_over_2_5:.1f}%")
            c3.metric("Média Estimada de Cantos", f"{avg_total_corners:.1f}")
