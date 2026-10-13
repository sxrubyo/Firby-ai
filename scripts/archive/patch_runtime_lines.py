import re

with open("/home/ubuntu/firby/src/core/runtime.py", "r") as f:
    lines = f.readlines()

def replace_method(lines, method_name, wrapper_lines):
    start_idx = -1
    for i, line in enumerate(lines):
        if line.startswith(f"    def {method_name}(") or line.startswith(f"    async def {method_name}("):
            start_idx = i
            break
            
    if start_idx == -1:
        print(f"Not found {method_name}")
        return lines
        
    end_idx = start_idx + 1
    while end_idx < len(lines):
        if lines[end_idx].startswith("    def ") or lines[end_idx].startswith("    async def ") or lines[end_idx].startswith("    @"):
            break
        end_idx += 1
        
    return lines[:start_idx] + [w + "\n" for w in wrapper_lines] + ["\n"] + lines[end_idx:]

lines = replace_method(lines, "_send_bubbles", [
    '    async def _send_bubbles(',
    '        self,',
    '        chat_id: str,',
    '        bubbles: List[str],',
    '        message_id: str = "",',
    '        route: Optional[Dict[str, Any]] = None,',
    '        user_text: str = "",',
    '    ):',
    '        """Envía burbujas con typing proporcional y pausas naturales."""',
    '        await self._sender._send_bubbles(chat_id, bubbles, message_id, route, user_text)'
])

lines = replace_method(lines, "_send_library_media", [
    '    async def _send_library_media(',
    '        self, chat_id: str, asset_id: str, route: Optional[Dict[str, Any]] = None',
    '    ):',
    '        """',
    '        Resolve a [MEDIA:asset_id] tag to a real file and send it',
    '        via the appropriate platform API (sendPhoto, sendVoice, sendDocument).',
    '        """',
    '        await self._sender._send_library_media(chat_id, asset_id, route)'
])

lines = replace_method(lines, "_typing_action", [
    '    async def _typing_action(',
    '        self,',
    '        chat_id: str,',
    '        text: str = "",',
    '        message_id: str = "",',
    '        route: Optional[Dict[str, Any]] = None,',
    '    ):',
    '        """',
    '        Indica escribiendo... proporcional al texto que va a enviar.',
    '        En WhatsApp Bridge también marca como leído si hay message_id.',
    '        """',
    '        await self._sender._typing_action(chat_id, text, message_id, route)'
])

lines = replace_method(lines, "_recording_action", [
    '    async def _recording_action(',
    '        self,',
    '        chat_id: str,',
    '        duration_ms: int = 4000,',
    '        route: Optional[Dict[str, Any]] = None,',
    '    ):',
    '        """',
    '        Indica grabando audio... en WhatsApp/Evolution/Telegram/Bridge.',
    '        """',
    '        await self._sender._recording_action(chat_id, duration_ms, route)'
])

with open("/home/ubuntu/firby/src/core/runtime.py", "w") as f:
    f.writelines(lines)
