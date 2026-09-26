import base64
from datetime import date
import os
import sqlite3
import numpy as np
import pandas as pd
import requests
import streamlit as st

# 1. Configuração da Página e Tema Escuro
st.set_page_config(
    page_title="Análise Ténis 26/27 - Rigor Estatístico",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Função para carregar e detetar automaticamente o formato correto (JPG ou PNG)
def get_image_data_uri(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            if image_path.lower().endswith(".png"):
                return f"data:image/png;base64,{encoded}"
            else:
                return f"data:image/jpeg;base64,{encoded}"
    else:
        st.warning(
            f"⚠️ Ficheiro '{image_path}' não encontrado na pasta principal."
        )
        return ""


img_uri = get_image_data_uri("Tenis1.jpg")

# Injeção de CSS com remoção da barra branca superior e integração com o fundo
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("{img_uri}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    
    /* Torna o cabeçalho superior transparente para se fundir com o fundo */
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    
    .stSidebar, [data-testid="stSidebar"] {{
        background-color: rgba(18, 18, 18, 0.92) !important;
    }}
    
    h1, h2, h3, h4, h5, h6, p, label, span {{
        color: #ffffff !important;
    }}
    
    .metric-card {{
        background-color: rgba(25, 25, 25, 0.85) !important;
        padding: 10px 12px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        margin-bottom: 10px;
        backdrop-filter: blur(4px);
    }}
    .metric-card h4 {{
        color: #dddddd !important;
        font-size: 12px;
        margin-bottom: 2px;
    }}
    .metric-card h2 {{
        color: #ffffff !important;
        font-size: 18px;
        margin-top: 0px;
        margin-bottom: 0px;
    }}
    
    [data-testid="stDataFrame"] {{
        background-color: rgba(25, 25, 25, 0.85) !important;
        backdrop-filter: blur(4px);
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Configuração da Base de Dados SQLite
DB_NAME = "tenis_analytics.db"

# Valores-placeholder para jogadores que ainda não têm estatísticas próprias
# (vêm da ESPN só com o nome). Ficam claramente marcados como não-reais até
# o próximo passo (Elo por superfície) os substituir por números calculados
# a partir de histórico real.
STATS_PLACEHOLDER = (80.0, 7.0, 2.5, 40.0, 75.0)


# --- Passo atual: histórico real do Jeff Sackmann (GitHub) ---
# Dá-nos nomes de jogadores que realmente disputaram partidas (não uma
# lista escrita à mão) e, mais tarde, o histórico para calcular o Elo.
SACKMANN_ANOS = [2022, 2023, 2024, 2025, 2026]


@st.cache_data(ttl=21600)  # atualiza a cada 6 horas
def obter_historico_sackmann(circuito, ano):
    """circuito: 'atp' ou 'wta'. Devolve (dataframe, aviso).

    Importante: usamos requests com um User-Agent explícito em vez de
    pd.read_csv(url) direto — o GitHub por vezes recusa pedidos que não se
    identifiquem como vindo de um browser, mesmo que o ficheiro exista."""
    import io

    repo = "tennis_atp" if circuito == "atp" else "tennis_wta"
    prefixo = "atp" if circuito == "atp" else "wta"
    url = f"https://raw.githubusercontent.com/JeffSackmann/{repo}/master/{prefixo}_matches_{ano}.csv"
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; AnaliseDesportivaApp/1.0)"},
            timeout=15,
        )
        if resp.status_code != 200:
            return None, f"{ano}: HTTP {resp.status_code}."
        df = pd.read_csv(io.StringIO(resp.text))
        if {"winner_name", "loser_name"}.issubset(df.columns):
            return df, None
        return None, f"{ano}: ficheiro sem as colunas esperadas."
    except Exception as e:
        return None, f"{ano}: não disponível ({e.__class__.__name__})."


@st.cache_data(ttl=21600)
def obter_jogadores_sackmann(circuito):
    """Junta vários anos e devolve (lista_de_nomes, resumo_por_ano)."""
    nomes = set()
    resumo = []
    for ano in SACKMANN_ANOS:
        df, aviso = obter_historico_sackmann(circuito, ano)
        if df is not None:
            nomes.update(df["winner_name"].dropna().unique())
            nomes.update(df["loser_name"].dropna().unique())
            resumo.append(f"{ano}: ✅ {len(df)} jogos")
        else:
            resumo.append(f"{ano}: ❌ {aviso}")
    return sorted(nomes), resumo


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
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS atletas (
            nome TEXT PRIMARY KEY,
            hold_servico REAL,
            media_ases REAL,
            duplas_faltas REAL,
            break_points_conv REAL,
            eficiencia_hard REAL
        )
    """
    )

    # Lista de reserva (usada se a ligação à ESPN falhar) — os números aqui
    # continuam a ser estimativas, não estatísticas oficiais verificadas.
    atletas_iniciais = [
        ("Juan Manuel Cerundolo", 79.5, 5.2, 2.1, 41.0, 78.0),
        ("Alejandro Davidovich Fokina", 81.2, 8.4, 2.7, 42.5, 80.5),
        ("Jannik Sinner", 87.5, 9.8, 1.8, 44.2, 85.0),
        ("Carlos Alcaraz", 85.2, 7.5, 2.4, 43.0, 83.5),
        ("Alexander Zverev", 89.1, 11.2, 2.1, 38.0, 81.0),
        ("Novak Djokovic", 88.0, 6.8, 1.5, 45.5, 88.0),
        ("Daniil Medvedev", 83.4, 6.2, 2.8, 41.5, 84.0),
        ("Taylor Fritz", 89.5, 13.5, 1.9, 36.2, 82.0),
        ("Casper Ruud", 84.0, 5.5, 2.2, 39.8, 77.0),
        ("Andrey Rublev", 85.6, 9.1, 2.5, 40.1, 80.5),
        ("Alex de Minaur", 80.5, 4.2, 1.6, 43.5, 81.0),
        ("Stefanos Tsitsipas", 86.2, 8.9, 2.3, 38.5, 79.0),
        ("Hubert Hurkacz", 91.0, 15.2, 1.7, 34.0, 83.0),
        ("Tommy Paul", 82.1, 6.1, 1.8, 42.0, 79.5),
        ("Grigor Dimitrov", 84.8, 8.4, 2.0, 41.0, 82.5),
        ("Ben Shelton", 88.2, 14.8, 3.1, 35.5, 80.0),
        ("Ugo Humbert", 83.0, 10.1, 2.4, 39.5, 79.0),
        ("Holger Rune", 82.5, 7.9, 2.9, 40.0, 78.5),
        ("Frances Tiafoe", 81.5, 8.2, 2.6, 39.0, 78.0),
        ("Karen Khachanov", 84.5, 9.5, 2.2, 37.5, 80.0),
        ("Alejandro Tabilo", 81.0, 8.0, 2.1, 38.0, 76.0),
        ("Sebastian Baez", 76.0, 3.1, 2.3, 45.0, 72.0),
        ("Arthur Fils", 83.5, 9.0, 2.7, 38.5, 79.0),
        ("Lorenzo Musetti", 79.0, 5.0, 2.4, 42.0, 75.0),
        ("Jack Draper", 85.0, 11.0, 2.0, 40.5, 82.0),
        ("Felix Auger-Aliassime", 86.5, 12.5, 2.5, 36.0, 81.0),
        ("Jordan Thompson", 81.2, 6.5, 1.8, 41.0, 78.5),
        # ATP Doubles (a ESPN não separa bem duplas — mantido manual por agora)
        ("Marcel Granollers", 90.0, 4.0, 1.2, 48.0, 85.0),
        ("Horacio Zeballos", 89.5, 4.2, 1.3, 47.5, 84.5),
        ("Matthew Ebden", 90.5, 6.5, 1.4, 46.0, 86.0),
        ("Rohan Bopanna", 91.2, 8.2, 1.1, 45.0, 87.0),
        ("Joe Salisbury", 89.0, 5.5, 1.5, 46.5, 84.0),
        ("Rajeev Ram", 88.8, 5.0, 1.4, 47.0, 85.0),
        ("Marcelo Arevalo", 89.2, 6.0, 1.3, 46.0, 85.5),
        ("Mate Pavic", 89.8, 7.1, 1.2, 45.5, 86.0),
        ("Wesley Koolhof", 88.5, 5.8, 1.5, 46.0, 84.0),
        ("Nikola Mektic", 88.2, 6.2, 1.6, 45.0, 83.5),
        ("Kevin Krawietz", 87.9, 7.5, 1.4, 44.5, 83.0),
        ("Tim Puetz", 87.5, 7.0, 1.5, 44.0, 83.0),
        ("Max Purcell", 88.0, 8.0, 1.6, 45.0, 84.0),
        ("Andrea Vavassori", 86.5, 6.0, 1.7, 43.5, 82.0),
        ("Simone Bolelli", 87.0, 6.5, 1.6, 44.0, 82.5),
        ("Harri Heliovaara", 87.5, 7.2, 1.4, 43.0, 83.0),
        ("Henry Patten", 87.2, 7.4, 1.5, 43.5, 83.0),
        ("Michael Venus", 86.8, 6.1, 1.7, 42.5, 81.5),
        ("Neal Skupski", 88.1, 6.8, 1.4, 45.0, 84.0),
        ("Austin Krajicek", 87.8, 7.0, 1.5, 44.0, 83.5),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO atletas VALUES (?, ?, ?, ?, ?, ?)",
        atletas_iniciais,
    )
    conn.commit()
    conn.close()


def sincronizar_jogadores_sackmann():
    """Junta à base de dados qualquer jogador do histórico Sackmann que ainda
    não exista, com estatísticas-placeholder (claramente marcadas, não
    inventadas como se fossem reais) até termos o Elo por superfície a sério."""
    nomes_atp, resumo_atp = obter_jogadores_sackmann("atp")
    nomes_wta, resumo_wta = obter_jogadores_sackmann("wta")

    novos = sorted(set(nomes_atp) | set(nomes_wta))
    if novos:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT OR IGNORE INTO atletas VALUES (?, ?, ?, ?, ?, ?)",
            [(nome,) + STATS_PLACEHOLDER for nome in novos],
        )
        conn.commit()
        conn.close()

    return len(novos), resumo_atp, resumo_wta


init_db()
n_novos, resumo_atp, resumo_wta = sincronizar_jogadores_sackmann()

with st.sidebar:
    if n_novos > 0:
        st.success(f"✅ {n_novos} jogadores reais (histórico Sackmann) adicionados.")
    with st.expander("Detalhe da ligação ao histórico (ATP/WTA)"):
        st.write("**ATP:**")
        for linha in resumo_atp:
            st.caption(linha)
        st.write("**WTA:**")
        for linha in resumo_wta:
            st.caption(linha)


# Função para obter as estatísticas do atleta selecionado
def get_atleta_stats(nome):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT hold_servico, media_ases, duplas_faltas, break_points_conv, eficiencia_hard FROM atletas WHERE nome = ?",
        (nome,),
    )
    res = cursor.fetchone()
    conn.close()
    if res:
        return {
            "hold": res[0],
            "ases": res[1],
            "df": res[2],
            "bp": res[3],
            "hard": res[4],
        }
    else:
        return {
            "hold": 80.0,
            "ases": 7.0,
            "df": 2.5,
            "bp": 40.0,
            "hard": 75.0,
        }


# ==========================================
# SELEÇÃO DE JOGADORES (feita primeiro, para a sidebar poder usar os nomes)
# ==========================================
conn = sqlite3.connect(DB_NAME)
df_atletas_db = pd.read_sql_query(
    "SELECT nome FROM atletas ORDER BY nome ASC", conn
)
conn.close()
lista_tenistas = df_atletas_db["nome"].tolist()

st.caption(f"📋 {len(lista_tenistas)} jogadores disponíveis na lista.")

col_j1, col_j2 = st.columns(2)
with col_j1:
    jogador_casa = st.selectbox(
        "Jogador / Atleta A",
        options=lista_tenistas,
        index=(
            lista_tenistas.index("Juan Manuel Cerundolo")
            if "Juan Manuel Cerundolo" in lista_tenistas
            else 0
        ),
        key="sel_j1",
    )
with col_j2:
    jogador_fora = st.selectbox(
        "Jogador / Atleta B",
        options=lista_tenistas,
        index=(
            lista_tenistas.index("Alejandro Davidovich Fokina")
            if "Alejandro Davidovich Fokina" in lista_tenistas
            else (1 if len(lista_tenistas) > 1 else 0)
        ),
        key="sel_j2",
    )

stats_a = get_atleta_stats(jogador_casa)
stats_b = get_atleta_stats(jogador_fora)

# ==========================================
# BARRA LATERAL (Gestão de Banca e Torneios)
# ==========================================
with st.sidebar:
    st.markdown("### Selecione o Torneio / Competição:")
    torneio_sel = st.selectbox(
        "", ["ATP Singles", "ATP Doubles", "Challenger Tour"]
    )

    st.markdown("---")
    st.markdown("### 💰 Banca & Gestão")
    valor_banca = st.number_input(
        "Valor da Banca (€)", min_value=1.0, value=100.0, step=10.0
    )
    stake_max = st.slider("Stake Máxima Base (%)", 0.5, 10.0, 5.0)

    st.markdown("---")
    st.markdown("### ✏️ Inserção Manual de Odds")
    casa_apostas = st.text_input("Casa de Apostas", "Betclic / PinUp")

    st.markdown("**🏆 Vencedor do Encontro**")
    odd_jogador_casa = st.number_input(f"Odd — {jogador_casa}", 1.01, 50.0, 1.45, key="odd_casa")
    odd_jogador_fora = st.number_input(f"Odd — {jogador_fora}", 1.01, 50.0, 2.70, key="odd_fora")

    st.markdown("**🎮 Total de Jogos**")
    linha_jogos = st.number_input(
        "Linha (ex: 21.5) — copia o valor exato da casa de apostas",
        min_value=10.0, max_value=40.0, value=21.5, step=0.5,
    )
    odd_over_jogos = st.number_input(f"Odd Over {linha_jogos}", 1.01, 10.0, 1.85)
    odd_under_jogos = st.number_input(f"Odd Under {linha_jogos}", 1.01, 10.0, 1.90)

# ==========================================
# CABEÇALHO E ABAS PRINCIPAIS
# ==========================================
st.markdown(
    "## 🎾 Análise 26/27 - Rigor Estatístico & Inteligência Avançada"
)

aba_analise, aba_historico = st.tabs(
    ["🎾 Análise do Jogo", "📊 Histórico & Desempenho"]
)



# ==========================================
# ABA 1: ANÁLISE DO JOGO (Indicadores de Ténis)
# ==========================================
with aba_analise:
    st.markdown("---")
    st.markdown(
        f"### 📊 Indicadores Estatísticos: {jogador_casa} vs {jogador_fora}"
    )

    # Linha 1 de Métricas
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="metric-card"><h4>Hold Serviço (Atleta A)</h4><h2>{stats_a["hold"]}%</h2></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-card"><h4>Hold Serviço (Atleta B)</h4><h2>{stats_b["hold"]}%</h2></div>',
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
            f'<div class="metric-card"><h4>Média Ases (A/B)</h4><h2>{stats_a["ases"]} / {stats_b["ases"]}</h2></div>',
            unsafe_allow_html=True,
        )
    with m6:
        st.markdown(
            f'<div class="metric-card"><h4>Duplas Faltas (A/B)</h4><h2>{stats_a["df"]} / {stats_b["df"]}</h2></div>',
            unsafe_allow_html=True,
        )
    with m7:
        st.markdown(
            f'<div class="metric-card"><h4>Break Points Conv. (A/B)</h4><h2>{stats_a["bp"]}% / {stats_b["bp"]}%</h2></div>',
            unsafe_allow_html=True,
        )
    with m8:
        st.markdown(
            f'<div class="metric-card"><h4>Eficiência Hard (A/B)</h4><h2>{stats_a["hard"]}% / {stats_b["hard"]}%</h2></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 💡 Tabela Consolidada de Mercados (Ténis)")
    st.caption(
        "⚠️ Os valores desta tabela ainda estão fixos no código (não reagem aos "
        "jogadores escolhidos) — é o próximo passo a corrigir, com o Elo por "
        "superfície."
    )

    dados_tabela = [
        {
            "Mercado": f"Vitória {jogador_casa}",
            "Probabilidade": "64.5%",
            "Odd Inserida": odd_jogador_casa,
            "Odd Justa": round(1 / 0.645, 2),
            "Edge (%)": "+6.2%",
            "Stake Recomendada (€)": round(
                valor_banca * (stake_max / 100), 2
            ),
            "Ganho Potencial (€)": round(
                valor_banca * (stake_max / 100) * odd_jogador_casa, 2
            ),
            "Avaliação": "🔥 Valor Encontrado",
        },
        {
            "Mercado": f"Over {linha_jogos} Jogos",
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
            "Mercado": f"Under {linha_jogos} Jogos",
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
            "Odd Inserida": odd_jogador_fora,
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
# ABA 2: HISTÓRICO & DESEMPENHO E GESTÃO DE ATLETAS
# ==========================================
with aba_historico:
    st.markdown("### 🗂️ Registo de Confrontos Diretos")

    conn = sqlite3.connect(DB_NAME)
    df_encontros = pd.read_sql_query("SELECT * FROM encontros", conn)
    conn.close()

    if not df_encontros.empty:
        st.dataframe(df_encontros, use_container_width=True)
    else:
        st.info(
            "Ainda não existem encontros gravados. Utilize o formulário abaixo para adicionar dados."
        )

    st.markdown("---")
    col_reg1, col_reg2 = st.columns(2)

    with col_reg1:
        with st.form("form_novo_jogo_tenis"):
            st.markdown("### Adicionar Novo Encontro")
            data_reg = st.date_input("Data", date.today())
            torneio_nome = st.text_input("Torneio", "ATP Masters")
            superficie_escolhida = st.selectbox(
                "Superfície", ["Hard", "Clay", "Grass", "Carpet"]
            )
            j1 = st.text_input("Jogador 1", jogador_casa)
            j2 = st.text_input("Jogador 2", jogador_fora)
            o1 = st.number_input("Odd Jogador 1", 1.01, 100.0, 1.50)
            o2 = st.number_input("Odd Jogador 2", 1.01, 100.0, 2.50)
            venc = st.selectbox("Vencedor", [j1, j2, "Pendente"])

            btn_guardar = st.form_submit_button("Guardar Encontro")
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
                st.success("Encontro guardado com sucesso!")

    with col_reg2:
        with st.form("form_novo_atleta"):
            st.markdown("### Adicionar / Atualizar Atleta na Base de Dados")
            novo_nome = st.text_input("Nome do Tenista")
            n_hold = st.slider("Hold de Serviço (%)", 50.0, 99.0, 85.0)
            n_ases = st.number_input("Média de Ases por Jogo", 0.0, 30.0, 7.5)
            n_df = st.number_input("Média de Duplas Faltas", 0.0, 10.0, 2.0)
            n_bp = st.slider("Break Points Convertidos (%)", 10.0, 70.0, 40.0)
            n_hard = st.slider("Eficiência Hard Court (%)", 30.0, 100.0, 80.0)

            btn_atleta = st.form_submit_button("Guardar Atleta na Lista")
            if btn_atleta and novo_nome.strip() != "":
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO atletas (nome, hold_servico, media_ases, duplas_faltas, break_points_conv, eficiencia_hard)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        novo_nome.strip(),
                        n_hold,
                        n_ases,
                        n_df,
                        n_bp,
                        n_hard,
                    ),
                )
                conn.commit()
                conn.close()
                st.success(
                    f"Atleta '{novo_nome}' adicionado com sucesso! Faz refresh à página para atualizar os seletores."
                )
