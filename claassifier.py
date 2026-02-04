import json
import re
import time

import streamlit as st
from groq import Groq
from prompts import SYSTEM_PROMPT

client = Groq(
     api_key=st.secrets["GROQ_API_KEY"]
 )
DEFAULT_MODEL = "llama-3.1-8b-instant"
DEFAULT_SUPPLIER = "Not provided"
RETRY_COUNT = 1
RETRY_DELAY_SECONDS = 0.5


def _clean_json_payload(raw_text: str) -> str:
  if not raw_text:
    return raw_text
  stripped = raw_text.strip()
  match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
  return match.group(0) if match else stripped


def _fallback_json(po_description: str) -> str:
  payload = {
      "po_description": po_description,
      "L1": "Not sure",
      "L2": "Not sure",
      "L3": "Not sure",
  }
  return json.dumps(payload)


def _get_model_name() -> str:
  try:
    model = st.secrets.get("GROQ_MODEL", DEFAULT_MODEL)
  except Exception:
    model = DEFAULT_MODEL
  return model or DEFAULT_MODEL


def _get_timeout_seconds():
  try:
    timeout = st.secrets.get("GROQ_TIMEOUT_SECONDS", None)
  except Exception:
    timeout = None
  if timeout is None:
    return None
  try:
    return float(timeout)
  except (TypeError, ValueError):
    return None


def classify_po(po_description: str, Supplier: str = DEFAULT_SUPPLIER) -> str:
  description = (po_description or "").strip()
  supplier = (Supplier or "").strip() or DEFAULT_SUPPLIER
  if not description:
    return _fallback_json(description)

  user_prompt = (
      f"PO Description: {description}\n"
      f"Supplier: {supplier}\n"
      "Output ONLY JSON."
  )

  model = _get_model_name()
  timeout_seconds = _get_timeout_seconds()
  request_kwargs = {
      "model": model,
      "temperature": 0,
      "messages": [
          {"role": "system", "content": SYSTEM_PROMPT},
          {"role": "user", "content": user_prompt},
      ],
  }
  if timeout_seconds is not None:
    request_kwargs["timeout"] = timeout_seconds

  last_error = None
  for attempt in range(RETRY_COUNT + 1):
    try:
      response = client.chat.completions.create(**request_kwargs)
      raw_text = response.choices[0].message.content
      cleaned = _clean_json_payload(raw_text)
      parsed = json.loads(cleaned)
      return json.dumps(parsed)
    except TypeError:
      if "timeout" in request_kwargs:
        request_kwargs.pop("timeout", None)
        try:
          response = client.chat.completions.create(**request_kwargs)
          raw_text = response.choices[0].message.content
          cleaned = _clean_json_payload(raw_text)
          parsed = json.loads(cleaned)
          return json.dumps(parsed)
        except Exception as exc:
          last_error = exc
      else:
        last_error = None
    except Exception as exc:
      last_error = exc

    if attempt < RETRY_COUNT:
      time.sleep(RETRY_DELAY_SECONDS)

  return _fallback_json(description)
