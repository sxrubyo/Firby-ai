# -*- coding: utf-8 -*-
"""Módulo de Empatía, Humanidad y Calidad de Respuesta modularizado de globals.py."""
from __future__ import annotations
import os
import re
import json
import logging
import time
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple, Optional, Any, Set

log = logging.getLogger("firby.humanity")

# Proxies dinámicos para evitar import circular en la inicialización
from src.firby.core.proxy import GlobalProxy

db = GlobalProxy("db")
Config = GlobalProxy("Config")

class EmotionalMirrorEngine:
    """
    V9: Motor de espejo emocional mejorado.

    La diferencia con ConversationIntelligence.EMOTIONAL_STATES es que
    este motor genera instrucciones de respuesta MUY específicas,
    no solo etiquetas de estado emocional.

    Investiga de dónde viene la emoción + qué necesita escuchar.
    """

    # Señales emocionales expandidas con más matices
    EMOTIONAL_SIGNALS: Dict[str, Dict] = {
        "MIEDO_RESULTADO": {
            "signals": [
                "me da miedo", "qué tal si quedo", "y si quedo", "quedé mal antes",
                "tengo miedo que", "no quiero quedar", "exagerado", "cara de muñeca",
                "se note demasiado", "que se vea", "que quede natural",
                "primera vez", "nunca me he hecho", "la primera vez que",
            ],
            "response_instruction": (
                "MIEDO AL RESULTADO. "
                "Primero: valida el miedo en 1 frase ('ese miedo es muy normal'). "
                "Luego: enfoca en la evaluación/valoración como solución: "
                "'en la valoración la dra te dice con honestidad qué aplica para tu caso'. "
                "NUNCA: listas de casos exitosos, porcentajes, testimonios sin que los pida. "
                "El antídoto al miedo al resultado es la figura del especialista, no el marketing."
            ),
            "tone_shift": "más suave, más pausada",
        },
        "MIEDO_DOLOR": {
            "signals": [
                "duele", "duele mucho", "me va a doler", "es doloroso",
                "dolor", "duele la inyección", "siente la aguja", "miedo al dolor",
                "muy sensible", "umbral de dolor", "no aguanto el dolor",
            ],
            "response_instruction": (
                "MIEDO AL DOLOR. "
                "Normaliza el miedo ('ese miedo lo tiene la mayoría'). "
                "Explica el proceso brevemente (anestesia, presión vs dolor). "
                "Dato concreto específico al sector: "
                "Dental: 'con anestesia local solo sientes presión, no dolor'. "
                "Estética: 'botox es una pequeña molestia de segundos, rellenos con anestesia tópica'. "
                "Fisio: 'la terapia puede ser incómoda los primeros días pero no dolorosa'. "
                "CIERRE: la valoración/primera sesión como el paso donde lo conocen en persona."
            ),
            "tone_shift": "tranquilizadora y precisa",
        },
        "FRUSTRACIÓN_PREVIA": {
            "signals": [
                "ya fui a otro lado", "quedé mal", "otra clínica me hizo", "no funcionó",
                "ya lo intenté", "no me sirvió", "gasté plata", "pérdida de tiempo",
                "me prometieron", "no vi resultados", "ya probé de todo",
                "llevo años", "nada me funciona",
            ],
            "response_instruction": (
                "FRUSTRACIÓN POR EXPERIENCIA PREVIA. "
                "PASO 1: Reconoce la mala experiencia SIN atacar al otro lugar: "
                "'ay qué pena, eso no debería pasar'. "
                "PASO 2: Pregunta QUÉ pasó exactamente (sin asumir). "
                "PASO 3: Diferencia explicando qué es diferente acá (específico, no genérico). "
                "NUNCA: 'somos mejores que...', 'los otros no saben...'. "
                "SIEMPRE: diferencia concreta y verificable."
            ),
            "tone_shift": "empática y diferenciadora",
        },
        "ESCÉPTICO_GENERAL": {
            "signals": [
                "lo estoy pensando", "lo estoy considerando", "estoy comparando",
                "no sé si vale la pena", "no sé si funciona", "y eso realmente sirve",
                "a ver si", "ya veremos", "tengo que pensarlo", "no estoy seguro/a",
                "lo consulto con", "qué tan efectivo es",
            ],
            "response_instruction": (
                "ESCEPTICISMO GENERAL. "
                "No intentes convencer — el escepticismo se profundiza si presionas. "
                "En cambio: haz UNA pregunta que lo acerque más a la decisión: "
                "'qué sería lo que más te haría decidir' / "
                "'qué información necesitarías para estar más seguro/a'. "
                "Si da una objeción específica → trabájala directamente. "
                "CIERRE escéptico: 'sin afán, la valoración es gratis y sin compromiso'."
            ),
            "tone_shift": "paciente, sin presión",
        },
        "EMOCIONADO_LISTO": {
            "signals": [
                "qué bueno", "sí quiero", "me interesa mucho", "de una",
                "emocionada", "emocionado", "por fin", "estaba esperando esto",
                "me encanta", "ya quiero empezar", "sí claro",
                "cuándo podemos", "qué necesito", "cómo arrancamos",
            ],
            "response_instruction": (
                "CLIENTE EMOCIONADO Y LISTO. "
                "Match su energía (brevemente, sin exagerar). "
                "Ve DIRECTO al siguiente paso concreto: fecha, hora, qué llevar. "
                "No pierdas el momentum con más preguntas de diagnóstico — ya pasó esa etapa. "
                "CIERRE rápido: 'esta semana hay espacio el {dia}, te queda'. "
                "Si confirma → CIERRA. No ofrezcas más opciones."
            ),
            "tone_shift": "matching energy but grounded",
        },
        "VERGÜENZA": {
            "signals": [
                "me da pena", "me da vergüenza", "llevo mucho tiempo sin ir",
                "está muy mal", "está muy feo", "es horrible", "me da vergüenza",
                "no sé si lo puedan arreglar", "está muy descuidado",
                "tengo el cabello muy dañado", "mis dientes están muy mal",
            ],
            "response_instruction": (
                "VERGÜENZA. Esta es muy delicada — el cliente se expone emocionalmente. "
                "NUNCA: minimizar ('ay no está tan mal'), tranquilizar genérico. "
                "SÍ: normalizar sin juzgar ('acá ven todo tipo de casos, sin juzgar'). "
                "Frase clave: 'lo importante es que llegaste — de ahí en adelante es trabajar'. "
                "Luego: un paso pequeño y manejable. "
                "La vergüenza necesita normalización + dirección."
            ),
            "tone_shift": "cálida, sin juicio, directa",
        },
        "PRECIO_SHOCK": {
            "signals": [
                "está caro", "es muy caro", "no tengo plata", "costoso", "muy costoso",
                "no me alcanza", "salió caro", "no tenía idea que era tan caro",
                "es mucho", "es harto dinero", "para ese precio",
                "ese presupuesto no lo tengo", "con qué plata",
            ],
            "response_instruction": (
                "SHOCK DE PRECIO. "
                "PASO 1: Valida honestamente ('sí, los buenos tienen un costo'). "
                "PASO 2: NO defiendas el precio con listas de beneficios genéricos. "
                "PASO 3: Explora si hay opción accesible: "
                "  - ¿Hay servicio más básico que resuelva lo esencial? "
                "  - ¿Hay financiamiento o pago en cuotas? "
                "  - ¿Qué incluye específicamente que justifica ese precio? "
                "Si no hay opción más económica → sé honesto: 'para ese presupuesto "
                "recomendaría [alternativa o lugar]'. Eso genera confianza real."
            ),
            "tone_shift": "honesta, sin defensiva",
        },
        "INDECISO_CRÓNICO": {
            "signals": [
                "lo pienso", "después te escribo", "mañana te confirmo",
                "lo consulto con mi esposo/a", "hay que ver", "voy a ver",
                "primero termino de ver", "esta semana no puedo", "la semana que viene",
                "cuando pueda", "más adelante", "no sé cuándo",
            ],
            "response_instruction": (
                "INDECISIÓN CRÓNICA. La causa real es miedo no expresado. "
                "No presiones con urgencia falsa. "
                "Haz UNA pregunta para descubrir qué lo frena realmente: "
                "'¿qué es lo que más te detiene: el precio, el resultado o el proceso?' "
                "Si responde → trabaja ESA objeción específica. "
                "Si no responde → deja la puerta abierta sin presión: "
                "'no hay afán, cuando estés listo/a me escribes y buscamos espacio'. "
                "Programar follow-up para 1 semana después."
            ),
            "tone_shift": "paciente, sin urgencia, exploratoria",
        },
    }

    def __init__(self):
        self._compiled: Dict[str, list] = {}
        for emotion_id, data in self.EMOTIONAL_SIGNALS.items():
            self._compiled[emotion_id] = [
                re.compile(r'\b' + re.escape(s) + r'\b', re.IGNORECASE)
                for s in data["signals"]
            ]

    def detect_emotion(self, text: str, history: List[Dict] = None) -> Optional[str]:
        """
        Detecta la emoción dominante en el texto actual + historial reciente.
        Retorna el ID de la emoción o None si no detecta nada específico.
        """
        text_lower = text.lower()

        # Contexto ampliado: considerar historial reciente
        full_context = text_lower
        if history:
            recent = [m["content"] for m in history[-4:] if m["role"] == "user"]
            full_context += " ".join(recent).lower()

        scores: Dict[str, int] = {}
        for emotion_id, patterns in self._compiled.items():
            score = sum(1 for p in patterns if p.search(full_context))
            if score > 0:
                scores[emotion_id] = score

        if not scores:
            return None

        # Retornar la emoción con más señales
        return max(scores, key=scores.get)

    def get_response_instruction(self, emotion_id: str) -> str:
        """Retorna la instrucción de respuesta para la emoción detectada."""
        if emotion_id not in self.EMOTIONAL_SIGNALS:
            return ""
        return self.EMOTIONAL_SIGNALS[emotion_id]["response_instruction"]

    def get_tone_shift(self, emotion_id: str) -> str:
        """Retorna el ajuste de tono para la emoción detectada."""
        if emotion_id not in self.EMOTIONAL_SIGNALS:
            return ""
        return self.EMOTIONAL_SIGNALS[emotion_id].get("tone_shift", "")

    def build_prompt_injection(self, text: str, history: List[Dict] = None) -> str:
        """
        Genera el bloque completo para inyectar en el prompt.
        Combina detección + instrucción + tono.
        """
        emotion_id = self.detect_emotion(text, history)
        if not emotion_id:
            return ""

        instruction = self.get_response_instruction(emotion_id)
        tone = self.get_tone_shift(emotion_id)

        # Una sola frase — sin headers, sin etiquetas en mayúsculas
        hint = instruction
        if tone:
            hint = f"{hint} {tone}"
        return hint


