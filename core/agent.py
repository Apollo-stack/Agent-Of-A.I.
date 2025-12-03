import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

class AgentIA:
    def __init__(self, modelo="gemini-pro"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("ERRO: A chave GOOGLE_API_KEY não foi encontrada no arquivo .env")

        self.llm = ChatGoogleGenerativeAI(
            model=modelo,
            google_api_key=api_key,
            temperature=0.7
        )
        self.system_message = SystemMessage(content="Você é um assistente útil.")

    def definir_persona(self, texto_persona):
        self.system_message = SystemMessage(content=texto_persona)

    def pensar(self, pergunta_usuario, contexto_extra=None):
        # Começa com a persona (Mensagem de Sistema - Posição 0)
        messages = [self.system_message]

        # A CORREÇÃO ESTÁ AQUI:
        # Em vez de criar uma nova SystemMessage (que o Gemini reclama na posição 1),
        # nós juntamos o contexto dentro da mensagem do usuário.
        
        texto_final = pergunta_usuario
        
        if contexto_extra:
            texto_final = f"""
            USE AS INFORMAÇÕES ABAIXO COMO CONTEXTO PARA RESPONDER:
            -----------------------------------------
            {contexto_extra}
            -----------------------------------------
            
            PERGUNTA DO USUÁRIO:
            {pergunta_usuario}
            """

        # Adiciona tudo como uma única mensagem humana (Posição 1 Aceita!)
        messages.append(HumanMessage(content=texto_final))

        try:
            resposta = self.llm.invoke(messages)
            return resposta.content
        except Exception as e:
            return f"Ocorreu um erro na IA: {e}"