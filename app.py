import streamlit as st
import pandas as pd
import numpy as np
import requests
from scipy.stats import poisson

st.set_page_config(
    page_title="Análise Desportiva 26/27", 
    layout="wide"
)
import streamlit as st


def aplicar_fundo_estadio():
    # Substitui pela URL direta da tua imagem no GitHub ou web
    url_imagem = "https://raw.githubusercontent.com/Rsousa1213/Analise-desportiva-2026/main/fundo_estadio.jpg"

    st.markdown(
        f"""
        <style>
        /* 1. Imagem de fundo no ecrã inteiro com overlay escuro suave */
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.6)), url('{url_imagem}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        /* 2. Remover fundo das barras de topo e elementos globais */
        [data-testid="stHeader"], [data-testid="stSidebar"] {{
            background-color: transparent !important;
        }}

        /* 3. Tornar o painel central semitransparente (estilo vidro) */
        .stMainBlockContainer {{
            background-color: rgba(18, 18, 18, 0.65) !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}

        /* 4. Ajustar legibilidade dos textos e cartões */
        h1, h2, h3, h4, h5, h6, p, label {{
            color: #FFFFFF !important;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


aplicar_fundo_estadio()

# --- REDUZIR LIGEIRAMENTE A LARGURA DA PÁGINA ---
st.markdown("""
    <style>
    .block-container {
        max-width: 85% !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ Análise Desportiva 26/27")
st.caption("Mercado de Golos & Cantos | Época 2026/2027")

# --- REDUZIR LIGEIRAMENTE A LARGURA DA PÁGINA ---
st.markdown("""
    <style>
    .block-container {
        max-width: 85% !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown("Análise focada no **Mercado de Golos (Over 1.5 Pré-Live & Over 2.5)** e **Cantos** com Odds Automáticas")

# --- DICIONÁRIO DE LIGAS (Época 2026/2027: pasta 2627) ---
LEAGUES = {
    "PT Liga Portugal": {
        "url": "https://www.football-data.co.uk/mmz4281/2627/P1.csv",
        "url_prev": "https://www.football-data.co.uk/mmz4281/2526/P1.csv",
        "api_key": "soccer_portugal_primeira_liga"
    },
    "ES La Liga (Espanha)": {
        "url": "https://www.football-data.co.uk/mmz4281/2627/SP1.csv",
        "url_prev": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
        "api_key": "soccer_spain_la_liga"
    },
    "IT Serie A (Itália)": {
        "url": "https://www.football-data.co.uk/mmz4281/2627/I1.csv",
        "url_prev": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
        "api_key": "soccer_italy_serie_a"
    },
    "GB Premier League (Inglaterra)": {
        "url": "https://www.football-data.co.uk/mmz4281/2627/E0.csv",
        "url_prev": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
        "api_key": "soccer_epl"
    },
 "BR Brasileirão Série A": {
        "url": "https://www.football-data.co.uk/new_league_data/BRA.csv",
        "url_prev": "https://www.football-data.co.uk/new_league_data/BRA.csv",
        "api_key": "soccer_brazil_campeonato"
    },
    "EU Liga dos Campeões": {
        "url": "https://www.football-data.co.uk/new_league_data/CL.csv",
        "url_prev": "https://www.football-data.co.uk/new_league_data/CL.csv",
        "api_key": "soccer_uefa_champs_league"
    },
    "EU Liga Europa": {
        "url": "https://www.football-data.co.uk/new_league_data/EL.csv",
        "url_prev": "https://www.football-data.co.uk/new_league_data/EL.csv",
        "api_key": "soccer_uefa_europa_league"
    },
    "NL Eerste Divisie (2ª Holanda)": {
        "url": "https://www.football-data.co.uk/mmz4281/2627/N1.csv",
        "url_prev": "https://www.football-data.co.uk/mmz4281/2526/N1.csv",
        "api_key": "soccer_netherlands_eerste_divisie"
    },
  "AR Liga Profesional (Argentina)": {
        "url": "https://www.football-data.co.uk/new_league_data/ARG.csv",
        "url_prev": "https://www.football-data.co.uk/new_league_data/ARG.csv",
        "api_key": "soccer_argentina_primera_division"
    },
}

# --- SIDEBAR: CONFIGURAÇÕES E API KEY ---
st.sidebar.header("⚙️ Configurações Gerais")
selected_league_name = st.sidebar.selectbox("Selecionar Liga / Competição", list(LEAGUES.keys()))
selected_league = LEAGUES[selected_league_name]

st.sidebar.subheader("🔑 Automação de Odds")
api_key = st.sidebar.text_input("Chave The Odds API", type="password", help="Insere a tua chave gratuita do site the-odds-api.com")

bankroll = st.sidebar.number_input("Banca Total (€)", value=1000.0, step=50.0)
kelly_fraction = st.sidebar.slider("Fração de Kelly", 0.1, 1.0, 0.25, step=0.05)

# --- FUNÇÃO PARA OBTER ODDS EM TEMPO REAL DA API ---
@st.cache_data(ttl=3600)
def fetch_live_odds(api_key, sport_key):
    if not api_key:
        return None
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=totals&oddsFormat=decimal"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

live_data = fetch_live_odds(api_key, selected_league["api_key"])

# --- GERADOR DE DADOS DE SEGURANÇA PARA UEFA ---
def generate_mock_european_data(is_champions=True):
    teams = [
        "Real Madrid", "Manchester City", "Bayern Munich", "PSG", "Barcelona", 
        "Arsenal", "Inter", "Atletico Madrid", "Benfica", "Sporting CP", "FC Porto", "Dortmund",
        "Leverkusen", "Juventus", "Atalanta", "Milan", "Aston Villa", "Lille"
    ] if is_champions else [
        "Roma", "Lazio", "Manchester United", "Tottenham", "Porto", 
        "Athletic Bilbao", "Real Sociedad", "Lyon", "Ajax", "Eintracht Frankfurt", "Nice", "AZ Alkmaar"
    ]
    
    data = []
    np.random.seed(42)
    for i in range(len(teams)):
        for j in range(len(teams)):
            if i != j:
                data.append({
                    "HomeTeam": teams[i],
                    "AwayTeam": teams[j],
                    "FTHG": np.random.poisson(1.6),
                    "FTAG": np.random.poisson(1.2),
                    "HC": np.random.randint(4, 9),
                    "AC": np.random.randint(3, 7)
                })
    return pd.DataFrame(data)

# --- CARREGAR DADOS HISTÓRICOS E LISTA COMPLETA DE EQUIPAS ---
@st.cache_data
def load_league_data(league_info):
    url = league_info["url"]
    
    # 1. Trata competições europeias (UEFA)
    if "new_league_data/CL.csv" in url or "new_league_data/EL.csv" in url:
        try:
            df = pd.read_csv(url, encoding="latin1", on_bad_lines="skip")
            if df.empty or "HomeTeam" not in df.columns:
                return generate_mock_european_data("CL.csv" in url)
            return df
        except:
            return generate_mock_european_data("CL.csv" in url)

    # 2. Trata Ligas Sul-Americanas e Domésticas Europeias
    try:
        df = pd.read_csv(url, encoding="latin1", on_bad_lines="skip")
        
        # Filtra a última época no Brasileirão/Argentina se existir coluna 'Season'
        if "Season" in df.columns:
            max_season = df['Season'].max()
            df = df[df['Season'] == max_season]

        # Padroniza os nomes das colunas
        if "Home" in df.columns and "HomeTeam" not in df.columns:
            df = df.rename(columns={"Home": "HomeTeam", "Away": "AwayTeam", "HG": "FTHG", "AG": "FTAG"})
            
        return df.dropna(subset=['HomeTeam', 'AwayTeam'])
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None
        if 'HC' in df.columns and 'AC' in df.columns:
            cols_needed.extend(['HC', 'AC'])
        
        # Se a época atual ainda tiver poucos jogos, junta dados da época anterior
        if len(df) < 50:
            try:
                df_prev = pd.read_csv(url_prev)
                df = pd.concat([df_prev[cols_needed], df[cols_needed]], ignore_index=True)
            except Exception:
                pass

        return df[cols_needed].dropna()
    except Exception:
        try:
            df = pd.read_csv(url_prev)
            cols_needed = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
            if 'HC' in df.columns and 'AC' in df.columns:
                cols_needed.extend(['HC', 'AC'])
            return df[cols_needed].dropna()
        except Exception:
            return None

df = load_league_data(selected_league)

if df is not None and not df.empty:
    teams = sorted(list(set(df['HomeTeam'].unique()).union(set(df['AwayTeam'].unique()))))
    
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Equipa da Casa", teams, index=0)
    with col2:
        away_options = [t for t in teams if t != home_team]
        away_team = st.selectbox("Equipa Visitante", away_options, index=0 if away_options else 0)

    def get_recent_form(team, is_home=True):
        games = df[(df['HomeTeam' if is_home else 'AwayTeam'] == team)].tail(5)
        goals_for = games['FTHG' if is_home else 'FTAG'].mean() if len(games) > 0 else 1.2
        goals_against = games['FTAG' if is_home else 'FTHG'].mean() if len(games) > 0 else 1.1
        corners = games['HC' if is_home else 'AC'].mean() if 'HC' in games.columns and len(games) > 0 else 5.0
        return goals_for, goals_against, corners

    h_gf, h_ga, h_corners = get_recent_form(home_team, is_home=True)
    a_gf, a_ga, a_corners = get_recent_form(away_team, is_home=False)

    st.subheader("📈 Média de Golos nas Últimas Partidas")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"Atq {home_team}", f"{h_gf:.2f} mar")
    m2.metric(f"Def {home_team}", f"{h_ga:.2f} sof")
    m3.metric(f"Atq {away_team}", f"{a_gf:.2f} mar")
    m4.metric(f"Def {away_team}", f"{a_ga:.2f} sof")

    lambda_home = max(0.2, (h_gf + a_ga) / 2)
    lambda_away = max(0.2, (a_gf + h_ga) / 2)
    
    max_g = 6
    p_home_g = [poisson.pmf(i, lambda_home) for i in range(max_g)]
    p_away_g = [poisson.pmf(i, lambda_away) for i in range(max_g)]
    matrix = np.outer(p_home_g, p_away_g)

    total_expected_goals = lambda_home + lambda_away

    prob_under_15 = sum(matrix[i, j] for i in range(max_g) for j in range(max_g) if i + j < 1.5)
    prob_over_15 = 1 - prob_under_15

    prob_under_25 = sum(matrix[i, j] for i in range(max_g) for j in range(max_g) if i + j < 2.5)
    prob_over_25 = 1 - prob_under_25

    auto_book_over15, auto_book_over25 = None, None

    if live_data:
        for match in live_data:
            h_name = match.get('home_team', '')
            if home_team.lower() in h_name.lower() or h_name.lower() in home_team.lower():
                bookmakers = match.get('bookmakers', [])
                if bookmakers:
                    markets = bookmakers[0].get('markets', [])
                    for m in markets:
                        if m['key'] == 'totals':
                            for outcome in m['outcomes']:
                                if outcome.get('point') == 1.5 and outcome['name'].lower() == 'over':
                                    auto_book_over15 = outcome['price']
                                elif outcome.get('point') == 2.5 and outcome['name'].lower() == 'over':
                                    auto_book_over25 = outcome['price']
                break

    def calc_stake(prob, odd):
        ev = (prob * odd) - 1
        if ev > 0:
            b = odd - 1
            f_k = (b * prob - (1 - prob)) / b
            return ev, max(0.0, bankroll * f_k * kelly_fraction)
        return ev, 0.0

    st.subheader("🎯 Análise Especializada do Mercado de Golos")
    
    if prob_over_15 >= 0.75:
        st.success(f"🟢 **LUZ VERDE PRÉ-LIVE:** Alta probabilidade estatística de **Over 1.5 Golos** ({prob_over_15*100:.1f}%). Ideal para entradas em pré-live ou early live.")
    else:
        st.warning(f"🟡 **ATENÇÃO:** Probabilidade de Over 1.5 é de {prob_over_15*100:.1f}%. Aguardar confirmação de ritmo de jogo no Live.")

    tab1, tab2 = st.tabs(["⚽ Mercado Over / Under Golos", "🚩 Mercado de Cantos"])

    fair_over15 = 1 / prob_over_15 if prob_over_15 > 0 else 0
    fair_over25 = 1 / prob_over_25 if prob_over_25 > 0 else 0

    with tab1:
        g1, g2, g3 = st.columns(3)
        g1.metric("Golos Esperados (xG)", f"{total_expected_goals:.2f}")
        g2.metric("Over 1.5 Golos", f"Fair Odd: {fair_over15:.2f}", f"{prob_over_15*100:.1f}%")
        g3.metric("Over 2.5 Golos", f"Fair Odd: {fair_over25:.2f}", f"{prob_over_25*100:.1f}%")

        st.markdown("---")
        gc1, gc2 = st.columns(2)
        book_over15 = gc1.number_input("Odd Mercado (Over 1.5)", value=float(auto_book_over15 if auto_book_over15 else round(fair_over15 * 1.05, 2)))
        book_over25 = gc2.number_input("Odd Mercado (Over 2.5)", value=float(auto_book_over25 if auto_book_over25 else round(fair_over25 * 1.05, 2)))

        ev_o15, st_o15 = calc_stake(prob_over_15, book_over15)
        ev_o25, st_o25 = calc_stake(prob_over_25, book_over25)

        st.table(pd.DataFrame({
            "Mercado": ["Over 1.5 Golos (Estratégia Base)", "Over 2.5 Golos"],
            "Probabilidade": [f"{prob_over_15*100:.1f}%", f"{prob_over_25*100:.1f}%"],
            "Fair Odd (Justa)": [round(fair_over15, 2), round(fair_over25, 2)],
            "Odd Mercado": [book_over15, book_over25],
            "EV (%)": [f"{ev_o15*100:+.1f}%", f"{ev_o25*100:+.1f}%"],
            "Stake Recomendada": [f"€ {st_o15:.2f}", f"€ {st_o25:.2f}"]
        }))

    with tab2:
        total_c = h_corners + a_corners
        cant1, cant2, cant3 = st.columns(3)
        cant1.metric(f"Média {home_team}", f"{h_corners:.1f}")
        cant2.metric(f"Média {away_team}", f"{a_corners:.1f}")
        cant3.metric("Cantos Totais Esperados", f"{total_c:.1f}")
        st.info(f"💡 Linha sugerida para cantos: ~{total_c:.1f} cantos.")

else:
    st.error("Erro ao carregar dados da competição selecionada.")