# ══════════════════════════════════════════════════════════════════════════════
# DETECTOR DE PERSONA DEL CLIENTE
# Identifica el tipo psicográfico del cliente para adaptar la comunicación
# ══════════════════════════════════════════════════════════════════════════════

class ClientPersonaDetector:
    """
    V9: Detecta el arquetipo psicográfico del cliente.

    Investigación de campo identifica 5 arquetipos dominantes
    en clientes de servicios en Colombia:
    - IMPULSIVO: decide rápido, poca información, necesita facilidades
    - ANALÍTICO: quiere datos, compara, toma su tiempo
    - EMOCIONAL: decide por cómo se siente, necesita conexión antes de lógica
    - ESCÉPTICO: ha sido quemado antes, desconfía por defecto
    - ENTUSIASTA: ya está convencido, necesita que no lo hagan desconfiar

    Cada arquetipo necesita una estrategia diferente.
    """

    PERSONA_PROFILES: Dict[str, Dict] = {
        "IMPULSIVO": {
            "signals": [
                "cuándo puedo ir", "qué necesito", "cómo arrancamos",
                "de una", "hoy mismo", "lo antes posible", "ya quiero",
                "me interesa", "para mañana", "puedo hoy",
                "cuánto es", "cómo pago",
            ],
            "strategy": (
                "CLIENTE IMPULSIVO. Decide rápido, no lo confundas con mucha info. "
                "Dale lo esencial (fecha, precio aproximado, paso siguiente). "
                "CIERRA en este mismo mensaje: 'esta semana el {dia}, te queda'. "
                "Si pone resistencia → NO explores demasiado, solo facilita el sí."
            ),
            "risk": "Se puede ir si el proceso es lento o tedioso",
        },
        "ANALÍTICO": {
            "signals": [
                "cuántas sesiones", "qué incluye exactamente", "cuánto tiempo dura",
                "qué pasa si", "cuáles son los riesgos", "qué porcentaje",
                "comparado con", "he leído que", "según estudios", "en qué se diferencia",
                "me puedes dar más detalles", "cómo funciona exactamente",
                "qué garantías tienen", "qué credenciales",
            ],
            "strategy": (
                "CLIENTE ANALÍTICO. Necesita datos concretos, no emociones. "
                "Da información precisa ('el procedimiento dura 45 minutos', "
                "'los resultados duran 6-12 meses dependiendo de'). "
                "NUNCA des estimaciones vagas — prefiere saber que no sabes a que inventes. "
                "Para cerrar: ofrécele la valoración como forma de obtener info personalizada. "
                "'En la valoración te dicen exactamente cuánto tiempo, costo y resultado para tu caso.'"
            ),
            "risk": "Si siente que le estás vendiendo en vez de informar, se va",
        },
        "EMOCIONAL": {
            "signals": [
                "siempre lo he querido hacer", "llevo años pensándolo", "me emociona",
                "una amiga me dijo", "vi el antes y después de", "me imagino cómo",
                "sería como mi regalo", "es para el evento de", "quiero verme bien para",
                "siempre me ha incomodado", "ya me cansé de", "finalmente",
            ],
            "strategy": (
                "CLIENTE EMOCIONAL. La conexión emocional primero, la lógica después. "
                "Reconoce el momento emocional ('qué bueno que te animaste'). "
                "Conecta el servicio con el resultado emocional que busca. "
                "NUNCA: listas de características, tecnicismos. "
                "SÍ: 'imagínate cómo te vas a sentir después' / 'muchas personas llegan "
                "sintiéndose exactamente como tú y salen sintiéndose...'. "
                "El cierre emocional: 'ese día que decides es el día que cambia algo'."
            ),
            "risk": "Si lo tratas puramente lógico pierde el 'feeling' y no decide",
        },
        "ESCÉPTICO": {
            "signals": [
                "ya fui a otro", "otra clínica me dijo", "no me creo", "lo dudo",
                "y realmente funciona", "qué garantía tienen", "y si no funciona",
                "he visto muchos prometer", "en internet dice que", "leí reviews malos",
                "un amigo tuvo mala experiencia", "cómo sé que es verdad",
            ],
            "strategy": (
                "CLIENTE ESCÉPTICO. No trates de convencerlo — eso profundiza el escepticismo. "
                "PASO 1: Reconoce que su escepticismo es válido ('es normal desconfiar, "
                "hay mucho que no cumple lo que promete'). "
                "PASO 2: Ofrece evidencia verificable (fotos de pacientes reales, "
                "proceso transparente, sin promesas exageradas). "
                "PASO 3: Baja el riesgo percibido: 'la valoración es gratis y sin compromiso'. "
                "NUNCA: prometas resultados garantizados si no los puedes probar."
            ),
            "risk": "Si exageras o prometes demasiado, confirmas sus miedos",
        },
        "ENTUSIASTA": {
            "signals": [
                "ya sé lo que quiero", "vengo del otro lado", "me recomendaron",
                "ya me informé", "sé exactamente", "solo necesito la cita",
                "ya decidí", "ya sé que es", "solo dime cuándo", "cómo pago",
                "ya está confirmado en mi mente", "vengo por",
            ],
            "strategy": (
                "CLIENTE ENTUSIASTA. Ya decidió. No necesita venta — necesita facilidades. "
                "Ve DIRECTO a lo operativo: fecha, precio exacto, cómo confirmar. "
                "NUNCA lo hagas pasar por el funnel de nuevo (no le preguntes 'qué buscas'). "
                "Si pregunta algo específico → responde directo. "
                "El mayor riesgo: complicar un proceso que para él ya era simple. "
                "Cierre: 'perfecto, te aparto para el {dia}'. Nada más."
            ),
            "risk": "Perderlo por hacer el proceso más complicado de lo necesario",
        },
    }

    def __init__(self):
        self._history: Dict[str, str] = {}  # chat_id → last detected persona

    def detect(self, text: str, history: List[Dict] = None) -> Optional[str]:
        """
        Detecta el arquetipo dominante del cliente.
        Considera historial para mayor precisión.
        """
        full_text = text.lower()
        if history:
            user_msgs = [m["content"].lower() for m in history[-6:]
                         if m["role"] == "user"]
            full_text += " ".join(user_msgs)

        scores: Dict[str, int] = {}
        for persona_id, data in self.PERSONA_PROFILES.items():
            score = sum(1 for signal in data["signals"]
                       if signal.lower() in full_text)
            if score > 0:
                scores[persona_id] = score

        if not scores:
            return None
        return max(scores, key=scores.get)

    def get_strategy(self, persona_id: str) -> str:
        """Retorna la estrategia para el arquetipo dado."""
        if persona_id not in self.PERSONA_PROFILES:
            return ""
        return self.PERSONA_PROFILES[persona_id]["strategy"]

    def get_risk(self, persona_id: str) -> str:
        """Retorna el riesgo de pérdida para este arquetipo."""
        if persona_id not in self.PERSONA_PROFILES:
            return ""
        return self.PERSONA_PROFILES[persona_id].get("risk", "")

    def build_prompt_injection(self, chat_id: str, text: str,
                               history: List[Dict] = None) -> str:
        """Genera bloque de inyección para el prompt."""
        persona = self.detect(text, history)
        if not persona:
            # Usar último detectado si existe
            persona = self._history.get(chat_id)
        if not persona:
            return ""

        self._history[chat_id] = persona
        strategy = self.get_strategy(persona)
        # Solo la estrategia — sin "ARQUETIPO CLIENTE:" ni "RIESGO A EVITAR:"
        # El LLM la aplica mejor cuando llega como instrucción directa
        return strategy if strategy else ""


