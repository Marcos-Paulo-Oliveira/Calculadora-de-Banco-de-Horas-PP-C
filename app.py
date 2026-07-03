import streamlit as st

# Configuração da página
st.set_page_config(page_title="Calculadora de Banco de Horas - PP&C", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .title { color: #333333; text-align: center; font-weight: bold; }
    .subtitle { color: #666666; text-align: center; font-size: 14px; margin-bottom: 20px; }
    .info-box { background-color: #e8ecf7; padding: 15px; border-left: 5px solid #667eea; border-radius: 4px; margin-bottom: 20px; }
    .alert-box { background-color: #fff3cd; padding: 15px; border-left: 5px solid #ffc107; border-radius: 4px; margin-bottom: 25px; color: #856404; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>💰 Calculadora de Banco de Horas</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>PP&C SERVIÇOS DE BPO LTDA</p>", unsafe_allow_html=True)

# Caixa de Contexto do Negócio
st.markdown("""
<div class='info-box'>
    <strong>Regra de Cálculo PP&C:</strong> Até 2h (60%) | Acima de 2h (80%) | Sábado/Dom/Feriado (100%) <br>
    <em>Base de Divisor Mensal: 176 horas.</em>
</div>
""", unsafe_allow_html=True)

# ALERTA INTUITIVO SOBRE O ESPELHO
st.markdown("""
<div class='alert-box'>
    <strong>📢 ATENÇÃO AO PREENCHER:</strong><br>
    Como o objetivo é calcular o valor total que você tem para <strong>receber</strong>, não olhe o valor do mês! 
    Preencha os campos abaixo utilizando o <strong>SALDO TOTAL ACUMULADO (os valores que ficam ENTRE PARÊNTESES <code>(HH:MM)</code></strong> na parte inferior de cada quadradinho do seu espelho).
</div>
""", unsafe_allow_html=True)

# Entrada do Salário
gross_salary = st.number_input("Salário Bruto Mensal (R$)", min_value=0.0, step=0.01, help="Informe seu salário base sem descontos.")

st.subheader("⏱️ Informe o Saldo Acumulado (Entre Parênteses no Espelho)")
st.caption("Digite no formato HH:MM. Se não possuir saldo em alguma categoria, deixe 00:00.")

# Entradas das Horas com exemplos baseados no seu espelho real
col_input1, col_input2, col_input3 = st.columns(3)

with col_input1:
    time_60 = st.text_input("Saldo Acumulado 60%", value="25:44", help="Olhe o valor entre parênteses na coluna 'H. Extra 60%'")
with col_input2:
    time_80 = st.text_input("Saldo Acumulado 80%", value="04:32", help="Olhe o valor entre parênteses na coluna 'H.E. Extra 80%' ou 'H.E. Not 80%'")
with col_input3:
    time_100 = st.text_input("Saldo Acumulado 100%", value="00:00", help="Olhe o valor entre parênteses na coluna 'H.E. Extraord 100%'")

def convert_hhmm_to_decimal(time_str):
    """Valida a string e converte HH:MM para decimal (ex: 02:30 -> 2.5)"""
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

if gross_salary > 0:
    if st.button("🚀 Calcular Valores a Receber", use_container_width=True):
        # Conversão dos inputs
        h60_dec = convert_hhmm_to_decimal(time_60)
        h80_dec = convert_hhmm_to_decimal(time_80)
        h100_dec = convert_hhmm_to_decimal(time_100)
        
        # Validação simples de formato
        if h60_dec is None or h80_dec is None or h100_dec is None:
            st.error("⚠️ Por favor, digite as horas no formato correto de dois pontos (HH:MM). Exemplo: 25:44")
        else:
            # Regras de Negócio (Base 176 horas)
            hourly_rate = gross_salary / 176
            
            # Guarda os valores originais informados pelo usuário para exibir no resumo
            orig_time_60 = time_60
            orig_time_80 = time_80
            
            # Aplica a regra de transbordo caso as horas de 60% passem de 2h
            # Como estamos falando do saldo TOTAL acumulado, as primeiras 2h vão para 60% e o resto vai para a faixa de 80%
            if h60_dec > 2:
                excess = h60_dec - 2
                h80_dec += excess
                h60_dec = 2
                # Ajusta a exibição para mostrar que houve o transbordo das horas
                orig_time_60 = "2:00"
                orig_time_80 = f"{h80_dec:.2f}h equiv."
            
            # Cálculos dos valores financeiros
            val_60 = h60_dec * hourly_rate * 1.60
            val_80 = h80_dec * hourly_rate * 1.80
            val_100 = h100_dec * hourly_rate * 2.00
            total_geral = val_60 + val_80 + val_100
            
            # Exibição dos Resultados
            st.success("✅ Cálculo realizado com sucesso!")
            st.metric(label="Valor Total Estimado a Receber", value=f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Pago a 60%", f"{orig_time_60}h", f"R$ {val_60:.2f}")
            with col2:
                st.metric("Total Pago a 80%", f"{orig_time_80}", f"R$ {val_80:.2f}")
            with col3:
                st.metric("Total Pago a 100%", f"{time_100}h", f"R$ {val_100:.2f}")
                
            st.info(f"💡 Base de Cálculo: Valor da sua hora normal = R$ {hourly_rate:.2f}")

st.markdown("""
<hr><p style='text-align: center; font-size: 11px; color: #999;'>
⚠️ Este é um cálculo estimado baseado nas regras informadas. Confirme os valores oficiais junto ao departamento de RH.
</p>
""", unsafe_allow_html=True)
