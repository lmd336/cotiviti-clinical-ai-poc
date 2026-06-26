import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Clinical AI Review Assistant",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Clinical AI Review Assistant")
st.caption("Proof of Concept for Clinical Decision Support & Payment Integrity")

st.divider()

sample_note = """67-year-old male with history of hypertension and type 2 diabetes presents with crushing chest pain radiating to the left arm. Blood pressure is 178/101. Troponin elevated. Started aspirin and heparin. Admitted for observation."""

note = st.text_area(
    "Paste Clinical Note",
    value=sample_note,
    height=220
)

def diagnosis_agent(note):
    note = note.lower()
    diagnoses = []

    if "hypertension" in note or "blood pressure" in note:
        diagnoses.append({
            "Diagnosis": "Hypertension",
            "ICD-10": "I10",
            "Confidence": "96%"
        })

    if "diabetes" in note:
        diagnoses.append({
            "Diagnosis": "Type 2 Diabetes",
            "ICD-10": "E11.9",
            "Confidence": "95%"
        })

    if "chest pain" in note:
        diagnoses.append({
            "Diagnosis": "Chest Pain",
            "ICD-10": "R07.9",
            "Confidence": "97%"
        })

    if "troponin" in note:
        diagnoses.append({
            "Diagnosis": "Possible Acute Coronary Syndrome",
            "ICD-10": "I24.9",
            "Confidence": "90%"
        })

    return diagnoses

if st.button("Analyze Clinical Note"):
    diagnoses = diagnosis_agent(note)

    st.success("Analysis Complete")

    st.subheader("Detected Diagnoses")
    df = pd.DataFrame(diagnoses)
    st.dataframe(df, use_container_width=True)