# ══════════════════════════════════════════════════════════════════════════════
# CONTEXTUALIZADOR DE TIEMPO
# Adapta el tono y vocabulario según la hora del día
# ══════════════════════════════════════════════════════════════════════════════

class TimeContextualizer:
    """
    V9: Adapta el tono según hora del día, día de semana y contexto temporal.

    Investigación: las personas escriben de forma diferente a las 8am
    que a las 10pm. Un bot que suena igual a todas horas es predecible.
    """

    # Colombia UTC-5
    _COL_TZ = timezone(timedelta(hours=-5))

    TIME_PROFILES: Dict[str, Dict] = {
        "madrugada": {  # 0-6
            "hour_range": (0, 6),
            "tone_note": (
                "Son las madrugada. Si el cliente escribe a estas horas es porque algo lo preocupa "
                "mucho o trabaja de noche. Tono más calmado. Respuestas más cortas. "
                "No menciones la hora explícitamente a menos que sea relevante."
            ),
            "greeting": "",  # No saludo especial
            "energy": "baja, calmada",
        },
        "mañana_temprano": {  # 6-9
            "hour_range": (6, 9),
            "tone_note": (
                "Mañana temprano. La persona empieza el día. "
                "Energía moderada. Puede ser eficiente y directa. "
                "Saludo de mañana si es primer mensaje: 'buenos días'."
            ),
            "greeting": "buenos días",
            "energy": "moderada, directa",
        },
        "mañana": {  # 9-12
            "hour_range": (9, 12),
            "tone_note": (
                "Mañana normal de trabajo. Hora pico de atención. "
                "Tono activo, eficiente, cálido. "
                "Buenos días si es primer mensaje."
            ),
            "greeting": "buenos días",
            "energy": "activa, eficiente",
        },
        "mediodia": {  # 12-14
            "hour_range": (12, 14),
            "tone_note": (
                "Hora del almuerzo. Muchas personas escriben desde el teléfono durante el descanso. "
                "Tono relajado pero eficiente. Sin buenos días ni buenas tardes forzado."
            ),
            "greeting": "buenas",
            "energy": "relajada, eficiente",
        },
        "tarde": {  # 14-18
            "hour_range": (14, 18),
            "tone_note": (
                "Tarde laboral. Buenas tardes si es primer mensaje. "
                "Ritmo normal, cálido. Es la hora pico de citas y decisiones."
            ),
            "greeting": "buenas tardes",
            "energy": "normal, cálida",
        },
        "tarde_noche": {  # 18-20
            "hour_range": (18, 20),
            "tone_note": (
                "Fin de la jornada. La persona puede estar más relajada o más cansada. "
                "Tono más relajado. Si es primer mensaje: 'buenas noches' o simplemente 'buenas'."
            ),
            "greeting": "buenas",
            "energy": "relajada",
        },
        "noche": {  # 20-24
            "hour_range": (20, 24),
            "tone_note": (
                "Noche. La persona está en su tiempo personal. Más emotiva, más reflexiva. "
                "Respuestas más cortas y cálidas. "
                "Es hora en que muchos toman decisiones ('hoy me animé a escribir'). "
                "Tono tranquilo, sin prisa, presente."
            ),
            "greeting": "buenas noches",
            "energy": "calmada, presente",
        },
    }

    WEEKDAY_NOTES: Dict[int, str] = {
        0: "lunes",    # Lunes — inicio de semana, energía variable
        1: "martes",   # Martes — semana en marcha
        2: "miércoles", # Miércoles — punto medio
        3: "jueves",   # Jueves — cerca del fin
        4: "viernes",  # Viernes — fin de semana próximo, más relajado
        5: "sábado",   # Sábado — tiempo libre, diferente agenda
        6: "domingo",  # Domingo — planning de semana, emotivo
    }

    def get_current_profile(self) -> Dict:
        """Retorna el perfil de tiempo actual."""
        now = datetime.now(self._COL_TZ)
        hour = now.hour
        for profile_id, data in self.TIME_PROFILES.items():
            start, end = data["hour_range"]
            if start <= hour < end:
                return {"id": profile_id, "hour": hour,
                        "weekday": now.weekday(), **data}
        return {"id": "noche", "hour": hour, **self.TIME_PROFILES["noche"]}

    def get_prompt_injection(self) -> str:
        """Genera instrucción de contexto temporal para el prompt."""
        profile = self.get_current_profile()
        weekday_name = self.WEEKDAY_NOTES.get(profile.get("weekday", 0), "")
        tone_note = profile.get("tone_note", "")
        energy = profile.get("energy", "")

        if not tone_note:
            return ""

        lines = [
            f"CONTEXTO TEMPORAL: {weekday_name}, {profile['id']} ({profile['hour']}h)",
            f"ENERGÍA SUGERIDA: {energy}",
            tone_note,
        ]
        return "\n".join(lines)

    def get_recommended_greeting(self) -> str:
        """Retorna el saludo recomendado para la hora actual."""
        profile = self.get_current_profile()
        return profile.get("greeting", "hola")


# ══════════════════════════════════════════════════════════════════════════════
# ANALIZADOR DE RITMO DE CONVERSACIÓN
# Detecta el ritmo de escritura del cliente y genera instrucciones
# para que Firby lo espeje naturalmente
# ══════════════════════════════════════════════════════════════════════════════

