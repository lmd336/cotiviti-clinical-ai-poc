import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Clinical AI Review Assistant",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Clinical AI Review Assistant")
st.caption("Agentic AI-style proof of concept for clinical decision support and payment integrity review")

st.divider()

sample_note = """67-year-old male with history of hypertension and type 2 diabetes presents with crushing chest pain radiating to the left arm. Blood pressure is 178/101. Troponin elevated. Started aspirin and heparin. Admitted for observation."""

note = st.text_area("Paste Clinical Note", value=sample_note, height=220)


def diagnosis_agent(note):
    text = note.lower()
    diagnoses = []

    if "hypertension" in text or "blood pressure" in text:
        diagnoses.append(["Hypertension", "I10", "Documented hypertension/elevated BP", "96%"])

    if "diabetes" in text:
        diagnoses.append(["Type 2 Diabetes", "E11.9", "Documented diabetes without complications", "95%"])

    if "chest pain" in text:
        diagnoses.append(["Chest Pain", "R07.9", "Patient presents with chest pain", "97%"])

    if "troponin" in text or "heparin" in text:
        diagnoses.append(["Possible Acute Coronary Syndrome", "I24.9", "Elevated troponin and heparin suggest cardiac concern", "90%"])

    return diagnoses


def documentation_agent(note):
    text = note.lower()

    checks = {
        "Smoking status": ["smoking", "smoker", "tobacco"],
        "Current medication list": ["home meds", "medication list", "current medications"],
        "ECG/EKG findings": ["ecg", "ekg"],
        "HbA1c value": ["a1c", "hba1c"],
        "Family cardiac history": ["family history"],
        "Final cardiac diagnosis": ["myocardial infarction", "nstemi", "stemi", "unstable angina"]
    }

    missing = []

    for item, keywords in checks.items():
        if not any(keyword in text for keyword in keywords):
            missing.append(item)

    return missing


def risk_agent(diagnoses, missing_docs):
    score = 0

    for diagnosis in diagnoses:
        name = diagnosis[0].lower()
        if "acute coronary" in name:
            score += 3
        elif "chest pain" in name:
            score += 2
        else:
            score += 1

    score += min(len(missing_docs), 4)

    if score >= 7:
        return "High", score
    elif score >= 4:
        return "Moderate", score
    else:
        return "Low", score


def summary_agent(diagnoses, missing_docs, risk_level):
    diagnosis_names = [d[0] for d in diagnoses]

    return (
        f"This note contains evidence of {', '.join(diagnosis_names)}. "
        f"The case is categorized as {risk_level.lower()} risk due to the combination of clinical findings "
        f"and documentation gaps. A human reviewer should validate the suggested codes and confirm whether "
        f"additional documentation is needed before payment or coding decisions are finalized."
    )


if st.button("Analyze Clinical Note"):
    diagnoses = diagnosis_agent(note)
    missing_docs = documentation_agent(note)
    risk_level, risk_score = risk_agent(diagnoses, missing_docs)
    summary = summary_agent(diagnoses, missing_docs, risk_level)

    st.success("Analysis Complete")

    col1, col2, col3 = st.columns(3)

    col1.metric("Detected Conditions", len(diagnoses))
    col2.metric("Documentation Gaps", len(missing_docs))
    col3.metric("Risk Level", risk_level)

    st.divider()

    st.subheader("🧠 Diagnosis Agent")
    diagnosis_df = pd.DataFrame(
        diagnoses,
        columns=["Detected Diagnosis", "Suggested ICD-10", "Evidence", "Confidence"]
    )
    st.dataframe(diagnosis_df, use_container_width=True)

    st.subheader("🔍 Documentation Review Agent")
    if missing_docs:
        for item in missing_docs:
            st.warning(f"Missing or unclear: {item}")
    else:
        st.success("No major documentation gaps detected.")

    st.subheader("📊 Risk Assessment Agent")
    if risk_level == "High":
        st.error(f"Risk Level: HIGH | Score: {risk_score}")
    elif risk_level == "Moderate":
        st.warning(f"Risk Level: MODERATE | Score: {risk_score}")
    else:
        st.success(f"Risk Level: LOW | Score: {risk_score}")

    st.subheader("📝 Clinical Summary Agent")
    st.info(summary)

    st.subheader("✅ Reviewer Recommendation")
    st.write(
        "Human review is recommended before claim approval or final coding. "
        "This prototype is designed to assist reviewers by prioritizing cases, highlighting evidence, "
        "and identifying missing documentation."
    )

    st.caption(
        "Disclaimer: This proof of concept uses simplified pattern recognition rules. "
        "It is not a production medical coding system or clinical decision-making tool."
    )
