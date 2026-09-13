import streamlit as st
import pandas as pd
import numpy as np
import requests
from scipy.stats import poisson

st.set_page_config(page_title="Plataforma de Análise Desportiva", layout="wide")

st.title("⚽ Plataforma Profissional de Análise Desportiva")
st.markdown("Análise de **Forma**, **Golos**, **Cantos** e **1X2 (+EV)** com Odds Automáticas")

# --- DICIONÁRIO DE LIGAS ---
LEAGUES = {
    "🇵🇹 Liga Portugal": {"url": "https://www.football-data.co.uk/mmz4281/2425/P1.csv", "api_key": "soccer_portugal_primeira_liga"},
    "🇪🇸 La Liga (Espanha)": {"url": "https://www.football-data.co.uk/mmz4281/2425/SP1.csv", "api_key": "soccer_spain_la_liga"},
    "🇮🇹 Serie A (Itália)": {"url": "https://www.football-data.co.uk/mmz4281/2425/I1.csv", "api_key": "soccer_italy_serie_a"},
    "🇬🇧 Premier League (Inglaterra)": {"url": "https://www.football-data.co.uk/mmz4281/2425/E0.csv", "api_key": "soccer_epl"},
    "🇧🇷 Brasileirão (Série A)": {"url": "https://www.football-data.co.uk/new/BRA.csv", "api_key": "soccer_brazil_campeonato"}
}

# --- SIDEBAR: CONFIGURAÇÕES E API KEY ---
st.sidebar.header("⚙️ Configurações Gerais")
selected_league_name = st.sidebar.selectbox("Selecionar Liga", list(LEAGUES.keys()))
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
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=h2h,totals&oddsFormat=decimal"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

live_data = fetch_live_odds(api_key, selected_league["api_key"])

# --- CARREGAR DADOS HISTÓRICOS ROBUSTO ---
@st.cache_data
def load_league_data(url, is_brazil=False):
    try:
        df = pd.read_csv(url)
        
        # Mapeamento para o Brasileirão (Série A)
        if is_brazil or "BRA.csv" in url:
            # Selecionar apenas a época mais recente do Brasileirão no ficheiro global
            if 'Season' in df.columns:
                max_season = df['Season'].max()
                df = df[df['Season'] == max_season]
            cols = ['Home', 'Away', 'HG', 'AG']
            df = df[cols].rename(columns={'Home': 'HomeTeam', 'Away': 'AwayTeam', 'HG': 'FTHG', 'AG': 'FTAG'})
            return df.dropna()
        
        # Mapeamento europeu
        cols_needed = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
        if 'HC' in df.columns and 'AC' in df.columns:
            cols_needed.extend(['HC', 'AC'])
        return df[cols_needed].dropna()
    except Exception:
        fallback_url = url.replace("2425", "2324")
        try:
            df = pd.read_csv(fallback_url)
            cols_needed = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
            if 'HC' in df.columns and 'AC' in df.columns:
                cols_needed.extend(['HC', 'AC'])
            return df[cols_needed].dropna()
        except Exception:
            return None

df = load_league_data(selected_league["url"], is_brazil=("Brasileirão" in selected_league_name))

