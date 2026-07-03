import streamlit as st
import anthropic
import json
import base64

# Configuração da página
st.set_page_config(page_title="Calculadora de Banco de Horas - PP&C", page_icon="💰", layout="centered")

# Estilização personalizada para ficar parecido com o layout moderno
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

# Caixa de informações da empresa
st.markdown("""
<div class='info-box'>
    <strong>Período Quadrimestral:</strong> 01/04/2026 a 31/07/2026<br>
    <strong>Regra de Cálculo:</strong> Até 2h (60%) | Acima de 2h (80%) | Sábado/Dom/Feriado (100%)
</div>
""", unsafe_allow_html=True)

# Inputs do usuário
gross_salary = st.number_input("Salário Bruto Mensal (R$)", min_value=0.0, step=0.01, help="Informe seu salário base sem descontos.")
uploaded_file = st.file_uploader("Upload do Espelho de Ponto (PDF)", type=["pdf"])

if gross_salary > 0 and uploaded_file is not None:
    if st.button("🚀 Calcular Banco de Horas", use_container_width=True):
        with st.spinner("Analisando o espelho de ponto com IA..."):
            try:
                # 1. Puxa a chave de forma segura das configurações do Streamlit
                if "ANTHROPIC_API_KEY" not in st.secrets:
                    st.error("Chave API da Anthropic não configurada nos Secrets do Streamlit.")
                    st.stop()
                
                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                
                # 2. Converte o PDF enviado para Base64
                file_bytes = uploaded_file.read()
                base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
                
                # 3. Prompt para extração dos dados
                prompt = """Analise este espelho de ponto e extraia APENAS os valores de horas do banco de horas em JSON.
                Procure pela seção "Banco de horas: mensal" e extraia:
                - H. Extra 60% (horas com acréscimo de 60%)
                - H.E. Extra 80% (horas com acréscimo de 80%)
                - H.E. Extraordin 100% ou horas em sábado/domingo/feriado (acréscimo de 100%)

                IMPORTANTE: Converta o formato HH:MM para decimal (exemplo: 2:30 = 2.5 horas)

                Responda APENAS com JSON neste formato, sem textos antes ou depois:
                {
                  "hours_60": número_decimal,
                  "hours_80": número_decimal,
                  "hours_100": número_decimal,
                  "period": "descrição do período (exemplo: 'Maio/2026')"
                }"""
                
                # 4. Chamada da API usando o modelo correto
                message = client.messages.create(
                    model="claude-3-5-sonnet-latest",
                    max_tokens=1000,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "document",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "application/pdf",
                                        "data": base64_pdf
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                )
                
                # 5. Processando a resposta da IA
                response_text = message.content[0].text.strip()
                result = json.loads(response_text)
                
                # 6. Cálculos de negócio (Regras PP&C)
                hourly_rate = gross_salary / 176
                
                hours60 = float(result.get("hours_60", 0))
                hours80 = float(result.get("hours_80", 0))
                hours100 = float(result.get("hours_100", 0))
                period = result.get("period", "Não identificado")
                
                # Ajuste de limite de 2h para 60%
                if hours60 > 2:
                    excess = hours60 - 2
                    hours80 += excess
                    hours60 = 2
                    
                val_60 = hours60 * hourly_rate * 1.60
                val_80 = hours80 * hourly_rate * 1.80
                val_100 = hours100 * hourly_rate * 2.00
                total_geral = val_60 + val_80 + val_100
                
                # 7. Exibição dos Resultados na Tela
                st.success("✅ Cálculo realizado com sucesso!")
                st.subheader(f"Resumo do Cálculo - Período: {period}")
                st.metric(label="Valor Total Estimado a Receber", value=f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Horas 60%", f"{hours60}h", f"R$ {val_60:.2f}")
                with col2:
                    st.metric("Horas 80%", f"{hours80}h", f"R$ {val_80:.2f}")
                with col3:
                    st.metric("Horas 100%", f"{hours100}h", f"R$ {val_100:.2f}")
                    
                st.info(f"💡 Valor da sua hora base calculada: R$ {hourly_rate:.2f}")
                
            except Exception as e:
                st.error(f"Erro ao processar o documento: {e}")

st.markdown("""
<hr><p style='text-align: center; font-size: 11px; color: #999;'>
⚠️ Este é um cálculo estimado. A PP&C deve confirmar e processar o pagamento via RH.
</p>
""", unsafe_allow_html=True)