"""
ElectroVerse AI Provider Abstraction Layer
Supports Local Knowledge Base Provider (Offline) and Gemini AI Provider (Online)
with seamless, fail-safe automatic fallback.
"""

import json
import urllib.request
import urllib.error
import socket
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from src.core.logger import log
from src.core.config import config_manager
from src.ai.knowledge_base import knowledge_base
from src.ai.safety import safety_manager


class BaseAIProvider(ABC):
    """Abstract Base Class for ElectroVerse AI Providers."""

    @abstractmethod
    def generate_response(self, query: str, context: Dict[str, Any], system_prompt: str) -> str:
        pass


class LocalKnowledgeProvider(BaseAIProvider):
    """Offline Provider using ElectroVerse Verified Local Knowledge Base & ECKB."""

    def generate_response(self, query: str, context: Dict[str, Any], system_prompt: str) -> str:
        q_lower = query.lower()

        # Check 8085 Instruction Search
        for word in query.split():
            clean_word = word.strip().upper().replace(",", "").replace(";", "")
            inst_info = knowledge_base.search_8085_instruction(clean_word)
            if inst_info:
                return (
                    f"### 📘 Intel 8085 Instruction: `{clean_word}`\n\n"
                    f"- **Description**: {inst_info['desc']}\n"
                    f"- **Bytes**: {inst_info['bytes']} Byte(s)\n"
                    f"- **Machine Cycles & T-States**: {inst_info['cycles']}\n"
                    f"- **Status Flags Affected**: `{inst_info['flags']}`\n"
                    f"- **Worked Example**: `{inst_info['example']}`\n\n"
                    f"*Source: Verified ElectroVerse 8085 Microprocessor Database*"
                )

        # Check TTL IC Search
        for word in query.split():
            clean_ic = word.strip().replace("IC", "").replace("_", "")
            ic_data = knowledge_base.search_ic_registry(clean_ic)
            if ic_data:
                return (
                    f"### ⚡ TTL Integrated Circuit: `{ic_data.get('part_number', clean_ic)}`\n\n"
                    f"- **Name**: {ic_data.get('name', 'Logic Gate IC')}\n"
                    f"- **Logic Type**: {ic_data.get('logic_type', 'Digital Logic')}\n"
                    f"- **Pin Count**: {ic_data.get('pin_count', 14)} Pins\n"
                    f"- **VCC Power Pin**: Pin {ic_data.get('vcc_pin', 14)} (+5V)\n"
                    f"- **GND Ground Pin**: Pin {ic_data.get('gnd_pin', 7)} (0V)\n"
                    f"- **Description**: {ic_data.get('description', '')}\n\n"
                    f"*Source: Verified ElectroVerse ECKB Registry*"
                )

        # Check Theory Topics Search
        topics = knowledge_base.search_theory(query)
        if topics:
            top = topics[0]
            summary = top.get("summary", "")
            principle = top.get("working_principle", "")
            notes = "\n".join([f"- {n}" for n in top.get("quick_notes", [])])
            eq = top.get("boolean_equation", "")

            resp = f"### 📖 ElectroVerse Knowledge Base: **{top.get('title', 'Engineering Topic')}**\n\n"
            if summary:
                resp += f"**Overview**: {summary}\n\n"
            if eq:
                resp += f"**Governing Formula**: `{eq}`\n\n"
            if principle:
                resp += f"**Working Principle**: {principle}\n\n"
            if notes:
                resp += f"**Key Laboratory Notes**:\n{notes}\n\n"
            resp += "*Source: Verified ElectroVerse Learning Database*"
            return resp

        # Check 8085 Program Database Search
        prog = knowledge_base.search_program_db(query)
        if prog:
            title = prog.get("title", "8085 Assembly Program")
            code = prog.get("code", "")
            desc = prog.get("description", "")
            return (
                f"### 💻 8085 Assembly Program: **{title}**\n\n"
                f"**Description**: {desc}\n\n"
                f"```assembly\n{code}\n```\n\n"
                f"*Source: Verified ElectroVerse 8085 Program Database*"
            )

        # Check Component Database Search
        comp = knowledge_base.search_component_db(query)
        if comp:
            c_name = comp.get("name", "Component")
            c_desc = comp.get("description", "")
            c_specs = comp.get("specifications", {})
            specs_str = "\n".join([f"- **{k}**: {v}" for k, v in c_specs.items()])
            return (
                f"### 🔬 Component Specification: **{c_name}**\n\n"
                f"**Overview**: {c_desc}\n\n"
                f"**Technical Specifications**:\n{specs_str}\n\n"
                f"*Source: Verified ElectroVerse Component Database*"
            )

        # Fallback if no local match
        return safety_manager.format_hallucination_fallback()


class GeminiAIProvider(BaseAIProvider):
    """Google Gemini Online REST API Provider with Multi-Model Resolution & Asynchronous Fail-Safe."""

    AVAILABLE_MODELS = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
        "gemini-pro"
    ]

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.local_provider = LocalKnowledgeProvider()

    def generate_response(self, query: str, context: Dict[str, Any], system_prompt: str) -> str:
        # First check if local provider has exact 8085 instruction or IC match for instant response
        local_fast = self.local_provider.generate_response(query, context, system_prompt)
        if local_fast != safety_manager.format_hallucination_fallback() and len(query.strip()) < 15:
            return local_fast

        # Build Context-Aware Prompt Payload
        ctx_str = json.dumps(context, indent=2)
        full_prompt = (
            f"{system_prompt}\n\n"
            f"=== CURRENT LIVE ELECTROVERSE CONTEXT ===\n"
            f"{ctx_str}\n\n"
            f"=== USER QUERY ===\n"
            f"{query}\n\n"
            f"Provide a clear, engineering-student level explanation with equations, step-by-step breakdown, and practical insights."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024
            }
        }
        req_data = json.dumps(payload).encode("utf-8")

        # Try model endpoints sequentially
        for model in self.AVAILABLE_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            try:
                req = urllib.request.Request(
                    url,
                    data=req_data,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    if response.status == 200:
                        resp_body = json.loads(response.read().decode("utf-8"))
                        candidates = resp_body.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                text = parts[0].get("text", "").strip()
                                if text:
                                    log.info(f"[GeminiAIProvider] Successfully generated online response using model '{model}'.")
                                    return text
            except Exception as e:
                log.debug(f"[GeminiAIProvider] Model '{model}' endpoint failed ({e}). Trying next model...")

        log.warning("[GeminiAIProvider] Online API unavailable or key unverified. Falling back to Local Knowledge Base.")
        return self.local_provider.generate_response(query, context, system_prompt)


class ProviderFactory:
    """Factory to instantiate the appropriate AI Provider based on settings & network."""

    @staticmethod
    def get_provider() -> BaseAIProvider:
        import os
        api_key = (
            config_manager.get("ai_api_key", "").strip() or
            os.environ.get("GEMINI_API_KEY", "").strip() or
            os.environ.get("ELECTROVERSE_AI_KEY", "").strip()
        )
        provider_type = config_manager.get("ai_provider", "auto").lower()

        if provider_type != "local" and api_key and len(api_key) > 5:
            log.info("[ProviderFactory] Using Gemini AI Provider")
            return GeminiAIProvider(api_key=api_key)

        log.info("[ProviderFactory] Using Local Verified Knowledge Base Provider")
        return LocalKnowledgeProvider()
