# option1.py
from pypdf import PdfReader
import docx
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import google.generativeai as genai
import io
from io import BytesIO
from utils import extract_cv_information, extract_job_posting_information,resume_education_info_personal,resume_promt_summary,resume_delete_experience_not_related,resume_skills, validate_with_gemini
import pymongo
import json
import improve_skills

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Tailor my resume for a specific job opportunity</h1>", unsafe_allow_html=True)
    st.write("Here you can upload your resume and customize it for a job opportunity.")
    
    st.write("")
    
    uploaded_cv = None
    uploaded_cv = st.file_uploader("Please upload your PDF Resume", type=["pdf"])

    st.write("")

    uploaded_job = None
    uploaded_job = st.file_uploader("Please upload your PDF Job Description", type=["pdf"])

    if ((uploaded_cv is not None) and (uploaded_job is not None)):
        extract_cv_information(uploaded_cv)
        extract_job_posting_information(uploaded_job)
        resume_education_info_personal()
        resume_promt_summary()
        resume_skills()
        resume_delete_experience_not_related()


        # Verificar si todos los achievements están vacíos
        # Load the resume data
        file_path = "resume/resume_delete_experience_not_relate.json"
        with open(file_path, "r", encoding="utf-8") as file_load:
            filter_to_continue = json.load(file_load)

        if all(not experience["achievement"] for experience in filter_to_continue["work_experience"]):
            print("entro line 46")
            st.warning(
                "⚠️ Sorry, none of your experiences match the job posting. "
                "We recommend rewriting your achievements to better highlight relevant skills and trying again. "
                "Click below to return to the home page."
            )
            if st.button("🏠 Back to Home"):
                st.session_state.page = "Home"
                st.rerun()
        
        else:
            st.session_state.page == "analize_skills"
            # Inicializar session state si no existe
            if "achievements_pass" not in st.session_state:
                st.session_state.achievements_pass = []

            if "achievements_do_not_pass" not in st.session_state:
                st.session_state.achievements_do_not_pass = []

            # Load the resume data
            file_path = "resume/resume_delete_experience_not_relate.json"

            with open(file_path, "r", encoding="utf-8") as file_load:
                resume_data = json.load(file_load)

            work_experience = resume_data.get("work_experience", [])

            # Procesar los logros y validarlos
            for job in work_experience:
                st.write(f"### Evaluando logros para: {job['job_title']} en {job['company']}")
                
                for achievement in job["achievement"]:
                    is_valid, feedback = validate_with_gemini(job['job_title'], achievement)

                    if is_valid:
                        st.session_state.achievements_pass.append(
                            {"job_title": job['job_title'], "achievement": achievement, "company":job['company'], "key":job['key'] }
                        )
                    else:
                        st.session_state.achievements_do_not_pass.append(
                            {"job_title": job['job_title'], "achievement": achievement, "feedback": feedback,  "company":job['company'], "key":job['key']}
                        )

            # Mostrar resultados
            st.write("## ✅ Logros Validados")
            st.write(st.session_state.achievements_pass)

            st.write("## ❌ Logros que necesitan mejora")
            for item in st.session_state.achievements_do_not_pass:
                st.write(f"- **{item['key']}**: {item['achievement']}")

            st.session_state.page = "improve_skills"
            if st.button("Improve skills"):
                st.write(st.session_state.page)
                st.rerun()
    #     import json
    #     # Load the resume data
    #     file_path = "resume/resume_delete_experience_not_relate.json"

    #     with open(file_path, "r", encoding="utf-8") as file_load:
    #         resume_data = json.load(file_load)

    #     work_experience = resume_data.get("work_experience", [])

    #     # Process achievements and validate them
    #     for job in work_experience:
    #         print(f"\nEvaluating achievements for: {job['job_title']} at {job['company']}\n")
    #         for i, achievement in enumerate(job["achievement"]):
    #             while True:
    #                 is_valid, feedback = validate_with_gemini(job['job_title'], achievement)
    #                 if is_valid:
    #                     print(f"✅ Valid achievement: {achievement}")
    #                     break
    #                 else:
    #                     print(f"\n❌ Needs improvement: {achievement}")
    #                     print(f"Suggested improvement: {feedback}")
    #                     achievement = input("Please rewrite the achievement with improvements: ")
                
    #             # Save the validated achievement
    #             job["achievement"][i] = achievement

    #     # Save the updated JSON file
    #     output_file = "resume/resume_updated.json"
    #     with open(output_file, "w", encoding="utf-8") as file:
    #         json.dump(resume_data, file, indent=4, ensure_ascii=False)

    #     ### add more skills
    #     input_filepath = f"resume/resume_missing_skills.json"
    #     with open(input_filepath, "r", encoding="utf-8") as file_load:
    #         missing_skills = json.load(file_load)

    #     # Process missing technical and soft skills
        
    #     # Extract company names from work experience
    #     companies = list({exp["key"] for exp in resume_data.get("work_experience", [])})

    #     # Dictionary to store user responses
    #     save_answers = {}
 
    #     """Prompts the user for missing skills, asks for the company, and validates responses with Gemini."""
    #     for skill_type, skills in missing_skills.items():  # Iterar sobre "technical_skills" y "soft_skills"
    #         for skill in skills:  # Iterar sobre las habilidades dentro de cada tipo
    #             answer = input(f"Do you have experience with {skill}? (yes/no): ").strip().lower()

    #             if answer == "yes":
    #                 # Mostrar lista numerada de empresas
    #                 print("\nSelect the company where you gained experience with this skill:")
    #                 for i, company in enumerate(companies, 1):
    #                     print(f"{i}. {company}")

    #                 while True:
    #                     try:
    #                         company_index = int(input("Enter the number corresponding to the company: ").strip())
    #                         if 1 <= company_index <= len(companies):
    #                             selected_company = companies[company_index - 1]
    #                             break
    #                         else:
    #                             print("Invalid selection. Please enter a valid number from the list.")
    #                     except ValueError:
    #                         print("Invalid input. Please enter a number.")

    #                 while True:
    #                     detail = input(f"Describe your experience with {skill}, including how you obtained it and a metric or result achieved: ")

    #                     is_valid, feedback = validate_with_gemini(skill, detail)

    #                     if is_valid:
    #                         if selected_company not in save_answers:
    #                             save_answers[selected_company] = {"technical_skills": {}, "soft_skills": {}}
    #                         save_answers[selected_company][skill_type][skill] = detail  # Usar skill_type para clasificar
    #                         print("Response accepted.")
    #                         break
    #                     else:
    #                         print("Your answer needs improvement.")
    #                         print(f"Example: {feedback}")
    #                         print("Please try again with more detail.")

        
    #     # Save user responses to a JSON file
    #     with open("resume/resume_user_answers.json", "w") as file:
    #         json.dump(save_answers, file, indent=4)

    #     # Join user_answer with resume_update
        
    #     input_filepath = "resume/resume_updated.json"
    #     with open(input_filepath, "r", encoding="utf-8") as file_load:
    #         resume_update = json.load(file_load)

    #     input_filepath = "resume/resume_user_answers.json"
    #     with open(input_filepath, "r", encoding="utf-8") as file_load:
    #         user_answers = json.load(file_load)
    #     # Verificar si `user_answers` está vacío
    #     if not user_answers:
    #         with open("resume/resume_final_experience.json", "w") as file:
    #             json.dump(resume_update, file, indent=4)
    #     else:

    #         # Iterar sobre las experiencias de trabajo en resume_update
    #         for experience in resume_update["work_experience"]:
    #             job_key = experience["key"]  # Obtener la clave de la experiencia laboral

    #             if job_key in user_answers:  # Verificar si hay información adicional en user_answers
    #                 new_achievements = []

    #                 # Agregar logros de habilidades técnicas
    #                 for skill, detail in user_answers[job_key].get("technical_skills", {}).items():
    #                     new_achievements.append(f"Technical Skill - {skill}: {detail}")

    #                 # Agregar logros de habilidades blandas
    #                 for skill, detail in user_answers[job_key].get("soft_skills", {}).items():
    #                     new_achievements.append(f"Soft Skill - {skill}: {detail}")

    #                 # Extender los logros existentes con los nuevos
    #                 experience["achievement"].extend(new_achievements)
            
    #         with open("resume/resume_final_experience.json", "w") as file:
    #             json.dump(resume_update, file, indent=4)

    #     # Ver resultado actualizado
    #     import json
    #     print(json.dumps(resume_update, indent=4))


    #     # 1. unir los json de las experiencias
    #     join_all_resume_json()
        
    #     # 2. completar la lista de skills
    #     generate_cv()
        
    #     #  skills_missing()

    #     st.write("Your resume for this application should be:")

    # if st.button("⬅️ Back to Home"):
    #     st.session_state.page = "Home"
    #     st.rerun()