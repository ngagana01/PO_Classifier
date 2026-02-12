# 📦 PO L1–L2–L3 Category Classifier (Generative AI + LLM)

A Generative AI powered Purchase Order (PO) classification system that automatically maps PO descriptions into L1, L2, and L3 categories using a controlled enterprise taxonomy and an LLM (via Groq API).
Built with Streamlit + LLM prompting + taxonomy grounding for consistent structured output.

***

# How It Works


* User enters PO description

- System sends prompt + taxonomy to LLM

- Model selects only allowed L1–L2–L3 categories

- Output returned in strict JSON format

- Results shown in Streamlit dashboard
  
***

# Features

  
- Taxonomy-restricted categories

- Structured JSON output

- Retry + fallback handling

- Example inputs

***

# Live Demo
The application is deployed and accessible here:

https://poclassifier-apdzrilabhb6zqmgp5c3xm.streamlit.app/
  
***

#  Project Structure


<pre> generativeai/

├── app.py

├── classifier.py

├── prompts.py

├── taxonomy.py

├── requirements.txt

└── README.md  <pre>
  

