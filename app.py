from datetime import date
import os
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st

# 1. Configuração da Página e Estilo Visual
st.set_page_config(
    page_title="Analise Tenis 26/27 - Rigor Estatístico",
    layout="wide",
    initial_sidebar_state="expanded",
)


def aplicar_estilo_visual():
    st.markdown(
        """
        <style>
        .main {
            background-color: #f8f9fa;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff;
            border-radius: 4px;
            padding: 10px 20px;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2e7d32 !important;
            color: white !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


aplicar_estilo_visual()

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

# Cabeçalho Principal
st.title("🎾 Análise Estatística & Apostas de Ténis")
st.markdown(
    "Plataforma avançada para análise de dados de ténis, cálculo de probabilidades e apoio à decisão em apostas desportivas."
)

# 3. Estrutura de Abas (Tabs)
aba_dashboard, aba_estatisticas, aba_simulador, aba_gestao = st.tabs(
    [
        "📊 Dashboard Geral",
        "📈 Análise de Confrontos & Jogadores",
        "💡 Simulador de Apostas & Valor",
        "⚙️ Gestão de Dados",
    ]
)

# ==========================================
# ABA 1: DASHBOARD GERAL
# ==========================================
with aba_dashboard:
    st.subheader("Resumo da Base de Dados e Métricas Principais")

    conn = sqlite3.connect(DB_NAME)
    df_encontros = pd.read_sql_query("SELECT * FROM encontros", conn)
    conn.close()

    if not df_encontros.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Encontros", len(df_encontros))
        with col2:
            st.metric(
                "Torneios Registados",
                df_encontros["torneio"].nunique()
                if "torneio" in df_encontros.columns
                else 0,
            )
        with col3:
            st.metric(
                "Superfícies Únicas",
                df_encontros["superficie"].nunique()
                if "superficie" in df_encontros.columns
                else 0,
            )
        with col4:
            st.metric("Jogadores Mapeados", "N/D")

        st.markdown("---")
        st.markdown("### Últimos Encontros Registados")
        st.dataframe(df_encontros.tail(10), use_container_width=True)
    else:
        st.info(
            "Ainda não existem dados na base de dados. Utilize a aba 'Gestão de Dados' para inserir registos."
        )

# ==========================================
# ABA 2: ANÁLISE DE CONFRONTOS & JOGADORES
# ==========================================
with aba_estatisticas:
    st.subheader("Análise Detalhada por Jogador e Superfície")

    if not df_encontros.empty:
        lista_jogadores = sorted(
            list(
                set(
                    df_encontros["jogador_1"].tolist()
                    + df_encontros["jogador_2"].tolist()
                )
            )
        )

        col_j1, col_j2 = st.columns(2)
        with col_j1:
            jogador_selecionado = st.selectbox(
                "Selecione o Jogador", lista_jogadores
            )

        if jogador_selecionado:
            df_jogador = df_encontros[
                (df_encontros["jogador_1"] == jogador_selecionado)
                | (df_encontros["jogador_2"] == jogador_selecionado)
            ]
            st.markdown(f"### Histórico para: **{jogador_selecionado}**")
            st.dataframe(df_jogador, use_container_width=True)

            # Filtro por superfície
            if "superficie" in df_encontros.columns:
                superficies = df_encontros["superficie"].unique()
                sup_escolhida = st.selectbox(
                    "Filtrar por Superfície", superficies
                )
                df_sup = df_jogador[df_jogador["superficie"] == sup_escolhida]
                st.write(
                    f"Desempenho em **{sup_escolhida}**: {len(df_sup)} encontros encontrados."
                )
    else:
        st.warning(
            "Insira dados de encontros para poder realizar análises estatísticas."
        )

# ==========================================
# ABA 3: SIMULADOR DE APOSTAS & VALOR
# ==========================================
with aba_simulador:
    st.subheader("Calculadora de Valor Esperado (EV) & Apostas")

    st.markdown(
        "Insira as odds oferecidas pelas casas de apostas e a sua probabilidade estimada para calcular o valor da aposta."
    )

    col_odds1, col_odds2 = st.columns(2)
    with col_odds1:
        odd_jog_1 = st.number_input(
            "Odd Jogador 1", min_value=1.01, value=1.85, step=0.01
        )
        prob_est_1 = st.slider(
            "Probabilidade Estimada (%) - Jogador 1", 1, 99, 55
        )

    with col_odds2:
        odd_jog_2 = st.number_input(
            "Odd Jogador 2", min_value=1.01, value=2.00, step=0.01
        )
        prob_est_2 = 100 - prob_est_1
        st.info(f"Probabilidade Estimada (%) - Jogador 2: {prob_est_2}%")

    st.markdown("---")
    if st.button("Calcular Valor de Aposta"):
        ev_1 = (prob_est_1 / 100.0) * odd_jog_1 - 1
        ev_2 = (prob_est_2 / 100.0) * odd_jog_2 - 1

        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Expected Value (EV) - Jogador 1", f"{ev_1 * 100:.2f}%")
            if ev_1 > 0:
                st.success(
                    "Aposta com Valor Positivo (Value Bet) detetada no Jogador 1!"
                )
            else:
                st.warning("Sem valor estatístico para o Jogador 1.")

        with col_res2:
            st.metric("Expected Value (EV) - Jogador 2", f"{ev_2 * 100:.2f}%")
            if ev_2 > 0:
                st.success(
                    "Aposta com Valor Positivo (Value Bet) detetada no Jogador 2!"
                )
            else:
                st.warning("Sem valor estatístico para o Jogador 2.")

# ==========================================
# ABA 4: GESTÃO DE DADOS
# ==========================================
with aba_gestao:
    st.subheader("Adicionar Novo Encontro / Importar Dados")

    with st.form("form_inserir_encontro"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            data_enc = st.date_input("Data do Encontro", date.today())
            torneio = st.text_input("Nome do Torneio", "ATP Masters")
            superficie = st.selectbox(
                "Superfície", ["Hard", "Clay", "Grass", "Carpet"]
            )
        with col_f2:
            jogador_1 = st.text_input("Jogador 1", "Novak Djokovic")
            jogador_2 = st.text_input("Jogador 2", "Carlos Alcaraz")
            odd_1 = st.number_input("Odd Jogador 1", 1.01, 100.0, 1.50)
            odd_2 = st.number_input("Odd Jogador 2", 1.01, 100.0, 2.50)
            vencedor = st.selectbox(
                "Vencedor", [jogador_1, jogador_2, "Pendente"]
            )

        submit_button = st.form_submit_button(
            label="Guardar Encontro na Base de Dados"
        )

        if submit_button:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO encontros (data, torneio, superficie, jogador_1, jogador_2, odd_1, odd_2, vencedor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    str(data_enc),
                    torneio,
                    superficie,
                    jogador_1,
                    jogador_2,
                    odd_1,
                    odd_2,
                    vencedor,
                ),
            )
            conn.commit()
            conn.close()
            st.success("Encontro registado com sucesso na base de dados SQLite!")
        
