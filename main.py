import numpy as np
import pandas as pd
from scipy.stats import poisson
import streamlit as st
import sqlite3
import os
from datetime import datetime

# 1. Configuração da Página e Estilo Visual
st.set_page_config(
    page_title="Analise 26/27 - Avançada",
    layout="wide",
    initial_sidebar_state="expanded",
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
            background-color: rgba(15, 15, 15, 0.85) !important;
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
        div[data-testid="stMetricValue"] {{
            font-size: 1.8rem !important;
        }}
        .badge-sintetico {{
            display: inline-block;
            background-color: rgba(180, 60, 20, 0.85);
            color: #fff !important;
            padding: 4px 12px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        .badge-real {{
            display: inline-block;
            background-color: rgba(30, 120, 60, 0.85);
            color: #fff !important;
            padding: 4px 12px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


aplicar_estilo_visual()

# Título Principal
st.markdown("### ⚽ Analise 26/27 - Rigor Estatístico & Inteligência Avançada")

# 2. Mapeamento das Ligas Oficiais (com a J-League integrada)
LEAGUES_CONFIG = {
    "J-League": {
        "teams": [
            "Avispa Fukuoka", "Cerezo Osaka", "Fagiano Okayama", "FC Machida Zelvia", 
            "FC Tokyo", "Gamba Osaka", "JEF United Chiba", "Kashima Antlers", 
            "Kashiwa Reysol", "Kawasaki Frontale", "Kyoto Sanga FC", "Mito HollyHock", 
            "Nagoya Grampus", "Sanfrecce Hiroshima", "Shimizu S-Pulse", "Tokyo Verdy", 
            "Urawa Red Diamonds", "V-Varen Nagasaki", "Vissel Kobe", "Yokohama F. Marinos",
        ],
        "csv_url": "",
    },
    "Portuguesa": {
        "teams": [
            "Académico Casa Pia AC", "CD Nacional", "Estoril Praia", "Estrela Amadora",
            "FC Alverca", "FC Arouca", "FC Famalicão", "FC Porto", "Gil Vicente FC",
            "Marítimo M.", "Moreirense FC", "Rio Ave FC", "Santa Clara", "SC Braga",
            "SL Benfica", "Sporting CP", "Vitória SC",
        ],
        "csv_url": "https://www.football-data.co.uk/mmh2627/P1.csv",
    },
    "Inglesa": {
        "teams": [
            "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Chelsea",
            "Coventry City", "Crystal Palace", "Everton", "Fulham", "Hull City",
            "Ipswich Town", "Leeds United", "Liverpool", "Manchester City",
            "Manchester United", "Newcastle", "Nottingham Forest", "Sunderland",
            "Tottenham",
        ],
        "csv_url": "https://www.football-data.co.uk/mmh2627/E0.csv",
    },
    "Espanhola": {
        "teams": [
            "Athletic Bilbao", "Atlético de Madrid", "Osasuna", "Elche", "Alavés",
            "Espanyol", "Barcelona", "Getafe", "Levante", "Málaga", "Racing Santander",
            "Rayo Vallecano", "Celta de Vigo", "Deportivo La Coruña", "Real Betis",
            "Real Madrid", "Real Sociedad", "Sevilla", "Valencia", "Villarreal",
        ],
        "csv_url": "https://www.football-data.co.uk/mmh2627/SP1.csv",
    },
    "Italiana": {
        "teams": [
            "Atalanta", "Bologna", "Cagliari", "Como", "Fiorentina", "Frosinone",
            "Genoa", "Inter de Milão", "Juventus", "Lazio", "Lecce", "Milan", "Monza",
            "Napoli", "Parma", "Roma", "Sassuolo", "Torino", "Udinese", "Venezia",
        ],
        "csv_url": "https://www.football-data.co.uk/mmh2627/I1.csv",
    },
    "Francesa": {
        "teams": [
            "Angers SCO", "AJ Auxerre", "Stade Brestois 29", "Le Havre AC",
            "Le Mans FC", "RC Lens", "LOSC Lille", "FC Lorient", "Olympique Lyonnais",
            "Olympique de Marseille", "AS Monaco", "OGC Nice", "Paris FC",
            "Paris Saint-Germain", "Stade Rennais", "RC Strasbourg Alsace",
            "Toulouse FC", "ESTAC Troyes",
        ],
        "csv_url": "https://www.football-data.co.uk/mmh2627/F1.csv",
    },
    "Brasileira Série A": {
        "teams": [
            "Flamengo", "Palmeiras", "Athletico PR", "Bahia", "Fluminense", "Cruzeiro",
            "Atlético MG", "Coritiba", "Bragantino", "Santos", "Botafogo", "São Paulo",
            "Vitória", "Corinthians", "Mirassol", "Grêmio", "Vasco", "Internacional",
            "Remo", "Chapecoense",
        ],
        "csv_url": "",
    },
    "Brasileira Série B": {
        "teams": [
            "Ponte Preta", "Londrina", "São Bernardo", "Náutico", "Criciúma", "Goiás",
            "Novorizontino", "CRB", "Avaí", "Atlético-GO", "Cuiabá", "América-MG",
            "Vila Nova", "Operário-PR", "Athletic", "Botafogo-SP", "Sport",
            "Juventude", "Ceará", "Fortaleza",
        ],
        "csv_url": "",
    },
    "Argentina": {
        "teams": [
            "AA Estudiantes", "Aldosivi", "Argentinos Juniors", "Atlético Tucumán",
            "Banfield", "Barracas Central", "Belgrano Córdoba", "Boca Juniors",
            "Central Córdoba", "Defensa y Justicia", "Deportivo Riestra",
            "Estudiantes", "Gimnasia La Plata", "Gimnasia Mendoza", "Huracán",
            "Independiente", "Independiente Rivadavia", "Instituto Córdoba", "Lanús",
            "Newell´s Old Boys", "Platense", "Racing Club", "River Plate",
            "Rosario Central", "San Lorenzo", "Sarmiento de Junín", "Talleres Córdoba",
            "Tigre", "Unión de Santa Fe", "Vélez Sarsfield",
        ],
        "csv_url": "",
    },
    "Liga Campeoes": {
        "teams": [
            "Bayern de Munique", "Borussia Dortmund", "RB Leipzig", "Stuttgart",
            "Club Brugge", "Barcelona", "Real Madrid", "Villarreal",
            "Atlético de Madrid", "Betis", "PSG", "Lens", "Lille", "Arsenal",
            "Manchester City", "Manchester United", "Aston Villa", "Liverpool",
            "Inter de Milão", "Napoli", "Roma", "Como", "PSV", "Feyernoord", "Porto",
            "Sporting", "Slavia Praga", "Galatasaray", "Shakhtar Donetsk",
        ],
        "csv_url": "",
    },
    "Liga Europa": {
        "teams": [
            "Anderlecht", "Ararat-Armenia", "AZ Alkmaar", "Benfica", "Beşiktaş",
            "Bournemouth", "Celje", "Celta", "Celtic", "Crystal Palace",
            "Ferencváros", "GNK Dinamo", "H. Beer-Sheva", "Hoffenheim", "Jagiellonia",
            "Juventus", "Lech Poznań", "Leverkusen", "Levski Sofia", "Lillestrøm",
            "Lyon", "Marseille", "Milan", "N.E.C.", "OFI Crete", "Olympiacos",
            "Omonia", "Real Sociedad", "Rennes", "Salzburg", "Sparta Praha",
            "Sturm Graz", "Sunderland", "Torreense", "Union SG", "Viktoria Plzeň",
        ],
        "csv_url": "",
    },
}

# --- Constantes do modelo ---
JOGOS_MIN_PARA_CONFIANCA_TOTAL = 8
RHO_DIXON_COLES = -0.10
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historico_apostas.db")


def rho_correction(gh, ga, lam_h, lam_a, rho):
    if gh == 0 and ga == 0:
        return 1 - (lam_h * lam_a * rho)
    elif gh == 0 and ga == 1:
        return 1 + (lam_h * rho)
    elif gh == 1 and ga == 0:
        return 1 + (lam_a * rho)
    elif gh == 1 and ga == 1:
        return 1 - rho
    return 1.0


def media_com_shrinkage(valores, pesos, media_liga, n_min=JOGOS_MIN_PARA_CONFIANCA_TOTAL):
    n = len(valores)
    if n == 0:
        return media_liga
    media_equipa = np.average(valores, weights=pesos)
    peso_confianca = min(n / n_min, 1.0)
    return peso_confianca * media_equipa + (1 - peso_confianca) * media_liga


def calcular_lambdas_mercado(df_liga, home_team, away_team, col_pro_casa, col_pro_fora, floor=0.4):
    df_home_all = df_liga[df_liga["HomeTeam"] == home_team]
    df_away_all = df_liga[df_liga["AwayTeam"] == away_team]

    media_liga_casa = df_liga[col_pro_casa].mean()
    media_liga_fora = df_liga[col_pro_fora].mean()

    ataque_casa = media_com_shrinkage(df_home_all[col_pro_casa], df_home_all["Peso_Temporal"], media_liga_casa)
    defesa_casa = media_com_shrinkage(df_home_all[col_pro_fora], df_home_all["Peso_Temporal"], media_liga_fora)

    ataque_fora = media_com_shrinkage(df_away_all[col_pro_fora], df_away_all["Peso_Temporal"], media_liga_fora)
    defesa_fora = media_com_shrinkage(df_away_all[col_pro_casa], df_away_all["Peso_Temporal"], media_liga_casa)

    lambda_casa = max(floor, (ataque_casa / media_liga_casa) * (defesa_fora / media_liga_casa) * media_liga_casa)
    lambda_fora = max(floor, (ataque_fora / media_liga_fora) * (defesa_casa / media_liga_fora) * media_liga_fora)

    return lambda_casa, lambda_fora


@st.cache_data(ttl=3600)
def carregar_dados_reais(liga_nome, team_list):
    config = LEAGUES_CONFIG.get(liga_nome, {})
    csv_url = config.get("csv_url", "")
    df = None
    dados_reais = False

    if csv_url:
        try:
            df_raw = pd.read_csv(csv_url)
            if {"HomeTeam", "AwayTeam", "FTHG", "FTAG"}.issubset(df_raw.columns):
                df = df_raw.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"]).copy()
                for col, default_val in [("HC", 5), ("AC", 4), ("HY", 2), ("AY", 2)]:
                    if col not in df.columns:
                        df[col] = default_val

                if "Date" in df.columns:
                    try:
                        df["Date_parsed"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
                        df = df.sort_values("Date_parsed").drop(columns=["Date_parsed"])
                    except Exception:
                        pass
                dados_reais = True
        except Exception:
            df = None

    if df is None or df.empty:
        records = []
        np.random.seed(42)
        for i in range(len(team_list)):
            for j in range(len(team_list)):
                if i != j:
                    records.append({
                        "HomeTeam": team_list[i],
                        "AwayTeam": team_list[j],
                        "FTHG": np.random.poisson(1.5),
                        "FTAG": np.random.poisson(1.1),
                        "HC": np.random.randint(3, 9),
                        "AC": np.random.randint(2, 7),
                        "HY": np.random.randint(1, 4),
                        "AY": np.random.randint(1, 4),
                    })
        df = pd.DataFrame(records)
        dados_reais = False

    n_rows = len(df)
    df["Peso_Temporal"] = np.linspace(0.5, 1.0, n_rows)
    return df, dados_reais


# --- Persistência do histórico de apostas ---
def inicializar_bd():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS apostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_registo TEXT,
            liga TEXT,
            equipa_casa TEXT,
            equipa_fora TEXT,
            mercado TEXT,
            probabilidade REAL,
            odd REAL,
            edge REAL,
            stake REAL,
            resultado TEXT DEFAULT 'Pendente',
            lucro REAL
        )
    """)
    for coluna, tipo in [("casa_aposta", "TEXT"), ("odd_fecho", "REAL")]:
        try:
            conn.execute(f"ALTER TABLE apostas ADD COLUMN {coluna} {tipo}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()


def registar_aposta(liga, casa, fora, mercado, prob, odd, edge, stake, casa_aposta=""):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO apostas (data_registo, liga, equipa_casa, equipa_fora, mercado, "
        "probabilidade, odd, edge, stake, resultado, lucro, casa_aposta, odd_fecho) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M"), liga, casa, fora, mercado,
         prob, odd, edge, stake, "Pendente", None, casa_aposta, None),
    )
    conn.commit()
    conn.close()


def atualizar_odd_fecho(aposta_id, odd_fecho):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE apostas SET odd_fecho=? WHERE id=?", (odd_fecho, aposta_id))
    conn.commit()
    conn.close()


def obter_apostas():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM apostas ORDER BY id DESC", conn)
    conn.close()
    return df


def atualizar_resultado(aposta_id, resultado):
    conn = sqlite3.connect(DB_PATH)
    stake, odd = conn.execute("SELECT stake, odd FROM apostas WHERE id=?", (aposta_id,)).fetchone()
    if resultado == "Ganhou":
        lucro = stake * (odd - 1)
    elif resultado == "Perdeu":
        lucro = -stake
    else:
        lucro = 0.0
    conn.execute("UPDATE apostas SET resultado=?, lucro=? WHERE id=?", (resultado, lucro, aposta_id))
    conn.commit()
    conn.close()


inicializar_bd()

# Configuração na Barra Lateral
selected_league = st.sidebar.selectbox(
    "Selecione a Liga / Competição:", list(LEAGUES_CONFIG.keys())
)

st.sidebar.markdown("---")
st.sidebar.subheader("Banca & Gestão")
banca_inicial = st.sidebar.number_input(
    "Valor da Banca (€)", min_value=1.0, value=100.0, step=10.0
)
stake_pct_max = st.sidebar.slider(
    "Stake Máxima Base (%)", min_value=0.5, max_value=5.0, value=5.0, step=0.5
)
fracao_kelly = st.sidebar.slider(
    "Fração de Kelly a usar",
    min_value=0.1, max_value=1.0, value=0.25, step=0.05,
    help="Kelly puro (1.0) maximiza crescimento a longo prazo mas com muita variância. "
         "Valores entre 0.25 e 0.5 ('Kelly fracionário') são o standard para reduzir risco de ruína."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filtros de Rigor")
min_odd_permitida = st.sidebar.number_input(
    "Odd Mínima de Segurança", min_value=1.01, value=1.30, step=0.05
)
edge_minimo = st.sidebar.slider(
    "Edge Mínimo Exigido (%)", min_value=0.5, max_value=10.0, value=3.0, step=0.5
) / 100

st.sidebar.markdown("---")
st.sidebar.subheader("✏️ Inserção Manual de Odds")
casa_de_apostas = st.sidebar.text_input(
    "Casa de Apostas (fonte das odds)", value="", placeholder="ex: Captain's"
)
odd_over_15 = st.sidebar.number_input("Odd Over 1.5 Golos", min_value=1.01, value=1.65, step=0.01)
odd_under_15 = st.sidebar.number_input("Odd Under 1.5 Golos", min_value=1.01, value=2.20, step=0.01)
odd_over_25 = st.sidebar.number_input("Odd Over 2.5 Golos", min_value=1.01, value=1.95, step=0.01)
odd_under_25 = st.sidebar.number_input("Odd Under 2.5 Golos", min_value=1.01, value=1.85, step=0.01)
odd_btts = st.sidebar.number_input("Odd Ambas Marcam (BTTS)", min_value=1.01, value=1.80, step=0.01)
odd_cantos_over_75 = st.sidebar.number_input("Odd Cantos Over 7.5", min_value=1.01, value=1.55, step=0.01)
odd_cartoes_over_45 = st.sidebar.number_input("Odd Cartões Over 4.5", min_value=1.01, value=1.90, step=0.01)
odd_over_05_1p = st.sidebar.number_input("Odd Over 0.5 1ª Parte", min_value=1.01, value=1.40, step=0.01)

tab_analise, tab_historico = st.tabs(["🎯 Análise do Jogo", "📈 Histórico & Desempenho"])

with tab_analise:
    teams_available = LEAGUES_CONFIG[selected_league]["teams"]
    df_liga, dados_sao_reais = carregar_dados_reais(selected_league, teams_available)

    if dados_sao_reais:
        st.markdown('<span class="badge-real">✅ Dados reais (football-data.co.uk)</span>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<span class="badge-sintetico">⚠️ Dados simulados — não há CSV real para esta competição, '
            'os números abaixo são apenas ilustrativos</span>',
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Equipa da Casa", teams_available, index=0 if len(teams_available) > 0 else 0)
    with col2:
        away_team = st.selectbox("Equipa Visitante", teams_available, index=1 if len(teams_available) > 1 else 0)

    if home_team == away_team:
        st.warning("⚠️ Seleciona duas equipas diferentes para realizar a análise.")
    else:
        df_home_all = df_liga[df_liga["HomeTeam"] == home_team]
        df_away_all = df_liga[df_liga["AwayTeam"] == away_team]

        lambda_home, lambda_away = calcular_lambdas_mercado(df_liga, home_team, away_team, "FTHG", "FTAG", floor=0.4)
        lambda_home_cantos, lambda_away_cantos = calcular_lambdas_mercado(df_liga, home_team, away_team, "HC", "AC", floor=1.5)
        lambda_home_cartoes, lambda_away_cartoes = calcular_lambdas_mercado(df_liga, home_team, away_team, "HY", "AY", floor=0.5)

        lambda_total_cantos = lambda_home_cantos + lambda_away_cantos
        prob_cantos_over_75 = 1 - poisson.cdf(7, lambda_total_cantos)

        lambda_total_cartoes = lambda_home_cartoes + lambda_away_cartoes
        prob_cartoes_over_45 = 1 - poisson.cdf(4, lambda_total_cartoes)

        cs_home_prob = (df_home_all["FTAG"] == 0).mean() if not df_home_all.empty else 0.30
        cs_away_prob = (df_away_all["FTHG"] == 0).mean() if not df_away_all.empty else 0.20

        lambda_1p = (lambda_home + lambda_away) * 0.45
        prob_over_05_1p = 1 - poisson.pmf(0, lambda_1p)

        max_goals = 6
        matriz_prob = np.outer(
            poisson.pmf(np.arange(max_goals + 1), lambda_home),
            poisson.pmf(np.arange(max_goals + 1), lambda_away),
        )
        for gh in range(2):
            for ga in range(2):
                matriz_prob[gh, ga] *= rho_correction(gh, ga, lambda_home, lambda_away, RHO_DIXON_COLES)
        matriz_prob = matriz_prob / matriz_prob.sum()

        prob_over_15 = 1 - np.sum(matriz_prob[0, 0]) - np.sum(matriz_prob[0, 1]) - np.sum(matriz_prob[1, 0])
        prob_over_25 = 1 - np.sum(matriz_prob[0:2, 0:2])
        prob_btts = 1 - (np.sum(matriz_prob[0, :]) + np.sum(matriz_prob[:, 0]) - matriz_prob[0, 0])

        st.markdown("---")
        st.subheader("📊 Indicadores Avançados & Fator Casa/Fora")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Esperança Golos (Casa)", f"{lambda_home:.2f}")
        m2.metric("Esperança Golos (Fora)", f"{lambda_away:.2f}")
        m3.metric("Prob. Over 2.5", f"{prob_over_25*100:.1f}%")
        m4.metric("Prob. Ambas Marcam", f"{prob_btts*100:.1f}%")

        m5, m6, m7, m8 = st.columns(4)
        m5.metric("Jogo Sem Sofrer Golos (Casa)", f"{cs_home_prob*100:.1f}%")
        m6.metric("Jogo Sem Sofrer Golos (Fora)", f"{cs_away_prob*100:.1f}%")
        m7.metric("Cantos Esperados (Casa/Fora)", f"{lambda_home_cantos:.1f} / {lambda_away_cantos:.1f}")
        m8.metric("Cartões Esperados (Casa/Fora)", f"{lambda_home_cartoes:.1f} / {lambda_away_cartoes:.1f}")

        st.markdown("---")
        st.subheader("💡 Tabela Consolidada de Mercados")

        mercados_analise = [
            {"Mercado": "Over 1.5 Golos", "Prob_Calc": prob_over_15, "Odd_Manual": odd_over_15, "Grupo": "golos"},
            {"Mercado": "Under 1.5 Golos", "Prob_Calc": 1 - prob_over_15, "Odd_Manual": odd_under_15, "Grupo": "golos"},
            {"Mercado": "Over 2.5 Golos", "Prob_Calc": prob_over_25, "Odd_Manual": odd_over_25, "Grupo": "golos"},
            {"Mercado": "Under 2.5 Golos", "Prob_Calc": 1 - prob_over_25, "Odd_Manual": odd_under_25, "Grupo": "golos"},
            {"Mercado": "Ambas Marcam (BTTS)", "Prob_Calc": prob_btts, "Odd_Manual": odd_btts, "Grupo": "golos"},
            {"Mercado": "Cantos Over 7.5", "Prob_Calc": prob_cantos_over_75, "Odd_Manual": odd_cantos_over_75, "Grupo": "cantos"},
            {"Mercado": "Cartões Over 4.5", "Prob_Calc": prob_cartoes_over_45, "Odd_Manual": odd_cartoes_over_45, "Grupo": "cartoes"},
            {"Mercado": "Over 0.5 1ª Parte", "Prob_Calc": prob_over_05_1p, "Odd_Manual": odd_over_05_1p, "Grupo": "golos_1p"},
        ]

        dados_tabela = []
        mercados_com_valor = []

        for item in mercados_analise:
            prob = item["Prob_Calc"]
            odd = item["Odd_Manual"]
            fair_odd = 1 / prob if prob > 0 else 99.0
            edge = (prob * odd) - 1
            kelly_fraction = (prob * odd - 1) / (odd - 1) if odd > 1 else 0

            if odd < min_odd_permitida:
                status = "🛡️ Bloqueado (Odd Abaixo do Mínimo)"
                stake_recomendada = 0.0
            elif edge > edge_minimo and kelly_fraction > 0:
                stake_kelly = banca_inicial * kelly_fraction * fracao_kelly
                teto_stake = banca_inicial * (stake_pct_max / 100)
                stake_recomendada = min(stake_kelly, teto_stake)
                status = "🔥 Valor Encontrado"
                mercados_com_valor.append({
                    "Mercado": item["Mercado"], "Grupo": item["Grupo"],
                    "prob": prob, "odd": odd, "edge": edge, "stake": stake_recomendada,
                })
            else:
                stake_recomendada = 0.0
                status = "⚖️ Neutro / Evitar"

            ganho_potencial = stake_recomendada * odd

            dados_tabela.append({
                "Mercado": item["Mercado"],
                "Probabilidade": f"{prob*100:.1f}%",
                "Odd Inserida": f"{odd:.2f}",
                "Odd Justa": f"{fair_odd:.2f}",
                "Edge (%)": f"{edge*100:+.1f}%",
                "Stake Recomendada (€)": f"€{stake_recomendada:.2f}",
                "Ganho Potencial (€)": f"€{ganho_potencial:.2f}",
                "Avaliação": status,
            })

        melhores_por_grupo = {}
        for m in mercados_com_valor:
            grupo = m["Grupo"]
            if grupo not in melhores_por_grupo or m["edge"] > melhores_por_grupo[grupo]["edge"]:
                melhores_por_grupo[grupo] = m
        mercados_para_multipla = list(melhores_por_grupo.values())

        if len(mercados_para_multipla) > 0:
            prob_multipla = 1.0
            odd_multipla = 1.0
            for m in mercados_para_multipla:
                prob_multipla *= m["prob"]
                odd_multipla *= m["odd"]

            fair_odd_multipla = 1 / prob_multipla if prob_multipla > 0 else 99.0
            edge_multipla = (prob_multipla * odd_multipla) - 1
            kelly_multipla = (prob_multipla * odd_multipla - 1) / (odd_multipla - 1) if odd_multipla > 1 else 0

            if edge_multipla > edge_minimo and kelly_multipla > 0:
                stake_rec_mult = min(
                    banca_inicial * kelly_multipla * fracao_kelly * 0.5,
                    banca_inicial * (stake_pct_max / 100),
                )
                status_mult = f"🚀 Múltipla de Valor ({len(mercados_para_multipla)} seleções, 1 por grupo correlacionado)"
            else:
                stake_rec_mult = 0.0
                status_mult = f"⚖️ Múltipla Neutra ({len(mercados_para_multipla)} seleções)"

            ganho_rec_mult = stake_rec_mult * odd_multipla
            nomes_mercados_str = ", ".join([m["Mercado"] for m in mercados_para_multipla])
            nome_linha_multipla = f"🔗 Múltipla Automática ({nomes_mercados_str})"
        else:
            prob_multipla = odd_multipla = fair_odd_multipla = edge_multipla = 0.0
            stake_rec_mult = ganho_rec_mult = 0.0
            status_mult = "⚠️ Nenhuma seleção em verde no momento"
            nome_linha_multipla = "🔗 Múltipla Automática do Jogo (Sem Seleções de Valor)"

        dados_tabela.append({
            "Mercado": nome_linha_multipla,
            "Probabilidade": f"{prob_multipla*100:.1f}%" if mercados_para_multipla else "-",
            "Odd Inserida": f"{odd_multipla:.2f}" if mercados_para_multipla else "-",
            "Odd Justa": f"{fair_odd_multipla:.2f}" if mercados_para_multipla else "-",
            "Edge (%)": f"{edge_multipla*100:+.1f}%" if mercados_para_multipla else "-",
            "Stake Recomendada (€)": f"€{stake_rec_mult:.2f}",
            "Ganho Potencial (€)": f"€{ganho_rec_mult:.2f}",
            "Avaliação": status_mult,
        })

        df_resumo = pd.DataFrame(dados_tabela)

        def destacar_valor(row):
            if "🔥 Valor Encontrado" in str(row["Avaliação"]) or "🚀 Múltipla de Valor" in str(row["Avaliação"]):
                return ["background-color: rgba(46, 125, 50, 0.35); color: #ffffff"] * len(row)
            return [""] * len(row)

        df_estilizado = df_resumo.style.apply(destacar_valor, axis=1)
        st.dataframe(df_estilizado, use_container_width=True)

        n_jogos_casa = len(df_home_all)
        n_jogos_fora = len(df_away_all)
        if n_jogos_casa < JOGOS_MIN_PARA_CONFIANCA_TOTAL or n_jogos_fora < JOGOS_MIN_PARA_CONFIANCA_TOTAL:
            st.caption(
                f"ℹ️ Amostra pequena ({home_team}: {n_jogos_casa} jogos em casa · "
                f"{away_team}: {n_jogos_fora} jogos fora) — as médias foram ajustadas "
                f"em direção à média da liga (shrinkage) para compensar."
            )

        st.markdown("---")
        if st.button("💾 Registar sugestões de valor deste jogo no histórico"):
            registos = 0
            for m in mercados_com_valor:
                registar_aposta(selected_league, home_team, away_team, m["Mercado"], m["prob"], m["odd"], m["edge"], m["stake"], casa_aposta=casa_de_apostas)
                registos += 1
            if mercados_para_multipla and status_mult.startswith("🚀"):
                registar_aposta(selected_league, home_team, away_team, nome_linha_multipla, prob_multipla, odd_multipla, edge_multipla, stake_rec_mult, casa_aposta=casa_de_apostas)
                registos += 1
            if registos > 0:
                st.success(f"{registos} sugestão(ões) registada(s). Vai à aba 'Histórico & Desempenho' para marcar o resultado quando o jogo acabar.")
            else:
                st.info("Não há sugestões de valor para registar neste jogo, com os filtros atuais.")

with tab_historico:
    st.subheader("📈 Histórico & Desempenho Real do Modelo")
    st.caption(
        "Esta aba mede se o modelo tem edge de verdade a longo prazo — taxa de acerto "
        "e ROI, não apenas 'sensação' de sucesso. Marca o resultado de cada sugestão "
        "assim que o jogo terminar."
    )

    df_hist = obter_apostas()

    if df_hist.empty:
        st.info("Ainda não há sugestões registadas. Vai à aba 'Análise do Jogo' e regista as apostas de valor que encontrares.")
    else:
        pendentes = df_hist[df_hist["resultado"] == "Pendente"]
        resolvidas = df_hist[df_hist["resultado"] != "Pendente"]

        st.markdown("#### ⏳ Apostas Pendentes")
        if not pendentes.empty:
            for _, row in pendentes.iterrows():
                casa_label = f" · {row['casa_aposta']}" if row.get("casa_aposta") else ""
                with st.expander(f"{row['equipa_casa']} vs {row['equipa_fora']} — {row['mercado']} (odd {row['odd']:.2f}, stake €{row['stake']:.2f}){casa_label}"):
                    st.write(f"Registado em: {row['data_registo']} · Probabilidade estimada: {row['probabilidade']*100:.1f}% · Edge: {row['edge']*100:+.1f}%")

                    st.markdown("**Resultado do jogo**")
                    col_a, col_b, col_c = st.columns(3)
                    if col_a.button("✅ Ganhou", key=f"ganhou_{row['id']}"):
                        atualizar_resultado(row["id"], "Ganhou")
                        st.rerun()
                    if col_b.button("❌ Perdeu", key=f"perdeu_{row['id']}"):
                        atualizar_resultado(row["id"], "Perdeu")
                        st.rerun()
                    if col_c.button("➖ Anulada", key=f"anulada_{row['id']}"):
                        atualizar_resultado(row["id"], "Anulada")
                        st.rerun()

                    st.markdown("**Odd de fecho (CLV)** — regista pouco antes do jogo começar")
                    col_d, col_e = st.columns([2, 1])
                    odd_fecho_atual = row["odd_fecho"] if pd.notna(row.get("odd_fecho")) else float(row["odd"])
                    nova_odd_fecho = col_d.number_input(
                        "Odd de fecho observada", min_value=1.01, value=float(odd_fecho_atual),
                        step=0.01, key=f"oddfecho_{row['id']}", label_visibility="collapsed",
                    )
                    if col_e.button("Guardar", key=f"guardaroddfecho_{row['id']}"):
                        atualizar_odd_fecho(row["id"], nova_odd_fecho)
                        st.rerun()
                    if pd.notna(row.get("odd_fecho")):
                        clv_pct = (row["odd"] / row["odd_fecho"] - 1) * 100
                        st.caption(f"CLV atual: {clv_pct:+.1f}% ({'bateste o fecho ✅' if clv_pct > 0 else 'ficaste abaixo do fecho'})")
        else:
            st.caption("Sem apostas pendentes de momento.")

        st.markdown("---")
        st.markdown("#### 📊 Desempenho Real (apostas já resolvidas)")

        if not resolvidas.empty:
            apostas_validas = resolvidas[resolvidas["resultado"] != "Anulada"]
            n_total = len(apostas_validas)
            n_ganhas = int((apostas_validas["resultado"] == "Ganhou").sum())
            taxa_acerto = (n_ganhas / n_total) if n_total > 0 else 0
            stake_total = apostas_validas["stake"].sum()
            lucro_total = resolvidas["lucro"].sum()
            roi = (lucro_total / stake_total) if stake_total > 0 else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Apostas Resolvidas", n_total)
            c2.metric("Taxa de Acerto Real", f"{taxa_acerto*100:.1f}%")
            c3.metric("Lucro / Prejuízo Total", f"€{lucro_total:.2f}")
            c4.metric("ROI", f"{roi*100:.1f}%")

            com_odd_fecho = df_hist[df_hist["odd_fecho"].notna()].copy()
            if not com_odd_fecho.empty:
                com_odd_fecho["clv_pct"] = (com_odd_fecho["odd"] / com_odd_fecho["odd_fecho"] - 1) * 100
                clv_medio = com_odd_fecho["clv_pct"].mean()
                pct_bateu_fecho = (com_odd_fecho["clv_pct"] > 0).mean() * 100
                c5, c6 = st.columns(2)
                c5.metric("CLV Médio", f"{clv_medio:+.1f}%", help="Diferença média entre a odd a que apostaste e a odd de fecho do mercado. Positivo = bates o mercado.")
                c6.metric("% Apostas que Bateram o Fecho", f"{pct_bateu_fecho:.0f}%")
                st.caption(
                    f"Baseado em {len(com_odd_fecho)} aposta(s) com odd de fecho registada. "
                    "O CLV é o indicador mais fiável de edge real a longo prazo — mais do que "
                    "o resultado de qualquer aposta isolada."
                )
            else:
                st.caption("ℹ️ Ainda não registaste nenhuma odd de fecho — vê a secção 'Apostas Pendentes' para começares a captar o CLV.")

            hist_ordenado = resolvidas.sort_values("data_registo").copy()
            hist_ordenado["saldo_acumulado"] = hist_ordenado["lucro"].cumsum()
            st.line_chart(hist_ordenado.set_index("data_registo")["saldo_acumulado"])

            st.caption(
                "💡 Nota: isto mede taxa de acerto e ROI reais, que já dizem muito mais do que "
                "uma 'sensação' de sucesso de curto prazo. A métrica ainda mais rigorosa usada "
                "por profissionais — Closing Line Value (comparar a tua odd com a odd de fecho "
                "do mercado) — exigiria uma API de odds ao vivo, o que fica como possível "
                "evolução futura."
            )
        else:
            st.caption("Ainda não há apostas com resultado registado.")

        st.markdown("---")
        with st.expander("🗂️ Ver todas as apostas registadas"):
            st.dataframe(df_hist, use_container_width=True)
