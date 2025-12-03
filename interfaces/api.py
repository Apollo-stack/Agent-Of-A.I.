from flask import Flask, request, jsonify
import sys
import os
import requests
from dotenv import load_dotenv
# 1. O Import novo da Twilio fica aqui em cima
from twilio.twiml.messaging_response import MessagingResponse  # type: ignore

# Configurações
load_dotenv()
PIPEDRIVE_TOKEN = os.getenv("PIPEDRIVE_TOKEN")
PIPEDRIVE_DOMAIN = os.getenv("PIPEDRIVE_DOMAIN")

app = Flask(__name__)

# Caminhos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.agent import AgentIA

print("Carregando IA...")
try:
    minha_ia = AgentIA(modelo="gemini-2.5-flash")
    # Persona padrão (para o Pipedrive)
    minha_ia.definir_persona("Você é um gerente de vendas sênior. Dê dicas táticas e curtas.")
    print("✅ IA Pronta!")
except Exception as e:
    print(f"❌ Erro na IA: {e}")

def salvar_nota_pipedrive(deal_id, conteudo):
    if not PIPEDRIVE_TOKEN or not PIPEDRIVE_DOMAIN:
        return
    url = f"https://{PIPEDRIVE_DOMAIN}.pipedrive.com/api/v1/notes?api_token={PIPEDRIVE_TOKEN}"
    payload = {
        "deal_id": deal_id,
        "content": f"🤖 <b>Análise da IA:</b><br>{conteudo.replace('\n', '<br>')}"
    }
    requests.post(url, json=payload)

# --- ROTA DO PIPEDRIVE (Mantida igual) ---
@app.route('/analisar_lead', methods=['POST'])
def receber_pedido():
    dados = request.json
    info_negocio = dados.get('data') or dados.get('current')

    if info_negocio:
        deal_id = info_negocio.get('id')
        nome_cliente = info_negocio.get('title')
        valor = info_negocio.get('value', 0)
        observacoes = f"Cliente: {nome_cliente}. Valor: {valor}"
        
        # Garante que volta a ser Vendedor antes de responder o Pipedrive
        minha_ia.definir_persona("Você é um gerente de vendas sênior. Dê dicas táticas.")
        
        resposta = minha_ia.pensar(f"Analise: {nome_cliente}", contexto_extra=observacoes)
        salvar_nota_pipedrive(deal_id, resposta)
        return jsonify({"status": "sucesso", "dica": resposta})
    
    return jsonify({"erro": "sem dados"}), 400

# --- NOVA ROTA DO WHATSAPP (MODO JARVIS) ---
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    # 1. Pega a mensagem do Zap
    mensagem_usuario = request.form.get('Body')
    remetente = request.form.get('From')
    
    print(f"📩 Jarvis recebeu: {mensagem_usuario}")

    # 2. ATIVA O MODO JARVIS AQUI
    # Essa é a parte que muda a personalidade
    minha_ia.definir_persona(
        "Você é o J.A.R.V.I.S., uma IA assistente pessoal avançada. "
        "Seja eficiente, levemente sarcástico, chame o usuário de 'Senhor' e use emojis futuristas (🤖, 🚀, ⚡)."
    )

    # 3. Pensa e Responde
    resposta_ia = minha_ia.pensar(mensagem_usuario)

    # 4. Formata para o WhatsApp
    resp = MessagingResponse()
    resp.message(resposta_ia)

    return str(resp)

if __name__ == '__main__':
    app.run(port=5000)