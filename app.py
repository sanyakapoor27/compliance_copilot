import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Digio Compliance Copilot",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("📄 Digio Compliance Copilot")
st.markdown(
    """
    Upload structured ID verification results (JSON) to generate clear, actionable explanations
    for end-users or support teams.
    """
)

FASTAPI_URL = "https://compliance-copilot.onrender.com/generate_explanation"

sample_input_json = {
  "document_type": "AADHAAR_FRONT",
  "fields": {
    "name": { "value": "RAHUL SHARMA", "confidence": 0.67 },
    "dob": { "value": "2005-01-15", "confidence": 0.89 },
    "aadhaar_number": { "masked": False }
  },
  "face_match": {
    "selfie_image_score": 0.82,
    "id_photo_score": 0.44,
    "similarity_score": 0.39
  },
  "forgery_checks": {
    "template_match": False,
    "glare_detected": True,
    "tampering_signals": ["edge_noise", "misalignment"]
  },
  "compliance_checks": {
    "age_check": "FAILED",
    "aadhaar_masking": "FAILED",
    "face_match_threshold": "FAILED"
  },
  "integrity_issues": ["partial crop", "low resolution"],
  "language_hint": "en"
}

st.header("Input Compliance Data (JSON)")
json_input = st.text_area(
    "Paste your structured JSON data here:",
    value=json.dumps(sample_input_json, indent=2),
    height=400,
    help="Ensure the JSON is valid and follows the expected schema."
)

if st.button("Generate Explanation", type="primary"):
    if not json_input:
        st.error("Please paste valid JSON data to generate an explanation.")
    else:
        try:
            json.loads(json_input)

            with st.spinner("Generating explanation..."):
                parsed_json = json.loads(json_input)
                payload_for_fastapi = {"json_data": parsed_json}

                response = requests.post(
                    FASTAPI_URL,
                    json=payload_for_fastapi 
                )
                response.raise_for_status()

                result = response.json()
                explanation = result.get("explanation", "No explanation generated.")

            st.success("Explanation Generated!")
            st.markdown("---")
            st.header("Generated Explanation")
            st.write(explanation)
            st.markdown("---")

        except json.JSONDecodeError:
            st.error("Invalid JSON format. Please check your input.")
        except requests.exceptions.ConnectionError:
            st.error(f"Could not connect to the FastAPI backend at {FASTAPI_URL}. "
                     "Please ensure the FastAPI server is running.")
        except requests.exceptions.HTTPError as e:
            st.error(f"FastAPI backend returned an error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")