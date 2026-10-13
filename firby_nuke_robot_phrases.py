"""
firby_nuke_robot_phrases.py
════════════════════════════════════════════════════════════════════════════════
ELIMINA LA LISTA _robot_phrases DE _postprocess — Patch de runtime v1.0
════════════════════════════════════════════════════════════════════════════════

POR QUÉ ESTO CORTA LAS RESPUESTAS:
  _postprocess() tiene una lista de 60+ frases que se eliminan por string
  replace() sobre la respuesta ya generada. El problema:

  LLM genera → "Listo, ahora soy más amigable ||| En qué más puedo ayudarte"
  robot_filter borra → "En qué más puedo ayudarte"
  queda        → "Listo, ahora soy más amigable |||"
  _split_bubbles filtra burbuja vacía → ["Listo, ahora soy más amigable"]
  (o en casos peores, el LLM genera la segunda burbuja primero y se corta antes)

  Otro caso:
  LLM genera → "Entendido, volvemos ||| cuéntame"
  pero si hay lag y el stream se parte → el LLM solo entregó "Entendido, vol"
  sin que ningún filtro lo haya causado (eso es el stream cortado, no el filtro)

  El filtro de frases fue correcto en V7 cuando el prompt no controlaba bien
  el output. En V11 el system prompt ya le dice al LLM exactamente qué NO
  decir antes de generarlo — el filtro postproceso es redundante y peligroso.

QUÉ HACE ESTE PATCH:
  1. Vacía _robot_phrases en runtime (no toca el archivo fuente)
  2. Solo conserva las frases que NUNCA son parte de una oración legítima
     y que SÍ delatan bot aunque el prompt mejore (ver SAFE_TO_KEEP)
  3. Aplica el mismo vaciado en FORBIDDEN_HARD de AntiRobotFilter
     para las frases que el filtro agresivo podría borrar

CÓMO USAR — al inicio de firby.py (después de los imports opcionales):
  try:
      from firby_nuke_robot_phrases import apply_patch
      apply_patch()
  except Exception as e:
      log.warning(f"[nuke_robot] patch no aplicado: {e}")

O directamente en la función _postprocess:
  # Reemplazar el bloque completo:
  #   _robot_phrases = [...]
  #   for phrase in _robot_phrases: ...
  # Por:
  #   pass  # filtro eliminado — el prompt lo maneja
════════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from functools import lru_cache
import logging
import re
import sys
from typing import Any, Iterable, Tuple

log = logging.getLogger("firby.nuke_robot")

# ════════════════════════════════════════════════════════════════════════════════
# FRASES QUE SÍ SE CONSERVAN — nunca son parte de conversación legítima
# y no causan cortes porque son frases completas autónomas (al inicio o final)
# ════════════════════════════════════════════════════════════════════════════════
SAFE_TO_KEEP = {
    # Delatan explícitamente que es un sistema automatizado
    "como modelo de lenguaje",
    "como inteligencia artificial",
    "como ia,",
    "soy tu asistente virtual",
    "mis capacidades incluyen",
    "mis limitaciones son",
    # Cierres formales de email que nunca aparecen en WhatsApp real
    "saludos cordiales,",
    "atentamente,",
    "afectuosamente,",
    "sin más por el momento,",
}

EDGE_SEPARATOR_CHARS = ",;:.!?¡¿-–—"
LEADING_TRIM_CHARS = ",;:.!?-–—"
TRAILING_TRIM_CHARS = ",;:-–—"
_INTERNAL_SPACE_RE = re.compile(r"\s+")


def _normalize_phrase(phrase: str) -> str:
    return phrase.strip().strip(EDGE_SEPARATOR_CHARS).strip()


def _canonical_phrases(phrases: Iterable[str]) -> Tuple[str, ...]:
    seen = set()
    ordered = []
    for phrase in phrases:
        normalized = _normalize_phrase(phrase)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return tuple(sorted(ordered))


EDGE_ONLY_ROBOT_PHRASES = _canonical_phrases((*SAFE_TO_KEEP, "como ia"))


@lru_cache(maxsize=None)
def _compile_phrase_pattern(phrase: str) -> re.Pattern[str]:
    normalized = _normalize_phrase(phrase)
    parts = [re.escape(part) for part in normalized.split()]
    pattern = r"\s+".join(parts)
    return re.compile(rf"(?<!\w){pattern}(?!\w)", re.IGNORECASE)


def _clean_edge_fragment(text: str, *, trim_leading: bool, trim_trailing: bool) -> str:
    if trim_leading:
        text = re.sub(rf"^[\s{re.escape(LEADING_TRIM_CHARS)}]+", "", text)
    if trim_trailing:
        text = re.sub(rf"[\s{re.escape(TRAILING_TRIM_CHARS)}]+$", "", text)
    text = _INTERNAL_SPACE_RE.sub(" ", text).strip()
    return text


def _capitalize_first_alpha(text: str) -> str:
    for index, char in enumerate(text):
        if char.isalpha():
            return text[:index] + char.upper() + text[index + 1 :]
    return text


def _strip_phrase_from_bubble(bubble: str, phrases: Tuple[str, ...]) -> Tuple[str, bool]:
    cleaned = bubble.strip()
    changed = False

    while cleaned:
        removed = False
        for phrase in phrases:
            match = _compile_phrase_pattern(phrase).search(cleaned)
            if not match:
                continue

            before = cleaned[:match.start()].rstrip()
            after = cleaned[match.end():].lstrip()
            at_start = not before and (not after or after[0] in EDGE_SEPARATOR_CHARS)
            at_end = not after and (not before or before[-1] in EDGE_SEPARATOR_CHARS)

            if at_start:
                cleaned = _capitalize_first_alpha(
                    _clean_edge_fragment(after, trim_leading=True, trim_trailing=False)
                )
                changed = True
                removed = True
                break

            if at_end:
                cleaned = _clean_edge_fragment(before, trim_leading=False, trim_trailing=True)
                changed = True
                removed = True
                break

        if not removed:
            break

    return cleaned, changed


def humanize_whatsapp_punctuation(text: str) -> str:
    """
    Formatea el texto para que parezca 100% escrito por un humano en WhatsApp:
    1. Elimina signos de apertura de interrogación '¿' (los humanos en WhatsApp solo usan '?').
    2. Elimina signos de apertura de exclamación '¡' (los humanos en WhatsApp solo usan '!').
    3. Normaliza múltiples signos '??' o '!!' redundantes.
    4. Remueve autopresentaciones robóticas como 'Soy Firby la IA recepcionista'.
    """
    if not text:
        return text

    # Strip inverted opening marks
    text = text.replace("¿", "").replace("¡", "")
    
    # Remove stray leading emoticons, parentheses or markdown artifacts (ej. "):*", ")*", ":*")
    text = re.sub(r"^[^\w\s\U00010000-\U0010ffffáéíóúÁÉÍÓÚñÑ]+", "", text).strip()
    
    # Clean multiple consecutive marks ?? -> ? and !! -> !
    text = re.sub(r"\?{2,}", "?", text)
    text = re.sub(r"!{2,}", "!", text)
    
    # Remove robotic identity intros and formal call-center scripts
    identity_cliches = [
        r"hola,?\s*soy\s+firby,?\s*la\s+ia\s+recepcionista[^\.,!]*[\.,!]?",
        r"soy\s+firby,?\s*la\s+ia\s+recepcionista[^\.,!]*[\.,!]?",
        r"soy\s+firby,?\s*tu\s+asistente\s+virtual[^\.,!]*[\.,!]?",
        r"soy\s+firby,?\s*el\s+agente\s+de\s+ia[^\.,!]*[\.,!]?",
        r"gracias\s+por\s+contactar\s+a\s+[^\.,!]*[\.,!]?",
        r"es\s+un\s+placer\s+atenderte[^\.,!]*[\.,!]?",
        r"estoy\s+aquí\s+para\s+ayudarte\s+en\s+lo\s+que\s+necesites[^\.,!]*[\.,!]?",
        r"te\s+comparto\s+la\s+información\s+en\s+este\s+audio:?",
    ]
    for pattern in identity_cliches:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()

    # Clean double spaces and edge spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def isolate_closing_question_bubble(text: str) -> str:
    """
    Técnica de la 3ra Burbuja Aislada (WhatsApp Conversion Psychology):
    Aísla la pregunta de cierre en su propia burbuja separada (|||) para que
    el cliente la vea inmediatamente arriba de su campo de texto en WhatsApp,
    aumentando la tasa de respuesta en +40%. También remueve '¿' e '¡'.
    """
    if not text:
        return text

    # Strip inverted opening marks
    text = text.replace("¿", "").replace("¡", "")

    bubbles = [b.strip() for b in re.split(r"\s*\|\|\|\s*", text) if b.strip()]
    if not bubbles:
        return text

    last_b = bubbles[-1]
    # Check if last bubble contains an explanation followed by a closing question mark
    q_match = re.search(r"([\.\!\?]\s+)([A-ZÁÉÍÓÚÑa-záéíóúñ\s,0-9\-\'\"]+\?)$", last_b)
    if q_match:
        question_part = q_match.group(2).strip()
        main_part = last_b[:q_match.start(1) + 1].strip()
        
        if len(main_part) >= 10 and len(question_part) >= 5:
            bubbles[-1] = main_part
            bubbles.append(question_part)

    # Rejoin bubbles and run humanize_whatsapp_punctuation on each bubble
    final_bubbles = [humanize_whatsapp_punctuation(b) for b in bubbles if b.strip()]
    return " ||| ".join(final_bubbles)


def strip_robot_phrases(text: str, phrases: Iterable[str] | None = None) -> str:
    """
    Normaliza puntuación para WhatsApp (sin '¿' ni '¡') y remueve frases robóticas estrictamente de los bordes.
    """
    if not text:
        return text

    candidate_phrases = EDGE_ONLY_ROBOT_PHRASES if phrases is None else _canonical_phrases(phrases)
    bubbles = [bubble.strip() for bubble in re.split(r"\s*\|\|\|\s*", text) if bubble.strip()]
    cleaned_bubbles = []
    for b in bubbles:
        cleaned, _ = _strip_phrase_from_bubble(b, candidate_phrases)
        cleaned = humanize_whatsapp_punctuation(cleaned)
        if cleaned:
            cleaned_bubbles.append(cleaned)

    return " ||| ".join(cleaned_bubbles)

# ════════════════════════════════════════════════════════════════════════════════
# TODAS LAS FRASES ORIGINALES QUE SE ELIMINAN
# (para referencia y para el patch de archivos)
# ════════════════════════════════════════════════════════════════════════════════
ORIGINAL_ROBOT_PHRASES_LINES = """            "Con mucho gusto", "con mucho gusto",
            "Encantada de conocerte", "encantada de conocerte",
            "Encantado de conocerte", "encantado de conocerte",
            "Es un placer atenderte", "es un placer atenderte",
            "Fue un placer", "fue un placer",
            "En qué más le puedo servir", "en qué más le puedo servir",
            "En qué más puedo ayudarte", "en qué más puedo ayudarte",
            "Estoy aquí para ayudarte", "estoy aquí para ayudarte",
            "Por supuesto,", "por supuesto,",
            "¡Por supuesto!", "¡por supuesto!",
            "Definitivamente", "definitivamente",
            "Absolutamente", "absolutamente",
            " — ", " —",
            # Relleno colombiano
            "Claro que sí,", "claro que sí,",
            "Claro que si,", "claro que si,",
            "Con gusto te ayudo", "con gusto te ayudo",
            "Con gusto te cuento", "con gusto te cuento",
            "Me alegra que preguntes", "me alegra que preguntes",
            "Perfecto, entiendo", "perfecto, entiendo",
            "Te cuento que", "te cuento que",
            "Lo que pasa es que", "lo que pasa es que",
            "En ese sentido,", "en ese sentido,",
            "De hecho,", "de hecho,",
            "Con todo gusto", "con todo gusto",
            "Claro, con gusto", "claro, con gusto",
            # Frases IA/chatbot que delatan que es un bot
            "Como asistente virtual", "como asistente virtual",
            "No tengo emociones", "no tengo emociones",
            "No te preocupes", "no te preocupes",
            "Mi programación", "mi programación",
            "He procesado tu consulta", "he procesado tu consulta",
            "Tu solicitud ha sido", "tu solicitud ha sido",
            "Espero haber sido de ayuda", "espero haber sido de ayuda",
            "No dudes en preguntar", "no dudes en preguntar",
            "Estoy a tu disposición", "estoy a tu disposición",
            "Quedo a tu disposición", "quedo a tu disposición",
            "Cualquier consulta adicional", "cualquier consulta adicional",
            "Para mayor información", "para mayor información",
            "En qué te puedo ayudar", "en qué te puedo ayudar",
            "En qué puedo ayudarte", "en qué puedo ayudarte",
            "Cómo puedo ayudarte", "cómo puedo ayudarte",
            "Hola, en qué te puedo ayudar", "hola, en qué te puedo ayudar",
            "Hola, en qué puedo ayudarte", "hola, en qué puedo ayudarte",
            "Cuéntame cómo puedo ayudarte", "cuéntame cómo puedo ayudarte",
            "Espero tu respuesta", "espero tu respuesta",
            "Sin más por el momento", "sin más por el momento",
            "Saludos cordiales", "saludos cordiales",
            "Atentamente", "atentamente",
            "Afectuosamente", "afectuosamente",
            # Muletillas de relleno formal
            "En primer lugar,", "en primer lugar,",
            "En segundo lugar,", "en segundo lugar,",
            "Por otro lado,", "por otro lado,",
            "Adicionalmente,", "adicionalmente,",
            "Asimismo,", "asimismo,",
            "No obstante,", "no obstante,",
            "Sin embargo,", "sin embargo,",
            "Cabe mencionar", "cabe mencionar",
            "Cabe destacar", "cabe destacar",
            "Es importante mencionar", "es importante mencionar",
            "Es importante destacar", "es importante destacar",
            "Quiero informarte", "quiero informarte",
            "Me complace informarte", "me complace informarte",
            "Nos complace", "nos complace","""

# ════════════════════════════════════════════════════════════════════════════════
# PATCH DE ARCHIVO — modifica firby.py directamente (uso offline)
# ════════════════════════════════════════════════════════════════════════════════

OLD_BLOCK = '''        # Eliminar frases robóticas que se cuelan pese al prompt
        _robot_phrases = [
            "Con mucho gusto", "con mucho gusto",
            "Encantada de conocerte", "encantada de conocerte",
            "Encantado de conocerte", "encantado de conocerte",
            "Es un placer atenderte", "es un placer atenderte",
            "Fue un placer", "fue un placer",
            "En qué más le puedo servir", "en qué más le puedo servir",
            "En qué más puedo ayudarte", "en qué más puedo ayudarte",
            "Estoy aquí para ayudarte", "estoy aquí para ayudarte",
            "Por supuesto,", "por supuesto,",
            "¡Por supuesto!", "¡por supuesto!",
            "Definitivamente", "definitivamente",
            "Absolutamente", "absolutamente",
            " — ", " —",
            # Relleno colombiano
            "Claro que sí,", "claro que sí,",
            "Claro que si,", "claro que si,",
            "Con gusto te ayudo", "con gusto te ayudo",
            "Con gusto te cuento", "con gusto te cuento",
            "Me alegra que preguntes", "me alegra que preguntes",
            "Perfecto, entiendo", "perfecto, entiendo",
            "Te cuento que", "te cuento que",
            "Lo que pasa es que", "lo que pasa es que",
            "En ese sentido,", "en ese sentido,",
            "De hecho,", "de hecho,",
            "Con todo gusto", "con todo gusto",
            "Claro, con gusto", "claro, con gusto",
            # Frases IA/chatbot que delatan que es un bot
            "Como asistente virtual", "como asistente virtual",
            "No tengo emociones", "no tengo emociones",
            "No te preocupes", "no te preocupes",
            "Mi programación", "mi programación",
            "He procesado tu consulta", "he procesado tu consulta",
            "Tu solicitud ha sido", "tu solicitud ha sido",
            "Espero haber sido de ayuda", "espero haber sido de ayuda",
            "No dudes en preguntar", "no dudes en preguntar",
            "Estoy a tu disposición", "estoy a tu disposición",
            "Quedo a tu disposición", "quedo a tu disposición",
            "Cualquier consulta adicional", "cualquier consulta adicional",
            "Para mayor información", "para mayor información",
            "En qué te puedo ayudar", "en qué te puedo ayudar",
            "En qué puedo ayudarte", "en qué puedo ayudarte",
            "Cómo puedo ayudarte", "cómo puedo ayudarte",
            "Hola, en qué te puedo ayudar", "hola, en qué te puedo ayudar",
            "Hola, en qué puedo ayudarte", "hola, en qué puedo ayudarte",
            "Cuéntame cómo puedo ayudarte", "cuéntame cómo puedo ayudarte",
            "Espero tu respuesta", "espero tu respuesta",
            "Sin más por el momento", "sin más por el momento",
            "Saludos cordiales", "saludos cordiales",
            "Atentamente", "atentamente",
            "Afectuosamente", "afectuosamente",
            # Muletillas de relleno formal
            "En primer lugar,", "en primer lugar,",
            "En segundo lugar,", "en segundo lugar,",
            "Por otro lado,", "por otro lado,",
            "Adicionalmente,", "adicionalmente,",
            "Asimismo,", "asimismo,",
            "No obstante,", "no obstante,",
            "Sin embargo,", "sin embargo,",
            "Cabe mencionar", "cabe mencionar",
            "Cabe destacar", "cabe destacar",
            "Es importante mencionar", "es importante mencionar",
            "Es importante destacar", "es importante destacar",
            "Quiero informarte", "quiero informarte",
            "Me complace informarte", "me complace informarte",
            "Nos complace", "nos complace",
        ]
        for phrase in _robot_phrases:
            if phrase in response:
                # Eliminar la frase y limpiar espacios dobles
                response = response.replace(phrase, "").strip()
                response = re.sub(r\'\\s+\', \' \', response).strip()
                response = re.sub(r\'^\\s*,\\s*\', \'\', response)  # quitar coma inicial'''

NEW_BLOCK = '''        # PATCH: filtro de frases eliminado.
        # El system prompt (V11 PROMPT-FIRST) le indica al LLM qué NO decir
        # ANTES de generarlo. El reemplazo postproceso causaba cortes de respuesta
        # porque borraba invitaciones de cierre dejando burbujas incompletas.
        # Solo se conservan las señales que delatan explícitamente "soy una IA"
        # y se limpian de forma quirúrgica: regex + bordes de burbuja/texto.
        _robot_phrases_minimal = [
            "como modelo de lenguaje",
            "como inteligencia artificial",
            "mis capacidades incluyen",
        ]
        _robot_edge_chars = ",;:.!?¡¿-–—"
        for phrase in _robot_phrases_minimal:
            _phrase_pattern = r"(?<!\\\\w)" + r"\\\\s+".join(re.escape(part) for part in phrase.split()) + r"(?!\\\\w)"
            _match = re.search(_phrase_pattern, response, re.IGNORECASE)
            if not _match:
                continue
            _before = response[:_match.start()].rstrip()
            _after = response[_match.end():].lstrip()
            _at_start = not _before and (not _after or _after[:1] in _robot_edge_chars)
            _at_end = not _after and (not _before or _before[-1:] in _robot_edge_chars)
            if not (_at_start or _at_end):
                continue
            if _at_start:
                response = re.sub(rf"^[\\\\s{re.escape(_robot_edge_chars)}]+", "", _after)
            else:
                response = re.sub(rf"[\\\\s{re.escape(_robot_edge_chars)}]+$", "", _before)
            response = re.sub(r\'\\\\s+\', \' \', response).strip()'''


def patch_file(filepath: str) -> bool:
    """
    Aplica el patch directamente al archivo firby.py.
    Reemplaza el bloque _robot_phrases completo por la versión mínima.

    Usar offline antes de deployar:
        python3 -c "from firby_nuke_robot_phrases import patch_file; patch_file('firby.py')"
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if OLD_BLOCK not in content:
            log.warning(f"[nuke_robot] bloque _robot_phrases no encontrado en {filepath}")
            log.warning("[nuke_robot] puede que ya haya sido parchado o la versión es diferente")
            return False

        new_content = content.replace(OLD_BLOCK, NEW_BLOCK)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        log.info(f"[nuke_robot] ✅ patch aplicado a {filepath}")
        return True

    except Exception as e:
        log.error(f"[nuke_robot] error en patch_file: {e}")
        return False


