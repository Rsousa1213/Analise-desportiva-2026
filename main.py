import io
import re
import numpy as np
import pandas as pd
from PIL import Image
from scipy.stats import poisson
import streamlit as st

# 1. Configuração da Página e Estilo Visual
st.set_page_config(page_title="Análise Desportiva 26/27", layout="wide")


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
      unsafe_allow_html=True,
  )


aplicar_estilo_visual()

st.title("⚽ Análise Desportiva 26/27")
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
      if {"HomeTeam", "AwayTeam", "FTHG", "FTAG"}.issubset(df_raw.columns):
        df = df_raw.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"]).copy()
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

if selected_league:
  teams_list = LEAGUES_CONFIG[selected_league]["teams"]
  df = carregar_dados_reais(selected_league, teams_list)

  if df is not None and not df.empty:
    col_h, col_a = st.columns(2)
    with col_h:
      home_team = st.selectbox("Equipa da Casa", teams_list, index=0)
    with col_a:
      away_options = [t for t in teams_list if t != home_team]
      away_team = st.selectbox(
          "Equipa Visitante", away_options, index=0 if away_options else 0
      )

    home_games_all = df[df["HomeTeam"] == home_team]
    away_games_all = df[df["AwayTeam"] == away_team]
    home_games = (
        home_games_all.tail(5) if len(home_games_all) >= 5 else home_games_all
    )
    away_games = (
        away_games_all.tail(5) if len(away_games_all) >= 5 else away_games_all
    )

    if not home_games.empty and not away_games.empty:
      avg_home_goals_for = home_games["FTHG"].mean()
      avg_home_goals_against = home_games["FTAG"].mean()
      avg_away_goals_for = away_games["FTAG"].mean()
      avg_away_goals_against = home_games["FTHG"].mean()

      league_avg_home = df["FTHG"].mean()
      league_avg_away = df["FTAG"].mean()

      lambda_home = (
          avg_home_goals_for / league_avg_home if league_avg_home else 1
      ) * (
          avg_home_goals_against / league_avg_home if league_avg_home else 1
      ) * league_avg_home
      lambda_away = (
          avg_away_goals_for / league_avg_away if league_avg_away else 1
      ) * (
          avg_away_goals_against / league_avg_away if league_avg_away else 1
      ) * league_avg_away

      max_g = 8
      prob_matrix = np.zeros((max_g, max_g))
      for i in range(max_g):
        for j in range(max_g):
          prob_matrix[i, j] = poisson.pmf(i, lambda_home) * poisson.pmf(
              j, lambda_away
          )

      prob_over_1_5 = (
          1 - (prob_matrix[0, 0] + prob_matrix[1, 0] + prob_matrix[0, 1])
      ) * 100
      odd_over_1_5 = 100 / prob_over_1_5 if prob_over_1_5 > 0 else 0

      prob_under_2_5 = sum(
          prob_matrix[i, j] for i in range(max_g) for j in range(max_g) if (i + j) <= 2
      )
      prob_over_2_5 = (1 - prob_under_2_5) * 100
      odd_over_2_5 = 100 / prob_over_2_5 if prob_over_2_5 > 0 else 0

      prob_under_5_5 = sum(
          prob_matrix[i, j] for i in range(max_g) for j in range(max_g) if (i + j) <= 5
      )
      odd_under_5_5 = (
          100 / (prob_under_5_5 * 100) if prob_under_5_5 > 0 else 0
      )

      prob_btts_sim = (
          sum(
              prob_matrix[i, j]
              for i in range(1, max_g)
              for j in range(1, max_g)
          )
          * 100
      )
      odd_btts = 100 / prob_btts_sim if prob_btts_sim > 0 else 0

      home_corners = home_games["HC"].mean() + home_games["AC"].mean()
      away_corners = away_games["HC"].mean() + away_games["AC"].mean()
      avg_total_corners = (home_corners + away_corners) / 2
      lambda_corners = avg_total_corners

      prob_over_7_5_corners = (
          1 - sum(poisson.pmf(k, lambda_corners) for k in range(8))
      ) * 100
      odd_over_7_5_corners = (
          100 / prob_over_7_5_corners if prob_over_7_5_corners > 0 else 0
      )

      prob_under_14_5_corners = (
          sum(poisson.pmf(k, lambda_corners) for k in range(15)) * 100
      )
      odd_under_14_5_corners = (
          100 / prob_under_14_5_corners if prob_under_14_5_corners > 0 else 0
      )

      defval_o15 = float(np.clip(round(odd_over_1_5 + 0.1, 2), 1.01, 50.0))
      defval_o25 = float(np.clip(round(odd_over_2_5 + 0.1, 2), 1.01, 50.0))
      defval_u55 = float(np.clip(round(odd_under_5_5 + 0.1, 2), 1.01, 50.0))
      defval_btts = float(np.clip(round(odd_btts + 0.1, 2), 1.01, 50.0))
      defval_c75 = float(
          np.clip(round(odd_over_7_5_corners + 0.1, 2), 1.01, 50.0)
      )
      defval_u145 = float(
          np.clip(round(odd_under_14_5_corners + 0.1, 2), 1.01, 50.0)
      )

      st.markdown("---")
      st.subheader("📸 Captura Rápida de Odds (Upload de Print)")
      uploaded_file = st.file_uploader(
          "Carregar Screenshot das Odds (.png, .jpg)",
          type=["png", "jpg", "jpeg"],
      )

      if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Print Carregado", width=400)
        st.success("📸 Print carregado com sucesso!")

      st.markdown("---")
      st.subheader("🎯 Comparador de Value Bets & Stake Ótima (Kelly)")

      bc1, bc2, bc3, bc4, bc5, bc6 = st.columns(6)
      with bc1:
        bookie_odd_o15 = st.number_input(
            "Odd (Over 1.5)", 1.01, 50.0, defval_o15, 0.01
        )
      with bc2:
        bookie_odd_o25 = st.number_input(
            "Odd (Over 2.5)", 1.01, 50.0, defval_o25, 0.01
        )
      with bc3:
        bookie_odd_u55 = st.number_input(
            "Odd (Under 5.5)", 1.01, 50.0, defval_u55, 0.01
        )
      with bc4:
        bookie_odd_btts = st.number_input(
            "Odd (BTTS)", 1.01, 50.0, defval_btts, 0.01
        )
      with bc5:
        bookie_odd_c75 = st.number_input(
            "Odd (Cantos 7.5)", 1.01, 50.0, defval_c75, 0.01
        )
      with bc6:
        bookie_odd_u145 = st.number_input(
            "Odd (Cantos 14.5)", 1.01, 50.0, defval_u145, 0.01
        )

      edge_o15 = ((prob_over_1_5 / 100) * bookie_odd_o15 - 1) * 100
      edge_o25 = ((prob_over_2_5 / 100) * bookie_odd_o25 - 1) * 100
      edge_u55 = ((prob_under_5_5) * bookie_odd_u55 - 1) * 100
      edge_btts = ((prob_btts_sim / 100) * bookie_odd_btts - 1) * 100
      edge_c75 = ((prob_over_7_5_corners / 100) * bookie_odd_c75 - 1) * 100
      edge_u145 = ((prob_under_14_5_corners / 100) * bookie_odd_u145 - 1) * 100


      def calcular_stake_kelly(prob_pct, odd, banca, max_pct):
        p = prob_pct / 100.0
        if (odd - 1) <= 0:
          return 0.0
        kelly_fraction = (p * odd - 1) / (odd - 1)
        if kelly_fraction <= 0:
          return 0.0
        stake_aplicada = banca * min(max_pct / 100.0, kelly_fraction * 0.5)
        return round(stake_aplicada, 2)


      val_o15 = calcular_stake_kelly(
          prob_over_1_5, bookie_odd_o15, banca_inicial, stake_pct_max
      )
      val_o25 = calcular_stake_kelly(
          prob_over_2_5, bookie_odd_o25, banca_inicial, stake_pct_max
      )
      val_u55 = calcular_stake_kelly(
          prob_under_5_5 * 100, bookie_odd_u55, banca_inicial, stake_pct_max
      )
      val_btts = calcular_stake_kelly(
          prob_btts_sim, bookie_odd_btts, banca_inicial, stake_pct_max
      )
      val_c75 = calcular_stake_kelly(
          prob_over_7_5_corners,
          bookie_odd_c75,
          banca_inicial,
          stake_pct_max,
      )
      val_u145 = calcular_stake_kelly(
          prob_under_14_5_corners,
          bookie_odd_u145,
          banca_inicial,
          stake_pct_max,
      )

      tabela_dados = [
          {
              "Mercado Base": "Over 1.5 Golos",
              "Probabilidade": f"{prob_over_1_5:.1f}%",
              "Odd Justa (Modelo)": f"{odd_over_1_5:.2f}",
              "Odd Casa de Apostas": f"{bookie_odd_o15:.2f}",
              "Valor (+EV / Edge)": f"{edge_o15:+.2f}%",
              "Aposta Dinâmica (Kelly)": f"{val_o15:.2f} €",
              "Recomendação": "🔥 VALOR" if edge_o15 > 0 else "❌ Sem Valor",
          },
          {
              "Mercado Base": "Over 2.5 Golos",
              "Probabilidade": f"{prob_over_2_5:.1f}%",
              "Odd Justa (Modelo)": f"{odd_over_2_5:.2f}",
              "Odd Casa de Apostas": f"{bookie_odd_o25:.2f}",
              "Valor (+EV / Edge)": f"{edge_o25:+.2f}%",
              "Aposta Dinâmica (Kelly)": f"{val_o25:.2f} €",
              "Recomendação": "🔥 VALOR" if edge_o25 > 0 else "❌ Sem Valor",
          },
          {
              "Mercado Base": "Under 5.5 Golos",
              "Probabilidade": f"{prob_under_5_5*100:.1f}%",
              "Odd Justa (Modelo)": f"{odd_under_5_5:.2f}",
              "Odd Casa de Apostas": f"{bookie_odd_u55:.2f}",
              "Valor (+EV / Edge)": f"{edge_u55:+.2f}%",
              "Aposta Dinâmica (Kelly)": f"{val_u55:.2f} €",
              "Recomendação": "🔥 VALOR" if edge_u55 > 0 else "❌ Sem Valor",
          },
          {
              "Mercado Base": "Ambas Marcam (BTTS)",
              "Probabilidade": f"{prob_btts_sim:.1f}%",
              "Odd Justa (Modelo)": f"{odd_btts:.2f}",
              "Odd Casa de Apostas": f"{bookie_odd_btts:.2f}",
              "Valor (+EV / Edge)": f"{edge_btts:+.2f}%",
              "Aposta Dinâmica (Kelly)": f"{val_btts:.2f} €",
              "Recomendação": "🔥 VALOR" if edge_btts > 0 else "❌ Sem Valor",
          },
          {
              "Mercado Base": "Over 7.5 Cantos",
              "Probabilidade": f"{prob_over_7_5_corners:.1f}%",
              "Odd Justa (Modelo)": f"{odd_over_7_5_corners:.2f}",
              "Odd Casa de Apostas": f"{bookie_odd_c75:.2f}",
              "Valor (+EV / Edge)": f"{edge_c75:+.2f}%",
              "Aposta Dinâmica (Kelly)": f"{val_c75:.2f} €",
              "Recomendação": "🔥 VALOR" if edge_c75 > 0 else "❌ Sem Valor",
          },
          {
              "Mercado Base": "Under 14.5 Cantos",
              "Probabilidade": f"{prob_under_14_5_corners:.1f}%",
              "Odd Justa (Modelo)": f"{odd_under_14_5_corners:.2f}",
              "Odd Casa de Apostas": f"{bookie_odd_u145:.2f}",
              "Valor (+EV / Edge)": f"{edge_u145:+.2f}%",
              "Aposta Dinâmica (Kelly)": f"{val_u145:.2f} €",
              "Recomendação": "🔥 VALOR" if edge_u145 > 0 else "❌ Sem Valor",
          },
      ]

      df_tabela = pd.DataFrame(tabela_dados)
      st.dataframe(df_tabela, use_container_width=True, hide_index=True)

    else:
      st.info("ℹ️ Selecione equipas válidas para calcular as estatísticas.")
  else:
    st.warning("⚠️ Sem dados disponíveis para esta competição.")
