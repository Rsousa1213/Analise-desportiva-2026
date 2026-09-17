import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
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

# 2. Dicionário de Ligas (Com épocas estáveis e testadas)
LEAGUES = {
    "🇪🇺 Liga dos Campeões 26/27": {"type": "mock_cl"},
    "🇪🇺 Liga Europa 26/27": {"type": "mock_el"},
    "PT Liga Portugal": {"url": "https://www.football-data.co.uk/mmz4281/2324/P1.csv", "type": "domestic"},
    "ES La Liga (Espanha)": {"url": "https://www.football-data.co.uk/mmz4281/2324/SP1.csv", "type": "domestic"},
    "IT Serie A (Itália)": {"url": "https://www.football-data.co.uk/mmz4281/2324/I1.csv", "type": "domestic"},
    "EN Premier League (Inglaterra)": {"url": "https://www.football-data.co.uk/mmz4281/2324/E0.csv", "type": "domestic"},
    "BR Brasileirão (Brasil)": {"url": "https://www.football-data.co.uk/new/BRA.csv", "type": "domestic"},
    "AR Liga Profesional (Argentina)": {"url": "https://www.football-data.co.uk/new/ARG.csv", "type": "domestic"}
}

TEAMS_CL_2627 = [
    "Real Madrid", "Barcelona", "Manchester City", "Arsenal", "Bayern München", 
    "Bayer Leverkusen", "Inter", "Juventus", "PSG", "Benfica", "Sporting CP", 
    "FC Porto", "Atletico Madrid", "Borussia Dortmund", "Atalanta", "RB Leipzig"
]

TEAMS_EL_2627 = [
    "AS Roma", "Lazio", "Manchester United", "Tottenham", "Real Sociedad", 
    "Athletic Bilbao", "Eintracht Frankfurt", "Villarreal", "Braga", "Vitoria Guimarães", 
    "Lyon", "Marseille", "Feyenoord", "AZ Alkmaar"
]

def generate_mock_data(team_list):
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

@st.cache_data
def load_league_data(selected_league):
    info = LEAGUES.get(selected_league, {})
    league_type = info.get("type")

    if league_type == "mock_cl":
        return generate_mock_data(TEAMS_CL_2627)
    elif league_type == "mock_el":
        return generate_mock_data(TEAMS_EL_2627)

    url = info.get("url", "")
    if not url:
        return pd.DataFrame()

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            csv_data = io.StringIO(response.content.decode('latin1'))
            df = pd.read_csv(csv_data, on_bad_lines="skip")
            
            # Normalização robusta de colunas para evitar falhas de leitura
            rename_map = {}
            if 'Home' in df.columns: rename_map['Home'] = 'HomeTeam'
            if 'Away' in df.columns: rename_map['Away'] = 'AwayTeam'
            if 'HG' in df.columns: rename_map['HG'] = 'FTHG'
            if 'AG' in df.columns: rename_map['AG'] = 'FTAG'
            
            df = df.rename(columns=rename_map)
            
            # Garantir colunas essenciais
            if 'HomeTeam' not in df.columns or 'AwayTeam' not in df.columns:
                return pd.DataFrame()
            if 'FTHG' not in df.columns: df['FTHG'] = 0
            if 'FTAG' not in df.columns: df['FTAG'] = 0
            if 'HC' not in df.columns: df['HC'] = 0
            if 'AC' not in df.columns: df['AC'] = 0
            
            # Limpar linhas vazias
            df = df.dropna(subset=['HomeTeam', 'AwayTeam'])
            return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# 5. Interface da Barra Lateral (Ligas + Gestão de Banca)
selected_league = st.sidebar.selectbox("Selecione a Liga / Competição:", list(LEAGUES.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Gestão de Banca")
banca_inicial = st.sidebar.number_input("Valor da Banca (€)", min_value=1.0, value=100.0, step=10.0)
stake_pct = st.sidebar.slider("Percentagem de Aposta (%)", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
valor_stake = (banca_inicial * stake_pct) / 100
st.sidebar.info(f"Valor recomendado por aposta: **{valor_stake:.2f} €**")

# Processamento de Dados e Métricas
if selected_league:
    df = load_league_data(selected_league)
    if df is not None and not df.empty and 'HomeTeam' in df.columns:
        teams = sorted(list(set(df['HomeTeam'].dropna().unique()).union(set(df['AwayTeam'].dropna().unique()))))
        
        col1, col2 = st.columns(2)
        with col1:
            home_team = st.selectbox("Equipa da Casa", teams, index=0)
        with col2:
            away_options = [t for t in teams if t != home_team]
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
        else:
            st.info("ℹ️ Selecione equipas válidas para calcular as estatísticas.")
    else:
        st.warning("⚠️ A carregar dados da competição ou liga sem dados disponíveis de momento.")
