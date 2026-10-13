"""
Módulo Comercial Canónico de Firby SaaS.
Fuente Única de Verdad (Single Source of Truth) para planes, precios y condiciones comerciales.
"""
from src.core.commercial.plans import (
    COMMERCIAL_PLANS,
    CommercialPlan,
    get_all_plans,
    get_plan_by_id,
    get_pricing_summary_text,
    get_plan_specific_text,
    get_plans_dict,
)

__all__ = [
    "COMMERCIAL_PLANS",
    "CommercialPlan",
    "get_all_plans",
    "get_plan_by_id",
    "get_pricing_summary_text",
    "get_plan_specific_text",
    "get_plans_dict",
]
