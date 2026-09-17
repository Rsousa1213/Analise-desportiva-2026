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
st.markdown("Análise Avançada com Foco em **Over 1.5 & Over 2.5 Golos** & **Over 7.5 Cantos**")

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
stake_pct_max = st.sidebar.slider("Stake Máxima Base (%)", min_value=0.5, max_value=10.0, value=3.0, step=0.5)
st.sidebar.info("O valor a apostar agora varia dinamicamente consoante a força do Edge (+EV).")

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

            # Probabilidades de Golos (Over 1.5 e Over 2.5)
            prob_over_1_5 = (1 - (prob_matrix[0,0] + prob_matrix[1,0] + prob_matrix[0,1])) * 100
            odd_over_1_5 = 100 / prob_over_1_5 if prob_over_1_5 > 0 else 0

            prob_under_2_5 = 0
            for i in range(max_g):
                for j in range(max_g):
                    if (i + j) <= 2:
                        prob_under_2_5 += prob_matrix[i, j]
            prob_over_2_5 = (1 - prob_under_2_5) * 100
            odd_over_2_5 = 100 / prob_over_2_5 if prob_over_2_5 > 0 else 0

            # Cantos
            home_corners = home_games['HC'].mean() + home_games['AC'].mean()
            away_corners = away_games['HC'].mean() + away_games['AC'].mean()
            avg_total_corners = (home_corners + away_corners) / 2
            
            lambda_corners = avg_total_corners
            prob_over_7_5_corners = (1 - sum(poisson.pmf(k, lambda_corners) for k in range(8))) * 100
            odd_over_7_5_corners = 100 / prob_over_7_5_corners if prob_over_7_5_corners > 0 else 0

            # --- APRESENTAÇÃO DE DADOS ---
            st.markdown("---")
            st.subheader(f"📊 Análise Estatística: {home_team} vs {away_team}")
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Média Esperada (Casa)", f"{lambda_home:.2f} golos")
            col_m2.metric("Média Esperada (Fora)", f"{lambda_away:.2f} golos")
            col_m3.metric("Golos Totais Esperados", f"{(lambda_home + lambda_away):.2f}")
            col_m4.metric("Média Cantos Esperados", f"{avg_total_corners:.1f}")

            st.markdown("<br>", unsafe_allow_html=True)

            tab1, tab2, tab3, tab4 = st.tabs(["⚽ Over 1.5 Golos", "⚽ Over 2.5 Golos", "🚩 Cantos Over 7.5", "📈 Resumo de Banca"])

            with tab1:
                st.metric("Probabilidade Over 1.5 Golos", f"{prob_over_1_5:.1f}%", f"Odd Justa: {odd_over_1_5:.2f}")

            with tab2:
                st.metric("Probabilidade Over 2.5 Golos", f"{prob_over_2_5:.1f}%", f"Odd Justa: {odd_over_2_5:.2f}")

            with tab3:
                st.metric("Probabilidade Over 7.5 Cantos", f"{prob_over_7_5_corners:.1f}%", f"Odd Justa: {odd_over_7_5_corners:.2f}")

            with tab4:
                st.write(f"Banca Inicial: **{banca_inicial:.2f} €** | Stake Máxima Teto: **{stake_pct_max}%**")

            # --- TABELA COMPARATIVA DE VALUE BETS & STAKE DINÂMICA ---
            st.markdown("---")
            st.subheader("🎯 Comparador de Value Bets & Stake Dinâmica")
            st.markdown("Insere as **Odds da tua Casa de Apostas**. A stake em euros ajusta-se automaticamente de forma inteligente com base na magnitude do **Edge (+EV)**.")

            defval_o15 = float(np.clip(round(odd_over_1_5 + 0.1, 2), 1.01, 50.0))
            defval_o25 = float(np.clip(round(odd_over_2_5 + 0.1, 2), 1.01, 50.0))
            defval_c75 = float(np.clip(round(odd_over_7_5_corners + 0.1, 2), 1.01, 50.0))

            bc1, bc2, bc3 = st.columns(3)
            with bc1:
                bookie_odd_o15 = st.number_input("Odd Casa (Over 1.5)", min_value=1.01, max_value=50.0, value=defval_o15, step=0.01)
            with bc2:
                bookie_odd_o25 = st.number_input("Odd Casa (Over 2.5)", min_value=1.01, max_value=50.0, value=defval_o25, step=0.01)
            with bc3:
                bookie_odd_c75 = st.number_input("Odd Casa (Cantos 7.5)", min_value=1.01, max_value=50.0, value=defval_c75, step=0.01)

            # Cálculo de Edge / Valor (%)
            edge_o15 = ((prob_over_1_5 / 100) * bookie_odd_o15 - 1) * 100
            edge_o25 = ((prob_over_2_5 / 100) * bookie_odd_o25 - 1) * 100
            edge_c75 = ((prob_over_7_5_corners / 100) * bookie_odd_c75 - 1) * 100

            # Função de cálculo de stake dinâmica baseada no Edge (fator de escala progressivo limitado pela stake máxima)
            def calcular_stake_dinamica(edge, banca, max_pct):
                if edge <= 0:
                    return 0.0
                # Exemplo de fator dinâmico: cada 5% de edge aproxima-se da stake máxima definida
                fator = min(edge / 10.0, 1.0) 
                percentagem_aplicada = max_pct * fator
                return (banca * percentagem_aplicada) / 100.0

            val_o15 = calcular_stake_dinamica(edge_o15, banca_inicial, stake_pct_max)
            val_o25 = calcular_stake_dinamica(edge_o25, banca_inicial, stake_pct_max)
            val_c75 = calcular_stake_dinamica(edge_c75, banca_inicial, stake_pct_max)

            # Montagem da Tabela com valores dinâmicos
            tabela_dados = [
                {
                    "Mercado Base": "Over 1.5 Golos",
                    "Probabilidade": f"{prob_over_1_5:.1f}%",
                    "Odd Justa (Modelo)": f"{odd_over_1_5:.2f}",
                    "Odd Casa de Apostas": f"{bookie_odd_o15:.2f}",
                    "Valor (+EV / Edge)": f"{edge_o15:+.2f}%",
                    "Aposta Dinâmica": f"{val_o15:.2f} €" if val_o15 > 0 else "0.00 €",
                    "Recomendação": "🔥 VALOR" if edge_o15 > 0 else "❌ Sem Valor"
                },
                {
                    "Mercado Base": "Over 2.5 Golos",
                    "Probabilidade": f"{prob_over_2_5:.1f}%",
                    "Odd Justa (Modelo)": f"{odd_over_2_5:.2f}",
                    "Odd Casa de Apostas": f"{bookie_odd_o25:.2f}",
                    "Valor (+EV / Edge)": f"{edge_o25:+.2f}%",
                    "Aposta Dinâmica": f"{val_o25:.2f} €" if val_o25 > 0 else "0.00 €",
                    "Recomendação": "🔥 VALOR" if edge_o25 > 0 else "❌ Sem Valor"
                },
                {
                    "Mercado Base": "Over 7.5 Cantos",
                    "Probabilidade": f"{prob_over_7_5_corners:.1f}%",
                    "Odd Justa (Modelo)": f"{odd_over_7_5_corners:.2f}",
                    "Odd Casa de Apostas": f"{bookie_odd_c75:.2f}",
                    "Valor (+EV / Edge)": f"{edge_c75:+.2f}%",
                    "Aposta Dinâmica": f"{val_c75:.2f} €" if val_c75 > 0 else "0.00 €",
                    "Recomendação": "🔥 VALOR" if edge_c75 > 0 else "❌ Sem Valor"
                }
            ]

            df_tabela = pd.DataFrame(tabela_dados)
            st.dataframe(df_tabela, use_container_width=True, hide_index=True)

        else:
            st.info("ℹ️ Selecione equipas válidas para calcular as estatísticas.")
    else:
        st.warning("⚠️ Sem dados disponíveis para esta competição.")
