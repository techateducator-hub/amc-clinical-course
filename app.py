import streamlit as st
import google.generativeai as genai

# 1. SETUP
api_key = st.secrets["GEMINI_API_KEY"] 
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AMC Clinical Exam Trainer", layout="wide")
st.title("AMC Clinical Exam Simulation")

# 2. DEFINE THE CASE
# (You can swap this text out for any topic later)
if 'case_topic' not in st.session_state:
    st.session_state.case_topic = "Fatigue in a Young Woman"

col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Scenario")
    st.info("""
    **Patient:** Sarah, 28yo female.
    **Setting:** General Practice.
    **Complaint:** "Doctor, I'm just so tired all the time."
    """)
    st.markdown("### Tasks")
    st.markdown("""
    1.  **History:** Explore the presenting complaint.
    2.  **Diagnosis:** Explain what you think is wrong.
    3.  **Management:** Counsel the patient on the next steps.
    """)

# 3. THE AUDIO INTERACTION
with col2:
    st.header("2. Perform Task (Audio)")
    st.write("Click the microphone to record your response for **Task 1 (History)**.")

    # This creates the built-in audio recorder
    audio_value = st.audio_input("Record your answer")

    if audio_value:
        st.audio(audio_value) # Playback for the student to hear themselves

        if st.button("Grade My Audio"):
            with st.spinner('AI is listening and grading...'):
                try:
                    # We send the raw audio data directly to Gemini
                    audio_bytes = audio_value.read()
                    
                    prompt = """
                    You are a strict examiner for the Australian Medical Council (AMC) exam. 
                    Listen to the student's audio response. 
                    
                    Provide feedback in this format:
                    1. **Communication Style:** (Was it empathetic? clear?)
                    2. **Missing Questions:** (What critical questions did they fail to ask?)
                    3. **Pass/Fail:** (Give a verdict)
                    """

                    response = model.generate_content([
                        prompt,
                        {
                            "mime_type": "audio/wav",
                            "data": audio_bytes
                        }
                    ])
                    
                    st.success("Grading Complete")
                    st.write(response.text)
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# 4. RUBRIC (Hidden)
st.markdown("---")
with st.expander("Show Official Answer Key"):
    st.warning("Don't peek until you try!")
    st.markdown("""
    * **Must Ask:** Menstrual history (heavy periods?), Diet (vegetarian?), Family history of anemia.
    * **Red Flags:** Weight loss, night sweats.
    * **Diagnosis:** Iron Deficiency Anemia.
    """)
