# -*- coding: utf-8 -*-
"""
Firby AI — Knowledge Grounding & Boundary Engine
================================================
Gestiona el conocimiento oficial verificado de Firby y los límites de información.
Evita activamente la alucinación de datos no existentes y prohíbe desviar
preguntas directas hacia discursos comerciales o ventas no solicitadas.
"""

from __future__ import annotations
import re
from typing import Dict, Any, Optional, Tuple, List
from src.core.operator.models import UIAction, UIActionType, ActionChip, UserIntentCategory
from src.core.commercial.plans import COMMERCIAL_PLANS


OFFICIAL_KNOWLEDGE: Dict[str, Any] = {
    "product_name": "Firby",
    "product_type": "Operador digital autónomo para sitios web",
    "tagline": "Un operador en tu web que hace el trabajo por ti",
    "core_purpose": (
        "Vive en el sitio web de empresas y negocios para atender a los visitantes "
        "en tiempo real, resolver dudas comerciales con las políticas oficiales de la empresa "
        "y agendar citas confirmadas en Google Calendar y base de datos sin trabajo manual."
    ),
    "two_channels_rule": {
        "web": (
            "Atiende a los visitantes y pacientes en tiempo real a través del widget flotante. "
            "Resuelve consultas y agenda citas. Firby NUNCA atiende visitantes por WhatsApp."
        ),
        "whatsapp": (
            "Línea ejecutiva privada y continua (+57 324 369 9856) ÚNICA Y EXCLUSIVAMENTE "
            "con el dueño del negocio. Envía reportes diarios, alertas de citas confirmadas y "
            "solicita visto bueno para excepciones comerciales fuera de política."
        )
    },
    "installation": {
        "summary": "Se instala en menos de 1 minuto copiando y pegando una sola línea de código en el encabezado de tu web.",
        "platforms": ["WordPress", "Shopify", "Webflow", "WooCommerce", "Wix", "React", "Next.js", "HTML a medida"],
        "calendar_sync": "Se conecta de forma nativa con Google Calendar para verificar disponibilidad real y bloquear cupos confirmados."
    },
    "pricing": {
        "starter": {
            "price_cop": COMMERCIAL_PLANS["starter"].formatted_price_cop,
            "price_usd": COMMERCIAL_PLANS["starter"].formatted_price_usd,
            "features": f"Operador autónomo 24/7 en tu web, atención comercial y agendamiento confirmado de hasta {COMMERCIAL_PLANS['starter'].interactions_limit} interacciones y citas al mes."
        },
        "pro": {
            "price_cop": COMMERCIAL_PLANS["pro"].formatted_price_cop,
            "price_usd": COMMERCIAL_PLANS["pro"].formatted_price_usd,
            "features": f"Autonomía avanzada, reprogramación autónoma con código OTP, supervisión operativa y reglas de gobernanza a la medida (hasta {COMMERCIAL_PLANS['pro'].interactions_limit} interacciones al mes)."
        },
        "equipos": {
            "price_cop": COMMERCIAL_PLANS["equipos"].formatted_price_cop,
            "price_usd": COMMERCIAL_PLANS["equipos"].formatted_price_usd,
            "features": f"Para empresas con múltiples especialistas o sedes. Hasta 5 agendas concurrentes, roles de equipo y webhooks (hasta {COMMERCIAL_PLANS['equipos'].interactions_limit} interacciones al mes)."
        },
        "trial": "7 días de prueba gratis con acceso completo. Cancelación en 1 clic desde el panel cuando quieras sin penalidades. $0 cobrados durante la prueba."
    },
    "security": {
        "summary": "Cero improvisaciones, verificación de identidad por OTP de 6 dígitos, aislamiento estricto de datos y visto bueno humano para excepciones."
    },
    "pages": {
        "sobre_nosotros": "/sobre-nosotros",
        "faq": "/faq",
        "terminos": "/terminos",
        "privacidad": "/politica-de-privacidad"
    },
    # LÍMITES ESTRICTOS (DATOS NO EXISTENTES OFICIALMENTE)
    "unknown_entities": [
        "ceo", "nombre del ceo", "quien es el ceo", "quién es el ceo", "director ejecutivo",
        "fundador personal", "creador personal", "dueño de firby", "salario", "inversionistas privados"
    ]
}


