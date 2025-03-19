import streamlit as st
import json
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from io import BytesIO
import numpy as np
import re
from utils import validate_with_gemini

var_back_to_job_seleccion = "⬅️ Back to Job Selection"

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Improve Skills For My Resume</h1>", unsafe_allow_html=True)
    
    if "achievement" not in st.session_state:
        st.session_state.achievement = "Inicialice Achivement"

    if "count_key_area" not in st.session_state:
        st.session_state.count_key_area = 0

    print(len(st.session_state.achievements_do_not_pass))
    if (len(st.session_state.achievements_do_not_pass) > 0):
        to_improve = st.session_state.achievements_do_not_pass[0]
        st.write(f"**Current Achievement:** {to_improve['achievement']}")
        # improved_achievement = st.text_input("Please rewrite the achievement with improvements:", value=to_improve["feedback"])
        improved_achievement = st.text_area(
            "Please rewrite the achievement with improvements:",
            value=to_improve["feedback"],
            height=150,  # Ajusta la altura para mostrar 4+ líneas
            key = st.session_state.count_key_area
        )
        if st.button("Validate Improvement"):
            is_valid, feedback = validate_with_gemini(to_improve['job_title'], improved_achievement)
            st.session_state.count_key_area = st.session_state.count_key_area + 1
            if is_valid:
                st.session_state.achievements_pass.append(
                    {"job_title": to_improve['job_title'], "achievement": improved_achievement, "company":to_improve['company'], "key":to_improve['key'] }
                )
                st.session_state.achievements_do_not_pass.pop(0)
                st.success("✅ Achievement improved and validated successfully!")
                print("paso")
                st.rerun()
            else:
                print("No paso")
                st.error("❌ Improvement not valid. Try again with the suggested feedback.")
                st.rerun()  # Reinicia la aplicación

    else:
        output_file = "resume/resume_updated.json"
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(st.session_state.achievements_pass, file, indent=4, ensure_ascii=False)

        # Cargar los datos del archivo original con la estructura completa
        with open("resume/resume_delete_experience_not_relate.json", "r", encoding="utf-8") as file:
            resume_data = json.load(file)

        # Cargar los datos con los achievements actualizados
        with open("resume/resume_updated.json", "r", encoding="utf-8") as file:
            updated_achievements = json.load(file)

        # Crear un diccionario para acceder rápidamente a los achievements por clave
        achievements_dict = {}
        for item in updated_achievements:
            key = item["key"]
            if key in achievements_dict:
                achievements_dict[key].append(item["achievement"])
            else:
                achievements_dict[key] = [item["achievement"]]

        # Sobrescribir los achievements manteniendo la estructura original
        for experience in resume_data["work_experience"]:
            key = experience["key"]
            if key in achievements_dict:
                experience["achievement"] = achievements_dict[key]

        # Guardar el resultado en un nuevo archivo JSON
        with open("resume/resume_updated.json", "w", encoding="utf-8") as file:
            json.dump(resume_data, file, indent=4, ensure_ascii=False)

        print("Archivo resume_update.json generado correctamente.")

        option = st.radio("What would you like to do?", [
                        "Option 1: Add More Skills - Job Achivements",
                        "Option 2: Finalize the customization - Download the Customize CV"
                    ], index=None, key="paso_add_skills")
    
        if option == "Option 1: Add More Skills - Job Achivements":

            ### add more skills
            input_filepath = f"resume/resume_missing_skills.json"
            with open(input_filepath, "r", encoding="utf-8") as file_load:
                missing_skills = json.load(file_load)
            missing_skills = sum(missing_skills.values(), [])


            ### add more skills
            file_path = "resume/resume_delete_experience_not_relate.json"
            with open(file_path, "r", encoding="utf-8") as file_load:
                resume_data = json.load(file_load)

            # Process missing technical and soft skills
            
            # Extract company names from work experience
            jobs_keys = list({exp["key"] for exp in resume_data.get("work_experience", [])})

            st.session_state.page == "add_skills"
            # Inicializar session state si no existe
            if "jobs_keys" not in st.session_state:
                st.session_state.jobs_keys = jobs_keys
                print(st.session_state.jobs_keys)

            if "skills_add_achivments" not in st.session_state:
                st.session_state.skills_add_achievements = missing_skills
                print(st.session_state.skills_add_achievements)

            st.session_state.page = "add_skills"
            st.session_state.skill_pass = []
            st.session_state.to_improve_feedback = "No feedback"
            print(st.session_state.page)
            st.rerun()

        if option == "Option 2: Finalize the customization - Download the Customize CV":
            st.session_state.page = "customization_cv"
            st.rerun()

    # job_id_input = st.text_input("Enter the Job ID to proceed:", key="job_id_input")

    # # Ensure a job was selected in the previous step
    # if "selected_job_id" not in st.session_state or st.session_state.selected_job_id is None:
    #     st.error("⚠️ No job selected. Please go back and select a job first.")
    #     if st.button(var_back_to_job_seleccion):
    #         st.session_state.page = "Option1_2"
    #         st.rerun()
    #     return

    # # MongoDB Connection
    # MONGO_URI = "mongodb+srv://DavidRocha:davidoscar@capstone.9ajag.mongodb.net/?retryWrites=true&w=majority&appName=Capstone"
    # MONGO_DB_NAME = "jobsDB"
    # MONGO_JOBS_COLLECTION = "jobsCollection"

    # client_mongo = pymongo.MongoClient(MONGO_URI)
    # db = client_mongo[MONGO_DB_NAME]
    # collection = db[MONGO_JOBS_COLLECTION]

    # # Retrieve selected job details
    # job_id = ObjectId(st.session_state.selected_job_id)  # Convert back to MongoDB ObjectId
    # selected_job = collection.find_one({"_id": job_id})
    # selected_job["_id"] = str(selected_job["_id"])  # Convert ObjectId to string
    # # Ensure the job description field exists
    # job_description = selected_job.get("Job Description", "No description available")

    # if not selected_job:
    #     st.error("⚠️ Selected job not found in the database. Please go back and choose another job.")
    #     if st.button(var_back_to_job_seleccion):
    #         st.session_state.page = "Option1_2"
    #         st.rerun()
    #     return

    # # Display job details
    # st.subheader("📄 Selected Job")
    # job_details = pd.DataFrame([selected_job]).drop(columns=["_id"], errors="ignore")

    # st.dataframe(job_details)

    # # Upload CV
    # st.subheader("📤 Upload Your Resume")
    # uploaded_cv = st.file_uploader("Please upload your PDF Resume", type=["pdf"])

    # # Process when both CV and job data are available
    # if uploaded_cv is not None:
    #     st.write("Processing your resume and the selected job description...")

    #     extract_cv_information(uploaded_cv)
    #     extract_job_posting_information_from_str(job_description)
    #     customize_cv()
    #     generate_cv()
    #     st.write("✅ Your resume has been tailored for this job application!")

    # # Navigation buttons
    # col1, col2 = st.columns([1, 1])

    # with col1:
    #     if st.button(var_back_to_job_seleccion):
    #         st.session_state.page = "Option1_2"
    #         st.rerun()

    # with col2:
    #     if st.button("🏠 Back to Home"):
    #         st.session_state.page = "Home"
    #         st.rerun()
