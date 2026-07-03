import streamlit as st

# Configuração da página e estilo minimalista
st.set_page_config(page_title="Calculadora Banco de Horas", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h2 { color: #2D3748; font-weight: 700; margin-top: 10px; }
    .stButton>button { background-color: #4A5568; color: white; font-weight: bold; border-radius: 6px; width: 100%; }
    .stButton>button:hover { background-color: #2D3748; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("💰 Calculadora de Banco de Horas")
st.caption("PP&C SERVIÇOS DE BPO LTDA")
st.hr()

# Inputs principais
gross_salary = st.number_input("Salário Bruto Mensal (R$)", min_value=0.0, step=100.0, value=0.0)

st.subheader("⏱️ Saldo Acumulado (Valor entre parênteses)")

# Organização dos campos lado a lado
col1, col2, col3 = st.columns(3)
with col1:
    time_60 = st.text_input("Saldo 60%", value="25:44")
with col2:
    time_80 = st.text_input("Saldo 80%", value="04:32")
with col3:
    time_100 = st.text_input("Saldo 100%", value="00:00")

def convert_hhmm_to_decimal(time_str):
    """Converte formato HH:MM para decimal (ex: 02:30 -> 2.5)"""
    try:
        time_str = time_str.strip()
        if ":" not in time_str:
            return 0.0
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        if minutes >= 60 or hours < 0 or minutes < 0:
            return None
        return hours + (minutes / 60.0)
    except:
        return None

st.markdown("<br>", unsafe_allow_html=True)

# Só executa a validação e mostra o botão se o salário for maior que zero
if gross_salary > 0:
    if st.button("Calcular Total a Receber"):
        h60_dec = convert_hhmm_to_decimal(time_60)
        h80_dec = convert_hhmm_to_decimal(time_80)
        h100_dec = convert_hhmm_to_decimal(time_100)
        
        if h60_dec is None or h80_dec is None or h100_dec is None:
            st.error("Formato de hora inválido. Use o padrão HH:MM (Ex: 25:44)")
        else:
            # Regras de Negócio (Base 176 horas)
            hourly_rate = gross_salary / 176
            
            # Variáveis para exibição
            display_60 = time_60
            display_80 = f"{h80_dec:.2f}h"
            
            # Regra de transbordo: Limite de 2h na faixa de 60%
            if h60_dec > 2:
                excess = h60_dec - 2
                h80_dec += excess
                h60_dec = 2
                display_60 = "2:00"
                display_80 = f"{h80_dec:.2f}h"
            
            # Cálculos financeiros
            val_60 = h60_dec * hourly_rate * 1.60
            val_80 = h80_dec * hourly_rate * 1.80
            val_100 = h100_dec * hourly_rate * 2.00
            total_geral = val_60 + val_80 + val_100
            
            # Bloco de resultados limpo
            st.hr()
            st.metric(label="Valor Total Estimado a Receber", value=f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
            res_col1, res_col2, res_col3 = st.columns(3)
            with res_col1:
                st.metric("Total 60%", display_60, f"R$ {val_60:.2f}")
            with res_col2:
                st.metric("Total 80%", display_80, f"R$ {val_80:.2f}")
            with res_col3:
                st.metric("Total 100%", time_100, f"R$ {val_100:.2f}")
            
            st.caption(f"Valor calculado da hora normal: R$ {hourly_rate:.2f}")
else:
    st.info("💡 Insira o valor do seu Salário Bruto para liberar o cálculo.")