class ConversationRhythmAnalyzer:
    """
    V9: Analiza el ritmo de escritura del cliente y genera instrucciones.

    Métricas que analiza:
    - Longitud promedio de mensajes
    - Frecuencia de uso de preguntas
    - Nivel de informalidad (abreviaciones, sin tildes, etc.)
    - Velocidad de respuesta (cuando está disponible)
    - Patrón de burbujas (muchos mensajes cortos vs pocos largos)
    """

    def __init__(self):
        self._profiles: Dict[str, Dict] = {}

    def analyze(self, chat_id: str, history: List[Dict]) -> Dict:
        """Analiza el patrón de escritura del usuario y retorna perfil."""
        user_msgs = [m["content"] for m in history if m["role"] == "user"]
        if len(user_msgs) < 2:
            return self._profiles.get(chat_id, self._default_profile())

        # Métricas básicas
        avg_words = sum(len(m.split()) for m in user_msgs) / len(user_msgs)
        max_words = max(len(m.split()) for m in user_msgs)
        question_rate = sum(1 for m in user_msgs if "?" in m) / len(user_msgs)
        informal_markers = ["xq", "pq", "q ", " k ", "tmb", "tb", "jaja", "jeje",
                           "hahaha", "xD", "kkk", "omg", "lol"]
        informality = sum(1 for m in user_msgs
                         for marker in informal_markers
                         if marker in m.lower()) / len(user_msgs)

        profile = {
            "avg_words": round(avg_words, 1),
            "max_words": max_words,
            "question_rate": round(question_rate, 2),
            "informality_score": round(min(informality * 5, 1.0), 2),
            "msg_count": len(user_msgs),
            "style": self._classify_style(avg_words, informality, question_rate),
        }

        self._profiles[chat_id] = profile
        return profile

    def _classify_style(self, avg_words: float, informality: float,
                        question_rate: float) -> str:
        """Clasifica el estilo de escritura del cliente."""
        if avg_words < 5:
            return "ultra_conciso"
        if avg_words < 10 and informality > 0.3:
            return "informal_corto"
        if avg_words < 15:
            return "normal"
        if avg_words >= 15 and question_rate > 0.5:
            return "analítico_extenso"
        if avg_words >= 15:
            return "elaborado"
        return "normal"

    def _default_profile(self) -> Dict:
        return {"avg_words": 10, "max_words": 20, "question_rate": 0.3,
                "informality_score": 0.3, "msg_count": 0, "style": "normal"}

    def get_prompt_injection(self, chat_id: str, history: List[Dict]) -> str:
        """Genera instrucción de ritmo para el prompt."""
        if not history:
            return ""

        profile = self.analyze(chat_id, history)
        style = profile.get("style", "normal")
        avg_words = profile.get("avg_words", 10)

        style_instructions = {
            "ultra_conciso": (
                "CLIENTE ULTRA CONCISO: Escribe muy poco. "
                "TU RESPUESTA: máximo 5-8 palabras por burbuja. "
                "Sin introducciones, sin cierres. Solo lo esencial."
            ),
            "informal_corto": (
                "CLIENTE INFORMAL Y CORTO: Escribe rápido e informalmente. "
                "TU RESPUESTA: 8-12 palabras. Tuteo muy informal. "
                "Sin signos de apertura. Sin formulismos."
            ),
            "normal": (
                "CLIENTE NORMAL: Escribe de forma estándar. "
                "TU RESPUESTA: 10-20 palabras máximo. Tono natural del arquetipo activo."
            ),
            "analítico_extenso": (
                "CLIENTE ANALÍTICO: Hace muchas preguntas y escribe extenso. "
                "TU RESPUESTA: puedes ser un poco más elaborada (hasta 25 palabras). "
                "Responde sus preguntas con precisión. No estimes — da datos."
            ),
            "elaborado": (
                "CLIENTE ELABORADO: Escribe mucho. "
                "TU RESPUESTA: extrae lo esencial de lo que escribió y responde puntual. "
                "No respondas con igual extensión — responde con lo que importa."
            ),
        }

        return style_instructions.get(style, style_instructions["normal"])


# ══════════════════════════════════════════════════════════════════════════════
# SCRIPTS DE CIERRE POR SECTOR
# Scripts de cierre natural específicos para cada sector
# ══════════════════════════════════════════════════════════════════════════════