if df is not None and not df.empty:
    teams = sorted(list(set(df['HomeTeam'].unique()).union(set(df['AwayTeam'].unique()))))
    
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Equipa da Casa", teams, index=0)
    with col2:
        away_options = [t for t in teams if t != home_team]
        away_team = st.selectbox("Equipa Visitante", away_options, index=0 if away_options else 0)

    # MÉTRICAS DE FORMA
    def get_recent_form(team, is_home=True):
        games = df[(df['HomeTeam' if is_home else 'AwayTeam'] == team)].tail(5)
        goals_for = games['FTHG' if is_home else 'FTAG'].mean() if len(games) > 0 else 1.0
        goals_against = games['FTAG' if is_home else 'FTHG'].mean() if len(games) > 0 else 1.0
        corners = games['HC' if is_home else 'AC'].mean() if 'HC' in games.columns and len(games) > 0 else 0
        return goals_for, goals_against, corners

    h_gf, h_ga, h_corners = get_recent_form(home_team, is_home=True)
    a_gf, a_ga, a_corners = get_recent_form(away_team, is_home=False)

    st.subheader("📈 Forma Recente (Últimos 5 Jogos)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"Atq {home_team}", f"{h_gf:.2f} golos")
    m2.metric(f"Def {home_team}", f"{h_ga:.2f} sofridos")
    m3.metric(f"Atq {away_team}", f"{a_gf:.2f} golos")
    m4.metric(f"Def {away_team}", f"{a_ga:.2f} sofridos")

    # POISSON / DIXON-COLES
    lambda_home = max(0.2, (h_gf + a_ga) / 2)
    lambda_away = max(0.2, (a_gf + h_ga) / 2)
    
    max_g = 6
    p_home_g = [poisson.pmf(i, lambda_home) for i in range(max_g)]
    p_away_g = [poisson.pmf(i, lambda_away) for i in range(max_g)]
    matrix = np.outer(p_home_g, p_away_g)
    
    prob_home = np.sum(np.tril(matrix, -1))
    prob_draw = np.sum(np.diag(matrix))
    prob_away = np.sum(np.triu(matrix, 1))

    total_expected_goals = lambda_home + lambda_away
    prob_under_25 = sum(matrix[i, j] for i in range(max_g) for j in range(max_g) if i + j < 2.5)
    prob_over_25 = 1 - prob_under_25

    # TENTAR EXTRAIR ODDS AUTOMÁTICAS DA API
    auto_book_h, auto_book_d, auto_book_a = None, None, None
    auto_book_over, auto_book_under = None, None

    if live_data:
        for match in live_data:
            h_name = match.get('home_team', '')
            a_name = match.get('away_team', '')
            # Busca aproximada por nome da equipa
            if home_team.lower() in h_name.lower() or h_name.lower() in home_team.lower():
                bookmakers = match.get('bookmakers', [])
                if bookmakers:
                    markets = bookmakers[0].get('markets', [])
                    for m in markets:
                        if m['key'] == 'h2h':
                            for outcome in m['outcomes']:
                                if outcome['name'] == match['home_team']:
                                    auto_book_h = outcome['price']
                                elif outcome['name'] == match['away_team']:
                                    auto_book_a = outcome['price']
                                else:
                                    auto_book_d = outcome['price']
                        elif m['key'] == 'totals':
                            for outcome in m['outcomes']:
                                if outcome.get('point') == 2.5:
                                    if outcome['name'].lower() == 'over':
                                        auto_book_over = outcome['price']
                                    elif outcome['name'].lower() == 'under':
                                        auto_book_under = outcome['price']
                break

    def calc_stake(prob, odd):
        ev = (prob * odd) - 1
        if ev > 0:
            b = odd - 1
            f_k = (b * prob - (1 - prob)) / b
            return ev, max(0.0, bankroll * f_k * kelly_fraction)
        return ev, 0.0

    st.subheader("🎯 Estimativa de Odds & Recomendação (+EV)")
    tab1, tab2, tab3 = st.tabs([" Mercado 1X2", "⚽ Mercado de Golos", "🚩 Mercado de Cantos"])

    fair_h = 1 / prob_home if prob_home > 0 else 0
    fair_d = 1 / prob_draw if prob_draw > 0 else 0
    fair_a = 1 / prob_away if prob_away > 0 else 0

    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Vitória {home_team}", f"Fair Odd: {fair_h:.2f}", f"{prob_home*100:.1f}%")
        c2.metric("Empate", f"Fair Odd: {fair_d:.2f}", f"{prob_draw*100:.1f}%")
        c3.metric(f"Vitória {away_team}", f"Fair Odd: {fair_a:.2f}", f"{prob_away*100:.1f}%")

        st.markdown("---")
        if auto_book_h:
            st.success("⚡ Odds em tempo real carregadas automaticamente via API!")
        else:
            st.info("💡 Odds estimadas/manuais em uso para esta liga ou jogo.")

        oc1, oc2, oc3 = st.columns(3)
        book_h = oc1.number_input(f"Odd Casa ({home_team})", value=float(auto_book_h if auto_book_h else round(fair_h * 1.05, 2)))
        book_d = oc2.number_input("Odd Empate", value=float(auto_book_d if auto_book_d else round(fair_d * 1.05, 2)))
        book_a = oc3.number_input(f"Odd Fora ({away_team})", value=float(auto_book_a if auto_book_a else round(fair_a * 1.05, 2)))

        ev_h, st_h = calc_stake(prob_home, book_h)
        ev_d, st_d = calc_stake(prob_draw, book_d)
        ev_a, st_a = calc_stake(prob_away, book_a)

        st.table(pd.DataFrame({
            "Opção": [home_team, "Empate", away_team],
            "Probabilidade": [f"{prob_home*100:.1f}%", f"{prob_draw*100:.1f}%", f"{prob_away*100:.1f}%"],
            "Fair Odd": [round(fair_h, 2), round(fair_d, 2), round(fair_a, 2)],
            "Odd Mercado": [book_h, book_d, book_a],
            "EV (%)": [f"{ev_h*100:+.1f}%", f"{ev_d*100:+.1f}%", f"{ev_a*100:+.1f}%"],
            "Stake Recomendada": [f"€ {st_h:.2f}", f"€ {st_d:.2f}", f"€ {st_a:.2f}"]
        }))

    fair_over = 1 / prob_over_25 if prob_over_25 > 0 else 0
    fair_under = 1 / prob_under_25 if prob_under_25 > 0 else 0

    with tab2:
        g1, g2, g3 = st.columns(3)
        g1.metric("Golos Esperados", f"{total_expected_goals:.2f}")
        g2.metric("Over 2.5 Golos", f"Fair Odd: {fair_over:.2f}", f"{prob_over_25*100:.1f}%")
        g3.metric("Under 2.5 Golos", f"Fair Odd: {fair_under:.2f}", f"{prob_under_25*100:.1f}%")

        st.markdown("---")
        gc1, gc2 = st.columns(2)
        book_over = gc1.number_input("Odd Casa (Over 2.5)", value=float(auto_book_over if auto_book_over else round(fair_over * 1.05, 2)))
        book_under = gc2.number_input("Odd Casa (Under 2.5)", value=float(auto_book_under if auto_book_under else round(fair_under * 1.05, 2)))

        ev_o, st_o = calc_stake(prob_over_25, book_over)
        ev_u, st_u = calc_stake(prob_under_25, book_under)

        st.table(pd.DataFrame({
            "Mercado": ["Over 2.5 Golos", "Under 2.5 Golos"],
            "Probabilidade": [f"{prob_over_25*100:.1f}%", f"{prob_under_25*100:.1f}%"],
            "Fair Odd": [round(fair_over, 2), round(fair_under, 2)],
            "Odd Mercado": [book_over, book_under],
            "EV (%)": [f"{ev_o*100:+.1f}%", f"{ev_u*100:+.1f}%"],
            "Stake Recomendada": [f"€ {st_o:.2f}", f"€ {st_u:.2f}"]
        }))

    with tab3:
        if h_corners > 0 or a_corners > 0:
            total_c = h_corners + a_corners
            cant1, cant2, cant3 = st.columns(3)
            cant1.metric(f"Média {home_team}", f"{h_corners:.1f}")
            cant2.metric(f"Média {away_team}", f"{a_corners:.1f}")
            cant3.metric("Cantos Totais", f"{total_c:.1f}")
            st.info(f"💡 Linha sugerida: ~{total_c:.1f} cantos.")
        else:
            st.warning("⚠️ O ficheiro público do Brasileirão não fornece estatísticas detalhadas de cantos.")

else:
    st.error("Erro ao carregar dados do Brasileirão.")
