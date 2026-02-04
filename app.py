import json
from datetime import datetime

import streamlit as st

from claassifier import classify_po

st.set_page_config(page_title="PO Category Classifier", layout="centered")

st.title("PO L1-L2-L3 Classifier")
st.caption(
    "Classify purchase order descriptions into a three-level category hierarchy. "
    "Provide a clear, specific description for best results."
)

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

EXAMPLE_DESCRIPTION = "Annual SaaS subscription for project management software"

with st.container():
    st.subheader("Inputs")
    po_description = st.text_area(
        "PO Description",
        height=120,
        key="po_description",
        help="Describe the item or service clearly (e.g., what was purchased and its purpose).",
    )
    st.caption(
        "Tip: Include the item/service, purpose, and any key qualifiers (e.g., subscription, maintenance, parts)."
    )
    supplier = st.text_input(
        "Supplier (optional)",
        key="supplier",
        help="Add a supplier name to improve classification when relevant.",
        placeholder="e.g., Acme Corp",
    )

    example_col, spacer_col = st.columns([1, 3])
    with example_col:
        if st.button("Fill example"):
            st.session_state.po_description = EXAMPLE_DESCRIPTION
            st.rerun()
    with spacer_col:
        with st.expander("Example input"):
            st.write("Example PO Description:")
            st.code(EXAMPLE_DESCRIPTION, language="text")

st.caption("Expected output: JSON with L1, L2, and L3 category fields.")

st.divider()

action_col, clear_col = st.columns([3, 1])
with action_col:
    classify_clicked = st.button(
        "Classify",
        disabled=not po_description.strip(),
    )
with clear_col:
    clear_clicked = st.button("Clear")

if clear_clicked:
    st.session_state.po_description = ""
    st.session_state.supplier = ""
    st.session_state.last_result = None
    st.session_state.last_classified_at = None
    st.session_state.last_inputs = {"po_description": "", "supplier": ""}
    st.rerun()

if classify_clicked:
    with st.spinner("Classifying..."):
        st.session_state.last_result = classify_po(po_description, supplier)
        st.session_state.last_classified_at = datetime.now().strftime("%H:%M")
        st.session_state.last_inputs = {
            "po_description": po_description,
            "supplier": supplier,
        }

with st.container():
    st.subheader("Result")
    if st.session_state.last_result is None:
        st.info("Run a classification to see results here.")
    else:
        if st.session_state.last_classified_at:
            st.caption(f"Last classified at {st.session_state.last_classified_at}.")

        try:
            parsed = json.loads(st.session_state.last_result)
            st.success("Classification completed.")
            st.json(parsed)
            st.code(json.dumps(parsed, indent=2), language="json")
        except Exception:
            st.error("The model response was not valid JSON.")
            with st.expander("Show raw model output"):
                st.text(st.session_state.last_result)

        inputs_changed = (
            po_description != st.session_state.last_inputs.get("po_description", "")
            or supplier != st.session_state.last_inputs.get("supplier", "")
        )
        if inputs_changed:
            st.warning("Inputs changed since last run. Click Classify to refresh the result.")
