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
    model = genai.GenerativeModel("models/gemini-pro")
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
response = model.generate_content(f"""
You are an Australian Medical Council (AMC) Clinical Examiner.
You must grade STRICTLY using the provided rubric.
Do NOT be lenient.

========================
CASE INFORMATION
========================
SCENARIO:
{TOPIC_SCENARIO}

TASKS:
{TOPIC_TASKS}

========================
OFFICIAL EXAMINER RUBRIC
========================
{TOPIC_RUBRIC}

========================
STUDENT TRANSCRIPT
========================
{transcript}

========================
MARKING INSTRUCTIONS
========================

STEP 1: RUBRIC COMPARISON  
Compare the student's transcript AGAINST EACH of the following:

A. SAFETY  
- Did the student attempt or suggest forcing movement despite pain? (YES/NO)

B. CLINICAL EXAMINATION  
- Did the student inspect the hand appropriately? (YES/NO)
- Did the student assess motor function appropriately, respecting pain? (YES/NO)
- Did the student identify BOTH C8 (little finger) AND T1 (inner elbow) sensory loss? (YES/NO)

C. DIAGNOSIS  
- Did the student correctly diagnose Lower Brachial Plexus Injury / Klumpke’s Palsy? (YES/NO)
- Did the student explain C8/T1 involvement? (YES/NO)

STEP 2: CRITICAL ERROR CHECK  
If ANY of the following occurred, the candidate MUST FAIL:
- Forced passive movement
- Incorrect diagnosis (e.g. ulnar nerve palsy)
- Failure to assess T1 dermatome

STEP 3: FINAL VERDICT  
- If ANY critical error occurred → FAIL
- Otherwise → PASS

========================
OUTPUT FORMAT (MANDATORY)
========================

### 📝 Rubric Comparison
- Safety: YES/NO (with justification)
- Clinical Examination: YES/NO (with justification)
- Diagnosis: YES/NO (with justification)

### 🚨 Critical Errors
- List any critical errors explicitly (or state “None”)

### 👨‍⚕️ Examiner Feedback
- Brief, direct AMC-style feedback (no encouragement)

### ✅ Final Verdict
PASS or FAIL
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
