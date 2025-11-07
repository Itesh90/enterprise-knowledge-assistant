from __future__ import annotations

import os
import time
import json
from typing import Dict

import httpx

from app.core.config import settings
from app.rag.guardrails import assess_confidence, enforce_min_similarity

try:
    import google.generativeai as genai
except ImportError:
    genai = None


async def call_gemini_json(prompt: str) -> Dict:
    """Call Google Gemini API with JSON response format."""
    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback local answer to allow running without key
        return {
            "answer": "I'm not sure. Provide a Gemini API key to enable generation. Add GEMINI_API_KEY=your-key to backend/.env and restart the server.",
            "citations": [],
            "confidence": 0.2,
            "telemetry": {"latency_ms": 0, "tokens_prompt": 0, "tokens_completion": 0, "cost_usd": 0},
        }

    if genai is None:
        return {
            "answer": "I'm not sure. Please install google-generativeai: pip install google-generativeai",
            "citations": [],
            "confidence": 0.2,
            "telemetry": {"latency_ms": 0, "tokens_prompt": 0, "tokens_completion": 0, "cost_usd": 0},
        }

    genai.configure(api_key=api_key)
    
    # Validate and normalize model name
    model_name = settings.llm_model.strip().lower()
    # Map common variations to correct model names
    model_map = {
        "gemini 2.5 flash": "gemini-1.5-flash",
        "gemini-2.5-flash": "gemini-1.5-flash",
        "gemini 2.0 flash": "gemini-2.0-flash-exp",
        "gemini-2.0-flash": "gemini-2.0-flash-exp",
        "gemini flash": "gemini-1.5-flash",
        "gemini pro": "gemini-1.5-pro",
    }
    if model_name in model_map:
        model_name = model_map[model_name]
    elif model_name not in ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"]:
        # If not a known model, try to use as-is but warn
        print(f"Warning: Unknown model name '{settings.llm_model}', using as-is")
    
    model = genai.GenerativeModel(model_name)

    # Gemini JSON response format via prompt engineering
    system_instruction = """You are a helpful assistant. Always respond with valid JSON only, no markdown formatting.
Your response must be a JSON object with this exact structure:
{
  "answer": "string",
  "citations": [{"rank": 1, "title": "string", "url": "string"}],
  "confidence": 0.0-1.0,
  "telemetry": {"latency_ms": 0, "tokens_prompt": 0, "tokens_completion": 0, "cost_usd": 0}
}"""

    full_prompt = f"{system_instruction}\n\nUser query: {prompt}\n\nRespond with JSON only:"

    t0 = time.time()
    try:
        # Gemini 1.5 Pro supports JSON mode
        generation_config = genai.GenerationConfig(
            temperature=0.2,
            response_mime_type="application/json",
        )
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config,
        )
        latency_ms = int((time.time() - t0) * 1000)
        
        # Parse JSON response
        content = response.text.strip()
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        out = json.loads(content)
        # Estimate tokens (rough approximation)
        tokens_prompt = len(full_prompt.split()) * 1.3  # rough estimate
        tokens_completion = len(content.split()) * 1.3
        # Gemini pricing estimate (very rough, actual pricing may vary)
        cost_usd = (tokens_prompt * 0.0005 / 1000) + (tokens_completion * 0.0015 / 1000)
        
        out["telemetry"] = {
            "latency_ms": latency_ms,
            "tokens_prompt": int(tokens_prompt),
            "tokens_completion": int(tokens_completion),
            "cost_usd": round(cost_usd, 6),
        }
        return out
    except Exception as e:
        latency_ms = int((time.time() - t0) * 1000)
        return {
            "answer": f"I'm not sure. Error: {str(e)}",
            "citations": [],
            "confidence": 0.2,
            "telemetry": {"latency_ms": latency_ms, "tokens_prompt": 0, "tokens_completion": 0, "cost_usd": 0},
        }


# Keep old function name for backward compatibility during transition
call_openai_json = call_gemini_json
