import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from io import BytesIO
import numpy as np
import re
from utils import validate_with_gemini
import time

var_back_to_job_seleccion = "⬅️ Back to Job Selection"

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Add Skills For My Resume</h1>", unsafe_allow_html=True)

    # Check if there are skills to process
    print(st.session_state.skills_add_achievements)
    print(len(st.session_state.skills_add_achievements))
    st.session_state.count_key_area = st.session_state.count_key_area + 1

    if((len(st.session_state.skills_add_achievements) > 0) and ("skill_in_process" not in st.session_state)):
        
        add_skill = st.session_state.skills_add_achievements[0]

        st.write(f"**Skill to add achievements:** {add_skill}")

        choice = st.selectbox(f"Do you have experience with {add_skill}?", ("yes", "no"))

        if choice == "no":
            st.session_state.skills_add_achievements.pop(0)  # Eliminar la primera habilidad si selecciona "no"
            st.warning(f"Removed skill: {add_skill}")
            st.rerun()
        else:
            st.success(f"Proceeding with skill: {add_skill}")

            # Example list of companies (you can replace this with dynamic data)
            jobs_keys = st.session_state.jobs_keys

            # Let user select the company where they gained experience with this skill
            selected_key = st.selectbox("Select the Company - Job Name where you gained experience:", jobs_keys)

            # Let user describe their experience with this skill
            achievement_description = st.text_area(
                "Describe your experience with this skill, including how you obtained it and a metric or result achieved:",
                value=st.session_state.to_improve_feedback, 
                height=150,  # Ajusta la altura para mostrar 4+ líneas
                key = st.session_state.count_key_area
            )


            if st.button("Add Achievement"):

                st.session_state.count_key_area = st.session_state.count_key_area + 1

                if achievement_description:

                    # Load the resume data
                    file_path = "resume/resume_delete_experience_not_relate.json"

                    with open(file_path, "r", encoding="utf-8") as file_load:
                        job_experience = json.load(file_load)

                    selected_job = next((job for job in job_experience["work_experience"] if job["key"] == selected_key), None)

                    is_valid, feedback = validate_with_gemini(selected_job['job_title'], achievement_description)
                    st.session_state.to_improve_feedback = feedback
                    if is_valid:
                        st.session_state.skill_pass.append(
                            {"job_title": selected_job['job_title'], "achievement": achievement_description, "company":selected_job['company'], "key":selected_job['key'] }
                        )
                        st.session_state.skills_add_achievements.pop(0)
                        st.success("✅ Achievement improved and validated successfully!")
                        st.session_state.to_improve_feedback = "No feedback"
                        time.sleep(3)
                        if "skill_in_process" in st.session_state:
                            del st.session_state.skill_in_process

                        st.rerun()
                    else:
                        if "skill_in_process" not in st.session_state:
                            st.session_state.skill_in_process = add_skill
                        st.rerun()

    if((len(st.session_state.skills_add_achievements) > 0) and ("skill_in_process" in st.session_state)):

        add_skill = st.session_state.skill_in_process
        st.write(f"**Skill to add achievements:** {add_skill}")
        # Example list of companies (you can replace this with dynamic data)
        jobs_keys = st.session_state.jobs_keys

        # Let user select the company where they gained experience with this skill
        selected_key = st.selectbox("Select the Company - Job Name where you gained experience:", jobs_keys)

        # Let user describe their experience with this skill
        achievement_description = st.text_area(
            "Describe your experience with this skill, including how you obtained it and a metric or result achieved:",
            value=st.session_state.to_improve_feedback, 
            height=150,  # Ajusta la altura para mostrar 4+ líneas
            key = st.session_state.count_key_area
        )


        if st.button("Add Achievement"):

            st.session_state.count_key_area = st.session_state.count_key_area + 1

            if achievement_description:

                # Load the resume data
                file_path = "resume/resume_delete_experience_not_relate.json"

                with open(file_path, "r", encoding="utf-8") as file_load:
                    job_experience = json.load(file_load)

                selected_job = next((job for job in job_experience["work_experience"] if job["key"] == selected_key), None)

                is_valid, feedback = validate_with_gemini(selected_job['job_title'], achievement_description)
                st.session_state.to_improve_feedback = feedback
                if is_valid:
                    st.session_state.skill_pass(
                        {"job_title": selected_job['job_title'], "achievement": achievement_description, "company":selected_job['company'], "key":selected_job['key'] }
                    )
                    st.session_state.skills_add_achievements.pop(0)
                    st.success("✅ Achievement improved and validated successfully!")
                    st.session_state.to_improve_feedback = "No feedback"
                    time.sleep(3)
                    if "skill_in_process" in st.session_state:
                        del st.session_state.skill_in_process

                    st.rerun()

    if(len(st.session_state.skills_add_achievements) == 0):
        if len(st.session_state.skill_pass)>0:
            output_file = "resume/resume_user_answers.json"
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(st.session_state.skill_pass, file, indent=4, ensure_ascii=False)

            


        
        st.session_state.page = "customization_cv"
        st.rerun()
