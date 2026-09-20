import numpy as np
import pandas as pd
from scipy.stats import poisson
import streamlit as st

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
        </style>
        """,
      unsafe_allow_html=True,
  )


aplicar_estilo_visual()

# Título Principal
st.markdown("### ⚽ Analise 26/27 - Rigor Estatístico & Inteligência Avançada")

# 2. Mapeamento das 10 Ligas Oficiais Definidas
LEAGUES_CONFIG = {
    "Portuguesa": {
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
    "Inglesa": {
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
    "Espanhola": {
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
    "Italiana": {
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
    "Francesa": {
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
    "Brasileira Série A": {
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
    "Brasileira Série B": {
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
    "Argentina": {
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
    "Liga Campeoes": {
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
    "Liga Europa": {
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
      if {"HomeTeam", "AwayTeam", "FTHG", "FTAG"}.issubset(df_raw.columns):
        df = df_raw.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"]).copy()
        for col, default_val in [
            ("HC", 5),
            ("AC", 4),
            ("HY", 2),
            ("AY", 2),
        ]:
          if col not in df.columns:
            df[col] = default_val
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

  n_rows = len(df)
  df["Peso_Temporal"] = np.linspace(0.5, 1.0, n_rows)
  return df


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

st.sidebar.markdown("---")
st.sidebar.subheader("Filtros de Rigor")
min_odd_permitida = st.sidebar.number_input(
    "Odd Mínima de Segurança", min_value=1.01, value=1.30, step=0.05
)

st.sidebar.markdown("---")
st.sidebar.subheader("✏️ Inserção Manual de Odds")
odd_over_15 = st.sidebar.number_input(
    "Odd Over 1.5 Golos", min_value=1.01, value=1.65, step=0.01
)
odd_over_25 = st.sidebar.number_input(
    "Odd Over 2.5 Golos", min_value=1.01, value=1.95, step=0.01
)
odd_btts = st.sidebar.number_input(
    "Odd Ambas Marcam (BTTS)", min_value=1.01, value=1.80, step=0.01
)
odd_cantos_over_75 = st.sidebar.number_input(
    "Odd Cantos Over 7.5", min_value=1.01, value=1.55, step=0.01
)
odd_cartoes_over_45 = st.sidebar.number_input(
    "Odd Cartões Over 4.5", min_value=1.01, value=1.90, step=0.01
)
odd_over_05_1p = st.sidebar.number_input(
    "Odd Over 0.5 1ª Parte", min_value=1.01, value=1.40, step=0.01
)

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
  df_home_all = df_liga[df_liga["HomeTeam"] == home_team]
  df_away_all = df_liga[df_liga["AwayTeam"] == away_team]

  media_h_gs = (
      np.average(df_home_all["FTHG"], weights=df_home_all["Peso_Temporal"])
      if not df_home_all.empty
      else 1.5
  )
  media_h_gc = (
      np.average(df_home_all["FTAG"], weights=df_home_all["Peso_Temporal"])
      if not df_home_all.empty
      else 1.0
  )
  media_a_gs = (
      np.average(df_away_all["FTAG"], weights=df_away_all["Peso_Temporal"])
      if not df_away_all.empty
      else 1.1
  )
  media_a_gc = (
      np.average(df_away_all["FTHG"], weights=df_away_all["Peso_Temporal"])
      if not df_away_all.empty
      else 1.2
  )

  media_gols_geral_h = df_liga["FTHG"].mean()
  media_gols_geral_a = df_liga["FTAG"].mean()

  lambda_home = max(
      0.4,
      (media_h_gs / media_gols_geral_h)
      * (media_a_gc / media_gols_geral_a)
      * media_gols_geral_h,
  )
  lambda_away = max(
      0.4,
      (media_a_gs / media_gols_geral_a)
      * (media_h_gc / media_gols_geral_h)
      * media_gols_geral_a,
  )

  cs_home_prob = (
      (df_home_all["FTAG"] == 0).mean() if not df_home_all.empty else 0.30
  )
  cs_away_prob = (
      (df_away_all["FTHG"] == 0).mean() if not df_away_all.empty else 0.20
  )

  media_hc_pro = (
      np.average(df_home_all["HC"], weights=df_home_all["Peso_Temporal"])
      if not df_home_all.empty
      else 5.0
  )
  media_ac_contra = (
      np.average(df_away_all["AC"], weights=df_home_all["Peso_Temporal"])
      if not df_home_all.empty
      else 4.0
  )
  lambda_total_cantos = max(3.0, media_hc_pro) + max(2.5, media_ac_contra)
  prob_cantos_over_75 = 1 - poisson.cdf(7, lambda_total_cantos)

  media_hy = (
      np.average(df_home_all["HY"], weights=df_home_all["Peso_Temporal"])
      if not df_home_all.empty
      else 2.0
  )
  media_ay = (
      np.average(df_away_all["AY"], weights=df_home_all["Peso_Temporal"])
      if not df_away_all.empty
      else 2.1
  )
  lambda_total_cartoes = media_hy + media_ay + 0.5
  prob_cartoes_over_45 = 1 - poisson.cdf(4, lambda_total_cartoes)

  lambda_1p = (lambda_home + lambda_away) * 0.45
  prob_over_05_1p = 1 - poisson.pmf(0, lambda_1p)

  max_goals = 6
  matriz_prob = np.outer(
      poisson.pmf(np.arange(max_goals + 1), lambda_home),
      poisson.pmf(np.arange(max_goals + 1), lambda_away),
  )
  prob_over_15 = (
      1
      - np.sum(matriz_prob[0, 0])
      - np.sum(matriz_prob[0, 1])
      - np.sum(matriz_prob[1, 0])
  )
  prob_over_25 = 1 - np.sum(matriz_prob[0:2, 0:2])
  prob_btts = 1 - (
      np.sum(matriz_prob[0, :])
      + np.sum(matriz_prob[:, 0])
      - matriz_prob[0, 0]
  )

  st.markdown("---")
  st.subheader("📊 Indicadores Avançados & Fator Casa/Fora")

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Esperança Golos (Casa)", f"{lambda_home:.2f}")
  m2.metric("Esperança Golos (Fora)", f"{lambda_away:.2f}")
  m3.metric("Prob. Over 2.5", f"{prob_over_25*100:.1f}%")
  m4.metric("Prob. Ambas Marcam", f"{prob_btts*100:.1f}%")

  m5, m6, m7 = st.columns(3)
  m5.metric("Jogo Sem Sofrer Golos (Casa)", f"{cs_home_prob*100:.1f}%")
  m6.metric("Jogo Sem Sofrer Golos (Fora)", f"{cs_away_prob*100:.1f}%")
  m7.metric("Cartões Totais (Esp.)", f"{lambda_total_cartoes:.1f}")

  st.markdown("---")
  st.subheader("💡 Tabela Consolidada de Mercados")

  # Dicionário de referência para os mercados e respetivos dados calculados
  dicionario_mercados = {
      "Over 1.5 Golos": {"prob": prob_over_15, "odd": odd_over_15},
      "Over 2.5 Golos": {"prob": prob_over_25, "odd": odd_over_25},
      "Ambas Marcam (BTTS)": {"prob": prob_btts, "odd": odd_btts},
      "Cantos Over 7.5": {
          "prob": prob_cantos_over_75,
          "odd": odd_cantos_over_75,
      },
      "Cartões Over 4.5": {
          "prob": prob_cartoes_over_45,
          "odd": odd_cartoes_over_45,
      },
      "Over 0.5 1ª Parte": {"prob": prob_over_05_1p, "odd": odd_over_05_1p},
  }

  mercados_analise = [
      {"Mercado": "Over 1.5 Golos", "Prob_Calc": prob_over_15, "Odd_Manual": odd_over_15},
      {"Mercado": "Over 2.5 Golos", "Prob_Calc": prob_over_25, "Odd_Manual": odd_over_25},
      {"Mercado": "Ambas Marcam (BTTS)", "Prob_Calc": prob_btts, "Odd_Manual": odd_btts},
      {"Mercado": "Cantos Over 7.5", "Prob_Calc": prob_cantos_over_75, "Odd_Manual": odd_cantos_over_75},
      {"Mercado": "Cartões Over 4.5", "Prob_Calc": prob_cartoes_over_45, "Odd_Manual": odd_cartoes_over_45},
      {"Mercado": "Over 0.5 1ª Parte", "Prob_Calc": prob_over_05_1p, "Odd_Manual": odd_over_05_1p},
  ]

  # Seletor na Barra Lateral para o Utilizador escolher quais os mercados que compõem a Múltipla do Jogo
  st.sidebar.markdown("---")
  st.sidebar.subheader("🔗 Criar Múltipla do Jogo")
  mercados_selecionados_multipla = st.sidebar.multiselect(
      "Selecionar linhas para Combinada:",
      options=list(dicionario_mercados.keys()),
      default=[],
  )

  dados_tabela = []

  for item in mercados_analise:
    prob = item["Prob_Calc"]
    odd = item["Odd_Manual"]
    fair_odd = 1 / prob if prob > 0 else 99.0
    edge = (prob * odd) - 1

    if odd < min_odd_permitida:
      status = "🛡️ Bloqueado (Odd Abaixo do Mínimo)"
      stake_recomendada = 0.0
    else:
      kelly_fraction = (prob * odd - 1) / (odd - 1) if odd > 1 else 0
      if edge > 0.03 and kelly_fraction > 0:
        fator_probabilidade = prob
        stake_base = banca_inicial * (stake_pct_max / 100)
        stake_recomendada = stake_base * fator_probabilidade
        stake_recomendada = min(
            stake_recomendada, banca_inicial * (stake_pct_max / 100)
        )
        status = "🔥 Valor Encontrado"
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

  # Adicionar SEMPRE a Linha da Múltipla Personalizada na Tabela
  if len(mercados_selecionados_multipla) > 0:
    prob_multipla = 1.0
    odd_multipla = 1.0
    for m_nome in mercados_selecionados_multipla:
      prob_multipla *= dicionario_mercados[m_nome]["prob"]
      odd_multipla *= dicionario_mercados[m_nome]["odd"]

    fair_odd_multipla = (
        1 / prob_multipla if prob_multipla > 0 else 99.0
    )
    edge_multipla = (prob_multipla * odd_multipla) - 1
    kelly_multipla = (
        (prob_multipla * odd_multipla - 1) / (odd_multipla - 1)
        if odd_multipla > 1
        else 0
    )

    if edge_multipla > 0.02 and kelly_multipla > 0 and odd_multipla >= min_odd_permitida:
      stake_base_mult = banca_inicial * ((stake_pct_max * 0.5) / 100)
      stake_rec_mult = stake_base_mult * prob_multipla
      status_mult = "🚀 Múltipla de Valor (Personalizada)"
    else:
      stake_rec_mult = 0.0
      status_mult = "⚖️ Múltipla Neutra / Abaixo do Critério"

    ganho_rec_mult = stake_rec_mult * odd_multipla

    nome_linha_multipla = (
        f"🔗 Múltipla Personalizada ({len(mercados_selecionados_multipla)} seleções)"
    )
  else:
    prob_multipla = 0.0
    odd_multipla = 0.0
    fair_odd_multipla = 0.0
    edge_multipla = 0.0
    stake_rec_mult = 0.0
    ganho_rec_mult = 0.0
    status_mult = "⚠️ Nenhuma seleção escolhida na barra lateral"
    nome_linha_multipla = "🔗 Múltipla Personalizada do Jogo (Vazia)"

  dados_tabela.append({
      "Mercado": nome_linha_multipla,
      "Probabilidade": (
          f"{prob_multipla*100:.1f}%"
          if len(mercados_selecionados_multipla) > 0
          else "-"
      ),
      "Odd Inserida": (
          f"{odd_multipla:.2f}"
          if len(mercados_selecionados_multipla) > 0
          else "-"
      ),
      "Odd Justa": (
          f"{fair_odd_multipla:.2f}"
          if len(mercados_selecionados_multipla) > 0
          else "-"
      ),
      "Edge (%)": (
          f"{edge_multipla*100:+.1f}%"
          if len(mercados_selecionados_multipla) > 0
          else "-"
      ),
      "Stake Recomendada (€)": f"€{stake_rec_mult:.2f}",
      "Ganho Potencial (€)": f"€{ganho_rec_mult:.2f}",
      "Avaliação": status_mult,
  })

  df_resumo = pd.DataFrame(dados_tabela)


  def destacar_valor(row):
    if "🔥 Valor Encontrado" in str(row["Avaliação"]) or "🚀 Múltipla de Valor" in str(row["Avaliação"]):
      return ["background-color: rgba(46, 125, 50, 0.35); color: #ffffff"] * len(
          row
      )
    return [""] * len(row)


  df_estilizado = df_resumo.style.apply(destacar_valor, axis=1)

  st.dataframe(df_estilizado, use_container_width=True)
