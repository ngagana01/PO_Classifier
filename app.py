import json
import re
from datetime import datetime

import streamlit as st

from claassifier import classify_po

st.set_page_config(page_title="PO Category Classifier", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=Space+Grotesk:wght@500;600&display=swap');

    :root {
        --bg: #f6f8fb;
        --card: #ffffff;
        --ink: #1f2937;
        --muted: #6b7280;
        --accent: #0ea5a4;
        --accent-soft: #e6f7f7;
        --warning: #f59e0b;
        --danger: #ef4444;
        --success: #10b981;
        --border: #e5e7eb;
    }

    html, body, [class*="css"]  {
        font-family: 'DM Sans', system-ui, -apple-system, Segoe UI, sans-serif;
        color: var(--ink);
    }

    .stApp {
        background: radial-gradient(1200px 600px at 10% -10%, #e0f2fe 0%, transparent 55%),
                    radial-gradient(900px 500px at 100% 0%, #fef3c7 0%, transparent 50%),
                    var(--bg);
    }

    .title-block h1 {
        font-family: 'Space Grotesk', system-ui, -apple-system, Segoe UI, sans-serif;
        font-weight: 600;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: var(--muted);
        font-size: 0.98rem;
        margin-bottom: 1.2rem;
    }

    .card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
    }

    .pill {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        background: var(--accent-soft);
        color: var(--accent);
    }

    .metric-row {
        display: flex;
        gap: 0.8rem;
        flex-wrap: wrap;
    }

    .metric {
        background: #f9fafb;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.7rem 0.9rem;
        min-width: 140px;
    }

    .metric h4 {
        font-size: 0.8rem;
        color: var(--muted);
        margin: 0 0 0.2rem;
    }

    .metric div {
        font-size: 1.2rem;
        font-weight: 700;
    }

    .status-complete {
        color: #065f46;
        background: #d1fae5;
        border: 1px solid #a7f3d0;
        padding: 0.5rem 0.7rem;
        border-radius: 10px;
        font-weight: 600;
    }

    .status-review {
        color: #92400e;
        background: #fef3c7;
        border: 1px solid #fde68a;
        padding: 0.5rem 0.7rem;
        border-radius: 10px;
        font-weight: 600;
    }

    .section-title {
        font-family: 'Space Grotesk', system-ui, -apple-system, Segoe UI, sans-serif;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="title-block">
        <h1>PO L1-L2-L3 Classifier</h1>
        <div class="subtitle">Provide a clear description to get the most accurate category mapping.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

EXAMPLE_DESCRIPTION = "Annual SaaS subscription for project management software"
MIN_DESCRIPTION_CHARS = 20
NOT_SURE_VALUE = "Not sure"


def _clean_json_payload(raw_text: str) -> str:
    if not raw_text:
        return raw_text
    stripped = raw_text.strip()
    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    return match.group(0) if match else stripped


def _parse_result(raw_text: str):
    if not raw_text:
        return None, "Empty response from classifier."
    try:
        return json.loads(raw_text), None
    except Exception:
        cleaned = _clean_json_payload(raw_text)
        try:
            return json.loads(cleaned), None
        except Exception:
            return None, "Invalid model response."


def _extract_not_sure_fields(parsed: dict):
    if not isinstance(parsed, dict):
        return []
    return [key for key in ("L1", "L2", "L3") if parsed.get(key) == NOT_SURE_VALUE]


def _init_state():
    if "po_description" not in st.session_state:
        st.session_state.po_description = ""
    if "supplier" not in st.session_state:
        st.session_state.supplier = ""
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_classified_at" not in st.session_state:
        st.session_state.last_classified_at = None
    if "last_inputs" not in st.session_state:
        st.session_state.last_inputs = {"po_description": "", "supplier": ""}
    if "history" not in st.session_state:
        st.session_state.history = []


_init_state()


def _apply_example():
    st.session_state.po_description = EXAMPLE_DESCRIPTION


def _clear_all():
    st.session_state.po_description = ""
    st.session_state.supplier = ""
    st.session_state.last_result = None
    st.session_state.last_classified_at = None
    st.session_state.last_inputs = {"po_description": "", "supplier": ""}
    st.session_state.history = []


top_left, top_right = st.columns([2, 1], gap="large")
with top_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
    st.caption("Use a clear, specific description for the best classification.")
    st.markdown(
        """
        <span class="pill">Tip</span>
        <span style="margin-left: 0.4rem; color: #374151;">Mention the item, purpose, and key qualifiers.</span>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
with top_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Run Stats</div>', unsafe_allow_html=True)
    last_run_label = st.session_state.last_classified_at or "No runs yet"
    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric">
                <h4>Total runs</h4>
                <div>{len(st.session_state.history)}</div>
            </div>
            <div class="metric">
                <h4>Last run</h4>
                <div>{last_run_label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

left_col, right_col = st.columns([2, 1], gap="large")

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Inputs</div>', unsafe_allow_html=True)
    helper_col, insert_col = st.columns([4, 1])
    with helper_col:
        st.caption("Need an example? Insert one to see the expected level of detail.")
    with insert_col:
        st.button("Insert example", on_click=_apply_example)

    with st.form("classify_form"):
        po_description = st.text_area(
            "PO Description",
            height=140,
            key="po_description",
            help="What was purchased and why? Add key qualifiers like subscription or maintenance.",
        )
        supplier = st.text_input(
            "Supplier (optional)",
            key="supplier",
            placeholder="e.g., Acme Corp",
        )

        description_length = len(po_description.strip())
        remaining_chars = max(MIN_DESCRIPTION_CHARS - description_length, 0)
        if description_length < MIN_DESCRIPTION_CHARS:
            st.caption(
                f"Characters: {description_length}/{MIN_DESCRIPTION_CHARS}. "
                f"Add {remaining_chars} more to reach the minimum."
            )
        else:
            st.caption(f"Characters: {description_length}/{MIN_DESCRIPTION_CHARS}. Looks good.")

        action_col, clear_col = st.columns([3, 1])
        with action_col:
            classify_clicked = st.form_submit_button(
                "Classify",
                disabled=description_length < MIN_DESCRIPTION_CHARS,
            )
        with clear_col:
            st.form_submit_button("Clear", on_click=_clear_all)
    st.markdown("</div>", unsafe_allow_html=True)

    if classify_clicked:
        if len(po_description.strip()) < MIN_DESCRIPTION_CHARS:
            st.warning(
                f"Provide at least {MIN_DESCRIPTION_CHARS} characters including purpose and qualifiers."
            )
        else:
            with st.spinner("Classifying..."):
                st.session_state.last_result = classify_po(po_description, supplier)
                st.session_state.last_classified_at = (
                    datetime.now().strftime("%b %d, %Y %I:%M %p") + " (Local time)"
                )
                st.session_state.last_inputs = {
                    "po_description": po_description,
                    "supplier": supplier,
                }
                if st.session_state.last_result:
                    st.session_state.history = (
                        [
                            {
                                "timestamp": st.session_state.last_classified_at,
                                "po_description": po_description,
                                "supplier": supplier,
                                "result": st.session_state.last_result,
                            }
                        ]
                        + st.session_state.history
                    )[:6]

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Status</div>', unsafe_allow_html=True)
    if st.session_state.last_result is None:
        st.info("No runs yet. Submit a description to start.")
    else:
        if st.session_state.last_classified_at:
            st.caption(f"Last run: {st.session_state.last_classified_at}")
        if st.session_state.last_inputs.get("po_description"):
            st.caption(
                f"Description: {st.session_state.last_inputs.get('po_description', '').strip()}"
            )
        if st.session_state.last_inputs.get("supplier"):
            st.caption(f"Supplier: {st.session_state.last_inputs.get('supplier')}")

        parsed, error_message = _parse_result(st.session_state.last_result)
        if parsed is None:
            st.error(error_message)
        else:
            not_sure_fields = _extract_not_sure_fields(parsed)
            if not_sure_fields:
                st.markdown('<div class="status-review">Needs review</div>', unsafe_allow_html=True)
                st.caption("Fields unsure: " + ", ".join(not_sure_fields))
            else:
                st.markdown('<div class="status-complete">Complete</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top: 1rem;">Recent Runs</div>', unsafe_allow_html=True)
    if st.session_state.history:
        for entry in st.session_state.history:
            st.write(f"{entry['timestamp']} - {entry['po_description']}")
    else:
        st.caption("History is empty.")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

st.subheader("Result")
st.caption("Expected output: JSON with L1, L2, and L3 category fields.")

if st.session_state.last_result is None:
    st.info("Run a classification to see results here.")
else:
    parsed, error_message = _parse_result(st.session_state.last_result)
    if parsed is None:
        st.error(error_message)
        with st.expander("Show raw model output"):
            st.text(st.session_state.last_result)
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)
        st.table(
            {
                "Level": ["L1", "L2", "L3"],
                "Category": [
                    parsed.get("L1", NOT_SURE_VALUE),
                    parsed.get("L2", NOT_SURE_VALUE),
                    parsed.get("L3", NOT_SURE_VALUE),
                ],
            }
        )
        st.markdown('<div class="section-title" style="margin-top: 1rem;">Raw JSON</div>', unsafe_allow_html=True)
        st.json(parsed)
        st.code(json.dumps(parsed, indent=2), language="json")
        st.caption("Tip: use the copy icon in the code block to copy JSON quickly.")
        st.markdown("</div>", unsafe_allow_html=True)
