import logging
import re
import json
import time
from app.core.config import settings
from openai import OpenAI
from pydantic import BaseModel
from typing import Type, TypeVar, Any

T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
BASE_RETRY_DELAY = 2  # seconds
MAX_OUTPUT_TOKENS = 4096

def _is_retryable(error: Exception) -> bool:
    """Check if an error is transient and worth retrying (429, 5xx, overloaded)."""
    err_str = str(error).lower()
    retryable_signals = ["429", "rate limit", "rate_limit", "overloaded", "too many requests",
                         "500", "502", "503", "504", "server error", "capacity"]
    return any(signal in err_str for signal in retryable_signals)

def clean_json_string(text: str) -> str:
    """Extract and clean JSON content from LLM model response."""
    text = text.strip()
    # Strip Qwen-style <think>...</think> reasoning blocks
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    if "```" in text:
        pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(pattern, text)
        if match:
            text = match.group(1).strip()
        else:
            text = re.sub(r"^```(?:json)?", "", text).strip()
            text = re.sub(r"```$", "", text).strip()
            
    if not (text.startswith("{") or text.startswith("[")):
        json_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if json_match:
            text = json_match.group(1).strip()
            
    return text

def _prompt_to_messages(prompt: Any) -> list[dict]:
    """Convert various prompt formats to OpenAI messages list."""
    if isinstance(prompt, str):
        return [{"role": "user", "content": prompt}]
    elif isinstance(prompt, list):
        messages = []
        for item in prompt:
            if isinstance(item, dict) and "role" in item:
                messages.append(item)
            elif isinstance(item, tuple) and len(item) == 2:
                # LangChain-style ("system", "...") or ("human", "...")
                role_map = {"system": "system", "human": "user", "ai": "assistant", "user": "user", "assistant": "assistant"}
                role = role_map.get(item[0], "user")
                messages.append({"role": role, "content": item[1]})
            elif hasattr(item, 'type') and hasattr(item, 'content'):
                # LangChain message objects
                role_map = {"system": "system", "human": "user", "ai": "assistant", "SystemMessage": "system", "HumanMessage": "user", "AIMessage": "assistant"}
                role = role_map.get(getattr(item, 'type', 'user'), "user")
                messages.append({"role": role, "content": item.content})
            else:
                messages.append({"role": "user", "content": str(item)})
        return messages if messages else [{"role": "user", "content": str(prompt)}]
    elif hasattr(prompt, 'to_messages'):
        # LangChain ChatPromptValue
        return _prompt_to_messages(prompt.to_messages())
    elif hasattr(prompt, 'content'):
        return [{"role": "user", "content": prompt.content}]
    else:
        return [{"role": "user", "content": str(prompt)}]

class LLMProvider:
    def __init__(self, provider: str, model: str, api_key: str):
        self.provider = provider
        self.model = model
        self.api_key = api_key

    def generate_structured(self, prompt: Any, schema: Type[T], agent: Any = None) -> T:
        """
        Uses the OpenAI SDK to call the LLM and return a structured Pydantic object.
        Includes retry with exponential backoff for transient errors (429, 5xx).
        """
        if not self.api_key:
            raise ValueError(f"API key missing for provider: {self.provider}")
        
        base_url = None
        if self.provider.lower() == "nvidia":
            base_url = "https://integrate.api.nvidia.com/v1"
        elif self.provider.lower() == "groq":
            base_url = "https://api.groq.com/openai/v1"
        elif self.provider.lower() in ["google", "gemini"]:
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            
        client = OpenAI(
            api_key=self.api_key,
            base_url=base_url,
        )
        
        messages = _prompt_to_messages(prompt)
        
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=MAX_OUTPUT_TOKENS,
                    response_format={"type": "json_object"}
                )
                
                raw_content = response.choices[0].message.content or ""
                
                if agent is not None and hasattr(agent, 'logs'):
                    agent.logs.append({
                        "timestamp": time.time(),
                        "provider": self.provider,
                        "model": self.model,
                        "messages": messages,
                        "raw_response": raw_content
                    })

                cleaned_content = clean_json_string(raw_content)

                try:
                    data = json.loads(cleaned_content)
                    return schema.model_validate(data)
                except Exception as parse_error:
                    logger.warning(f"JSON parse failed for provider {self.provider} (attempt {attempt}): {parse_error}. Raw output:\n{raw_content}")
                    raise parse_error

            except Exception as e:
                last_error = e
                if _is_retryable(e) and attempt < MAX_RETRIES:
                    delay = BASE_RETRY_DELAY * (2 ** (attempt - 1))  # 2s, 4s, 8s
                    logger.warning(f"[{self.provider}] Attempt {attempt}/{MAX_RETRIES} failed (retryable): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    raise
        
        raise last_error  # Should not be reached, but safety net

def generate_with_fallback(prompt: Any, schema: Type[T], agent: Any = None) -> T:
    """
    Attempts to generate a response using the primary LLM with retries.
    If it fails (e.g., quota finished, rate limited), it automatically 
    switches to the fallback LLM (also with retries).
    """
    primary_llm = LLMProvider(
        provider=settings.PRIMARY_LLM_PROVIDER,
        model=settings.PRIMARY_LLM_MODEL,
        api_key=settings.PRIMARY_LLM_API_KEY
    )
    
    fallback_llm = LLMProvider(
        provider=settings.FALLBACK_LLM_PROVIDER,
        model=settings.FALLBACK_LLM_MODEL,
        api_key=settings.FALLBACK_LLM_API_KEY
    )
    
    provider_errors = []
    try:
        logger.info(f"Attempting to generate with primary LLM: {primary_llm.provider} ({primary_llm.model})")
        response = primary_llm.generate_structured(prompt, schema)
        return response
        
    except Exception as e:
        provider_errors.append(f"{primary_llm.provider}: {e}")
        logger.warning(f"Primary LLM ({primary_llm.provider}/{primary_llm.model}) failed after retries: {str(e)}. Switching to fallback...")
        
        try:
            logger.info(f"Attempting to generate with fallback LLM: {fallback_llm.provider} ({fallback_llm.model})")
            response = fallback_llm.generate_structured(prompt, schema)
            return response
            
        except Exception as fallback_e:
            provider_errors.append(f"{fallback_llm.provider}: {fallback_e}")
            logger.error(f"Fallback LLM ({fallback_llm.provider}/{fallback_llm.model}) also failed: {str(fallback_e)}")
            raise RuntimeError(
                "All LLM providers failed. " + "; ".join(provider_errors)
            ) from fallback_e


