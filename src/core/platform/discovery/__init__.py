# -*- coding: utf-8 -*-
"""
Firby Platform — Discovery, Onboarding & Self-Inspection Engine
===============================================================
"""

from src.core.platform.discovery.crawler import ControlledSiteCrawler, SiteModel, DiscoveredPage
from src.core.platform.discovery.codebase_scanner import CodebaseScanner, CodebaseModel
from src.core.platform.discovery.conflict_detector import ConflictDetector, KnowledgeConflict
from src.core.platform.discovery.onboarding import OnboardingEngine, OnboardingSession, onboarding_engine
from src.core.platform.discovery.self_inspection import SelfInspector, SelfInspectionReport, self_inspector

__all__ = [
    "ControlledSiteCrawler",
    "SiteModel",
    "DiscoveredPage",
    "CodebaseScanner",
    "CodebaseModel",
    "ConflictDetector",
    "KnowledgeConflict",
    "OnboardingEngine",
    "OnboardingSession",
    "onboarding_engine",
    "SelfInspector",
    "SelfInspectionReport",
    "self_inspector",
]
