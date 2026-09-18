import numpy as np
import pandas as pd
import scipy.stats as stats
import streamlit as st

# --- Configuração da Página ---
st.set_page_config(
    page_title="Análise Desportiva 26/27", page_icon="⚽", layout="wide"
)

# --- Barra Lateral (Gestão de Banca, Ligas e Equipas) ---
st.sidebar.markdown("### Selecione a Liga / Competição:")
liga_selecionada = st.sidebar.selectbox(
    "Liga",
    [
        "EN Premier League (Inglaterra)",
        "🇵🇹 Liga Portugal Betclic",
        "🇪🇸 La Liga (Espanha)",
        "🇩🇪 DE Bundesliga (Alemanha)",
        "🇮🇹 Serie A (Itália)",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 Gestão de Banca")
banca_total = st.sidebar.number_input(
    "Valor da Banca (€)", 10.0, 10000.0, 100.0, 10.0
)
stake_max_base = st.sidebar.slider("Stake Máxima Base (%)", 0.5, 10.0, 3.0, 0.5)

st.sidebar.markdown(
    """
    <div style='background-color: #0e1117; padding: 10px; border-radius: 5px; border: 1px solid #1f2937;'>
    <small>O valor a apostar agora varia dinamicamente consoante a força do Edge (+EV).</small>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Cabeçalho Principal ---
st.markdown("### ⚽ Análise Desportiva 26/27")
st.markdown(
    "Análise Avançada com Foco em Over/Under Golos & Cantos",
    help="Modelo estatístico Poisson",
)

# Seleção de Equipas
col_eq1, col_eq2 = st.columns(2)
with col_eq1:
  equipa_casa = st.selectbox(
      "Equipa da Casa", ["Manchester City", "FC Porto", "Bayern München", "Sevilla"]
  )
with col_eq2:
  equipa_visitante = st.selectbox(
      "Equipa Visitante", ["Arsenal", "Sporting", "Union Berlin", "Barcelona"]
  )

# Valores simulados de xG e Cantos com base nas equipas (ou inputs ajustáveis)
xg_casa = 1.17
xg_fora = 0.79
lambda_golos = xg_casa + xg_fora
cantos_esperados = 10.3

# --- Métricas Estatísticas em Cartões ---
st.markdown(
    f"### 📊 Análise Estatística: {equipa_casa} vs {equipa_visitante}"
)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Média Esperada (Casa)", f"{xg_casa} golos")
m2.metric("Média Esperada (Fora)", f"{xg_fora} golos")
m3.metric("Golos Totais Esperados", f"{lambda_golos:.2f}")
m4.metric("Média Cantos Esperados", f"{cantos_esperados}")

# --- Cálculos Estatísticos (Poisson) ---
prob_over_15 = 1.0 - stats.poisson.cdf(1, lambda_golos)
prob_over_25 = 1.0 - stats.poisson.cdf(2, lambda_golos)
prob_over_35 = 1.0 - stats.poisson.cdf(3, lambda_golos)
prob_under_55 = stats.poisson.cdf(5, lambda_golos)

prob_over_cantos = 1.0 - stats.poisson.cdf(7, cantos_esperados)
prob_under_cantos = stats.poisson.cdf(14, cantos_esperados)

odd_justa_15 = 1.0 / prob_over_15 if prob_over_15 > 0 else 99.0
odd_justa_25 = 1.0 / prob_over_25 if prob_over_25 > 0 else 99.0
odd_justa_35 = 1.0 / prob_over_35 if prob_over_35 > 0 else 99.0
odd_justa_u55 = 1.0 / prob_under_55 if prob_under_55 > 0 else 99.0
odd_justa_cantos = 1.0 / prob_over_cantos if prob_over_cantos > 0 else 99.0
odd_justa_u145 = 1.0 / prob_under_cantos if prob_under_cantos > 0 else 99.0

# --- Comparador de Value Bets ---
st.markdown("### 🎯 Comparador de Value Bets & Stake Dinâmica")
st.markdown(
    "Insere as Odds da tua Casa de Apostas. A stake em euros ajusta-se"
    " automaticamente de forma inteligente com base na magnitude do Edge (+EV)."
)

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
  odd_casa_o15 = st.number_input(
      "Odd (Over 1.5)",
      1.01,
      50.0,
      float(np.clip(round(odd_justa_15 + 0.1, 2), 1.01, 50.0)),
  )
with c2:
  odd_casa_o25 = st.number_input(
      "Odd (Over 2.5)",
      1.01,
      50.0,
      float(np.clip(round(odd_justa_25 + 0.1, 2), 1.01, 50.0)),
  )
with c3:
  odd_casa_o35 = st.number_input(
      "Odd (Over 3.5)",
      1.01,
      50.0,
      float(np.clip(round(odd_justa_35 + 0.1, 2), 1.01, 50.0)),
  )
with c4:
  odd_casa_u55 = st.number_input(
      "Odd (Under 5.5)",
      1.01,
      50.0,
      float(np.clip(round(odd_justa_u55 + 0.1, 2), 1.01, 50.0)),
  )
with c5:
  odd_casa_cantos = st.number_input(
      "Odd (Cantos 7.5)",
      1.01,
      50.0,
      float(np.clip(round(odd_justa_cantos + 0.1, 2), 1.01, 50.0)),
  )
with c6:
  odd_casa_u145 = st.number_input(
      "Odd (Cantos 14.5)",
      1.01,
      50.0,
      float(np.clip(round(odd_justa_u145 + 0.1, 2), 1.01, 50.0)),
  )


def avaliar_mercado(prob, odd_justa, odd_casa, banca, max_stake_pct):
  edge = (odd_casa / odd_justa) - 1.0
  if edge > 0:
    stake = round(banca * min(max_stake_pct / 100.0, max(0.005, edge * 0.1)), 2)
    recomendacao = "🔥 VALOR"
  else:
    stake = 0.00
    recomendacao = "❌ Sem Valor"
  return edge * 100, stake, recomendacao


res_15 = avaliar_mercado(
    prob_over_15, odd_justa_15, odd_casa_o15, banca_total, stake_max_base
)
res_25 = avaliar_mercado(
    prob_over_25, odd_justa_25, odd_casa_o25, banca_total, stake_max_base
)
res_35 = avaliar_mercado(
    prob_over_35, odd_justa_35, odd_casa_o35, banca_total, stake_max_base
)
res_u55 = avaliar_mercado(
    prob_under_55, odd_justa_u55, odd_casa_u55, banca_total, stake_max_base
)
res_cantos = avaliar_mercado(
    prob_over_cantos,
    odd_justa_cantos,
    odd_casa_cantos,
    banca_total,
    stake_max_base,
)
res_u145 = avaliar_mercado(
    prob_under_cantos, odd_justa_u145, odd_casa_u145, banca_total, stake_max_base
)

mercados = [
    {
        "Mercado Base": "Over 1.5 Golos",
        "Probabilidade": f"{prob_over_15*100:.1f}%",
        "Odd Justa (Modelo)": round(odd_justa_15, 2),
        "Odd Casa de Apostas": odd_casa_o15,
        "Valor (+EV / Edge)": res_15[0],
        "Aposta Dinâmica": res_15[1],
        "Recomendação": res_15[2],
    },
    {
        "Mercado Base": "Over 2.5 Golos",
        "Probabilidade": f"{prob_over_25*100:.1f}%",
        "Odd Justa (Modelo)": round(odd_justa_25, 2),
        "Odd Casa de Apostas": odd_casa_o25,
        "Valor (+EV / Edge)": res_25[0],
        "Aposta Dinâmica": res_25[1],
        "Recomendação": res_25[2],
    },
    {
        "Mercado Base": "Over 3.5 Golos",
        "Probabilidade": f"{prob_over_35*100:.1f}%",
        "Odd Justa (Modelo)": round(odd_justa_35, 2),
        "Odd Casa de Apostas": odd_casa_o35,
        "Valor (+EV / Edge)": res_35[0],
        "Aposta Dinâmica": res_35[1],
        "Recomendação": res_35[2],
    },
    {
        "Mercado Base": "Under 5.5 Golos",
        "Probabilidade": f"{prob_under_55*100:.1f}%",
        "Odd Justa (Modelo)": round(odd_justa_u55, 2),
        "Odd Casa de Apostas": odd_casa_u55,
        "Valor (+EV / Edge)": res_u55[0],
        "Aposta Dinâmica": res_u55[1],
        "Recomendação": res_u55[2],
    },
    {
        "Mercado Base": "Over 7.5 Cantos",
        "Probabilidade": f"{prob_over_cantos*100:.1f}%",
        "Odd Justa (Modelo)": round(odd_justa_cantos, 2),
        "Odd Casa de Apostas": odd_casa_cantos,
        "Valor (+EV / Edge)": res_cantos[0],
        "Aposta Dinâmica": res_cantos[1],
        "Recomendação": res_cantos[2],
    },
    {
        "Mercado Base": "Under 14.5 Cantos",
        "Probabilidade": f"{prob_under_cantos*100:.1f}%",
        "Odd Justa (Modelo)": round(odd_justa_u145, 2),
        "Odd Casa de Apostas": odd_casa_u145,
        "Valor (+EV / Edge)": res_u145[0],
        "Aposta Dinâmica": res_u145[1],
        "Recomendação": res_u145[2],
    },
]

df = pd.DataFrame(mercados)
df["Valor (+EV / Edge)"] = df["Valor (+EV / Edge)"].apply(
    lambda x: f"+{x:.2f}%" if x > 0 else f"{x:.2f}%"
)
df["Aposta Dinâmica"] = df["Aposta Dinâmica"].apply(lambda x: f"{x:.2f} €")

st.dataframe(df, use_container_width=True, hide_index=True)
