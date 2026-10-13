#!/usr/bin/env python3
"""
Chat interactivo continuo con Firby via HTTP.
Mantiene la sesión entre mensajes.
"""
import requests
import json
import sys

FIRBY_URL = "http://localhost:8001"
MASTER_KEY = "firby_master_2026_santiago"

def chat_loop(user_id: str):
    """Loop de conversación interactiva con Firby."""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║         💬 CHAT CONTINUO CON FIRBY v8.0               ║
║         Escribe 'salir' para terminar                   ║
║         Escribe 'nuevo' para nueva sesión                ║
╚══════════════════════════════════════════════════════════╝
""")
    
    session = requests.Session()
    
    # Mensaje inicial
    mensaje_inicial = "Hola, me llegó un link de ti pero no sé qué es esto"
    print(f"👤 TÚ: {mensaje_inicial}")
    
    response = send_message(session, mensaje_inicial, user_id)
    print(f"🤖 FIRBY: {response}")
    
    while True:
        try:
            user_input = input("\n👤 TÚ: ").strip()
            
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("👋 Conversación terminada.")
                break
            
            if user_input.lower() == "nuevo":
                print("🔄 Nueva sesión")
                user_input = "Hola"
            
            if not user_input:
                continue
            
            response = send_message(session, user_input, user_id)
            print(f"🤖 FIRBY: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Chat interrumpido.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def send_message(session, text: str, user_id: str) -> str:
    """Envía mensaje a Firby y retorna respuesta."""
    try:
        resp = session.post(
            f"{FIRBY_URL}/test",
            json={"message": text, "user_id": user_id},
            headers={"X-Master-Key": MASTER_KEY, "Content-Type": "application/json"}
        )
        if resp.status_code != 200:
            return f"Error: {resp.status_code} - {resp.text}"
        
        data = resp.json()
        return data.get("response", data.get("message", str(data)))
    except Exception as e:
        return f"❌ Error de conexión: {e}"

if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else "interactive_lead"
    print(f"🔗 Conectando a Firby en {FIRBY_URL}...")
    chat_loop(user_id)