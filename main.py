import numpy as np
import scipy.stats as stats
import streamlit as st

# --- Configuração da Página ---
st.set_page_config(
    page_title="Modelo de Value Bets & Poisson",
    page_icon="⚽",
    layout="wide",
)

st.title("🎯 Calculadora de Value Bets & Stake Dinâmica")
st.markdown(
    "Insere as estatísticas e as odds da tua Casa de Apostas para calcular o Edge (+EV)."
)

# --- Barra Lateral para Inputs do Jogo ---
st.sidebar.header("⚙️ Parâmetros do Jogo")

# Inputs de xG (Golos Esperados)
xg_casa = st.sidebar.number_input("xG Equipas da Casa", 0.0, 5.0, 1.65, 0.05)
xg_fora = st.sidebar.number_input("xG Equipas de Fora", 0.0, 5.0, 1.15, 0.05)

# Média de Cantos Esperados
cantos_esperados = st.sidebar.number_input(
    "Média Total de Cantos Esperados", 0.0, 20.0, 9.5, 0.5
)

# --- Cálculos Estatísticos (Modelo de Poisson) ---
lambda_golos = xg_casa + xg_fora

# Probabilidades de Golos (Over / Under)
prob_over_15 = 1.0 - stats.poisson.cdf(1, lambda_golos)
prob_over_25 = 1.0 - stats.poisson.cdf(2, lambda_golos)
prob_over_35 = 1.0 - stats.poisson.cdf(3, lambda_golos)
prob_under_55 = stats.poisson.cdf(5, lambda_golos)  # Novo Under 5.5

# Probabilidades de Cantos (Over / Under com aproximação de Poisson)
prob_over_cantos = 1.0 - stats.poisson.cdf(
    7, cantos_esperados
)  # Over 7.5 Cantos
prob_under_cantos = stats.poisson.cdf(14, cantos_esperados)  # Novo Under 14.5

# Conversão em Odds Justas
odd_justa_15 = 1.0 / prob_over_15 if prob_over_15 > 0 else 99.0
odd_justa_25 = 1.0 / prob_over_25 if prob_over_25 > 0 else 99.0
odd_justa_35 = 1.0 / prob_over_35 if prob_over_35 > 0 else 99.0
odd_justa_u55 = 1.0 / prob_under_55 if prob_under_55 > 0 else 99.0
odd_justa_cantos = 1.0 / prob_over_cantos if prob_over_cantos > 0 else 99.0
odd_justa_u145 = 1.0 / prob_under_cantos if prob_under_cantos > 0 else 99.0

# --- Secção Principal: Inputs de Odds da Casa de Apostas ---
st.markdown("### 📋 Insere as Odds da tua Casa de Apostas")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    odd_casa_o15 = st.number_input(
        "Odd Casa (Over 1.5)",
        1.01,
        50.0,
        float(np.clip(round(odd_justa_15 + 0.1, 2), 1.01, 50.0)),
    )
with col2:
    odd_casa_o25 = st.number_input(
        "Odd Casa (Over 2.5)",
        1.01,
        50.0,
        float(np.clip(round(odd_justa_25 + 0.1, 2), 1.01, 50.0)),
    )
with col3:
    odd_casa_o35 = st.number_input(
        "Odd Casa (Over 3.5)",
        1.01,
        50.0,
        float(np.clip(round(odd_justa_35 + 0.1, 2), 1.01, 50.0)),
    )
with col4:
    odd_casa_u55 = st.number_input(
        "Odd Casa (Under 5.5)",
        1.01,
        50.0,
        float(np.clip(round(odd_justa_u55 + 0.1, 2), 1.01, 50.0)),
    )
with col5:
    odd_casa_cantos = st.number_input(
        "Odd Casa (Cantos 7.5)",
        1.01,
        50.0,
        float(np.clip(round(odd_justa_cantos + 0.1, 2), 1.01, 50.0)),
    )
