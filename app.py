import time
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Clinical AI Review Assistant",
    page_icon="🏥",
    layout="wide"
)

st.sidebar.title("Prototype Info")
st.sidebar.write("**Topic:** Clinical Decision Making & Pattern Recognition")
st.sidebar.write("**Use Case:** Treatment, Payment, and Operations")
st.sidebar.write("**Approach:** Modular agent-style workflow")
st.sidebar.warning("Proof of concept only. Not for clinical use.")

st.title("Clinical AI Review Assistant")
st.caption("Agentic AI-style proof of concept for clinical decision support and payment integrity review")

st.divider()

sample_notes = {
    "Cardiac Case": """67-year-old male with history of hypertension and type 2 diabetes presents with crushing chest pain radiating to the left arm. Blood pressure is 178/101. Troponin elevated. Started aspirin and heparin. Admitted for observation.""",

    "Respiratory Case": """72-year-old female presents with fever, productive cough, shortness of breath, and oxygen saturation of 88%. Chest x-ray shows right lower lobe infiltrate. Started on ceftriaxone and azithromycin for suspected pneumonia.""",

    "Diabetes Follow-up": """58-year-old patient with type 2 diabetes presents for follow-up. HbA1c is 9.4%. Patient reports medication nonadherence and numbness in both feet. Metformin continued and insulin adjustment discussed.""",

    "Stroke Case": """76-year-old male presents with sudden right-sided weakness, facial droop, and slurred speech. CT head negative for hemorrhage. Neurology consulted. Patient admitted for suspected ischemic stroke."""
}

case_choice = st.selectbox("Choose a sample case", list(sample_notes.keys()))

note = st.text_area(
    "Paste Clinical Note",
    value=sample_notes[case_choice],
    height=220
)


def diagnosis_agent(note):
    text = note.lower()
    diagnoses = []

    rules = [
        ("Hypertension", "I10", ["hypertension", "blood pressure"], "Documented hypertension/elevated BP"),
        ("Type 2 Diabetes", "E11.9", ["diabetes", "hba1c", "metformin", "insulin"], "Diabetes-related terms detected"),
        ("Chest Pain", "R07.9", ["chest pain"], "Patient presents with chest pain"),
        ("Possible Acute Coronary Syndrome", "I24.9", ["troponin", "heparin"], "Cardiac biomarkers/treatment detected"),
        ("Pneumonia", "J18.9", ["pneumonia", "infiltrate", "ceftriaxone", "azithromycin"], "Respiratory infection evidence detected"),
        ("Hypoxemia", "R09.02", ["oxygen saturation", "88%", "hypoxia"], "Low oxygenation evidence detected"),
        ("Diabetic Neuropathy", "E11.40", ["numbness", "feet", "neuropathy"], "Neuropathy symptoms in diabetic patient"),
        ("Suspected Ischemic Stroke", "I63.9", ["weakness", "facial droop", "slurred speech", "ischemic stroke"], "Neurologic deficits detected"),
    ]

    for diagnosis, code, keywords, evidence in rules:
        if any(keyword in text for keyword in keywords):
            diagnoses.append([diagnosis, code, evidence, "90-97%"])

    return diagnoses


def documentation_agent(note):
    text = note.lower()

    checks = {
        "Smoking status": ["smoking", "smoker", "tobacco"],
        "Medication list": ["home meds", "medication list", "current medications"],
        "Relevant lab values": ["troponin", "hba1c", "wbc", "creatinine"],
        "Imaging findings": ["x-ray", "ct", "mri"],
        "Final diagnosis": ["final diagnosis", "confirmed", "discharge diagnosis"],
        "Treatment plan": ["started", "continued", "admitted", "consulted"]
    }

    missing = []

    for item, keywords in checks.items():
        if not any(keyword in text for keyword in keywords):
            missing.append(item)

    return missing


def risk_agent(diagnoses, missing_docs):
    score = len(diagnoses) + len(missing_docs)

    high_risk_terms = ["acute coronary", "stroke", "hypoxemia", "pneumonia"]
    for diagnosis in diagnoses:
        if any(term in diagnosis[0].lower() for term in high_risk_terms):
            score += 2

    if score >= 8:
        return "High", score
    elif score >= 5:
        return "Moderate", score
    else:
        return "Low", score


