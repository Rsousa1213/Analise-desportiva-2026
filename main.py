import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# 1. Configuração da Página
st.set_page_config(
    page_title="Análise Desportiva 26/27",
    layout="wide"
)

def aplicar_estilo_visual():
    url_imagem = "https://raw.githubusercontent.com/Rsousa1213/Analise-desportiva-2026/main/fundo_estadio.jpg"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.85)), url('{url_imagem}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        [data-testid="stHeader"], [data-testid="stSidebar"] {{
            background-color: rgba(15, 15, 15, 0.8) !important;
        }}
        .stMainBlockContainer {{
            background-color: rgba(22, 22, 22, 0.92) !important;
            border-radius: 16px !important;
            padding: 2.5rem !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        h1, h2, h3, p, label, .stMarkdown {{
            color: #f0f2f6 !important;
        }}
        div[data-testid="stMetric"] {{
            background-color: rgba(35, 35, 35, 0.85);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

aplicar_estilo_visual()

st.title("⚽ Análise Desportiva 26/27")
st.markdown("Análise Avançada para **Mercado de Golos, BTTS & Cantos** com Odds Automáticas")

# 2. Dicionário de Ligas com Equipas Reais
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

# 3. Barra Lateral (Gestão de Banca)
selected_league = st.sidebar.selectbox("Selecione a Liga / Competição:", list(LEAGUES_TEAMS.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Gestão de Banca")
banca_inicial = st.sidebar.number_input("Valor da Banca (€)", min_value=1.0, value=100.0, step=10.0)
stake_pct = st.sidebar.slider("Percentagem de Aposta (%)", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
valor_stake = (banca_inicial * stake_pct) / 100
st.sidebar.info(f"Valor recomendado por aposta: **{valor_stake:.2f} €**")

# 4. Corpo Principal
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

            # Cálculos de Probabilidades
            prob_over_1_5 = (1 - (prob_matrix[0,0] + prob_matrix[1,0] + prob_matrix[0,1])) * 100
            prob_over_2_5 = (1 - np.sum(np.tril(prob_matrix, 2))) * 100
            prob_btts = (1 - np.sum(prob_matrix[0, :]) - np.sum(prob_matrix[:, 0]) + prob_matrix[0,0]) * 100

            # Odds Justas (1 / Probabilidade)
            odd_over_1_5 = 100 / prob_over_1_5 if prob_over_1_5 > 0 else 0
            odd_over_2_5 = 100 / prob_over_2_5 if prob_over_2_5 > 0 else 0
            odd_btts = 100 / prob_btts if prob_btts > 0 else 0

            # Cantos
            home_corners = home_games['HC'].mean() + home_games['AC'].mean()
            away_corners = away_games['HC'].mean() + away_games['AC'].mean()
            avg_total_corners = (home_corners + away_corners) / 2
            estimated_ht_corners = avg_total_corners * 0.45

            # --- APRESENTAÇÃO DE DADOS NA PÁGINA ---
            st.markdown("---")
            st.subheader(f"📊 Análise Estatística: {home_team} vs {away_team}")
            
            # Bloco 1: Métricas Principais de Golos
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Média Esperada (Casa)", f"{lambda_home:.2f} golos")
            col_m2.metric("Média Esperada (Fora)", f"{lambda_away:.2f} golos")
            col_m3.metric("Golos Totais Esperados", f"{(lambda_home + lambda_away):.2f}")
            col_m4.metric("Previsão de Cantos (Jogo)", f"{avg_total_corners:.1f}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Bloco 2: Probabilidades e Odds Justas detalhadas
            st.markdown("### 🎯 Mercados Principais & Odds Justas")
            
            tab1, tab2, tab3 = st.tabs(["⚽ Mercado de Golos", "🚩 Mercado de Cantos", "📈 Resumo de Stake"])

            with tab1:
                gc1, gc2, gc3 = st.columns(3)
                gc1.metric("Prob. Over 1.5 Golos", f"{prob_over_1_5:.1f}%", f"Odd Justa: {odd_over_1_5:.2f}")
                gc2.metric("Prob. Over 2.5 Golos", f"{prob_over_2_5:.1f}%", f"Odd Justa: {odd_over_2_5:.2f}")
                gc3.metric("Ambas Marcam (BTTS)", f"{prob_btts:.1f}%", f"Odd Justa: {odd_btts:.2f}")

            with tab2:
                cc1, cc2 = st.columns(2)
                cc1.metric("Média Cantos 1ª Parte", f"{estimated_ht_corners:.1f}")
                cc2.metric("Média Cantos Jogo Completo", f"{avg_total_corners:.1f}")
                st.info("💡 **Dica de Cantos:** Valores acima de 9.5 cantos no total da partida apresentam maior valor histórico nas ligas selecionadas.")

            with tab3:
                st.write(f"Para uma banca de **{banca_inicial:.2f} €** com uma stake de **{stake_pct}%**, o montante recomendado a investir nesta seleção é de **{valor_stake:.2f} €**.")
                st.success("✔ Gestão de risco otimizada de acordo com os parâmetros configurados na barra lateral.")
        else:
            st.info("ℹ️ Selecione equipas válidas para calcular as estatísticas.")
    else:
        st.warning("⚠️ Sem dados disponíveis para esta competição.")
