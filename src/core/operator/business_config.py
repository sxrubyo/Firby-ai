# -*- coding: utf-8 -*-
"""
Firby AI — Universal Business Configuration & Permissions System
================================================================
Separa estrictamente:
1. PLATFORM CAPABILITIES: Lo que Firby como plataforma sabe hacer a nivel técnico.
2. CONNECTED INTEGRATIONS: Qué servicios externos (Google Calendar, CRM, WhatsApp) tiene conectados este negocio.
3. TOOL PERMISSIONS: Qué herramientas tiene autorizadas y habilitadas este agente en particular.
4. BUSINESS KNOWLEDGE & POLICIES: El conocimiento oficial verificado del sitio y sus reglas.
5. STRUCTURED RULES & BEHAVIOR EXAMPLES: Reglas y ejemplos enseñados por el dueño en el Workspace.

Si un negocio no tiene Calendar conectado o no tiene la herramienta de agendamiento habilitada,
el agente NUNCA asumirá que puede agendar ni preguntará "¿mañana o tarde?".
Responderá con las políticas y canales oficiales definidos por la empresa.
"""

from __future__ import annotations
import re
import json
import sqlite3
import logging
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from src.core.commercial.plans import COMMERCIAL_PLANS

log = logging.getLogger("firby.operator.business_config")


class PlatformCapability(str, Enum):
    """Capacidades técnicas globales provistas por la plataforma Firby."""
    WEB_NAVIGATION = "web_navigation"
    HIGHLIGHT_UI = "highlight_ui"
    QUERY_KNOWLEDGE = "query_business_knowledge"
    CALENDAR_AVAILABILITY = "check_availability"
    CALENDAR_BOOKING = "book_appointment"
    CRM_LEAD_CAPTURE = "capture_lead"
    OWNER_ESCALATION = "escalate_to_human"


@dataclass
class ToolPermission:
    """Permiso explícito y estado de una herramienta para una instancia de negocio."""
    name: str
    enabled: bool = False
    requires_authorization: bool = False
    disabled_message: str = "Esta función no está habilitada para este sitio web."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "requires_authorization": self.requires_authorization,
            "disabled_message": self.disabled_message
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ToolPermission:
        return cls(
            name=d.get("name", ""),
            enabled=d.get("enabled", False),
            requires_authorization=d.get("requires_authorization", False),
            disabled_message=d.get("disabled_message", "Esta función no está habilitada.")
        )


@dataclass
class ConnectedIntegrations:
    """Integraciones de infraestructura efectivamente vinculadas por el cliente."""
    google_calendar: bool = False
    whatsapp_owner: bool = False
    crm_system: bool = False
    database_sync: bool = True
    email_gateway: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ConnectedIntegrations:
        return cls(**{k: v for k, v in d.items() if k in cls.__annotations__})


@dataclass
class BusinessIdentity:
    """Identidad y naturaleza del negocio."""
    name: str
    legal_name: str
    industry: str
    description: str
    website_url: str
    tone_and_voice: str = "profesional, cálido, directo y ejecutivo estilo Sierra AI"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BusinessIdentity:
        return cls(**{k: v for k, v in d.items() if k in cls.__annotations__})


@dataclass
class OfficialInfo:
    """Información oficial verificada del negocio."""
    locations: List[str] = field(default_factory=list)
    contact_email: str = ""
    executive_phone: str = ""
    operating_hours: str = ""
    team_overview: str = ""
    # Atributos explícitamente no listados / internos (el agente debe responder con honestidad que no están disponibles)
    unlisted_attributes: List[str] = field(default_factory=lambda: [
        "ceo", "director_ejecutivo", "dueño_personal", "salarios", "inversionistas_privados"
    ])

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> OfficialInfo:
        return cls(**{k: v for k, v in d.items() if k in cls.__annotations__})


@dataclass
class ServiceItem:
    """Servicio o tratamiento ofrecido por el negocio."""
    id: str
    name: str
    description: str
    price_cop: Optional[int] = None
    price_usd: Optional[float] = None
    duration_minutes: int = 30
    requires_consultation: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ServiceItem:
        return cls(**{k: v for k, v in d.items() if k in cls.__annotations__})


