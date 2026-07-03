import streamlit as st
import re
from pypdf import PdfReader

# Configuração da página
st.set_page_config(page_title="Calculadora de Banco de Horas - PP&C", page_icon="💰", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .title { color: #333333; text-align: center; font-weight: bold; }
    .subtitle { color: #666666; text-align: center; font-size: 14px; margin-bottom: 20px; }
    .info-box { background-color: #e8ecf7; padding: 15px; border-left: 5px solid #667eea; border-radius: 4px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>💰 Calculadora de Banco de Horas</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>PP&C SERVIÇOS DE BPO LTDA</p>", unsafe_allow_html=True)

st.markdown("""
<div class='info-box'>
    <strong>Período Quadrimestral:</strong> 01/04/2026 a 31/07/2026<br>
    <strong>Regra de Cálculo:</strong> Até 2h (60%) | Acima de 2h (80%) | Sábado/Dom/Feriado (100%)
</div>
""", unsafe_allow_html=True)

# Inputs
gross_salary = st.number_input("Salário Bruto Mensal (R$)", min_value=0.0, step=0.01, help="Informe seu salário base sem descontos.")
uploaded_file = st.file_uploader("Upload do Espelho de Ponto (PDF)", type=["pdf"])

def convert_hhmm_to_decimal(time_str):
    """Converte strings no formato HH:MM ou H:MM para decimal (ex: 02:30 -> 2.5)"""
    if not time_str or time_str.strip() == "":
        return 0.0
    try:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        return hours + (minutes / 60.0)
    except:
        return 0.0

def extrair_dados_pdf(file):
    """Lê o texto do PDF e busca os valores de horas usando expressões regulares"""
    reader = PdfReader(file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    # Dicionário padrão de retorno
    dados = {"hours_60": 0.0, "hours_80": 0.0, "hours_100": 0.0, "period": "Não identificado"}
    
    # Tenta capturar o período/mês de referência do espelho
    match_periodo = re.search(r"Período:\s*(\d{2}/\d{2}/\d{4})\s*a\s*(\d{2}/\d{2}/\d{4})", full_text, re.IGNORECASE)
    if match_periodo:
        dados["period"] = f"{match_periodo.group(1)} a {match_periodo.group(2)}"
    
    # Procura pelos padrões clássicos de banco de horas no texto
    # Captura formatos como "H. Extra 60% 02:30" ou variações comuns
    match_60 = re.search(r"(?:Extra|H\.E\.|H\.\s*Extra)\s*60%\s*.*?(\d{1,2}:\d{2})", full_text, re.IGNORECASE)
    match_80 = re.search(r"(?:Extra|H\.E\.|H\.\s*Extra)\s*80%\s*.*?(\d{1,2}:\d{2})", full_text, re.IGNORECASE)
    match_100 = re.search(r"(?:Extra|H\.E\.|H\.\s*Extra|Feriado)\s*100%\s*.*?(\d{1,2}:\d{2})", full_text, re.IGNORECASE)
    
    if match_60:
        dados["hours_60"] = convert_hhmm_to_decimal(match_60.group(1))
    if match_80:
        dados["hours_80"] = convert_hhmm_to_decimal(match_80.group(1))
    if match_100:
        dados["hours_100"] = convert_hhmm_to_decimal(match_100.group(1))
        
    return dados

if gross_salary > 0 and uploaded_file is not None:
    if st.button("🚀 Calcular Banco de Horas", use_container_width=True):
        with st.spinner("Processando o arquivo PDF localmente de forma gratuita..."):
            try:
                # Extração local via código puro
                result = extrair_dados_pdf(uploaded_file)
                
                # Regras de negócio
                hourly_rate = gross_salary / 176
                
                hours60 = result["hours_60"]
                hours80 = result["hours_80"]
                hours100 = result["hours_100"]
                period = result["period"]
                
                # Aplica a regra de transbordo da PP&C (máximo de 2 horas a 60%)
                if hours60 > 2:
                    excess = hours60 - 2
                    hours80 += excess
                    hours60 = 2
                
                val_60 = hours60 * hourly_rate * 1.60
                val_80 = hours80 * hourly_rate * 1.80
                val_100 = hours100 * hourly_rate * 2.00
                total_geral = val_60 + val_80 + val_100
                
                # Exibição
                st.success("✅ Cálculo efetuado com sucesso!")
                st.subheader(f"Resumo do Cálculo")
                st.caption(f"Período do Ponto: {period}")
                st.metric(label="Valor Total Estimado a Receber", value=f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Horas 60%", f"{hours60:.2f}h", f"R$ {val_60:.2f}")
                with col2:
                    st.metric("Horas 80%", f"{hours80:.2f}h", f"R$ {val_80:.2f}")
                with col3:
                    st.metric("Horas 100%", f"{hours100:.2f}h", f"R$ {val_100:.2f}")
                    
                st.info(f"💡 Base de Cálculo: Valor da hora normal = R$ {hourly_rate:.2f}")
                
            except Exception as e:
                st.error(f"Erro ao processar o layout do PDF: {e}. Certifique-se de que é um PDF contendo texto legível.")

st.markdown("""
<hr><p style='text-align: center; font-size: 11px; color: #999;'>
⚠️ Este é um cálculo estimado. A PP&C deve confirmar e processar o pagamento via RH.
</p>
""", unsafe_allow_html=True)
