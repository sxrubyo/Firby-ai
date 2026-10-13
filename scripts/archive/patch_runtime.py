import re

with open("/home/ubuntu/firby/src/core/runtime.py", "r") as f:
    text = f.read()

# 1. Update __init__
init_target = '''        # ── Atributos base (antes de managers que los usan) ──────────────────────
        self._demo_sessions: Dict[str, float] = {}
        self._emoji_chats_off: set = set()
        self._chat_routes: Dict[str, Dict[str, Any]] = {}'''
init_replacement = '''        # ── Atributos base (antes de managers que los usan) ──────────────────────
        self._demo_sessions: Dict[str, float] = {}
        self._emoji_chats_off: set = set()
        
        from firby.src.core.message_sender import MessageSender
        self._sender = MessageSender(Config, db, self._demo_sessions, self._emoji_chats_off)'''
text = text.replace(init_target, init_replacement)


# Regex replacements for methods
def replace_method(text, method_name, wrapper_code):
    # Regex to find `    (async )?def method_name(self, ...):` down to next method `    def ` or `    async def ` or EOF
    pattern = r"(    (?:async )?def " + method_name + r"\(self,[\s\S]*?)(?=^    (?:async )?def |\Z)"
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        print(f"Could not find method {method_name}")
        return text
    return text[:match.start()] + wrapper_code + "\n\n" + text[match.end():]

# _mark_read_action
text = replace_method(text, "_mark_read_action", '''    async def _mark_read_action(self, chat_id: str, route: Optional[Dict[str, Any]] = None):
        """
        Marca visto el mensaje en WhatsApp enviando chulos azules en el momento natural.
        """
        await self._sender._mark_read_action(chat_id, route)''')

# _remember_route
text = replace_method(text, "_remember_route", '''    def _remember_route(self, chat_id: str, route: Optional[Dict[str, Any]] = None):
        self._sender._remember_route(chat_id, route)''')

# _resolve_route
text = replace_method(text, "_resolve_route", '''    def _resolve_route(self, chat_id: str, route: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._sender._resolve_route(chat_id, route)''')

# _send_bubbles
text = replace_method(text, "_send_bubbles", '''    async def _send_bubbles(
        self,
        chat_id: str,
        bubbles: List[str],
        message_id: str = "",
        route: Optional[Dict[str, Any]] = None,
        user_text: str = "",
    ):
        """Envía burbujas con typing proporcional y pausas naturales."""
        await self._sender._send_bubbles(chat_id, bubbles, message_id, route, user_text)''')

# _send_library_media
text = replace_method(text, "_send_library_media", '''    async def _send_library_media(
        self, chat_id: str, asset_id: str, route: Optional[Dict[str, Any]] = None
    ):
        """
        Resolve a [MEDIA:asset_id] tag to a real file and send it
        via the appropriate platform API (sendPhoto, sendVoice, sendDocument).
        """
        await self._sender._send_library_media(chat_id, asset_id, route)''')

# _typing_action
text = replace_method(text, "_typing_action", '''    async def _typing_action(
        self,
        chat_id: str,
        text: str = "",
        message_id: str = "",
        route: Optional[Dict[str, Any]] = None,
    ):
        """
        Indica 'escribiendo...' proporcional al texto que va a enviar.
        En WhatsApp Bridge también marca como leído si hay message_id.
        """
        await self._sender._typing_action(chat_id, text, message_id, route)''')

# _recording_action
text = replace_method(text, "_recording_action", '''    async def _recording_action(
        self,
        chat_id: str,
        duration_ms: int = 4000,
        route: Optional[Dict[str, Any]] = None,
    ):
        """
        Indica 'grabando audio...' ('recording_audio' / 'recording' / 'record_voice') en WhatsApp/Evolution/Telegram/Bridge.
        """
        await self._sender._recording_action(chat_id, duration_ms, route)''')

# sanitize_outgoing
text = replace_method(text, "sanitize_outgoing", '''    def sanitize_outgoing(self, text: Optional[str]) -> Optional[str]:
        """
        Sanitiza TODO mensaje saliente antes de enviarlo.
        Previene JSON bleed, debug messages y respuestas vacías.
        """
        return self._sender.sanitize_outgoing(text)''')

# _send_audio
text = replace_method(text, "_send_audio", '''    async def _send_audio(self, chat_id: str, audio_path: str, route: Optional[Dict[str, Any]] = None):
        """Send audio file as voice note via WhatsApp bridge."""
        await self._sender._send_audio(chat_id, audio_path, route)''')

# _send_message
text = replace_method(text, "_send_message", '''    async def _send_message(self, chat_id: str, text: str, route: Optional[Dict[str, Any]] = None):
        """
        Envia mensaje al paciente/admin segun la plataforma configurada.
        Plataformas soportadas: telegram | whatsapp_cloud | evolution | whatsapp
        """
        await self._sender._send_message(chat_id, text, route)''')

# _strip_emojis
text = replace_method(text, "_strip_emojis", '''    def _strip_emojis(self, text: str) -> str:
        """Elimina todos los emojis."""
        return self._sender._strip_emojis(text)''')

with open("/home/ubuntu/firby/src/core/runtime.py", "w") as f:
    f.write(text)