@dataclass
class PricingTier:
    """Nivel de precio o plan comercial."""
    id: str
    name: str
    price_cop: str
    price_usd: str
    billing_period: str
    features: List[str] = field(default_factory=list)
    trial_days: int = 0
    trial_terms: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> PricingTier:
        return cls(**{k: v for k, v in d.items() if k in cls.__annotations__})


@dataclass
class BusinessPolicy:
    """Políticas comerciales, operativas y de privacidad."""
    booking_policy: str
    cancellation_policy: str
    data_privacy_url: str
    exception_approval_process: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BusinessPolicy:
        return cls(**{k: v for k, v in d.items() if k in cls.__annotations__})


@dataclass
class NavigationResource:
    """Página o sección accesible del sitio web con su propósito."""
    id: str
    target: str  # e.g. "/sobre-nosotros" o "#planes"
    label: str
    description: str
    relevance_keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> NavigationResource:
        return cls(**{k: v for k, v in d.items() if k in cls.__annotations__})


@dataclass
class StructuredRule:
    """Regla o directriz operativa enseñada por el propietario en el Workspace."""
    id: str
    category: str  # policy, tone, tool_permission, factual_knowledge, behavior
    trigger_condition: str
    directive: str
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> StructuredRule:
        return cls(**{k: v for k, v in d.items() if k in cls.__annotations__})


@dataclass
class BehaviorExample:
    """Ejemplo ilustrativo de comportamiento (few-shot) enseñado en el Workspace."""
    user_query: str
    assistant_response: str
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BehaviorExample:
        return cls(**{k: v for k, v in d.items() if k in cls.__annotations__})


