import base64
from io import BytesIO
import json
import urllib.request
import numpy as np
import pandas as pd
from PIL import Image
from scipy.stats import poisson
import streamlit as st

# 1. Configuração da Página e Estilo Visual
st.set_page_config(
    page_title="Análise Desportiva 26/27",
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
        </style>
        """,
        unsafe_allow_html=True,
    )


aplicar_estilo_visual()

st.title("⚽ Análise Desportiva 26/27 (Leitura Automática por IA)")
st.markdown(
    "Análise Avançada com Foco em **Golos, BTTS, Cantos & Critério de Kelly**"
)

# 2. Mapeamento Completo de Ligas e Equipas Oficiais
LEAGUES_CONFIG = {
    "PT Liga Portugal": {
        "teams": [
            "Académico Casa Pia AC",
            "CD Nacional",
            "Estoril Praia",
            "Estrela Amadora",
            "FC Alverca",
            "FC Arouca",
            "FC Famalicão",
            "FC Porto",
            "Gil Vicente FC",
            "Marítimo M.",
            "Moreirense FC",
            "Rio Ave FC",
            "Santa Clara",
            "SC Braga",
            "SL Benfica",
            "Sporting CP",
            "Vitória SC",
        ],
        "csv_url": "https://www.football-data.co.uk/mmh2627/P1.csv",
    },
    "EN Premier League (Inglaterra)": {
        "teams": [
            "Arsenal",
            "Aston Villa",
            "Bournemouth",
            "Brentford",
            "Brighton",
            "Chelsea",
            "Coventry City",
            "Crystal Palace",
            "Everton",
            "Fulham",
            "Hull City",
            "Ipswich Town",
            "Leeds United",
            "Liverpool",
            "Manchester City",
            "Manchester United",
            "Newcastle",
            "Nottingham Forest",
            "Sunderland",
            "Tottenham",
        ],
        "csv_url": "https://www.football-data.co.uk/mmh2627/E0.csv",
    },
    "ES La Liga (Espanha)": {
        "teams": [
            "Athletic Bilbao",
            "Atlético de Madrid",
            "Osasuna",
            "Elche",
            "Alavés",
            "Espanyol",
            "Barcelona",
            "Getafe",
            "Levante",
            "Málaga",
            "Racing Santander",
            "Rayo Vallecano",
            "Celta de Vigo",
            "Deportivo La Coruña",
            "Real Betis",
            "Real Madrid",
            "Real Sociedad",
            "Sevilla",
            "Valencia",
            "Villarreal",
        ],
        "csv_url": "https://www.football-data.co.uk/mmh2627/SP1.csv",
    },
    "DE Bundesliga (Alemanha)": {
        "teams": [
            "Bayern Munich",
            "Borussia Dortmund",
            "RB Leipzig",
            "VfB Stuttgart",
            "Hoffenheim",
            "Bayer Leverkusen",
            "Freiburg",
            "Eintracht Frankfurt",
            "Augsburg",
            "Mainz",
            "Union Berlin",
            "Borussia Mönchengladbach",
            "Hamburg",
            "Cologne",
            "Werder Bremen",
            "Schalke",
            "Elversberg",
            "Paderborn",
        ],
        "csv_url": "https://www.football-data.co.uk/mmh2627/D1.csv",
    },
    "IT Serie A (Itália)": {
        "teams": [
            "Atalanta",
            "Bologna",
            "Cagliari",
            "Como",
            "Fiorentina",
            "Frosinone",
            "Genoa",
            "Inter de Milão",
            "Juventus",
            "Lazio",
            "Lecce",
            "Milan",
            "Monza",
            "Napoli",
            "Parma",
            "Roma",
            "Sassuolo",
            "Torino",
            "Udinese",
            "Venezia",
        ],
        "csv_url": "https://www.football-data.co.uk/mmh2627/I1.csv",
    },
    "FR Ligue 1 (França)": {
        "teams": [
            "Angers SCO",
            "AJ Auxerre",
            "Stade Brestois 29",
            "Le Havre AC",
            "Le Mans FC",
            "RC Lens",
            "LOSC Lille",
            "FC Lorient",
            "Olympique Lyonnais",
            "Olympique de Marseille",
            "AS Monaco",
            "OGC Nice",
            "Paris FC",
            "Paris Saint-Germain",
            "Stade Rennais",
            "RC Strasbourg Alsace",
            "Toulouse FC",
            "ESTAC Troyes",
        ],
        "csv_url": "https://www.football-data.co.uk/mmh2627/F1.csv",
    },
    "BR Brasileirão (Brasil)": {
        "teams": [
            "Flamengo",
            "Palmeiras",
            "Athletico PR",
            "Bahia",
            "Fluminense",
            "Cruzeiro",
            "Atlético MG",
            "Coritiba",
            "Bragantino",
            "Santos",
            "Botafogo",
            "São Paulo",
            "Vitória",
            "Corinthians",
            "Mirassol",
            "Grêmio",
            "Vasco",
            "Internacional",
            "Remo",
            "Chapecoense",
        ],
        "csv_url": "",
    },
    "BR Brasil Série B": {
        "teams": [
            "Ponte Preta",
            "Londrina",
            "São Bernardo",
            "Náutico",
            "Criciúma",
            "Goiás",
            "Novorizontino",
            "CRB",
            "Avaí",
            "Atlético-GO",
            "Cuiabá",
            "América-MG",
            "Vila Nova",
            "Operário-PR",
            "Athletic",
            "Botafogo-SP",
            "Sport",
            "Juventude",
            "Ceará",
            "Fortaleza",
        ],
        "csv_url": "",
    },
    "AR Liga Argentina": {
        "teams": [
            "AA Estudiantes",
            "Aldosivi",
            "Argentinos Juniors",
            "Atlético Tucumán",
            "Banfield",
            "Barracas Central",
            "Belgrano Córdoba",
            "Boca Juniors",
            "Central Córdoba",
            "Defensa y Justicia",
            "Deportivo Riestra",
            "Estudiantes",
            "Gimnasia La Plata",
            "Gimnasia Mendoza",
            "Huracán",
            "Independiente",
            "Independiente Rivadavia",
            "Instituto Córdoba",
            "Lanús",
            "Newell´s Old Boys",
            "Platense",
            "Racing Club",
            "River Plate",
            "Rosario Central",
            "San Lorenzo",
            "Sarmiento de Junín",
            "Talleres Córdoba",
            "Tigre",
            "Unión de Santa Fe",
            "Vélez Sarsfield",
        ],
        "csv_url": "",
    },
    "UEFA Liga dos Campeões": {
        "teams": [
            "Bayern de Munique",
            "Borussia Dortmund",
            "RB Leipzig",
            "Stuttgart",
            "Club Brugge",
            "Barcelona",
            "Real Madrid",
            "Villarreal",
            "Atlético de Madrid",
            "Betis",
            "PSG",
            "Lens",
            "Lille",
            "Arsenal",
            "Manchester City",
            "Manchester United",
            "Aston Villa",
            "Liverpool",
            "Inter de Milão",
            "Napoli",
            "Roma",
            "Como",
            "PSV",
            "Feyernoord",
            "Porto",
            "Sporting",
            "Slavia Praga",
            "Galatasaray",
            "Shakhtar Donetsk",
        ],
        "csv_url": "",
    },
    "UEFA Liga Europa": {
        "teams": [
            "Anderlecht",
            "Ararat-Armenia",
            "AZ Alkmaar",
            "Benfica",
            "Beşiktaş",
            "Bournemouth",
            "Celje",
            "Celta",
            "Celtic",
            "Crystal Palace",
            "Ferencváros",
            "GNK Dinamo",
            "H. Beer-Sheva",
            "Hoffenheim",
            "Jagiellonia",
            "Juventus",
            "Lech Poznań",
            "Leverkusen",
            "Levski Sofia",
            "Lillestrøm",
            "Lyon",
            "Marseille",
            "Milan",
            "N.E.C.",
            "OFI Crete",
            "Olympiacos",
            "Omonia",
            "Real Sociedad",
            "Rennes",
            "Salzburg",
            "Sparta Praha",
            "Sturm Graz",
            "Sunderland",
            "Torreense",
            "Union SG",
            "Viktoria Plzeň",
        ],
        "csv_url": "",
    },
}


@st.cache_data(ttl=3600)
def carregar_dados_reais(liga_nome, team_list):
    config = LEAGUES_CONFIG.get(liga_nome, {})
    csv_url = config.get("csv_url", "")
    df = None
    if csv_url:
        try:
            df_raw = pd.read_csv(csv_url)
            if {"HomeTeam", "AwayTeam", "FTHG", "FTAG"}.issubset(
                df_raw.columns
            ):
                df = df_raw.dropna(
                    subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"]
                ).copy()
                if "HC" not in df.columns:
                    df["HC"] = 5
                if "AC" not in df.columns:
                    df["AC"] = 4
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
                    })
        df = pd.DataFrame(records)
    return df


selected_league = st.sidebar.selectbox(
    "Selecione a Liga / Competição:", list(LEAGUES_CONFIG.keys())
)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Gestão de Banca & Critério de Kelly")
banca_inicial = st.sidebar.number_input(
    "Valor da Banca (€)", min_value=1.0, value=100.0, step=10.0
)
stake_pct_max = st.sidebar.slider(
    "Stake Máxima Base (%)", min_value=0.5, max_value=10.0, value=3.0, step=0.5
)

# Secção na barra lateral para carregar prints e extrair com IA
st.sidebar.markdown("---")
st.sidebar.subheader("📸 Leitura Automática de Prints (IA)")

gemini_api_key = st.sidebar.text_input(
    "Chave API do Gemini", type="password", value=""
)

uploaded_prints = st.sidebar.file_uploader(
    "Carregar Prints das Odds (PNG/JPG)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
)

odds_extraidas = {}

if uploaded_prints:
    if not gemini_api_key:
        st.sidebar.warning(
            "⚠️ Por favor, insere a tua chave API do Gemini para ativar a leitura automática dos prints."
        )
    else:
        st.sidebar.info("🤖 A analisar os prints com Inteligência Artificial...")
        try:
            for print_file in uploaded_prints:
                imagem = Image.open(print_file)
                st.sidebar.image(
                    imagem,
                    caption=f"Print: {print_file.name}",
                    use_container_width=True,
                )

                # Tratamento de Transparência RGBA para JPEG
                if imagem.mode in ("RGBA", "LA"):
                    fundo = Image.new("RGB", imagem.size, (255, 255, 255))
                    fundo.paste(imagem, mask=imagem.split()[3])
                    imagem = fundo
                elif imagem.mode != "RGB":
                    imagem = imagem.convert("RGB")

                buffered = BytesIO()
                imagem.save(buffered, format="JPEG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode(
                    "utf-8"
                )

                prompt_extracao = """
                Analisa esta imagem de uma casa de apostas desportivas. 
                Identifica e extrai os valores numéricos das odds para os seguintes mercados (se presentes):
                - Over 1.5 golos
                - Over 2.5 golos
                - Under 2.5 golos
                - BTTS / Ambas Marcam (Sim)
                - Cantos Over 8.5 / 9.5 (ou o valor de cantos visível)
                Devolve o resultado estritamente em formato JSON com chaves em minúsculas e valores numéricos em float (ex: {"over_15": 1.30, "over_25": 1.85, "btts_sim": 1.75, "cantos_over": 1.90}). Se algum mercado não estiver visível, omite-o.
                """

                # Utilizando gemini-2.5-flash atualizado
                url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt_extracao},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": img_base64,
                                }
                            },
                        ]
                    }]
                }

                req = urllib.request.Request(
                    url_api,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )

                with urllib.request.urlopen(req) as response:
                    resposta_json = json.loads(
                        response.read().decode("utf-8")
                    )
                    texto_resposta = (
                        resposta_json.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "{}")
                    )

                    texto_limpo = (
                        texto_resposta.replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )
                    dados_lidos = json.loads(texto_limpo)
                    odds_extraidas.update(dados_lidos)

            st.sidebar.success("✅ Odds extraídas com sucesso via IA!")
            st.sidebar.json(odds_extraidas)

        except Exception as e:
            st.sidebar.error(f"❌ Erro ao processar com a IA: {e}")

# 3. Corpo Principal - Análise de Jogos
teams_available = LEAGUES_CONFIG[selected_league]["teams"]
df_liga = carregar_dados_reais(selected_league, teams_available)

col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox(
        "Equipa da Casa",
        teams_available,
        index=0 if len(teams_available) > 0 else 0,
    )
with col2:
    away_team = st.selectbox(
        "Equipa Visitante",
        teams_available,
        index=1 if len(teams_available) > 1 else 0,
    )

if home_team == away_team:
    st.warning("⚠️ Seleciona duas equipas diferentes para realizar a análise.")
else:
    # Cálculo de Médias Históricas (Golos)
    media_h_gs = df_liga[df_liga["HomeTeam"] == home_team]["FTHG"].mean()
    media_h_gc = df_liga[df_liga["HomeTeam"] == home_team]["FTAG"].mean()
    media_a_gs = df_liga[df_liga["AwayTeam"] == away_team]["FTAG"].mean()
    media_a_gc = df_liga[df_liga["AwayTeam"] == away_team]["FTHG"].mean()

    media_gols_geral_h = df_liga["FTHG"].mean()
    media_gols_geral_a = df_liga["FTAG"].mean()

    lambda_home = max(
        0.5, (media_h_gs / media_gols_geral_h) * (media_a_gc / media_gols_geral_a) * media_gols_geral_h
    )
    lambda_away = max(
        0.5, (media_a_gs / media_gols_geral_a) * (media_h_gc / media_gols_geral_h) * media_gols_geral_a
    )

    # Cálculo de Médias Históricas (Cantos)
    media_hc_pro = df_liga[df_liga["HomeTeam"] == home_team]["HC"].mean()
    media_ac_contra = df_liga[df_liga["AwayTeam"] == away_team]["AC"].mean()
    media_ac_pro = df_liga[df_liga["AwayTeam"] == away_team]["AC"].mean()
    media_hc_contra = df_liga[df_liga["HomeTeam"] == home_team]["HC"].mean()

    lambda_cantos_home = max(3.0, (media_hc_pro + media_ac_contra) / 2)
    lambda_cantos_away = max(2.5, (media_ac_pro + media_hc_contra) / 2)
    lambda_total_cantos = lambda_cantos_home + lambda_cantos_away

    # Probabilidade Poisson para Cantos (Over 8.5 Cantos)
    prob_cantos_over_85 = 1 - poisson.cdf(8, lambda_total_cantos)

    # Simulação Poisson de Placares (Golos)
    max_goals = 6
    matriz_prob = np.outer(
        poisson.pmf(np.arange(max_goals + 1), lambda_home),
        poisson.pmf(np.arange(max_goals + 1), lambda_away),
    )

    prob_over_15 = 1 - np.sum(matriz_prob[0, 0]) - np.sum(matriz_prob[0, 1]) - np.sum(matriz_prob[1, 0])
    prob_over_25 = 1 - np.sum(matriz_prob[0:2, 0:2])
    prob_btts = 1 - (np.sum(matriz_prob[0, :]) + np.sum(matriz_prob[:, 0]) - matriz_prob[0, 0])

    st.markdown("---")
    st.subheader("📊 Previsões Estatísticas (Modelo de Poisson)")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Esperança Golos (Casa)", f"{lambda_home:.2f}")
    m2.metric("Esperança Golos (Fora)", f"{lambda_away:.2f}")
    m3.metric("Prob. Over 2.5", f"{prob_over_25*100:.1f}%")
    m4.metric("Prob. Ambas Marcam (BTTS)", f"{prob_btts*100:.1f}%")

    m5, m6 = st.columns(2)
    m5.metric("Esperança Total de Cantos", f"{lambda_total_cantos:.2f}")
    m6.metric("Prob. Over 8.5 Cantos", f"{prob_cantos_over_85*100:.1f}%")

    st.markdown("---")
    st.subheader("💡 Sugestões de Valor & Critério de Kelly")

    # Tabela Unificada de Mercados (Golos + Cantos)
    mercados_analise = [
        {"Mercado": "Over 1.5 Golos", "Prob_Calc": prob_over_15, "Odd_Extraida": odds_extraidas.get("over_15", 1.35)},
        {"Mercado": "Over 2.5 Golos", "Prob_Calc": prob_over_25, "Odd_Extraida": odds_extraidas.get("over_25", 1.95)},
        {"Mercado": "Ambas Marcam (BTTS)", "Prob_Calc": prob_btts, "Odd_Extraida": odds_extraidas.get("btts_sim", 1.80)},
        {"Mercado": "Cantos Over 8.5", "Prob_Calc": prob_cantos_over_85, "Odd_Extraida": odds_extraidas.get("cantos_over", 1.85)},
    ]

    dados_tabela = []
    for item in mercados_analise:
        prob = item["Prob_Calc"]
        odd = item["Odd_Extraida"]
        fair_odd = 1 / prob if prob > 0 else 99.0
        edge = (prob * odd) - 1  # Vantagem matemática

        # Critério de Kelly Fracionado (¼ de Kelly)
        kelly_fraction = (prob * odd - 1) / (odd - 1) if odd > 1 else 0
        stake_recomendada = max(0.0, banca_inicial * (kelly_fraction / 4))
        stake_recomendada = min(stake_recomendada, banca_inicial * (stake_pct_max / 100))

        status = "🔥 Valor Encontrado" if edge > 0.05 else "⚖️ Neutro / Evitar"

        dados_tabela.append({
            "Mercado": item["Mercado"],
            "Probabilidade IA/Poisson": f"{prob*100:.1f}%",
            "Odd Disponível": f"{odd:.2f}",
            "Odd Justa": f"{fair_odd:.2f}",
            "Edge (%)": f"{edge*100:+.1f}%",
            "Stake Recomendada (€)": f"€{stake_recomendada:.2f}",
            "Avaliação": status,
        })

    df_resumo = pd.DataFrame(dados_tabela)
    st.dataframe(df_resumo, use_container_width=True)
