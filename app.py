import base64
from datetime import date, datetime
import os
import sqlite3
import numpy as np
import pandas as pd
import requests
import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="Análise NBA 26/27 - Rigor Estatístico",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Função para carregar o fundo, com deteção automática do formato (idêntica ao futebol/ténis)
def get_image_data_uri(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            if image_path.lower().endswith(".png"):
                return f"data:image/png;base64,{encoded}"
            else:
                return f"data:image/jpeg;base64,{encoded}"
    return ""


# ⚠️ PLACEHOLDER: substitui "fundo_nba.jpg" por uma imagem tua (sem direitos
# de autor de terceiros, sem pessoas reais identificáveis) quando a tiveres.
# Até lá, a app funciona com um fundo escuro neutro.
img_uri = get_image_data_uri("fundo_nba.jpg")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.55), rgba(0, 0, 0, 0.75)), url("{img_uri}") !important;
        background-color: #0b0e13 !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: rgba(18, 18, 18, 0.55) !important;
    }}
    h1, h2, h3, h4, h5, h6, p, label, span {{
        color: #ffffff !important;
    }}
    div[data-testid="stMetric"] {{
        background-color: rgba(25, 25, 25, 0.75);
        padding: 12px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }}
    [data-testid="stDataFrame"] {{
        background-color: rgba(25, 25, 25, 0.85) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("## 🏀 Análise NBA 26/27 - Rigor Estatístico & Inteligência Avançada")

# ==========================================
# 2. Equipas por Conferência / Divisão
# ==========================================
EQUIPAS_NBA = {
    "Leste": {
        "Atlantic": ["Boston Celtics", "Brooklyn Nets", "New York Knicks", "Philadelphia 76ers", "Toronto Raptors"],
        "Central": ["Chicago Bulls", "Cleveland Cavaliers", "Detroit Pistons", "Indiana Pacers", "Milwaukee Bucks"],
        "Southeast": ["Atlanta Hawks", "Charlotte Hornets", "Miami Heat", "Orlando Magic", "Washington Wizards"],
    },
    "Oeste": {
        "Northwest": ["Denver Nuggets", "Minnesota Timberwolves", "Oklahoma City Thunder", "Portland Trail Blazers", "Utah Jazz"],
        "Pacific": ["Golden State Warriors", "LA Clippers", "Los Angeles Lakers", "Phoenix Suns", "Sacramento Kings"],
        "Southwest": ["Dallas Mavericks", "Houston Rockets", "Memphis Grizzlies", "New Orleans Pelicans", "San Antonio Spurs"],
    },
}

TODAS_EQUIPAS = sorted(
    equipa
    for conferencia in EQUIPAS_NBA.values()
    for divisao in conferencia.values()
    for equipa in divisao
)

# ==========================================
# 3. Base de dados SQLite (histórico de apostas — mesma lógica do futebol)
# ==========================================
DB_NAME = "nba_analytics.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS apostas_nba (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_registo TEXT,
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
        """
    )
    conn.commit()
    conn.close()


def registar_aposta(casa, fora, mercado, prob, odd, edge, stake):
    conn = sqlite3.connect(DB_NAME)
    conn.execute(
        "INSERT INTO apostas_nba (data_registo, equipa_casa, equipa_fora, mercado, probabilidade, odd, edge, stake, resultado, lucro) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M"), casa, fora, mercado, prob, odd, edge, stake, "Pendente", None),
    )
    conn.commit()
    conn.close()


def atualizar_resultado(aposta_id, resultado):
    conn = sqlite3.connect(DB_NAME)
    stake, odd = conn.execute("SELECT stake, odd FROM apostas_nba WHERE id=?", (aposta_id,)).fetchone()
    lucro = stake * (odd - 1) if resultado == "Ganhou" else (-stake if resultado == "Perdeu" else 0.0)
    conn.execute("UPDATE apostas_nba SET resultado=?, lucro=? WHERE id=?", (resultado, lucro, aposta_id))
    conn.commit()
    conn.close()


init_db()

# ==========================================
# 4. Dados — placeholder por agora (PRÓXIMO PASSO: ligar fonte real testada ao vivo)
# ==========================================
# ⚠️ Ainda NÃO ligado a nenhuma fonte de estatísticas real. Depois da
# experiência do ténis, vamos confirmar UMA fonte de cada vez, ao vivo,
# antes de a assumirmos como garantida. Candidatas: ESPN (scoreboard/
# resultados, grátis, sem chave) e balldontlie.io (equipas/jogos, grátis,
# mas agora exige chave e só 5 pedidos/min).
st.info(
    "🚧 Esqueleto inicial — equipas e estrutura prontas, tal como no futebol. "
    "Os dados estatísticos ainda não estão ligados a nenhuma fonte real; "
    "vamos confirmar isso, passo a passo, testado ao vivo."
)

# ==========================================
# 5. Seleção de equipas (primeiro, para a sidebar poder usar os nomes)
# ==========================================
col_a, col_b = st.columns(2)
with col_a:
    equipa_casa = st.selectbox("Equipa da Casa", TODAS_EQUIPAS, index=TODAS_EQUIPAS.index("Boston Celtics"))
with col_b:
    equipa_fora = st.selectbox("Equipa Visitante", TODAS_EQUIPAS, index=TODAS_EQUIPAS.index("Los Angeles Lakers"))

# ==========================================
# 6. Barra lateral — Banca, Kelly, Odds (mesma filosofia do futebol)
# ==========================================
with st.sidebar:
    st.markdown("### 🏆 Conferência / Divisão")
    conf_sel = st.selectbox("Conferência", list(EQUIPAS_NBA.keys()))
    div_sel = st.selectbox("Divisão", list(EQUIPAS_NBA[conf_sel].keys()))
    st.caption(", ".join(EQUIPAS_NBA[conf_sel][div_sel]))

    st.markdown("---")
    st.markdown("### 💰 Banca & Gestão")
    banca_inicial = st.number_input("Valor da Banca (€)", min_value=1.0, value=100.0, step=10.0)
    stake_pct_max = st.slider("Stake Máxima Base (%)", 0.5, 10.0, 5.0)
    fracao_kelly = st.slider(
        "Fração de Kelly a usar", 0.1, 1.0, 0.25, 0.05,
        help="Kelly fracionário (0.25-0.5) reduz a variância face ao Kelly puro.",
    )

    st.markdown("---")
    st.markdown("### Filtros de Rigor")
    edge_minimo = st.slider("Edge Mínimo Exigido (%)", 0.5, 10.0, 3.0, 0.5) / 100

    st.markdown("---")
    st.markdown("### ✏️ Inserção Manual de Odds")
    casa_apostas = st.text_input("Casa de Apostas", "")

    st.markdown(f"**🏆 Vencedor — {equipa_casa} vs {equipa_fora}**")
    odd_casa = st.number_input(f"Odd — {equipa_casa}", 1.01, 20.0, 1.90, key="odd_casa_nba")
    odd_fora = st.number_input(f"Odd — {equipa_fora}", 1.01, 20.0, 1.90, key="odd_fora_nba")

    st.markdown("**🎯 Total de Pontos**")
    linha_pontos = st.number_input(
        "Linha (ex: 224.5) — copia o valor exato da casa de apostas",
        min_value=150.0, max_value=280.0, value=224.5, step=0.5,
    )
    odd_over_pontos = st.number_input(f"Odd Over {linha_pontos}", 1.01, 10.0, 1.90)
    odd_under_pontos = st.number_input(f"Odd Under {linha_pontos}", 1.01, 10.0, 1.90)

    st.markdown("**📏 Handicap (Spread)**")
    linha_handicap = st.number_input(
        "Linha de handicap (ex: -5.5 para a equipa da casa)",
        min_value=-30.0, max_value=30.0, value=-5.5, step=0.5,
    )
    odd_handicap_casa = st.number_input(f"Odd Handicap — {equipa_casa}", 1.01, 10.0, 1.90)
    odd_handicap_fora = st.number_input(f"Odd Handicap — {equipa_fora}", 1.01, 10.0, 1.90)

# ==========================================
# 7. Abas principais
# ==========================================
aba_analise, aba_historico = st.tabs(["🏀 Análise do Jogo", "📊 Histórico & Desempenho"])

with aba_analise:
    st.markdown("---")
    st.markdown(f"### 📊 {equipa_casa} vs {equipa_fora}")
    st.caption(
        "⚠️ Os indicadores abaixo são placeholders — ainda não vêm de uma fonte de dados real. "
        "É o próximo passo, a validar ao vivo antes de confiarmos nos números."
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pontos Esperados (Casa)", "—")
    m2.metric("Pontos Esperados (Fora)", "—")
    m3.metric(f"Prob. Over {linha_pontos}", "—")
    m4.metric("Ritmo de Jogo (Pace)", "—")

    st.markdown("---")
    st.markdown("### 💡 Tabela Consolidada de Mercados")
    st.info("A tabela de Edge/Kelly aparece aqui assim que ligarmos uma fonte de dados real e validada.")

with aba_historico:
    st.markdown("### 📈 Histórico & Desempenho")
    conn = sqlite3.connect(DB_NAME)
    df_hist = pd.read_sql_query("SELECT * FROM apostas_nba ORDER BY id DESC", conn)
    conn.close()

    if df_hist.empty:
        st.info("Ainda não há apostas registadas.")
    else:
        st.dataframe(df_hist, use_container_width=True)