@dataclass
class BusinessConfig:
    """Configuración Integral de Negocio para el Agente Operativo."""
    tenant_id: str
    identity: BusinessIdentity
    official_info: OfficialInfo
    services: List[ServiceItem] = field(default_factory=list)
    pricing_tiers: List[PricingTier] = field(default_factory=list)
    policies: BusinessPolicy = field(default_factory=lambda: BusinessPolicy(
        booking_policy="Confirmación en línea sujeta a disponibilidad de agenda.",
        cancellation_policy="Cancelación sin costo hasta 24 horas antes.",
        data_privacy_url="/politica-de-privacidad",
        exception_approval_process="Requiere visto bueno del dueño del negocio."
    ))
    navigation_resources: List[NavigationResource] = field(default_factory=list)
    connected_integrations: ConnectedIntegrations = field(default_factory=ConnectedIntegrations)
    tool_permissions: Dict[str, ToolPermission] = field(default_factory=dict)
    operational_limits: List[str] = field(default_factory=lambda: [
        "No prometer descuentos no establecidos en la lista oficial de precios.",
        "No inventar información sobre directivos, inversionistas o datos privados no listados.",
        "No procesar datos bancarios ni números de tarjeta en el chat conversacional.",
        "Acciones fuera de política estándar deben ser escaladas al dueño para visto bueno."
    ])
    custom_rules: List[StructuredRule] = field(default_factory=list)
    few_shot_examples: List[BehaviorExample] = field(default_factory=list)
    employee_role: str = "recepcionista"
    active_roles: List[str] = field(default_factory=lambda: ["recepcionista", "closer_ventas", "soporte_knowledge"])
    custom_prompt: str = ""
    voice_accent: str = "general"
    fts5_enabled: bool = True
    growth_settings: Dict[str, Any] = field(default_factory=dict)

    @property
    def allowed_tools(self) -> List[str]:
        """Retorna únicamente las herramientas habilitadas y autorizadas para este negocio."""
        return [name for name, perm in self.tool_permissions.items() if perm.enabled]

    def is_tool_authorized(self, tool_name: str) -> Tuple[bool, Optional[str]]:
        """Comprueba si una herramienta específica está autorizada y habilitada."""
        # Normalizar alias bidireccional
        alias_name = "web_navigation" if tool_name == "navigate_web" else ("navigate_web" if tool_name == "web_navigation" else tool_name)
        perm = self.tool_permissions.get(tool_name) or self.tool_permissions.get(alias_name)
        if not perm:
            return False, f"La herramienta '{tool_name}' no existe en la configuración de este negocio."
        if not perm.enabled:
            return False, perm.disabled_message
        return True, None

    def is_tool_allowed(self, tool_name: str) -> Tuple[bool, Optional[str]]:
        """Alias para is_tool_authorized."""
        return self.is_tool_authorized(tool_name)

    def find_navigation_target(self, query: str) -> Optional[NavigationResource]:
        """Encuentra el recurso de navegación más adecuado para la consulta del usuario."""
        q = query.lower()
        for res in self.navigation_resources:
            if any(k in q for k in res.relevance_keywords):
                return res
        return None

    def is_attribute_unlisted(self, attribute_name: str) -> bool:
        """Verifica si un atributo consultado no está listado en la configuración oficial o es confidencial."""
        attr = attribute_name.lower().strip()
        attr_under = "_".join(re.sub(r'[^\w\s]', ' ', attr).split())
        for u in self.official_info.unlisted_attributes:
            u_clean = u.lower().replace(" ", "_")
            if u_clean in attr_under:
                return True
        restricted_patterns = [
            r'\b(?:ceo|director\s+ejecutivo|due[ñn]o\s+de\s+la\s+empresa)\b',
            r'\b(?:salarios?|sueldos?|inversionistas?)\b',
            r'\b(?:tarjetas?\s*(?:de\s+cr[eé]dito|de\s+d[eé]bito)?|cvv|n[uú]mero\s+de\s+tarjeta)\b',
            r'\b(?:factur\w*|cu[aá]nto\s+(?:factur\w*|ingres\w*|ganan?|ganaron)|ingresos?\s+de\s+la\s+empresa)\b',
            r'\b(?:cliente\s+que\s+m[aá]s\s+paga|datos?\s+bancarios?|cuentas?\s+bancarias?)\b'
        ]
        return any(re.search(pat, attr) for pat in restricted_patterns)

    def is_confidential_query(self, query: str) -> bool:
        """Determina si la consulta involucra datos financieros o confidenciales de clientes o empresa."""
        q = query.lower()
        confidential_patterns = [
            r'\b(?:tarjeta\w*|cvv|n[uú]mero\s+de\s+tarjeta)\b',
            r'\b(?:factur\w*|cu[aá]nto\s+(?:factur\w*|ingres\w*|ganan?|ganaron)|ingresos?)\b',
            r'\b(?:datos?\s+bancarios?|cuentas?\s+bancarias?|pago\s+de\s+clientes?)\b',
            r'\b(?:cliente\s+que\s+m[aá]s\s+paga)\b'
        ]
        return any(re.search(pat, q) for pat in confidential_patterns)

    def add_structured_rule(self, rule: StructuredRule):
        """Agrega una regla estructurada enseñada en el Workspace."""
        # Reemplazar si ya existe con el mismo ID
        self.custom_rules = [r for r in self.custom_rules if r.id != rule.id]
        self.custom_rules.append(rule)

    def add_behavior_example(self, example: BehaviorExample):
        """Agrega un ejemplo de comportamiento (few-shot)."""
        self.few_shot_examples.append(example)

    def update_tool_permission(self, tool_name: str, enabled: bool, disabled_message: str = ""):
        """Actualiza el permiso de una herramienta."""
        perm = self.tool_permissions.get(tool_name)
        if perm:
            perm.enabled = enabled
            if disabled_message:
                perm.disabled_message = disabled_message
        else:
            self.tool_permissions[tool_name] = ToolPermission(
                name=tool_name,
                enabled=enabled,
                disabled_message=disabled_message or f"La herramienta {tool_name} está deshabilitada."
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "identity": self.identity.to_dict(),
            "official_info": self.official_info.to_dict(),
            "services": [s.to_dict() for s in self.services],
            "pricing_tiers": [p.to_dict() for p in self.pricing_tiers],
            "policies": self.policies.to_dict(),
            "navigation_resources": [n.to_dict() for n in self.navigation_resources],
            "connected_integrations": self.connected_integrations.to_dict(),
            "tool_permissions": {k: v.to_dict() for k, v in self.tool_permissions.items()},
            "operational_limits": self.operational_limits,
            "custom_rules": [r.to_dict() for r in self.custom_rules],
            "few_shot_examples": [e.to_dict() for e in self.few_shot_examples],
            "employee_role": self.employee_role,
            "active_roles": self.active_roles,
            "custom_prompt": self.custom_prompt,
            "voice_accent": self.voice_accent,
            "fts5_enabled": self.fts5_enabled,
            "growth_settings": self.growth_settings
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BusinessConfig:
        return cls(
            tenant_id=d["tenant_id"],
            identity=BusinessIdentity.from_dict(d.get("identity", {})),
            official_info=OfficialInfo.from_dict(d.get("official_info", {})),
            services=[ServiceItem.from_dict(s) for s in d.get("services", [])],
            pricing_tiers=[PricingTier.from_dict(p) for p in d.get("pricing_tiers", [])],
            policies=BusinessPolicy.from_dict(d.get("policies", {})),
            navigation_resources=[NavigationResource.from_dict(n) for n in d.get("navigation_resources", [])],
            connected_integrations=ConnectedIntegrations.from_dict(d.get("connected_integrations", {})),
            tool_permissions={k: ToolPermission.from_dict(v) for k, v in d.get("tool_permissions", {}).items()},
            operational_limits=d.get("operational_limits", []),
            custom_rules=[StructuredRule.from_dict(r) for r in d.get("custom_rules", [])],
            few_shot_examples=[BehaviorExample.from_dict(e) for e in d.get("few_shot_examples", [])],
            employee_role=d.get("employee_role", "recepcionista"),
            active_roles=d.get("active_roles", ["recepcionista", "closer_ventas", "soporte_knowledge"]),
            custom_prompt=d.get("custom_prompt", d.get("system_prompt", "")),
            voice_accent=d.get("voice_accent", "general"),
            fts5_enabled=bool(d.get("fts5_enabled", True)),
            growth_settings=d.get("growth_settings", {})
        )

    def save_to_db(self, db_path: str = "firby_ultra.db"):
        """Persiste la configuración en la base de datos SQLite."""
        try:
            with sqlite3.connect(db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS business_configs (
                        tenant_id TEXT PRIMARY KEY,
                        config_json TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.execute("""
                    INSERT INTO business_configs (tenant_id, config_json, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(tenant_id) DO UPDATE SET
                        config_json = excluded.config_json,
                        updated_at = CURRENT_TIMESTAMP
                """, (self.tenant_id, json.dumps(self.to_dict(), ensure_ascii=False)))
                conn.commit()
                log.info(f"[BusinessConfig] Guardada configuración de tenant: {self.tenant_id}")
        except Exception as e:
            log.error(f"[BusinessConfig] Error persistiendo configuración {self.tenant_id}: {e}")

    @classmethod
    def load_from_db(cls, tenant_id: str, db_path: str = "firby_ultra.db") -> Optional[BusinessConfig]:
        """Carga la configuración desde SQLite si existe."""
        try:
            with sqlite3.connect(db_path, timeout=3.0) as conn:
                cur = conn.cursor()
                cur.execute("SELECT config_json FROM business_configs WHERE tenant_id = ?", (tenant_id,))
                row = cur.fetchone()
                if row and row[0]:
                    data = json.loads(row[0])
                    return cls.from_dict(data)
        except Exception as e:
            log.warning(f"[BusinessConfig] No se pudo leer config para {tenant_id} desde DB: {e}")
        return None


# ═════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE FIRBY (FIRBYAI.LAT COMO NEGOCIO REAL)
# ═════════════════════════════════════════════════════════════════════════════

FIRBY_LANDING_CONFIG = BusinessConfig(
    tenant_id="firby_landing",
    identity=BusinessIdentity(
        name="Firby",
        legal_name="Firby AI S.A.S.",
        industry="Plataforma de Operadores Digitales Autónomos para Sitios Web",
        description=(
            "Plataforma de agentes y operadores autónomos para páginas web empresariales. "
            "Vive en el sitio web para atender visitantes 24/7, resolver dudas con políticas oficiales "
            "y operar la navegación del sitio, mientras mantiene una línea privada por WhatsApp con el dueño."
        ),
        website_url="https://firbyai.lat",
        tone_and_voice="ejecutivo, preciso, sin clichés corporativos, estructurado, limpio y directo estilo Sierra AI"
    ),
    official_info=OfficialInfo(
        locations=["Medellín, Colombia (Sede principal, Operación cloud global)"],
        contact_email="soporte@firbyai.lat",
        executive_phone="+57 324 369 9856",
        operating_hours="Operador web: 24/7. Atención ejecutiva: lunes a viernes 8:00 AM – 6:00 PM COT.",
        team_overview=(
            "Equipo de ingeniería de software, arquitectura de IA y sistemas distribuidos. "
            "Para conocer la visión y enfoque de ingeniería, consultar la página Sobre Nosotros."
        ),
        unlisted_attributes=[
            "ceo", "director_ejecutivo", "nombre_del_ceo", "dueño_personal", "salarios", "inversionistas",
            "tarjeta", "facturacion", "datos_bancarios", "cliente_que_mas_paga", "ingresos"
        ]
    ),
    pricing_tiers=[
        PricingTier(
            id="starter",
            name=COMMERCIAL_PLANS["starter"].name,
            price_cop=COMMERCIAL_PLANS["starter"].formatted_price_cop,
            price_usd=COMMERCIAL_PLANS["starter"].formatted_price_usd,
            billing_period=COMMERCIAL_PLANS["starter"].billing_period,
            features=[
                "operador digital autónomo en tu web",
                "sincronización con 1 agenda de Google Calendar",
                f"hasta {COMMERCIAL_PLANS['starter'].interactions_limit} interacciones mensuales"
            ],
            trial_days=COMMERCIAL_PLANS["starter"].trial_days,
            trial_terms=COMMERCIAL_PLANS["starter"].trial_terms
        ),
        PricingTier(
            id="pro",
            name=COMMERCIAL_PLANS["pro"].name,
            price_cop=COMMERCIAL_PLANS["pro"].formatted_price_cop,
            price_usd=COMMERCIAL_PLANS["pro"].formatted_price_usd,
            billing_period=COMMERCIAL_PLANS["pro"].billing_period,
            features=[
                "autonomía avanzada en web",
                "reprogramación autónoma con código OTP",
                "línea ejecutiva en WhatsApp para el dueño",
                f"hasta {COMMERCIAL_PLANS['pro'].interactions_limit} interacciones mensuales"
            ],
            trial_days=COMMERCIAL_PLANS["pro"].trial_days,
            trial_terms=COMMERCIAL_PLANS["pro"].trial_terms
        ),
        PricingTier(
            id="equipos",
            name=COMMERCIAL_PLANS["equipos"].name,
            price_cop=COMMERCIAL_PLANS["equipos"].formatted_price_cop,
            price_usd=COMMERCIAL_PLANS["equipos"].formatted_price_usd,
            billing_period=COMMERCIAL_PLANS["equipos"].billing_period,
            features=[
                "múltiples sedes",
                "hasta 5 agendas concurrentes",
                "roles de equipo",
                "webhooks e integraciones CRM",
                f"hasta {COMMERCIAL_PLANS['equipos'].interactions_limit} interacciones mensuales"
            ],
            trial_days=COMMERCIAL_PLANS["equipos"].trial_days,
            trial_terms=COMMERCIAL_PLANS["equipos"].trial_terms
        )
    ],
    services=[
        ServiceItem(
            id="demo_operator",
            name="Demostración y activación del operador",
            description="Instalación del snippet en 60 segundos en cualquier página web.",
            duration_minutes=15
        ),
        ServiceItem(
            id="enterprise_onboarding",
            name="Onboarding asistido para empresas",
            description="Integración personalizada con CRM, calendarios y políticas a medida.",
            duration_minutes=45
        )
    ],
    policies=BusinessPolicy(
        booking_policy="En Firby la activación es directa en la web con 7 días de prueba gratis. Para demostraciones personalizadas, contactar vía WhatsApp.",
        cancellation_policy="Los clientes pueden cancelar su suscripción en 1 clic en cualquier momento sin penalidad.",
        data_privacy_url="/politica-de-privacidad",
        exception_approval_process="Toda excepción comercial o descuento no listado se envía por WhatsApp al dueño para visto bueno."
    ),
    navigation_resources=[
        NavigationResource(
            id="free_trial",
            target="/free-trial",
            label="Iniciar prueba 7 días",
            description="Activación directa de la prueba gratuita de 7 días sin permanencia.",
            relevance_keywords=["prueba", "iniciar prueba", "activar prueba", "probar", "7 dias", "7 días", "registro", "registrarse", "sign up", "sign-up"]
        ),
        NavigationResource(
            id="planes",
            target="#planes",
            label="Planes y Precios",
            description="Tabla comparativa de planes Starter ($290.000 COP), Pro ($490.000 COP) y Equipos ($890.000 COP).",
            relevance_keywords=["precio", "precios", "plan", "planes", "costo", "cuanto cuesta", "tarifa", "mensualidad", "starter", "pro"]
        ),
        NavigationResource(
            id="como_funciona",
            target="#como-funciona",
            label="Cómo Funciona",
            description="Explicación del flujo: widget web para visitantes, conexión al servidor y línea privada WhatsApp con el dueño.",
            relevance_keywords=["como funciona", "cómo funciona", "instalacion", "instalar", "que hace", "paso a paso", "wordpress", "shopify"]
        ),
        NavigationResource(
            id="sobre_nosotros",
            target="/sobre-nosotros",
            label="Sobre Nosotros",
            description="Página oficial que explica la visión, arquitectura y equipo de ingeniería de Firby.",
            relevance_keywords=["sobre nosotros", "equipo", "quienes son", "quiénes son", "quienes crearon", "quiénes crearon", "creadores", "vision", "historia"]
        ),
        NavigationResource(
            id="seguridad",
            target="#seguridad-cumplimiento",
            label="Seguridad y Control",
            description="Detalles de gobernanza, autenticación OTP de 6 dígitos y aislamiento de datos.",
            relevance_keywords=["seguridad", "privacidad", "cumplimiento", "otp", "bancaria", "datos"]
        ),
        NavigationResource(
            id="canales",
            target="#canales",
            label="Dos Canales",
            description="La regla inquebrantable de los dos canales: Web para visitantes, WhatsApp exclusivo para el dueño.",
            relevance_keywords=["canales", "whatsapp", "dos canales", "canal"]
        ),
        NavigationResource(
            id="faq",
            target="/faq",
            label="Preguntas Frecuentes",
            description="Respuestas detalladas a preguntas frecuentes técnicas y comerciales.",
            relevance_keywords=["faq", "preguntas frecuentes", "dudas", "soporte"]
        )
    ],
    connected_integrations=ConnectedIntegrations(
        google_calendar=False,  # Firby Landing NO usa calendar de citas abierto para el público
        whatsapp_owner=True,
        crm_system=False,
        database_sync=True,
        email_gateway=True
    ),
    tool_permissions={
        "navigate_web": ToolPermission(name="navigate_web", enabled=True),
        "web_navigation": ToolPermission(name="web_navigation", enabled=True),
        "highlight_ui": ToolPermission(name="highlight_ui", enabled=True),
        "query_business_knowledge": ToolPermission(name="query_business_knowledge", enabled=True),
        "escalate_to_human": ToolPermission(name="escalate_to_human", enabled=True),
        "check_availability": ToolPermission(
            name="check_availability",
            enabled=False,
            disabled_message=(
                "Firby integra consulta de disponibilidad en tiempo real con Google Calendar en los sitios web de sus clientes. "
                "En este portal oficial la activación del servicio es 100% autoservicio con 7 días de prueba gratuita."
            )
        ),
        "book_appointment": ToolPermission(
            name="book_appointment",
            enabled=False,
            disabled_message=(
                "Firby integra agendamiento en tiempo real sincronizado con Google Calendar para los sitios web de sus clientes. "
                "En este portal oficial la activación de su operador es 100% autoservicio con 7 días de prueba gratuita sin permanencia."
            )
        )
    },
    operational_limits=[
        "No revelar nombres personales o información ejecutiva no publicada oficialmente (ej. CEO). Responder con honestidad que no se tiene ese dato.",
        "No ofrecer citas ni horarios si la herramienta de reservas no está habilitada.",
        "No inventar precios ni servicios fuera de los planes oficiales.",
        "Priorizar la acción real (navegar, destacar) antes que explicar teóricamente que se puede hacer.",
        "Mantener un tono conversacional ejecutivo estilo Sierra AI, sin saludos robóticos ni preguntas forzadas al final."
    ]
)


# ═════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN CLÍNICA DENTAL (INSTANCIA CON AGENDA HABILITADA)
# ═════════════════════════════════════════════════════════════════════════════

CLINICA_AMERICAS_CONFIG = BusinessConfig(
    tenant_id="clinica-de-las-americas",
    identity=BusinessIdentity(
        name="Clínica Dental Las Américas",
        legal_name="Clínica Odontológica Las Américas S.A.S.",
        industry="Salud y Odontología Especializada",
        description="Clínica dental especializada en ortodoncia invisible, diseño de sonrisa e implantes dentales.",
        website_url="https://clinicaamericas.com",
        tone_and_voice="médico, empático, claro, seguro y reconfortante"
    ),
    official_info=OfficialInfo(
        locations=["Sede Poblado: Cra 43A # 1-50, Medellín"],
        contact_email="citas@clinicaamericas.com",
        executive_phone="+57 300 123 4567",
        operating_hours="Lunes a Viernes de 7:00 AM a 7:00 PM. Sábados de 8:00 AM a 2:00 PM.",
        team_overview="Equipo de odontólogos especialistas certificados con tecnología 3D.",
        unlisted_attributes=["dueño_personal", "salarios_medicos", "inversionistas"]
    ),
    services=[
        ServiceItem(id="ortodoncia", name="Valoración de Ortodoncia", description="Evaluación clínica y escaneo 3D.", price_cop=80000, duration_minutes=40),
        ServiceItem(id="limpieza", name="Limpieza Dental Profunda (Profilaxis)", description="Higiene con ultrasonido.", price_cop=120000, duration_minutes=45),
        ServiceItem(id="diseno", name="Diseño de Sonrisa", description="Planificación digital de carillas.", price_cop=150000, duration_minutes=60),
        ServiceItem(id="implante", name="Valoración de Implantes", description="Estudio tomográfico para implantes.", price_cop=100000, duration_minutes=45)
    ],
    policies=BusinessPolicy(
        booking_policy="Se requiere nombre completo y WhatsApp para apartar la cita en agenda.",
        cancellation_policy="Agradecemos avisar con al menos 12 horas de anticipación.",
        data_privacy_url="/politica-de-privacidad",
        exception_approval_process="Casos especiales se coordinan con la dirección médica."
    ),
    navigation_resources=[
        NavigationResource(id="servicios", target="#servicios", label="Nuestros Servicios", description="Tratamientos odontológicos.", relevance_keywords=["servicios", "tratamientos", "ortodoncia", "implantes"]),
        NavigationResource(id="horarios", target="#contacto", label="Horarios y Ubicación", description="Dirección y horarios.", relevance_keywords=["horarios", "donde estan", "ubicacion", "direccion"])
    ],
    connected_integrations=ConnectedIntegrations(
        google_calendar=True,  # Esta clínica SÍ tiene calendar conectado
        whatsapp_owner=True,
        crm_system=False,
        database_sync=True
    ),
    tool_permissions={
        "navigate_web": ToolPermission(name="navigate_web", enabled=True),
        "highlight_ui": ToolPermission(name="highlight_ui", enabled=True),
        "check_availability": ToolPermission(name="check_availability", enabled=True),
        "book_appointment": ToolPermission(name="book_appointment", enabled=True),
        "query_business_knowledge": ToolPermission(name="query_business_knowledge", enabled=True),
        "escalate_to_human": ToolPermission(name="escalate_to_human", enabled=True)
    }
)

# Cache en memoria de configuraciones activas
_CONFIG_REGISTRY: Dict[str, BusinessConfig] = {
    "firby_landing": FIRBY_LANDING_CONFIG,
    "clinica-de-las-americas": CLINICA_AMERICAS_CONFIG
}


def get_business_config(tenant_id: str = "firby_landing") -> BusinessConfig:
    """
    Obtiene la configuración de negocio según el identificador de la organización.
    Primero busca en la base de datos persistente; si no hay personalizaciones,
    utiliza el registro en memoria.
    """
    tid = (tenant_id or "firby_landing").strip().lower()

    # 1. Intentar cargar desde SQLite (para soportar cambios hechos desde el Workspace)
    loaded = BusinessConfig.load_from_db(tid)
    if loaded:
        _CONFIG_REGISTRY[tid] = loaded
        return loaded

    # 2. Búsqueda en memoria
    if tid in _CONFIG_REGISTRY:
        return _CONFIG_REGISTRY[tid]

    if "clinica" in tid:
        return CLINICA_AMERICAS_CONFIG

    return FIRBY_LANDING_CONFIG


def register_business_config(config: BusinessConfig, persist: bool = True):
    """Registra una nueva configuración de negocio y opcionalmente la persiste en SQLite."""
    _CONFIG_REGISTRY[config.tenant_id] = config
    if persist:
        config.save_to_db()