class SectorClosingScripts:
    """
    V9: Scripts de cierre específicos por sector.

    Cada sector tiene patrones de cierre únicos que suenan naturales
    para ese contexto. Un cierre de gym no suena igual que uno de spa.
    """

    SCRIPTS: Dict[str, Dict[str, List[str]]] = {
        "estetica": {
            "valoracion": [
                "te agendo la valoración con la doctora, es gratis y dura 30 minutos ||| "
                "esta semana hay espacio el {dia}, te queda",
                "la valoración es con la doctora directamente ||| "
                "sin compromiso, es para que te diga exactamente qué aplica para tu caso ||| "
                "el {dia} en la tarde hay espacio, te llega",
                "te separo la valoración ya, dura 30 minutos ||| "
                "el {dia} a las {hora} está disponible, cómo quedas",
            ],
            "post_valoracion": [
                "listo, quedó la valoración para el {dia} ||| "
                "llega como 10 minutos antes. te mando recordatorio el día anterior",
                "confirmado el {dia} con la dra ||| "
                "si necesitas cambiar, avísame con tiempo",
            ],
        },
        "dental": {
            "primera_cita": [
                "te agendo la valoración con la dra, incluye rayos X ||| "
                "dura unos 20 minutos. esta semana hay el {dia}, te queda",
                "la primera cita es la evaluación, dura 20 minutos ||| "
                "hay espacio el {dia}, a qué hora te queda mejor",
            ],
            "urgencia": [
                "si es dolor fuerte, hay espacio hoy para urgencias ||| "
                "a qué hora puedes estar acá",
                "para dolor de muela tenemos urgencias ||| "
                "cuándo puedes venir, hay espacio hoy",
            ],
        },
        "gimnasio": {
            "evaluacion": [
                "hacemos la evaluación física primero, es gratis ||| "
                "esta semana el {dia} en {periodo} hay espacio, te cuadra",
                "arrancamos con la evaluación para saber de dónde partimos ||| "
                "el {dia} hay espacio, cuándo puedes",
            ],
            "matricula": [
                "te matriculo esta semana si quieres ||| "
                "cuándo tienes 20 minutos para venir a firmar y empezar",
            ],
        },
        "restaurante": {
            "reserva": [
                "les aparto la mesa para el {dia} a las {hora}, a nombre de {nombre} ||| "
                "confirmado, los esperamos",
                "reserva hecha para el {dia} a las {hora}, {personas} personas ||| "
                "si necesitan cambio, avísenme con anticipación",
            ],
            "evento": [
                "para el evento de {N} personas les paso con el coordinador ||| "
                "me dan el número para que los llame hoy",
            ],
        },
        "belleza": {
            "cita": [
                "te aparto la cita con {estilista} para el {dia} a las {hora} ||| "
                "llega 5 minutos antes para lavar y preparar",
                "queda agendado el {dia} para {servicio} ||| "
                "cualquier cambio me avisas",
            ],
        },
        "spa": {
            "sesion": [
                "les reservo el {servicio} para el {dia} a las {hora} ||| "
                "lleguen 15 minutos antes para prepararse y aprovechar mejor",
                "queda reservado el {dia} para los dos ||| "
                "les recomendamos llegar relajados, sin afán",
            ],
        },
        "veterinaria": {
            "cita_rutina": [
                "te agendo a {nombre_mascota} para el {dia} en {periodo} ||| "
                "recuerda traer el carné de vacunación si tiene",
                "queda la cita de {nombre_mascota} para el {dia} ||| "
                "cualquier cambio me avisas",
            ],
            "urgencia": [
                "tráelo ahora, hay espacio para urgencias ||| "
                "avísame cuándo sales para que te estén esperando",
            ],
        },
        "medico": {
            "consulta": [
                "te agendo con el dr/dra para el {dia} a las {hora} ||| "
                "lleva documentos de identidad y seguro médico si tienes",
                "queda la cita para el {dia} ||| "
                "llega 15 minutos antes para el registro",
            ],
        },
        "psicologo": {
            "primera_sesion": [
                "te agendo la primera sesión para el {dia} ||| "
                "es de evaluación, 50 minutos, sin compromiso de continuar",
                "primera sesión el {dia} con {terapeuta} ||| "
                "si tienes alguna preferencia de tema principal antes de ir, me la cuentas",
            ],
        },
        "abogado": {
            "consulta_inicial": [
                "le agendo la consulta inicial para el {dia} ||| "
                "lleve los documentos que tenga relacionados con el caso",
                "consulta inicial el {dia} a las {hora} ||| "
                "en esa sesión el dr le dice qué opciones tiene y cuál es el camino",
            ],
        },
        "taller": {
            "servicio": [
                "lo esperamos el {dia} a las {hora} ||| "
                "si puede llegar un poco antes mejor para no hacer fila",
                "queda agendado el servicio para el {dia} ||| "
                "al llegar preguntas por {tecnico}",
            ],
            "urgencia": [
                "si no puede mover el carro, tenemos grúa ||| "
                "dónde está para coordinar",
            ],
        },
        "nutricion": {
            "consulta": [
                "te agendo la consulta inicial con la nutricionista el {dia} ||| "
                "lleva exámenes recientes si tienes, si no igual",
                "consulta el {dia} para hacer el plan personalizado ||| "
                "cuánto tiempo tienes disponible esa mañana/tarde",
            ],
        },
        "academia": {
            "inscripcion": [
                "te inscribo al grupo del {dia} a las {hora} ||| "
                "te mando el link de pago para confirmar el cupo",
                "cupo confirmado en el grupo de {nivel} ||| "
                "el primer día es el {fecha}. te mando los detalles",
            ],
        },
    }

    def get_script(self, sector: str, script_type: str = "default") -> Optional[str]:
        """Retorna un script de cierre aleatorio para el sector y tipo dado."""
        sector_scripts = self.SCRIPTS.get(sector, {})
        if not sector_scripts:
            return None

        scripts_for_type = sector_scripts.get(script_type)
        if not scripts_for_type:
            # Buscar cualquier tipo disponible
            all_scripts = [s for scripts in sector_scripts.values() for s in scripts]
            if not all_scripts:
                return None
            return random.choice(all_scripts)

        return random.choice(scripts_for_type)

    def format_script(self, script: str, **kwargs) -> str:
        """Reemplaza variables en el script con valores reales."""
        try:
            return script.format(**kwargs)
        except KeyError:
            # Si faltan variables, retorna el script sin formatear
            return script

    def get_closing_instruction(self, sector: str) -> str:
        """Genera instrucción de cierre para inyectar al prompt."""
        sector_scripts = self.SCRIPTS.get(sector)
        if not sector_scripts:
            return ""

        # Muestra 2-3 ejemplos del sector como guía
        examples = []
        for script_type, scripts in sector_scripts.items():
            if scripts:
                examples.append(f"  [{script_type}]: {scripts[0]}")
            if len(examples) >= 2:
                break

        if not examples:
            return ""

        return (
            f"CIERRES NATURALES PARA {sector.upper()} — usa como referencia:\n"
            + "\n".join(examples)
        )


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL — CONSTRUYE EL BLOQUE V9 COMPLETO
# Se llama desde v8_build_quality_system_prompt_addon()
# ══════════════════════════════════════════════════════════════════════════════

# Instancias globales del módulo (se inicializan en init_v9_systems())
_emotional_mirror: Optional[EmotionalMirrorEngine] = None
_persona_detector: Optional[ClientPersonaDetector] = None
_time_contextualizer: Optional[TimeContextualizer] = None
_rhythm_analyzer: Optional[ConversationRhythmAnalyzer] = None
_sector_closing: Optional[SectorClosingScripts] = None


def init_v9_systems():
    """
    Inicializa todos los sistemas V9.
    Llama esto en el startup de firby.py, después de init_v8_systems().
    """
    global _emotional_mirror, _persona_detector, _time_contextualizer
    global _rhythm_analyzer, _sector_closing

    _emotional_mirror      = EmotionalMirrorEngine()
    _persona_detector      = ClientPersonaDetector()
    _time_contextualizer   = TimeContextualizer()
    _rhythm_analyzer       = ConversationRhythmAnalyzer()
    _sector_closing        = SectorClosingScripts()

    try:
        # Importar log si está disponible
        import logging
        logging.getLogger("firby.ultra").info("═══ V9 HUMANIZATION SYSTEMS: 5/5 OK ═══")
    except Exception:
        pass


def v9_build_humanization_block(
    chat_id: str,
    archetype: str,
    history: List[Dict],
    current_message: str = "",
    sector: str = "",
) -> str:
    """
    Construye el bloque de humanización V9 para inyectar en el system prompt.

    Este bloque combina:
    1. Contexto temporal (hora del día, día de semana)
    2. Estado emocional detectado + instrucción de respuesta
    3. Arquetipo psicográfico del cliente + estrategia
    4. Ritmo de conversación + instrucción de espejo
    5. Script de cierre del sector (si aplica)

    INTEGRACIÓN en firby.py:
    En _v8_build_addon_inner(), al final antes del return:
        lines.append(v9_build_humanization_block(
            chat_id, archetype, history, current_message, sector
        ))
    """
    if not any([_emotional_mirror, _persona_detector,
                _time_contextualizer, _rhythm_analyzer]):
        init_v9_systems()

    blocks: List[str] = []

    # 1. Contexto temporal
    try:
        if _time_contextualizer:
            time_block = _time_contextualizer.get_prompt_injection()
            if time_block:
                blocks.append(time_block)
    except Exception:
        pass

    # 2. Estado emocional
    try:
        if _emotional_mirror and current_message:
            emotion_block = _emotional_mirror.build_prompt_injection(
                current_message, history
            )
            if emotion_block:
                blocks.append(emotion_block)
    except Exception:
        pass

    # 3. Arquetipo del cliente
    try:
        if _persona_detector and current_message:
            persona_block = _persona_detector.build_prompt_injection(
                chat_id, current_message, history
            )
            if persona_block:
                blocks.append(persona_block)
    except Exception:
        pass

    # 4. Ritmo de conversación
    try:
        if _rhythm_analyzer and history and len(history) >= 3:
            rhythm_block = _rhythm_analyzer.get_prompt_injection(chat_id, history)
            if rhythm_block:
                blocks.append(rhythm_block)
    except Exception:
        pass

    # 5. Script de cierre del sector
    try:
        if _sector_closing and sector and sector != "otro":
            closing_block = _sector_closing.get_closing_instruction(sector)
            if closing_block:
                blocks.append(closing_block)
    except Exception:
        pass

    if not blocks:
        return ""

    # Sin header "V9 HUMANIZACIÓN TOTAL" ni separadores ━━━━
    # El contenido fluye como parte orgánica del prompt
    return "\n".join(b for b in blocks if b and b.strip())


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE PARCHE — INTEGRAN V9 EN LOS SISTEMAS EXISTENTES DE FIRBY
# ══════════════════════════════════════════════════════════════════════════════

