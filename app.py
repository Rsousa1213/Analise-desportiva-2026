from datetime import date
import os
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st

# 1. Configuração da Página e Tema Escuro
st.set_page_config(
    page_title="Análise Ténis 26/27 - Rigor Estatístico",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo Visual Profissional com Fundo de Ténis / Estádio e Cartões Compactos
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url('https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .main {
        color: #ffffff !important;
    }
    .stSidebar {
        background-color: rgba(20, 20, 20, 0.95) !important;
    }
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #ffffff !important;
    }
    .metric-card {
        background-color: rgba(30, 30, 30, 0.9) !important;
        padding: 10px 12px;
        border-radius: 6px;
        border: 1px solid #444444;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 10px;
    }
    .metric-card h4 {
        color: #aaaaaa !important;
        font-size: 12px;
        margin-bottom: 2px;
    }
    .metric-card h2 {
        color: #ffffff !important;
        font-size: 18px;
        margin-top: 0px;
        margin-bottom: 0px;
    }
    dataframe, .stDataFrame {
        background-color: rgba(20, 20, 20, 0.85) !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Configuração da Base de Dados SQLite
DB_NAME = "tenis_analytics.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS encontros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            torneio TEXT,
            superficie TEXT,
            jogador_1 TEXT,
            jogador_2 TEXT,
            odd_1 REAL,
            odd_2 REAL,
            vencedor TEXT
        )
    """
    )
    conn.commit()
    conn.close()


init_db()

# ==========================================
# BARRA LATERAL (Gestão de Banca e Torneios)
# ==========================================
with st.sidebar:
    st.markdown("### Selecione o Torneio / Competição:")
    torneio_sel = st.selectbox(
        "", ["ATP Masters / Grand Slam", "WTA Tour", "Challenger Tour"]
    )

    st.markdown("---")
    st.markdown("### 💰 Banca & Gestão")
    valor_banca = st.number_input(
        "Valor da Banca (€)", min_value=1.0, value=100.0, step=10.0
    )
    stake_max = st.slider("Stake Máxima Base (%)", 0.5, 10.0, 5.0)

    st.markdown("---")
    st.markdown("### Inserção Manual de Odds")
    casa_apostas = st.text_input("Casa de Apostas", "Betclic / PinUp")
    odd_over_jogos = st.number_input("Odd Over Jogos (ex: 21.5)", 1.01, 10.0, 1.85)
    odd_under_jogos = st.number_input("Odd Under Jogos", 1.01, 10.0, 1.90)
    odd_favorito = st.number_input("Odd Vitória Favorito", 1.01, 10.0, 1.45)
    odd_underdog = st.number_input("Odd Vitória Underdog", 1.01, 10.0, 2.70)

# ==========================================
# CABEÇALHO E ABAS PRINCIPAIS
# ==========================================
st.markdown(
    "## 🎾 Análise 26/27 - Rigor Estatístico & Inteligência Avançada"
)

aba_analise, aba_historico = st.tabs(
    ["🎾 Análise do Jogo", "📊 Histórico & Desempenho"]
)

# Seleção de Atletas
col_j1, col_j2 = st.columns(2)
with col_j1:
    jogador_casa = st.selectbox(
        "Jogador / Atleta A", ["Novak Djokovic", "Carlos Alcaraz", "Jannik Sinner"]
    )
with col_j2:
    jogador_fora = st.selectbox(
        "Jogador / Atleta B", [
            "Alexander Zverev",
            "Daniil Medvedev",
            "Stefanos Tsitsipas",
        ]
    )

# ==========================================
# ABA 1: ANÁLISE DO JOGO (Indicadores de Ténis)
# ==========================================
with aba_analise:
    st.markdown("---")
    st.markdown("### 📊 Indicadores Avançados & Fator Superfície")

    # Linha 1 de Métricas
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            '<div class="metric-card"><h4>Hold de Serviço (A)</h4><h2>86.4%</h2></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            '<div class="metric-card"><h4>Hold de Serviço (B)</h4><h2>81.2%</h2></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            '<div class="metric-card"><h4>Prob. Tie-Break</h4><h2>34.5%</h2></div>',
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            '<div class="metric-card"><h4>Prob. 3 Sets / Longo</h4><h2>58.2%</h2></div>',
            unsafe_allow_html=True,
        )

    # Linha 2 de Métricas
    m5, m6, m7, m8 = st.columns(4)
    with m5:
        st.markdown(
            '<div class="metric-card"><h4>Média Ases (A/B)</h4><h2>9.4 / 6.1</h2></div>',
            unsafe_allow_html=True,
        )
    with m6:
        st.markdown(
            '<div class="metric-card"><h4>Duplas Faltas (A/B)</h4><h2>2.1 / 3.4</h2></div>',
            unsafe_allow_html=True,
        )
    with m7:
        st.markdown(
            '<div class="metric-card"><h4>Break Points Conv.</h4><h2>42.1%</h2></div>',
            unsafe_allow_html=True,
        )
    with m8:
        st.markdown(
            '<div class="metric-card"><h4>Eficiência Terra/Hard</h4><h2>78% / 82%</h2></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 💡 Tabela Consolidada de Mercados (Ténis)")

    # Simulação da Tabela Consolidada
    dados_tabela = [
        {
            "Mercado": f"Vitória {jogador_casa}",
            "Probabilidade": "64.5%",
            "Odd Inserida": odd_favorito,
            "Odd Justa": round(1 / 0.645, 2),
            "Edge (%)": "+6.2%",
            "Stake Recomendada (€)": round(
                valor_banca * (stake_max / 100), 2
            ),
            "Ganho Potencial (€)": round(
                valor_banca * (stake_max / 100) * odd_favorito, 2
            ),
            "Avaliação": "🔥 Valor Encontrado",
        },
        {
            "Mercado": "Over 21.5 Jogos",
            "Probabilidade": "57.0%",
            "Odd Inserida": odd_over_jogos,
            "Odd Justa": round(1 / 0.57, 2),
            "Edge (%)": "+5.5%",
            "Stake Recomendada (€)": round(
                valor_banca * (stake_max / 100), 2
            ),
            "Ganho Potencial (€)": round(
                valor_banca * (stake_max / 100) * odd_over_jogos, 2
            ),
            "Avaliação": "🔥 Valor Encontrado",
        },
        {
            "Mercado": "Under 21.5 Jogos",
            "Probabilidade": "43.0%",
            "Odd Inserida": odd_under_jogos,
            "Odd Justa": round(1 / 0.43, 2),
            "Edge (%)": "-18.2%",
            "Stake Recomendada (€)": 0.00,
            "Ganho Potencial (€)": 0.00,
            "Avaliação": "❄️ Neutro / Evitar",
        },
        {
            "Mercado": f"Vitória {jogador_fora}",
            "Probabilidade": "35.5%",
            "Odd Inserida": odd_underdog,
            "Odd Justa": round(1 / 0.355, 2),
            "Edge (%)": "-4.1%",
            "Stake Recomendada (€)": 0.00,
            "Ganho Potencial (€)": 0.00,
            "Avaliação": "❄️ Neutro / Evitar",
        },
    ]

    df_mercados = pd.DataFrame(dados_tabela)
    st.dataframe(df_mercados, use_container_width=True)

# ==========================================
# ABA 2: HISTÓRICO & DESEMPENHO
# ==========================================
with aba_historico:
    st.markdown("### Registo e Histórico de Confrontos Diretos")

    conn = sqlite3.connect(DB_NAME)
    df_encontros = pd.read_sql_query("SELECT * FROM encontros", conn)
    conn.close()

    if not df_encontros.empty:
        st.dataframe(df_encontros, use_container_width=True)
    else:
        st.info(
            "Ainda não existem encontros gravados. Utilize o formulário abaixo para adicionar dados."
        )

    with st.form("form_novo_jogo_tenis"):
        st.markdown("### Adicionar Novo Encontro à Base de Dados")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            data_reg = st.date_input("Data", date.today())
            torneio_nome = st.text_input("Torneio", "ATP Masters")
            superficie_escolhida = st.selectbox(
                "Superfície", ["Hard", "Clay", "Grass", "Carpet"]
            )
        with col_f2:
            j1 = st.text_input("Jogador 1", jogador_casa)
            j2 = st.text_input("Jogador 2", jogador_fora)
            o1 = st.number_input("Odd Jogador 1", 1.01, 100.0, 1.50)
            o2 = st.number_input("Odd Jogador 2", 1.01, 100.0, 2.50)
            venc = st.selectbox("Vencedor", [j1, j2, "Pendente"])

        btn_guardar = st.form_submit_button("Guardar Registo na Base de Dados")
        if btn_guardar:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO encontros (data, torneio, superficie, jogador_1, jogador_2, odd_1, odd_2, vencedor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    str(data_reg),
                    torneio_nome,
                    superficie_escolhida,
                    j1,
                    j2,
                    o1,
                    o2,
                    venc,
                ),
            )
            conn.commit()
            conn.close()
            st.success("Encontro de ténis guardado com sucesso!")