def timeline_agent(note):
    text = note.lower()
    events = []

    if "presents" in text:
        events.append("Patient presentation documented")
    if "blood pressure" in text or "oxygen saturation" in text or "hba1c" in text:
        events.append("Objective clinical findings identified")
    if "x-ray" in text or "ct" in text or "mri" in text:
        events.append("Imaging results referenced")
    if "started" in text or "continued" in text or "insulin" in text:
        events.append("Treatment or medication action documented")
    if "admitted" in text or "consulted" in text:
        events.append("Care escalation or specialist involvement documented")

    return events


def confidence_agent(diagnoses, missing_docs):
    base = 95
    penalty = len(missing_docs) * 4
    bonus = min(len(diagnoses) * 2, 6)
    confidence = max(50, min(99, base + bonus - penalty))
    return confidence


def summary_agent(diagnoses, missing_docs, risk_level):
    diagnosis_names = [d[0] for d in diagnoses]

    if diagnosis_names:
        diagnosis_text = ", ".join(diagnosis_names)
    else:
        diagnosis_text = "no major coded conditions"

    if missing_docs:
        missing_text = ", ".join(missing_docs[:3])
    else:
        missing_text = "no major documentation gaps"

    return (
        f"The clinical note suggests {diagnosis_text}. "
        f"The case is categorized as {risk_level.lower()} risk based on detected conditions and documentation completeness. "
        f"Key documentation concerns include {missing_text}. "
        f"This workflow supports human reviewers by prioritizing cases, surfacing evidence, and identifying documentation gaps before final coding or payment decisions."
    )


if st.button("Analyze Clinical Note"):
    with st.spinner("Running Clinical Pattern Recognition Agent..."):
        time.sleep(0.5)
        diagnoses = diagnosis_agent(note)

    with st.spinner("Running Documentation Completeness Agent..."):
        time.sleep(0.5)
        missing_docs = documentation_agent(note)

    with st.spinner("Running Risk Stratification Agent..."):
        time.sleep(0.5)
        risk_level, risk_score = risk_agent(diagnoses, missing_docs)

    with st.spinner("Generating Clinical Timeline and Summary..."):
        time.sleep(0.5)
        timeline = timeline_agent(note)
        confidence = confidence_agent(diagnoses, missing_docs)
        summary = summary_agent(diagnoses, missing_docs, risk_level)

    st.success("Agentic workflow complete")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Detected Conditions", len(diagnoses))
    col2.metric("Documentation Gaps", len(missing_docs))
    col3.metric("Risk Level", risk_level)
    col4.metric("Confidence", f"{confidence}%")

    st.divider()

    st.subheader("Clinical Pattern Recognition Agent")
    diagnosis_df = pd.DataFrame(
        diagnoses,
        columns=["Detected Diagnosis", "Suggested ICD-10", "Evidence", "Confidence"]
    )
    st.dataframe(diagnosis_df, use_container_width=True)

    st.subheader("Documentation Completeness Agent")
    if missing_docs:
        for item in missing_docs:
            st.warning(f"Missing or unclear: {item}")
    else:
        st.success("No major documentation gaps detected.")

    st.subheader("Risk Stratification Agent")
    if risk_level == "High":
        st.error(f"Risk Level: HIGH | Score: {risk_score}")
    elif risk_level == "Moderate":
        st.warning(f"Risk Level: MODERATE | Score: {risk_score}")
    else:
        st.success(f"Risk Level: LOW | Score: {risk_score}")

    st.subheader("Clinical Timeline Agent")
    for event in timeline:
        st.write(f"✅ {event}")

    st.subheader("Clinical Reasoning Summary")
    st.info(summary)

    st.subheader("Reviewer Recommendation")
    st.write(
        "Human review is recommended before claim approval, denial, or final coding. "
        "This prototype demonstrates how modular AI agents can assist reviewers without replacing clinical or coding judgment."
    )