def v9_patch_archetypes() -> int:
    """
    Agrega los arquetipos V9 al dict PERSONALITY_ARCHETYPES de firby.py.
    Retorna el número de arquetipos agregados.

    USO: Llamar en el startup DESPUÉS de que firby.py ya cargó.
    Requiere que PERSONALITY_ARCHETYPES sea importable como global.

    Ejemplo:
        from firby import PERSONALITY_ARCHETYPES
        from firby_v9_humanization import v9_patch_archetypes, V9_PERSONALITY_ARCHETYPES
        # Parchea automáticamente
        count = v9_patch_archetypes()
    """
    try:
        import firby as _firby_module
        existing = getattr(_firby_module, "PERSONALITY_ARCHETYPES", {})
        added = 0
        for archetype_id, archetype_data in V9_PERSONALITY_ARCHETYPES.items():
            if archetype_id not in existing:
                existing[archetype_id] = archetype_data
                added += 1
        return added
    except ImportError:
        # Si no se puede importar el módulo directamente,
        # el parche se hace manualmente en firby.py
        return 0


def v9_patch_skills() -> int:
    """
    Agrega las skills V9 al dict SKILL_DEFINITIONS de firby.py.
    Retorna el número de skills agregadas.

    USO: Llamar en el startup DESPUÉS de que firby.py ya cargó.
    """
    try:
        import firby as _firby_module
        existing = getattr(_firby_module, "SKILL_DEFINITIONS", {})
        added = 0
        for skill_id, skill_data in V9_SKILL_DEFINITIONS.items():
            if skill_id not in existing:
                existing[skill_id] = skill_data
                added += 1
        return added
    except ImportError:
        return 0


def v9_get_sector_profile(sector: str) -> Optional[Dict]:
    """Retorna el perfil profundo del sector, o None si no existe."""
    return V9_SECTOR_DEEP_PROFILES.get(sector)


def v9_get_sector_prompt_injection(sector: str) -> str:
    """
    Genera el bloque de prompt para el sector específico.
    Incluye perfil del cliente, frases clave y scripts de objeción.
    """
    profile = V9_SECTOR_DEEP_PROFILES.get(sector)
    if not profile:
        return ""

    lines = []

    client_profile = profile.get("client_profile", "")
    if client_profile:
        lines.append(client_profile.strip())

    key_phrases = profile.get("key_phrases", [])
    if key_phrases:
        lines.append("\nPREGUNTAS CLAVE PARA ESTE SECTOR:")
        for phrase in key_phrases[:5]:  # Solo 5 para no saturar el prompt
            lines.append(f"  · {phrase}")

    objections = profile.get("objection_scripts", {})
    if objections:
        lines.append("\nMANEJO DE OBJECIONES FRECUENTES:")
        for obj_id, script in list(objections.items())[:3]:  # Solo 3
            lines.append(f"  [{obj_id}]: {script}")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# FILTRO ANTI-ROBOT V9 — EXTENSIÓN DEL ANTIROBOT EXISTENTE
# Patrones adicionales identificados en auditoría de conversaciones reales
# ══════════════════════════════════════════════════════════════════════════════

# Patrones adicionales para AntiRobotFilter (se agregan a los existentes)
V9_ADDITIONAL_FORBIDDEN_EXACT: set = {
    # Patrones que escaparon al filtro V8
    "sin ningún inconveniente",
    "sin ningún problema",
    "quedo atento",
    "quedo pendiente",
    "le comento que",
    "me complace informarle",
    "me es grato comunicarle",
    "en atención a su solicitud",
    "adjunto le envío",
    "aprovecho para informarle",
    "de antemano agradezco",
    "espero su pronta respuesta",
    "cordial saludo",
    "atentamente",
    "quedo a su entera disposición",
    "de ser así",
    "en caso de requerir",
    "si tiene alguna duda adicional",
    "no dude en comunicarse",
    "estoy a sus órdenes",
    "a la orden",
    "¿gusta que le explique",
    "¿desea que le amplíe",
    "¿le gustaría que",
    "le hago saber que",
    "le informo que",
    "le comunico que",
    "le notifico que",
    "al respecto le comento",
    "en relación a su consulta",
    # Patrones que revelan estructura de chatbot
    "opción 1", "opción 2", "opción 3",
    "paso 1:", "paso 2:", "paso 3:",
    "primero,", "segundo,", "tercero,",
    "en primer lugar,", "en segundo lugar,",
    "por un lado,", "por otro lado,",
    # Frases que solo dice un bot corporativo
    "nuestro equipo especializado",
    "nuestros profesionales altamente capacitados",
    "contamos con la más alta tecnología",
    "somos líderes en",
    "nos distinguimos por",
    "nuestra misión es",
    "nos comprometemos a",
}

V9_ADDITIONAL_PATTERNS: List[str] = [
    # Respuestas que empiezan con "Entiendo que..." — clásico bot
    r"^entiendo\s+que\s+",
    r"^comprendo\s+que\s+",
    r"^me\s+imagino\s+que\s+",
    # Frases de confirmación robóticas
    r"he\s+tomado\s+nota\s+de\s+",
    r"he\s+registrado\s+tu\s+(solicitud|consulta|pregunta)",
    r"quedo\s+en\s+espera\s+de\s+",
    r"estoy\s+a\s+la\s+espera\s+de\s+",
    # Estructuras de lista disfrazadas
    r"\n\s*[-•]\s+\w",  # Bullets en respuesta de chat
    r"\n\s*\d+\.\s+\w",  # Listas numeradas en respuesta de chat
    # Cierres formulaicos
    r"hasta\s+pronto\s+y\s+(que\s+)?tenga",
    r"que\s+pase\s+(un\s+)?(excelente|buen)\s+día",
    r"feliz\s+(lunes|martes|miércoles|jueves|viernes|sábado|domingo)",
    r"que\s+disfrute\s+(el\s+)?(resto\s+de\s+)?su\s+día",
    # Frases de apertura robóticas adicionales
    r"bienvenido/a\s+a\s+",
    r"gracias\s+por\s+(comunicarte|escribirnos|contactarnos|tu\s+(mensaje|consulta|interés))",
    r"es\s+(un\s+)?placer\s+(atenderte|ayudarte|servirte)",
    # Frases de meta-conversación (bot hablando de la conversación)
    r"respecto\s+a\s+tu\s+(pregunta|consulta|solicitud)",
    r"en\s+respuesta\s+a\s+tu\s+(mensaje|consulta)",
    r"sobre\s+lo\s+que\s+(me\s+)?(preguntas|comentas|mencionas)",
]


def v9_enhance_anti_robot_filter(anti_robot_filter_instance) -> bool:
    """
    Agrega los patrones V9 adicionales a un AntiRobotFilter existente.
    Retorna True si se pudo parchear, False si falló.

    USO:
        from firby_v9_humanization import v9_enhance_anti_robot_filter
        # Después de init_v8_systems():
        if anti_robot_filter:
            v9_enhance_anti_robot_filter(anti_robot_filter)
    """
    try:
        import re as _re

        # Agregar frases exactas adicionales
        if hasattr(anti_robot_filter_instance, 'FORBIDDEN_EXACT'):
            anti_robot_filter_instance.FORBIDDEN_EXACT.update(
                V9_ADDITIONAL_FORBIDDEN_EXACT
            )

        # Agregar patrones compilados adicionales
        if hasattr(anti_robot_filter_instance, '_patterns_l2'):
            new_patterns = [
                _re.compile(p, _re.IGNORECASE | _re.MULTILINE)
                for p in V9_ADDITIONAL_PATTERNS
            ]
            anti_robot_filter_instance._patterns_l2.extend(new_patterns)

        return True
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
# CORRECTOR DE CALIDAD DE RESPUESTA V9
# Detecta y corrige patrones específicos que el V8 no cubría
# ══════════════════════════════════════════════════════════════════════════════

