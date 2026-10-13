import re

with open("/home/ubuntu/firby/src/core/runtime.py", "r") as f:
    text = f.read()

def replace_method(text, method_name, wrapper_code):
    pattern = r"(    (?:async )?def " + method_name + r"\(self,[\s\S]*?)(?=\n    (?:async )?def |\n    @|\Z)"
    match = re.search(pattern, text)
    if not match:
        print(f"Could not find method {method_name}")
        return text
    
    return text[:match.start()] + wrapper_code + text[match.end():]

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

with open("/home/ubuntu/firby/src/core/runtime.py", "w") as f:
    f.write(text)
