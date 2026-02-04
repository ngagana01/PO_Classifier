diff --git a/c:\Users\student\Desktop\generativeai\app.py b/c:\Users\student\Desktop\generativeai\app.py
new file mode 100644
--- /dev/null
+++ b/c:\Users\student\Desktop\generativeai\app.py
@@ -0,0 +1,68 @@
+import json
+import streamlit as st
+from claassifier import classify_po
+
+st.set_page_config(page_title="PO Category Classifier", layout="centered")
+
+st.title("PO L1-L2-L3 Classifier")
+st.caption(
+    "Classify purchase order descriptions into a three-level category hierarchy. "
+    "Provide a clear, specific description for best results."
+)
+
+if "po_description" not in st.session_state:
+    st.session_state.po_description = ""
+if "supplier" not in st.session_state:
+    st.session_state.supplier = ""
+if "last_result" not in st.session_state:
+    st.session_state.last_result = None
+
+with st.container():
+    po_description = st.text_area(
+        "PO Description",
+        height=120,
+        key="po_description",
+        help="Describe the item or service clearly (e.g., what was purchased and its purpose).",
+    )
+    supplier = st.text_input(
+        "Supplier (optional)",
+        key="supplier",
+        help="Add a supplier name to improve classification when relevant.",
+    )
+    with st.expander("Example input"):
+        st.write("Example PO Description:")
+        st.code("Annual SaaS subscription for project management software", language="text")
+
+st.caption("Expected output: JSON with L1, L2, and L3 category fields.")
+
+st.divider()
+
+action_col, clear_col = st.columns([1, 1])
+with action_col:
+    classify_clicked = st.button(
+        "Classify",
+        disabled=not po_description.strip(),
+    )
+with clear_col:
+    clear_clicked = st.button("Clear")
+
+if clear_clicked:
+    st.session_state.po_description = ""
+    st.session_state.supplier = ""
+    st.session_state.last_result = None
+    st.rerun()
+
+if classify_clicked:
+    with st.spinner("Classifying..."):
+        st.session_state.last_result = classify_po(po_description, supplier)
+
+with st.container():
+    st.subheader("Result")
+    if st.session_state.last_result is None:
+        st.info("Run a classification to see results here.")
+    else:
+        try:
+            st.json(json.loads(st.session_state.last_result))
+        except Exception:
+            st.error("The model response was not valid JSON.")
+            st.text(st.session_state.last_result)