class ResponseQualityPatcher:
    """
    V9: Parches específicos de calidad basados en auditoría de respuestas reales.

    Patrones que V8 no corregía pero que se identificaron en producción:
    1. Respuestas que terminan en pregunta retórica que suena a script
    2. Uso de listas cuando debería ser prosa
    3. Mezcla de tuteo y ustedeo en la misma respuesta
    4. Confirmaciones dobles innecesarias
    5. Información que ya dio en el turno anterior
    """

    # Patrones de terminación robóticos que escapan al antirobot
    ROBOTIC_ENDINGS: List[Tuple[str, str]] = [
        # Patrón → Reemplazo sugerido (vacío = eliminar)
        (r'\.\s*¿Hay algo más en lo que pueda ayudarte[?!]?\s*$', ''),
        (r'\.\s*¿Tienes alguna otra (pregunta|consulta|duda)[?!]?\s*$', ''),
        (r'\.\s*¿Puedo ayudarte con algo más[?!]?\s*$', ''),
        (r'\.\s*¿Necesitas (más|alguna) información[?!]?\s*$', ''),
        (r'\s*Quedamos a tu (entera )?disposición\.?\s*$', ''),
        (r'\s*Estamos para servirte\.?\s*$', ''),
    ]

    # Detectar mezcla de tuteo/ustedeo (inconsistencia)
    TUTEO_MARKERS = ["te ", "tu ", "tus ", "tienes", "puedes", "quieres"]
    USTEDEO_MARKERS = ["usted", "le ", "su ", "sus ", "tiene ", "puede "]

    def __init__(self):
        self._compiled_endings = [
            (re.compile(pattern, re.IGNORECASE), replacement)
            for pattern, replacement in self.ROBOTIC_ENDINGS
        ]

    def fix_endings(self, text: str) -> str:
        """Elimina terminaciones robóticas del texto."""
        for pattern, replacement in self._compiled_endings:
            text = pattern.sub(replacement, text).strip()
        return text

    def detect_mixed_formality(self, text: str) -> bool:
        """Detecta si hay mezcla de tuteo y ustedeo."""
        text_lower = text.lower()
        has_tuteo = any(m in text_lower for m in self.TUTEO_MARKERS)
        has_ustedeo = "usted" in text_lower or (
            sum(1 for m in self.USTEDEO_MARKERS if m in text_lower) >= 2
        )
        return has_tuteo and has_ustedeo

    def fix_mixed_formality(self, text: str, archetype: str) -> str:
        """
        Corrige mezcla de tuteo/ustedeo según el arquetipo.
        Para arquetipos informales → tuteo. Para formales → ustedeo.
        """
        FORMAL_ARCHETYPES = {"profesional", "luxury", "experta",
                             "abogado_asistente", "recepcionista_medica"}

        if archetype in FORMAL_ARCHETYPES:
            # Convertir tuteo a ustedeo (básico)
            replacements = [
                (r'\bte\b', 'le'), (r'\btu\b', 'su'), (r'\btus\b', 'sus'),
                (r'\btienes\b', 'tiene'), (r'\bpuedes\b', 'puede'),
            ]
        else:
            # Convertir ustedeo a tuteo (básico)
            replacements = [
                (r'\busted\b', ''), (r'\ble\b', 'te'), (r'\bsu\b', 'tu'),
            ]

        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text.strip()

    def detect_double_question(self, text: str) -> bool:
        """Detecta si hay más de una pregunta en el mensaje."""
        return text.count('?') > 1

    def process(self, text: str, archetype: str = "amigable") -> str:
        """Aplica todos los parches de calidad V9."""
        if not text:
            return text

        # 1. Fix terminaciones robóticas
        text = self.fix_endings(text)

        # 2. Fix mezcla de formalidad (solo si se detecta)
        if self.detect_mixed_formality(text):
            text = self.fix_mixed_formality(text, archetype)

        return text.strip()

    def score_bonus(self, text: str) -> float:
        """
        Bonus al score de humanidad de AntiRobotFilter.score_humanness()
        para patrones positivos identificados en V9.
        """
        bonus = 0.0
        text_lower = text.lower()

        # Bonus por reacciones emocionales naturales
        positive_reactions = ["ay qué", "qué bacano", "qué bien", "ay sí", "uy qué"]
        if any(r in text_lower for r in positive_reactions):
            bonus += 0.08

        # Bonus por vocabulario paisa/colombiano auténtico
        v9_colombian = ["de una", "hágale", "pues", "fresco", "bacano",
                        "chévere", "bien o qué", "qué más"]
        hits = sum(1 for w in v9_colombian if w in text_lower)
        bonus += hits * 0.04

        # Bonus por respuesta muy corta y directa (señal de humano)
        words = len(text.split())
        if 3 <= words <= 10:
            bonus += 0.10

        # Penalización por listas en el texto
        if "\n-" in text or "\n•" in text or re.search(r'\n\d+\.', text):
            bonus -= 0.20

        return round(max(-0.3, min(0.3, bonus)), 3)


# ══════════════════════════════════════════════════════════════════════════════
# VOCABULARIO EXTENDIDO POR SECTOR — para prompts específicos
# ══════════════════════════════════════════════════════════════════════════════

SECTOR_VOCABULARY: Dict[str, Dict[str, List[str]]] = {
    "dental": {
        "servicios": ["limpieza", "blanqueamiento", "ortodoncia", "implante",
                      "extracción", "endodoncia", "carilla", "corona", "resina"],
        "dolores": ["me duele una muela", "tengo un dolor", "se me cayó un diente",
                    "me sangran las encías", "tengo sensibilidad", "se me partió",
                    "tengo caries", "se me movió", "me duele al morder"],
        "miedos_frecuentes": ["miedo a la aguja", "odio el dentista", "siempre me duele",
                               "el ruido de la fresa", "me da miedo el sillón"],
        "palabras_tranquilizar": ["anestesia local", "presión pero no dolor", "muy rápido",
                                   "sin complicaciones", "el dr te explica primero",
                                   "muchas personas llegan con ese miedo"],
    },
    "estetica": {
        "procedimientos": ["botox", "relleno", "ácido hialurónico", "mesoterapia",
                           "bótox", "lifting", "peel", "láser", "hidrafacial",
                           "perfilado", "rejuvenecimiento", "bioestimulación"],
        "zonas": ["frente", "entrecejo", "párpados", "pómulos", "labios",
                  "ojeras", "papada", "cuello", "nasolabiales", "código de barras"],
        "objeciones_típicas": ["que quede natural", "que no se note",
                                "que no me vea operada", "miedo que quede exagerado",
                                "ya me hicieron algo y quedé mal"],
        "cierres_poderosos": ["valoración gratuita con la doctora",
                               "la dra tiene mano muy natural",
                               "muchas pacientes del sector dicen lo mismo",
                               "el resultado lo defines tú con la especialista"],
    },
    "gimnasio": {
        "objetivos": ["bajar de peso", "ganar músculo", "mejorar resistencia",
                      "ponerse en forma", "rehabilitación", "perder barriga",
                      "definición", "cardio", "fuerza", "flexibilidad"],
        "obstáculos": ["no tengo tiempo", "nunca he ido", "ya lo intenté",
                       "no sé qué hacer", "me da pena", "tengo una lesión",
                       "trabajo muy tarde", "solo los fines de semana puedo"],
        "motivadores": ["evento próximo", "boda", "vacaciones en diciembre",
                         "el médico me dijo", "ya no aguanto verme así",
                         "quiero tener más energía"],
    },
    "psicologo": {
        "razones": ["ansiedad", "depresión", "estrés", "relación de pareja",
                    "duelo", "autoestima", "fobias", "ataques de pánico",
                    "problemas familiares", "trabajo", "no sé qué me pasa"],
        "barreras": ["me da pena", "no sé si lo necesito", "ya lo intenté antes",
                     "es muy caro", "no tengo tiempo", "lo veo como debilidad",
                     "no quiero que nadie sepa"],
        "normalizar": ["muchas personas sienten lo mismo",
                        "buscar ayuda es de valientes",
                        "la primera sesión es sin compromiso",
                        "es confidencial"],
    },
}


def get_sector_vocabulary(sector: str, category: str = None) -> Dict:
    """Retorna el vocabulario del sector, opcionalmente filtrado por categoría."""
    vocab = SECTOR_VOCABULARY.get(sector, {})
    if category:
        return {category: vocab.get(category, [])}
    return vocab