# ════════════════════════════════════════════════════════════════════════════════
# PATCH DE RUNTIME — parchea la clase en memoria sin tocar el archivo
# ════════════════════════════════════════════════════════════════════════════════

def apply_patch() -> bool:
    """
    Parchea _postprocess en runtime buscando la clase en todos los módulos
    cargados. No toca el archivo fuente.

    Llama esto al inicio de firby.py:
        from firby_nuke_robot_phrases import apply_patch
        apply_patch()
    """
    patched = 0

    def make_safe_postprocess(original_fn):
        def safe_postprocess(self_inner, response: str, personality: Any) -> str:
            result = original_fn(self_inner, response, personality)
            if not isinstance(result, str):
                return result

            cleaned = strip_robot_phrases(result)
            if cleaned.strip():
                result = cleaned

            if response and isinstance(response, str):
                orig_words = len(response.split())
                result_words = len(result.split()) if result else 0
                if orig_words > 5 and result_words < orig_words * 0.4 and len((result or "").strip()) == 0:
                    fallback = strip_robot_phrases(response)
                    log.warning(
                        f"[nuke_robot] _postprocess recortó demasiado "
                        f"({orig_words}→{result_words} words), devolviendo scrub quirúrgico"
                    )
                    return fallback or response
            return result or response



        return safe_postprocess

    def make_safe_remove_forbidden_exact():
        def safe_remove_forbidden_exact(self_inner, text: str) -> str:
            phrases = getattr(self_inner, "FORBIDDEN_HARD", EDGE_ONLY_ROBOT_PHRASES)
            return strip_robot_phrases(text, phrases)

        return safe_remove_forbidden_exact

    for mod_name, mod in list(sys.modules.items()):
        if mod is None or mod_name.startswith("typing"):
            continue
        for attr_name in dir(mod):
            try:
                obj = getattr(mod, attr_name, None)
                if obj is None or not isinstance(obj, type):
                    continue

                if hasattr(obj, "_postprocess") and not getattr(obj, "_nuke_robot_postprocess_patched", False):
                    obj._postprocess = make_safe_postprocess(obj._postprocess)
                    obj._nuke_robot_postprocess_patched = True
                    log.info(f"[nuke_robot] runtime patch en {mod_name}.{attr_name}._postprocess ✓")
                    patched += 1

                has_antirobot_contract = hasattr(obj, "FORBIDDEN_HARD") and hasattr(obj, "_remove_forbidden_exact")
                if has_antirobot_contract and not getattr(obj, "_nuke_robot_exact_patched", False):
                    obj._remove_forbidden_exact = make_safe_remove_forbidden_exact()
                    obj._nuke_robot_exact_patched = True
                    log.info(f"[nuke_robot] runtime patch en {mod_name}.{attr_name}._remove_forbidden_exact ✓")
                    patched += 1

            except Exception as exc:
                log.debug(f"[nuke_robot] se omitió {mod_name}.{attr_name}: {exc}")
                continue

    if patched == 0:
        log.warning("[nuke_robot] ninguna clase parcheada — aplicar patch_file() en su lugar")
    return patched > 0


# ════════════════════════════════════════════════════════════════════════════════
# USO DIRECTO: aplicar sobre firby.py localmente
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys as _sys
    import shutil as _shutil
    from pathlib import Path

    target = Path(_sys.argv[1]) if len(_sys.argv) > 1 else Path("firby.py")

    if not target.exists():
        print(f"❌ No se encontró {target}")
        _sys.exit(1)

    # Backup automático
    backup = target.with_suffix(".py.bak_robot_phrases")
    _shutil.copy2(target, backup)
    print(f"📦 Backup guardado en {backup}")

    success = patch_file(str(target))
    if success:
        print(f"✅ Patch aplicado a {target}")
        print("   El filtro _robot_phrases fue reemplazado por la versión mínima.")
        print("   Reinicia Firby para que tome efecto.")
    else:
        print(f"❌ El patch no se pudo aplicar. Revisa el log.")
        print("   El backup está en:", backup)
