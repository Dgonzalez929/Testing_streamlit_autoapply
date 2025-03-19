import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from io import BytesIO
import numpy as np
import re
from utils import join_all_resume_json, generate_cv
import os



var_back_to_job_seleccion = "⬅️ Back to Job Selection"

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Customization CV - Download CV</h1>", unsafe_allow_html=True)
   
    # Cargar `resume_updated.json`
    input_filepath = "resume/resume_updated.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
        resume_update = json.load(file_load)

    # Intentar cargar `resume_user_answers.json`, si no existe, usar un diccionario vacío
    input_filepath = "resume/resume_user_answers.json"
    if os.path.exists(input_filepath):
        with open(input_filepath, "r", encoding="utf-8") as file_load:
            user_answers = json.load(file_load)
    else:
        user_answers = {}  # Si el archivo no existe, asignar un diccionario vacío

    # Si `user_answers` está vacío, guardar `resume_update`
    if not user_answers:
        output_filepath = "resume/resume_final_experience.json"
        with open(output_filepath, "w", encoding="utf-8") as file:
            json.dump(resume_update, file, indent=4)

    else:

        # Iterar sobre las experiencias de trabajo en resume_update
        for experience in resume_update["work_experience"]:
            job_key = experience["key"]  # Obtener la clave de la experiencia laboral

            if job_key in user_answers:  # Verificar si hay información adicional en user_answers
                new_achievements = []

                # Agregar logros de habilidades técnicas
                for skill, detail in user_answers[job_key].get("technical_skills", {}).items():
                    new_achievements.append(f"Technical Skill - {skill}: {detail}")

                # Agregar logros de habilidades blandas
                for skill, detail in user_answers[job_key].get("soft_skills", {}).items():
                    new_achievements.append(f"Soft Skill - {skill}: {detail}")

                # Extender los logros existentes con los nuevos
                experience["achievement"].extend(new_achievements)
        
        with open("resume/resume_final_experience.json", "w") as file:
            json.dump(resume_update, file, indent=4)

    join_all_resume_json()
    generate_cv()

    # Ruta del archivo
    json_file_path = f"resume/resume_final_to_word.json"
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    user_name = data.get('personal_information', {}).get('name', 'Unknown').strip()
    user_name = " ".join(user_name.title().split())
    output_path = f"output/{user_name}_customization.docx" 

    # Leer el archivo en modo binario
    with open(output_path, "rb") as file:
        file_bytes = file.read()

    # Botón de descarga
    st.download_button(
        label="📥 Descargar CV personalizado",
        data=file_bytes,
        file_name="customization_cv.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    # descargar el word
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        if "app_initialized" in st.session_state:
            del st.session_state.app_initialized
        st.rerun()