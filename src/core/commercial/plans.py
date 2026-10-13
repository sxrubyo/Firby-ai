"""
Canonical Source of Truth for Firby Commercial Plans, Pricing, and Guarantees.
Zero emojis, exact pricing across landing, chat, backend, and database.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class CommercialPlan:
    id: str
    name: str
    price_cop: int
    price_usd_approx: int
    formatted_price_cop: str
    formatted_price_usd: str
    billing_period: str
    tagline: str
    features: List[str]
    interactions_limit: int
    trial_days: int = 7
    trial_terms: str = "Prueba 7 días gratis. Cancela cuando quieras en 1 clic."
    is_popular: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "price_cop": self.price_cop,
            "price_usd_approx": self.price_usd_approx,
            "formatted_price_cop": self.formatted_price_cop,
            "formatted_price_usd": self.formatted_price_usd,
            "billing_period": self.billing_period,
            "tagline": self.tagline,
            "features": list(self.features),
            "interactions_limit": self.interactions_limit,
            "trial_days": self.trial_days,
            "trial_terms": self.trial_terms,
            "is_popular": self.is_popular,
        }


COMMERCIAL_PLANS: Dict[str, CommercialPlan] = {
    "starter": CommercialPlan(
        id="starter",
        name="Plan Starter",
        price_cop=290000,
        price_usd_approx=72,
        formatted_price_cop="$290.000 COP / mes",
        formatted_price_usd="~$72 USD",
        billing_period="mensual",
        tagline="Operador digital autónomo para tu sitio web. Resuelve trámites, califica prospectos y ejecuta acciones en tiempo real.",
        features=[
            "Operador digital autónomo en tu sitio web (instalación en 1 línea de código)",
            "Sincronización directa con 1 agenda de Google Calendar (consulta de disponibilidad y agendamiento autónomo)",
            "Captura estructurada y calificación de prospectos (nombre, WhatsApp verificado y requerimiento)",
            "Confirmación y registro de cada cita en tiempo real sin intervención humana",
            "Base de conocimiento propia de tu negocio (servicios, horarios, preguntas frecuentes y políticas)",
            "Panel de control con historial de conversaciones, citas confirmadas y contactos generados",
            "Hasta 800 interacciones resueltas al mes"
        ],
        interactions_limit=800,
        trial_days=7,
        trial_terms="Prueba 7 días gratis. Cancela cuando quieras en 1 clic.",
        is_popular=False,
    ),
    "pro": CommercialPlan(
        id="pro",
        name="Plan Pro",
        price_cop=490000,
        price_usd_approx=125,
        formatted_price_cop="$490.000 COP / mes",
        formatted_price_usd="~$125 USD",
        billing_period="mensual",
        tagline="Autonomía avanzada en tu web con línea ejecutiva de alertas, visto bueno y control por WhatsApp para el dueño del negocio.",
        features=[
            "Todo lo incluido en el Plan Starter",
            "Línea privada en WhatsApp para el dueño: alertas de eventos clave y visto bueno para excepciones fuera de política",
            "Control operativo por WhatsApp: consulta métricas, pide resúmenes o bloquea agendas hablándole directamente a tu IA",
            "Reprogramación y cancelación autónoma en Google Calendar con validación de identidad por código OTP",
            "Reglas de decisión configurables: define qué resuelve de forma autónoma y qué requiere tu aprobación previa",
            "Atención con memoria contextual del historial de cada cliente para personalizar respuestas",
            "Hasta 2.500 interacciones resueltas al mes"
        ],
        interactions_limit=2500,
        trial_days=7,
        trial_terms="Prueba 7 días gratis. Cancela cuando quieras en 1 clic.",
        is_popular=True,
    ),
    "equipos": CommercialPlan(
        id="equipos",
        name="Plan Equipos",
        price_cop=890000,
        price_usd_approx=225,
        formatted_price_cop="$890.000 COP / mes",
        formatted_price_usd="~$225 USD",
        billing_period="mensual",
        tagline="Infraestructura para empresas con múltiples especialistas, áreas de atención o sedes.",
        features=[
            "Todo lo incluido en el Plan Pro",
            "Gestión concurrente de hasta 5 agendas o sedes independientes",
            "Roles de equipo y permisos multi-administrador",
            "Webhooks personalizados e integraciones CRM (HubSpot, Salesforce)",
            "Hasta 7.500 interacciones resueltas al mes"
        ],
        interactions_limit=7500,
        trial_days=7,
        trial_terms="Prueba 7 días gratis. Cancela cuando quieras en 1 clic.",
        is_popular=False,
    ),
}


def get_all_plans() -> List[CommercialPlan]:
    """Retorna la lista ordenada de planes comerciales oficiales."""
    return list(COMMERCIAL_PLANS.values())


def get_plan_by_id(plan_id: str) -> Optional[CommercialPlan]:
    """Busca un plan por su ID normalizado."""
    if not plan_id:
        return None
    normalized = plan_id.strip().lower()
    return COMMERCIAL_PLANS.get(normalized)


def get_plans_dict() -> Dict[str, Any]:
    """Retorna representación serializable para APIs."""
    return {
        "ok": True,
        "currency": "COP",
        "trial_policy": {
            "trial_days": 7,
            "terms": "Prueba 7 días gratis. Cancela cuando quieras en 1 clic.",
            "charge_during_trial": 0,
        },
        "plans": [p.to_dict() for p in get_all_plans()],
    }


def get_pricing_summary_text() -> str:
    """Texto unificado canónico para respuestas del agente conversacional sin negritas y con respiración visual."""
    starter = COMMERCIAL_PLANS["starter"]
    pro = COMMERCIAL_PLANS["pro"]
    equipos = COMMERCIAL_PLANS["equipos"]
    return (
        f"Nuestros planes oficiales son:\n\n"
        f"- Starter: {starter.formatted_price_cop} ({starter.formatted_price_usd}): operador digital autónomo 24/7 en su sitio web, sincronización con Google Calendar y hasta {starter.interactions_limit} interacciones al mes.\n\n"
        f"- Pro: {pro.formatted_price_cop} ({pro.formatted_price_usd}) [Más Popular]: autonomía avanzada en web, reprogramación por OTP y línea ejecutiva por WhatsApp para el dueño del negocio (hasta {pro.interactions_limit} interacciones al mes).\n\n"
        f"- Equipos: {equipos.formatted_price_cop} ({equipos.formatted_price_usd}): para empresas con múltiples sedes o especialistas, hasta 5 agendas concurrentes, roles de equipo, webhooks e integraciones CRM.\n\n"
        f"Todos los planes incluyen prueba de 7 días gratis con cancelación en 1 clic sin permanencia."
    )


def get_plan_specific_text(plan_id: str, is_most_complete: bool = False) -> str:
    """Texto unificado canónico para un plan específico sin negritas y con párrafos claros."""
    plan = get_plan_by_id(plan_id)
    if not plan:
        return get_pricing_summary_text()
    if is_most_complete or (plan_id == "equipos" and is_most_complete):
        return (
            f"El plan más completo es el Plan Equipos, con un costo de {plan.formatted_price_cop} ({plan.formatted_price_usd}).\n\n"
            f"Está diseñado para empresas con múltiples especialistas, áreas de atención o sedes:\n\n"
            f"- Gestión concurrente de hasta 5 agendas independientes.\n\n"
            f"- Roles de equipo, webhooks personalizados e integraciones CRM (HubSpot, Salesforce).\n\n"
            f"- Hasta {plan.interactions_limit} interacciones al mes.\n\n"
            f"Incluye {plan.trial_terms}"
        )
    return (
        f"El Plan {plan.name.replace('Plan ', '')} tiene un costo de {plan.formatted_price_cop} ({plan.formatted_price_usd}).\n\n"
        f"{plan.tagline}\n\n"
        f"Incluye prueba de 7 días gratis con cancelación en 1 clic sin permanencia."
    )