with col6:
    odd_casa_u145 = st.number_input(
        "Odd Casa (Cantos 14.5)",
        1.01,
        50.0,
        float(np.clip(round(odd_justa_u145 + 0.1, 2), 1.01, 50.0)),
    )


# Função de cálculo de Value Bet e Stake Dinâmica
def avaliar_mercado(prob, odd_justa, odd_casa):
  edge = (odd_casa / odd_justa) - 1.0
  if edge > 0:
    # Stake base proporcional ao edge (exemplo de lógica dinâmica)
    stake = round(max(1.0, edge * 30), 2)
    recomendacion = "🔥 VALOR"
  else:
    stake = 0.00
    recomendacion = "❌ Sem Valor"
  return edge * 100, stake, recomendacion


# Compilação dos dados para a tabela
mercados = [
    {
        "Mercado": "Over 1.5 Golos",
        "Prob": f"{prob_over_15*100:.1f}%",
        "Odd Justa": round(odd_justa_15, 2),
        "Odd Casa": odd_casa_o15,
        *zip(
            ["Edge", "Stake", "Rec"], avaliar_mercado(prob_over_15, odd_justa_15, odd_casa_o15)
        ),
    },
    {
        "Mercado": "Over 2.5 Golos",
        "Prob": f"{prob_over_25*100:.1f}%",
        "Odd Justa": round(odd_justa_25, 2),
        "Odd Casa": odd_casa_o25,
        *zip(
            ["Edge", "Stake", "Rec"], avaliar_mercado(prob_over_25, odd_justa_25, odd_casa_o25)
        ),
    },
    {
        "Mercado": "Over 3.5 Golos",
        "Prob": f"{prob_over_35*100:.1f}%",
        "Odd Justa": round(odd_justa_35, 2),
        "Odd Casa": odd_casa_o35,
        *zip(
            ["Edge", "Stake", "Rec"], avaliar_mercado(prob_over_35, odd_justa_35, odd_casa_o35)
        ),
    },
    {
        "Mercado": "Under 5.5 Golos",
        "Prob": f"{prob_under_55*100:.1f}%",
        "Odd Justa": round(odd_justa_u55, 2),
        "Odd Casa": odd_casa_u55,
        *zip(
            ["Edge", "Stake", "Rec"], avaliar_mercado(prob_under_55, odd_justa_u55, odd_casa_u55)
        ),
    },
    {
        "Mercado": "Over 7.5 Cantos",
        "Prob": f"{prob_over_cantos*100:.1f}%",
        "Odd Justa": round(odd_justa_cantos, 2),
        "Odd Casa": odd_casa_cantos,
        *zip(
            ["Edge", "Stake", "Rec"],
            avaliar_mercado(prob_over_cantos, odd_justa_cantos, odd_casa_cantos),
        ),
    },
    {
        "Mercado": "Under 14.5 Cantos",
        "Prob": f"{prob_under_cantos*100:.1f}%",
        "Odd Justa": round(odd_justa_u145, 2),
        "Odd Casa": odd_casa_u145,
        *zip(
            ["Edge", "Stake", "Rec"],
            avaliar_mercado(prob_under_cantos, odd_justa_u145, odd_casa_u145),
        ),
    },
]

# --- Exibição da Tabela Final ---
st.markdown("### 📊 Tabela Comparativa de Value Bets")

import pandas as pd

df = pd.DataFrame(mercados)
# Renomear colunas descompactadas do zip
df.columns = [
    "Mercado Base",
    "Probabilidade",
    "Odd Justa (Modelo)",
    "Odd Casa de Apostas",
    "Valor (+EV / Edge)",
    "Aposta Dinâmica",
    "Recomendação",
]

# Formatação visual do Edge em percentagem
df["Valor (+EV / Edge)"] = df["Valor (+EV / Edge)"].apply(lambda x: f"+{x:.2f}%" if x > 0 else f"{x:.2f}%")
df["Aposta Dinâmica"] = df["Aposta Dinâmica"].apply(lambda x: f"{x:.2f} €")

st.dataframe(df, use_container_width=True, hide_index=True)
