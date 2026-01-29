import streamlit as st
import google.generativeai as genai
import whisper
import tempfile
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

**PATIENT SCRIPT (Mental Model):**
* **Opening Statement:** "I tried to grab a branch to stop myself falling, and it nearly ripped my arm off. Now my hand feels dead and tingly."
* **Reaction:** If doctor tries to force movement, James cries out and pulls away.
"""

# ==========================================
# 2. DO NOT TOUCH THE CODE BELOW
# ==========================================

# A. Setup Google Gemini (TEXT ONLY – CORRECT)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-1.0-pro")
except Exception as e:
    st.error(f"Gemini setup error: {e}")

# B. Load Whisper model ONCE (cached)
@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

whisper_model = load_whisper()

# C. Page Setup
st.set_page_config(page_title="AMC Clinical Exam", layout="wide")
st.title("AMC Clinical Exam Simulation")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# D. Left Column: Scenario
with col1:
    st.header("1. Scenario")
    st.info(TOPIC_SCENARIO)

    st.subheader("Tasks")
    st.markdown(TOPIC_TASKS)

# E. Right Column: Audio + Grading
with col2:
    st.header("2. Perform Task (Audio)")
    st.write("Record your answer to the tasks on the left.")

    audio_value = st.audio_input("Record your answer")

    if audio_value:
        st.audio(audio_value)

        if st.button("Transcribe & Grade My Audio"):
            try:
                # Save audio to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_value.read())
                    audio_path = tmp.name

                # Step 1: Transcription
                with st.spinner("📝 Transcribing audio..."):
                    transcription = whisper_model.transcribe(audio_path)
                    transcript = transcription["text"]

                st.markdown("### 📝 Audio Transcript")
                st.write(transcript)

                # Step 2: Gemini Evaluation
                with st.spinner("👨‍⚕️ Examiner is grading..."):
                    response = model.generate_content(f"""
You are an expert AMC Examiner.

--- CASE DATA ---
SCENARIO:
{TOPIC_SCENARIO}

TASKS:
{TOPIC_TASKS}

RUBRIC:
{TOPIC_RUBRIC}

--- STUDENT TRANSCRIPT ---
{transcript}

--- INSTRUCTIONS ---
1. Identify any CRITICAL ERRORS.
2. Comment on Safety, Clinical Examination, and Diagnosis.
3. Give a final verdict: PASS or FAIL.

Use AMC examiner tone.
""")

                st.markdown("### 👨‍⚕️ Examiner Feedback")
                st.write(response.text)

                # Cleanup
                os.remove(audio_path)

            except Exception as e:
                st.error(f"Error processing audio: {e}")

# F. Hidden Rubric
st.markdown("---")
st.write("### Review")

with st.expander("👁️ Click to Reveal Official Rubric & Diagnosis"):
    st.markdown("### Official Examiner Guide")
    st.markdown(TOPIC_RUBRIC)
    st.info("Tip: Compare the 'Critical Errors' above with the AI feedback.")
