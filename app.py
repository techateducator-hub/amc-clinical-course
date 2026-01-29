import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. EDIT THIS SECTION ONLY (YOUR CONTENT)
# ==========================================

TOPIC_SCENARIO = """
**Patient:** James, 68-year-old male.
**Setting:** Emergency Department.
**Presenting Complaint:** Pain, weakness, and "pins and needles" in the right hand after a fall.

**Situation:**
James was brought in after falling from a tree. He states he tried to grab a branch on the way down to break his fall. He is hemodynamically stable.
"""

TOPIC_TASKS = """
1. **General Inspection:** Perform a focused inspection of the hand and arm, noting specific deformities.
2. **Neurological Exam:** Assess Motor and Sensory function using a myotomal/dermatomal approach (adapting to patient's pain).
3. **Diagnosis:** Explain the diagnosis of Lower Brachial Plexus Injury to the patient, detailing the C8/T1 involvement.
"""

TOPIC_RUBRIC = """
**DIAGNOSIS:** Lower Brachial Plexus Injury (Klumpke’s Palsy).

**CRITICAL ERRORS (FAIL CRITERIA):**
* **Forcing Passive Movement:** Attempting to force joints when the patient refuses due to pain.
* **Incorrect Diagnosis:** Diagnosing simple Ulnar Nerve palsy instead of Brachial Plexus injury.
* **Missing T1 Involvement:** Failing to check sensation on the inner elbow (T1 dermatome).

**KEY FINDINGS (To be elicited):**
* **Inspection:** Full Claw Hand (all fingers curled), patient holds arm still.
* **Motor:** Patient refuses active movement due to pain.
* **Sensory:** Numbness in Little Finger (C8) AND Inner Elbow (T1). Normal sensation in Thumb (C6) and Middle Finger (C7).
"""

# ==========================================
# 2. DO NOT TOUCH THE CODE BELOW
# ==========================================

# A. Setup Google Gemini
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Using gemini-1.5-flash as it supports native audio processing
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Gemini setup error: {e}")

# B. Page Setup
st.set_page_config(page_title="AMC Clinical Exam", layout="wide")
st.title("AMC Clinical Exam Simulation")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# C. Left Column: Scenario
with col1:
    st.header("1. Scenario")
    st.info(TOPIC_SCENARIO)

    st.subheader("Tasks")
    st.markdown(TOPIC_TASKS)

# D. Right Column: Audio + Grading
with col2:
    st.header("2. Perform Task (Audio)")
    st.write("Record your answer to the tasks on the left.")

    audio_value = st.audio_input("Record your answer")

    if audio_value:
        st.audio(audio_value)

        if st.button("Grade My Performance"):
            try:
                # Step: Gemini Evaluation (Audio-to-Text + Grading)
                with st.spinner("👨‍⚕️ Examiner is listening and grading..."):
                    
                    examiner_prompt = f"""
You are an Australian Medical Council (AMC) Clinical Examiner.
You must grade STRICTLY using the provided rubric.
Do NOT be lenient. 

First, transcribe the student's audio. Then, evaluate them based on the transcript.

========================
CASE INFORMATION
========================
SCENARIO: {TOPIC_SCENARIO}
TASKS: {TOPIC_TASKS}
OFFICIAL EXAMINER RUBRIC: {TOPIC_RUBRIC}

========================
MARKING INSTRUCTIONS
========================
STEP 1: RUBRIC COMPARISON
Compare the student's performance AGAINST EACH of the following:
- SAFETY: Did they force movement?
- CLINICAL: Did they identify C8 and T1 loss?
- DIAGNOSIS: Did they correctly identify Lower Brachial Plexus Injury?

STEP 2: FINAL VERDICT
- If ANY critical error occurred (forced movement, wrong diagnosis, missed T1) -> FAIL
- Otherwise -> PASS

========================
OUTPUT FORMAT (MANDATORY)
========================
### 📝 Transcription
(Provide the full text of what the student said)

### 📊 Rubric Analysis
(Point by point breakdown)

### 🚨 Critical Errors
(Explicitly list them or state "None")

### ✅ Final Verdict
PASS or FAIL
"""
                    # Sending audio data directly to Gemini
                    audio_data = audio_value.read()
                    response = model.generate_content([
                        examiner_prompt,
                        {"mime_type": "audio/wav", "data": audio_data}
                    ])

                    st.markdown("### 👨‍⚕️ Examiner Feedback")
                    st.write(response.text)

            except Exception as e:
                st.error(f"Error processing audio: {e}")

# E. Hidden Rubric
st.markdown("---")
st.write("### Review")

with st.expander("👁️ Click to Reveal Official Rubric & Diagnosis"):
    st.markdown("### Official Examiner Guide")
    st.markdown(TOPIC_RUBRIC)
    st.info("Tip: Compare the 'Critical Errors' above with the AI feedback.")