class GroundingEngine:
    """Motor de análisis de límites y respuestas directas fundamentadas."""

    @classmethod
    def detect_intent(cls, message: str) -> UserIntentCategory:
        """Determina la categoría de intención del usuario."""
        m = message.lower().strip()

        # 1. Saludo puro
        if re.match(r'^(hola|buenas|buenos d[ií]as|buenas tardes|buenas noches|hey|qu[eé] tal)\b[!\.\?]?$', m):
            return UserIntentCategory.GREETING

        # 2. Preguntas sobre CEO o datos desconocidos
        if any(term in m for term in ["quien es el ceo", "quién es el ceo", "nombre del ceo", "quien es el director", "quién es el director", "quien es el dueño de firby", "quién es el dueño de firby"]):
            return UserIntentCategory.UNKNOWN_BOUNDARY

        # 3. Preguntas sobre creadores / equipo
        if any(term in m for term in ["quien creo", "quién creó", "quienes crearon", "quiénes crearon", "conocer al equipo", "sobre ustedes", "sobre nosotros", "conocer el equipo"]):
            return UserIntentCategory.TEAM_INQUIRY

        # 4. Solicitud directa de navegación
        if any(term in m for term in ["llevame a", "llévame a", "quiero ir a", "muestrame los", "muéstrame los", "ir a planes", "ir a precios", "ver planes", "ver precios"]):
            return UserIntentCategory.NAVIGATION_REQUEST

        # 5. Cómo funciona
        if any(term in m for term in ["como funciona", "cómo funciona", "que hace firby", "qué hace firby", "explicame como funciona", "explícame cómo funciona"]):
            return UserIntentCategory.HOW_IT_WORKS

        # 6. Precios y planes
        if any(term in m for term in ["cuanto cuesta", "cuánto cuesta", "precio", "precios", "planes", "tarifas", "costo", "mensualidad", "valor"]):
            return UserIntentCategory.PRICING_INQUIRY

        # 7. Instalación y soporte técnico
        if any(term in m for term in ["como lo instalo", "cómo lo instalo", "como se instala", "cómo se instala", "instalacion", "instalación", "wordpress", "shopify"]):
            return UserIntentCategory.SETUP_INQUIRY

        # 8. Agendamiento
        if any(term in m for term in ["agendar", "cita", "apartar", "reserva", "horario"]):
            return UserIntentCategory.BOOKING_REQUEST

        return UserIntentCategory.GENERAL

    @classmethod
    def get_grounded_response(
        cls,
        intent: UserIntentCategory,
        message: str,
        current_url: str = "/",
        current_section: str = "#hero"
    ) -> Optional[Tuple[List[str], Optional[UIAction], List[ActionChip], List[str]]]:
        """
        Retorna respuesta determinista si la intención corresponde a una regla
        de oro de honestidad, navegación o factual directo.
        Retorna (bubbles, ui_action, action_chips, string_chips).
        """
        m = message.lower().strip()

        # CASO 1: Desconocimiento honesto (CEO u otro dato no oficial)
        if intent == UserIntentCategory.UNKNOWN_BOUNDARY:
            bubbles = [
                "No tengo ese dato disponible todavía."
            ]
            action_chips = [
                ActionChip(label="Cómo funciona", action_type="navigate_to_section", action_target="#como-funciona"),
                ActionChip(label="Sobre nosotros", action_type="navigate_to", action_target="/sobre-nosotros"),
                ActionChip(label="Ver planes", action_type="navigate_to_section", action_target="#planes")
            ]
            chips = ["Cómo funciona", "Sobre nosotros", "Ver planes"]
            return bubbles, None, action_chips, chips

        # CASO 2: Creadores / Equipo / Sobre Nosotros
        if intent == UserIntentCategory.TEAM_INQUIRY:
            bubbles = [
                "Firby fue creado como una plataforma de operadores digitales autónomos para sitios web empresariales.",
                "Si deseas conocer a fondo nuestra visión, arquitectura y filosofía de operación, te puedo guiar a la página sobre nosotros."
            ]
            action_chips = [
                ActionChip(label="Conocer al equipo", action_type="navigate_to", action_target="/sobre-nosotros"),
                ActionChip(label="Cómo funciona", action_type="navigate_to_section", action_target="#como-funciona")
            ]
            chips = ["Conocer al equipo", "Cómo funciona"]
            return bubbles, None, action_chips, chips

        # CASO 3: Cómo funciona (Navegación + Demostración Copiloto)
        if intent == UserIntentCategory.HOW_IT_WORKS:
            bubbles = [
                "Te lo muestro.",
                "Firby vive en tu sitio web para recibir visitantes, responder consultas con tus políticas oficiales y confirmar citas en tu calendario 24/7. Además, mantiene una línea privada por WhatsApp con el dueño para alertas y visto bueno."
            ]
            ui_action = UIAction(
                type=UIActionType.NAVIGATE_TO_SECTION,
                target="#como-funciona",
                label="Sección Cómo Funciona"
            )
            action_chips = [
                ActionChip(label="Cómo se instala", action_type="navigate_to_section", action_target="#como-funciona"),
                ActionChip(label="Ver planes", action_type="navigate_to_section", action_target="#planes"),
                ActionChip(label="Seguridad y control", action_type="navigate_to_section", action_target="#seguridad-cumplimiento")
            ]
            chips = ["Cómo se instala", "Ver planes", "Seguridad y control"]
            return bubbles, ui_action, action_chips, chips

        # CASO 4: Precios y planes (Respuesta directa primero, sin desvío agresivo)
        if intent == UserIntentCategory.PRICING_INQUIRY:
            bubbles = [
                "Nuestros planes comienzan desde $290.000 COP al mes (~$72 USD) e incluyen el operador autónomo 24/7 en tu web con 7 días de prueba gratis.",
                "Si quieres, puedo mostrarte qué incluye cada plan en la pantalla."
            ]
            action_chips = [
                ActionChip(label="Ver planes", action_type="navigate_to_section", action_target="#planes"),
                ActionChip(label="Activar 7 días gratis", action_type="navigate_to", action_target="/sign-up"),
                ActionChip(label="Hablar con el equipo", action_type="navigate_to", action_target="#contacto")
            ]
            chips = ["Ver planes", "Activar 7 días gratis", "Hablar con el equipo"]
            return bubbles, None, action_chips, chips

        # CASO 5: Instalación
        if intent == UserIntentCategory.SETUP_INQUIRY:
            bubbles = [
                "Se instala en menos de un minuto copiando y pegando una sola línea de código en tu sitio web.",
                "Es compatible de inmediato con WordPress, Shopify, Webflow, React o cualquier desarrollo a medida, sincronizándose con tu Google Calendar."
            ]
            action_chips = [
                ActionChip(label="Ver cómo funciona", action_type="navigate_to_section", action_target="#como-funciona"),
                ActionChip(label="Ver planes", action_type="navigate_to_section", action_target="#planes")
            ]
            chips = ["Ver cómo funciona", "Ver planes"]
            return bubbles, None, action_chips, chips

        # CASO 6: Saludo cordial limpio
        if intent == UserIntentCategory.GREETING:
            bubbles = [
                "Hola. Soy Firby, el operador digital de este sitio.",
                "Puedo orientarte sobre cómo opera la plataforma, mostrarte secciones de la web o resolver cualquier duda que tengas."
            ]
            action_chips = [
                ActionChip(label="Cómo funciona", action_type="navigate_to_section", action_target="#como-funciona"),
                ActionChip(label="Ver planes", action_type="navigate_to_section", action_target="#planes"),
                ActionChip(label="Sobre nosotros", action_type="navigate_to", action_target="/sobre-nosotros")
            ]
            chips = ["Cómo funciona", "Ver planes", "Sobre nosotros"]
            return bubbles, None, action_chips, chips

        # CASO 7: Solicitud expresa de navegación
        if intent == UserIntentCategory.NAVIGATION_REQUEST:
            target_sec = "#planes"
            if any(k in m for k in ["como funciona", "cómo funciona"]):
                target_sec = "#como-funciona"
            elif any(k in m for k in ["equipo", "sobre nosotros"]):
                target_sec = "#sobre-nosotros"
            elif any(k in m for k in ["seguridad"]):
                target_sec = "#seguridad-cumplimiento"

            bubbles = [
                "Con gusto, te llevo a la sección correspondiente."
            ]
            ui_action = UIAction(
                type=UIActionType.NAVIGATE_TO_SECTION,
                target=target_sec,
                label=f"Navegación a {target_sec}"
            )
            chips = ["Cómo funciona", "Ver planes", "Sobre nosotros"]
            action_chips = [
                ActionChip(label="Cómo funciona", action_type="navigate_to_section", action_target="#como-funciona"),
                ActionChip(label="Ver planes", action_type="navigate_to_section", action_target="#planes")
            ]
            return bubbles, ui_action, action_chips, chips

        return None
