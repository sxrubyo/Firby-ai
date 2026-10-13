# -*- coding: utf-8 -*-
"""
Firby Telemetry & Observability Data Models (inspired by Langfuse & OpenTelemetry).
Provides structured trace, span, and token metrics tracking for autonomous agent debugging.
"""
from __future__ import annotations

import json
import time
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class SpanType(str, Enum):
    AGENT_STEP = "agent_step"
    TOOL = "tool"
    LLM = "llm"
    VERIFICATION = "verification"
    HANDOFF = "handoff"
    SELF_REPAIR = "self_repair"


class SpanStatus(str, Enum):
    OK = "ok"
    ERROR = "error"


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": round(self.estimated_cost_usd, 6),
        }


@dataclass
class Span:
    id: str = field(default_factory=lambda: f"span_{uuid.uuid4().hex[:12]}")
    trace_id: str = ""
    parent_span_id: Optional[str] = None
    name: str = ""
    span_type: SpanType = SpanType.AGENT_STEP
    status: SpanStatus = SpanStatus.OK
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    error_message: Optional[str] = None
    usage: TokenUsage = field(default_factory=TokenUsage)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def finish(self, status: SpanStatus = SpanStatus.OK, output_data: Any = None, error: Optional[str] = None) -> None:
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000.0, 2)
        self.status = status
        if output_data is not None:
            self.output_data = output_data
        if error:
            self.error_message = error
            self.status = SpanStatus.ERROR

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "span_type": self.span_type.value if isinstance(self.span_type, SpanType) else str(self.span_type),
            "status": self.status.value if isinstance(self.status, SpanStatus) else str(self.status),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "usage": self.usage.to_dict(),
            "metadata": self.metadata,
        }


@dataclass
class Trace:
    id: str = field(default_factory=lambda: f"trc_{uuid.uuid4().hex[:12]}")
    name: str = ""
    session_id: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    spans: List[Span] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: SpanStatus = SpanStatus.OK

    def create_span(
        self,
        name: str,
        span_type: SpanType = SpanType.AGENT_STEP,
        parent_span_id: Optional[str] = None,
        input_data: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Span:
        span = Span(
            trace_id=self.id,
            parent_span_id=parent_span_id,
            name=name,
            span_type=span_type,
            input_data=input_data,
            metadata=metadata or {},
        )
        self.spans.append(span)
        return span

    def finish(self, status: SpanStatus = SpanStatus.OK) -> None:
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000.0, 2)
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        total_tokens = sum(s.usage.total_tokens for s in self.spans)
        total_cost = sum(s.usage.estimated_cost_usd for s in self.spans)
        return {
            "id": self.id,
            "name": self.name,
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status.value if isinstance(self.status, SpanStatus) else str(self.status),
            "span_count": len(self.spans),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "metadata": self.metadata,
            "spans": [s.to_dict() for s in self.spans],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
