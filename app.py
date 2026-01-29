import streamlit as st
import google.generativeai as genai

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

# A. Setup Google AI (Simplified to avoid errors)
try:
    api_key = st.secrets["GEMINI_API_KEY"] 
    genai.configure(api_key=api_key)
    # This line is now simplified to prevent the "Unknown field" error
    model = genai.GenerativeModel('models/gemini-1.0-pro-vision')
except Exception as e:
    st.error(f"Error: {e}")

# B. Page Setup
st.set_page_config(page_title="AMC Clinical Exam", layout="wide")
st.title("AMC Clinical Exam Simulation")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# C. Left Column: The Case
with col1:
    st.header("1. Scenario")
    st.info(TOPIC_SCENARIO)  
    
    st.subheader("Tasks")
    st.markdown(TOPIC_TASKS) 

# D. Right Column: Audio Recorder & Grading
with col2:
    st.header("2. Perform Task (Audio)")
    st.write("Record your answer to the tasks on the left.")
    
    audio_value = st.audio_input("Record your answer")

    if audio_value:
        st.audio(audio_value)
        if st.button("Transcribe & Grade My Audio"):
            with st.spinner('AI is transcribing and analyzing...'):
                try:
                    prompt = f"""
                    You are an expert AMC Examiner.
                    
                    --- CASE DATA ---
                    SCENARIO: {TOPIC_SCENARIO}
                    TASKS: {TOPIC_TASKS}
                    RUBRIC/ANSWER KEY: {TOPIC_RUBRIC}
                    
                    --- INSTRUCTIONS ---
                    Listen to the student's audio recording.
                    
                    STEP 1: TRANSCRIPT
                    Write down a verbatim transcript of what the student said.
                    Label this section "### 📝 Audio Transcript".
                    
                    STEP 2: EVALUATION
                    Compare the transcript against the Rubric.
                    1. **Safety:** Did they force movement despite James's pain?
                    2. **Clinical:** Did they find the C8/T1 sensory loss?
                    3. **Diagnosis:** Did they identify Klumpke's Palsy?
                    Label this section "### 👨‍⚕️ Examiner Feedback".
                    
                    STEP 3: VERDICT
                    Give a final PASS or FAIL.
                    """
                    
                    response = model.generate_content([
                        prompt, 
                        {"mime_type": "audio/wav", "data": audio_value.read()}
                    ])
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error processing audio: {e}")

# E. The Hidden Rubric (Clickable Reveal)
st.markdown("---")
st.write("### Review")

with st.expander("👁️ Click to Reveal Official Rubric & Diagnosis"):
    st.markdown("### Official Examiner Guide")
    st.markdown(TOPIC_RUBRIC)
    st.info("Tip: Compare the 'Critical Errors' above with the AI feedback.")