def build_sector_vocabulary_prompt(sector: str) -> str:
    """Genera instrucción de vocabulario para el sector dado."""
    vocab = SECTOR_VOCABULARY.get(sector)
    if not vocab:
        return ""

    lines = [f"VOCABULARIO NATURAL — {sector.upper()}:"]

    for category, words in vocab.items():
        if words and len(lines) < 8:  # Limitar para no saturar el prompt
            sample = words[:6]  # Solo primeros 6
            lines.append(f"  {category}: {', '.join(sample)}")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES DE TESTING Y DEBUGGING
# ══════════════════════════════════════════════════════════════════════════════

def test_emotional_detection(messages: List[str]) -> Dict[str, str]:
    """
    Utilidad de testing: detecta la emoción en una lista de mensajes.
    Útil para verificar que el motor funciona correctamente.
    
    Uso:
        results = test_emotional_detection([
            "me da miedo que quede exagerado",
            "está muy caro",
            "ya fui a otro lado y quedé mal",
        ])
        for msg, emotion in results.items():
            print(f"'{msg}' → {emotion}")
    """
    engine = EmotionalMirrorEngine()
    return {msg: (engine.detect_emotion(msg) or "NINGUNA") for msg in messages}


def test_persona_detection(messages: List[str]) -> Dict[str, str]:
    """
    Utilidad de testing: detecta el arquetipo de cliente en una lista de mensajes.
    
    Uso:
        results = test_persona_detection([
            "cuándo puedo ir hoy mismo",
            "qué incluye exactamente y cuántas sesiones necesito",
            "siempre lo quise hacer, por fin me animé",
        ])
    """
    detector = ClientPersonaDetector()
    return {msg: (detector.detect(msg) or "NO_DETECTADO") for msg in messages}


def run_v9_diagnostics() -> Dict[str, Any]:
    """
    Ejecuta diagnósticos de todos los sistemas V9.
    Retorna reporte de estado.
    
    Uso:
        report = run_v9_diagnostics()
        print(report)
    """
    results = {}

    # Test EmotionalMirrorEngine
    try:
        engine = EmotionalMirrorEngine()
        test_result = engine.detect_emotion("me da miedo que quede exagerado")
        results["EmotionalMirrorEngine"] = {
            "status": "OK",
            "test_detection": test_result,
            "total_emotions": len(engine.EMOTIONAL_SIGNALS),
        }
    except Exception as e:
        results["EmotionalMirrorEngine"] = {"status": "ERROR", "error": str(e)}

    # Test ClientPersonaDetector
    try:
        detector = ClientPersonaDetector()
        test_result = detector.detect("cuándo puedo ir hoy mismo de una")
        results["ClientPersonaDetector"] = {
            "status": "OK",
            "test_detection": test_result,
            "total_personas": len(detector.PERSONA_PROFILES),
        }
    except Exception as e:
        results["ClientPersonaDetector"] = {"status": "ERROR", "error": str(e)}

    # Test TimeContextualizer
    try:
        tc = TimeContextualizer()
        profile = tc.get_current_profile()
        results["TimeContextualizer"] = {
            "status": "OK",
            "current_period": profile.get("id"),
            "recommended_greeting": tc.get_recommended_greeting(),
        }
    except Exception as e:
        results["TimeContextualizer"] = {"status": "ERROR", "error": str(e)}

    # Test ConversationRhythmAnalyzer
    try:
        ra = ConversationRhythmAnalyzer()
        test_history = [
            {"role": "user", "content": "hola"},
            {"role": "assistant", "content": "hola qué más"},
            {"role": "user", "content": "quiero saber sobre botox"},
        ]
        profile = ra.analyze("test_chat", test_history)
        results["ConversationRhythmAnalyzer"] = {
            "status": "OK",
            "test_style": profile.get("style"),
            "avg_words": profile.get("avg_words"),
        }
    except Exception as e:
        results["ConversationRhythmAnalyzer"] = {"status": "ERROR", "error": str(e)}

    # Test SectorClosingScripts
    try:
        sc = SectorClosingScripts()
        test_script = sc.get_script("dental", "primera_cita")
        results["SectorClosingScripts"] = {
            "status": "OK",
            "total_sectors": len(sc.SCRIPTS),
            "test_script_available": test_script is not None,
        }
    except Exception as e:
        results["SectorClosingScripts"] = {"status": "ERROR", "error": str(e)}

    # Test ResponseQualityPatcher
    try:
        patcher = ResponseQualityPatcher()
        test_text = "Claro que sí, con mucho gusto. ¿Hay algo más en lo que pueda ayudarte?"
        patched = patcher.process(test_text)
        results["ResponseQualityPatcher"] = {
            "status": "OK",
            "test_input": test_text[:50],
            "test_output": patched[:50],
            "changed": test_text != patched,
        }
    except Exception as e:
        results["ResponseQualityPatcher"] = {"status": "ERROR", "error": str(e)}

    # Resumen
    ok_count = sum(1 for r in results.values() if r.get("status") == "OK")
    results["SUMMARY"] = {
        "systems_ok": ok_count,
        "systems_total": len(results) - 1,
        "new_archetypes": len(V9_PERSONALITY_ARCHETYPES),
        "new_skills": len(V9_SKILL_DEFINITIONS),
        "deep_sector_profiles": len(V9_SECTOR_DEEP_PROFILES),
        "version": "V9.0",
    }

    return results


# ══════════════════════════════════════════════════════════════════════════════
# INSTRUCCIONES COMPLETAS DE INTEGRACIÓN
# ══════════════════════════════════════════════════════════════════════════════


import httpx
from fastapi import FastAPI, Request, Response, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ── Helpers globales ──────────────────────────────────────────────────────────

def _parse_admin_ids(raw) -> list:
    """
    Parsea admin_chat_ids de forma segura.
    Maneja str JSON, lista, None — nunca lanza excepción.
    Centraliza la lógica que antes estaba duplicada 10+ veces en el código.
    """
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw]
    if isinstance(raw, str):
        try:
            result = json.loads(raw)
            return [str(x) for x in result] if isinstance(result, list) else []
        except Exception:
            return []
    return []


def _split_env_values(raw) -> list:
    """Divide una variable de entorno tipo lista en valores útiles, preservando orden."""
    if not raw:
        return []
    if isinstance(raw, (list, tuple, set)):
        values = [str(x).strip() for x in raw if str(x).strip()]
    else:
        text = str(raw).strip()
        if not text:
            return []
        parsed = None
        if text.startswith("["):
            try:
                parsed = json.loads(text)
            except Exception:
                parsed = None
        if isinstance(parsed, list):
            values = [str(x).strip() for x in parsed if str(x).strip()]
        else:
            values = [part.strip() for part in re.split(r"[\n,]+", text) if part.strip()]
    deduped = []
    seen = set()
    for value in values:
        if value not in seen:
            deduped.append(value)
            seen.add(value)
    return deduped


def _collect_env_series(base_name: str, *extra_names: str) -> list:
    """Recolecta BASE, BASE_2..BASE_N y también listas BASES/BASE_LIST."""
    pattern = re.compile(rf"^{re.escape(base_name)}(?:_(\d+))?$")
    ranked = []
    for env_name, env_value in os.environ.items():
        match = pattern.match(env_name)
        if not match:
            continue
        rank = int(match.group(1) or 1)
        for value in _split_env_values(env_value):
            ranked.append((rank, value))
    ranked.sort(key=lambda item: item[0])
    ordered = [value for _, value in ranked]
    for alias in extra_names or (f"{base_name}S", f"{base_name}_LIST"):
        ordered.extend(_split_env_values(os.getenv(alias, "")))
    deduped = []
    seen = set()
    for value in ordered:
        if value and value not in seen:
            deduped.append(value)
            seen.add(value)
    return deduped

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN GLOBAL AVANZADA
# ═══════════════════════════════════════════════════════════════════════════════

