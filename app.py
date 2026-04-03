import streamlit as st
import numpy as np
import openpyxl
import tempfile
import os
import shutil
import datetime
from pathlib import Path
from remeses_v2026 import run_crear_remeses, read_file_CMS, get_list_of_unique_activities

PRE_SELECTED_ACTIVITIES_NO_GESTIO_AMPA = ['Anglès I (A)', 'Anglès I (B)', 'Anglès I (C)', 'Anglès I (D)',
                            'Anglès II (A)', 'Anglès II (B)', 'Anglès II (C)', 'Anglès II (D)',
                            'Anglès III (A)', 'Anglès III (B)', 'Anglès III (C)', 'Anglès III (D)',
                             'Càlcul Aloha (A)', 'Càlcul Aloha  (A)', 'Càlcul Aloha (B)',
                             'Lego Robotix I', 'Lego Robotix II', 'Lego Robotix III',
                             'Natació (A)', 'Natació (B) - comença 11.45h',
                             'Arts &amp; Crafts', 'Arts &amp; Crafts + Kitsune', 'Kitsune',
                             'Brain games', 'Brain games + Ciència divertida', 'Ciència divertida',
                             'Cook&amp;Kids', 'Cook&amp;Kids + Ciència divertida', 'Ciència divertida',
                             'Pre-Aloha',
                             'Arts &amp; Crafts', 'Arts &amp; Crafts + Pre-Aloha',
                             'Robòtica I', 'Robòtica II', 'Robòtica III',]

# ─────────────────────────────────────────────
#  PUT YOUR TRANSFORMATION LOGIC HERE
# ─────────────────────────────────────────────


# ─── UI ───────────────────────────────────────
#st.markdown("// Eina per crear remeses de sòcies o de quota d'extraescolars (CEIP Aina Moll i Marquès", unsafe_allow_html=False)
st.title("Creador de remeses")
st.markdown("Puja el fitxer d'activitats o de socis, tria la data de cobrament, seleciona el tipus de remesa i baixa't el fitxer resultant")
#st.divider()

concept = st.selectbox(
    label="Elegiu el concepte",
    options=["Quota Activitats 1T", "Quota Activitats 2T", "Quota Activitats 3T", "Quota Socis"],
    help="This concept will be passed to the transformation function",
)
if concept != "Quota Socis":
    uploaded_file = st.file_uploader(
        "Puja el fitxer d'activitats del Panell (.xlsx)",
        type=["xlsx", "xls"],
        help="Drag and drop or click to browse",
    )




else:
    uploaded_file = st.file_uploader(
        "Puja el fitxer de Socies del Panell (.xlsx)",
        type=["xlsx", "xls"],
        help="Drag and drop or click to browse",
    )

    quota_soci = st.number_input(label="Quota de sòcia en Euros", min_value=0, max_value=10000,
                                 value=30)
    descompte_fam_nombrosa = st.number_input(label="Descompte família nombrosa (%)", min_value=0, max_value=100,
                                             value=15)
    descompte_fam_nombrosa = descompte_fam_nombrosa/100




avui = datetime.date.today()
delta = datetime.timedelta(days= 3)
data_cobrament = st.date_input('Data de cobrament', value = avui + delta)
selected_activities = None



if (uploaded_file is not None) and concept != "Quota Socis":
    try:
        list_columns_activitats = ['Dia alta', 'Dia baixa', 'Alumne Nom', 'Alumne Cognom', 'Curs', 'Activitat', 'Horari',
                                   'Pare/Mare/Tutor', 'Dni', 'Soci', 'Banc', 'Iban', 'Email', 'Telèfon',
                                   'Fam. nombrosa', 'Import trimestral']

        # list_columns_activitats = ['Dia alta', 'Dia baixa', 'Alumne', 'Curs', 'Activitat', 'Horari',
        #                            'Pare/Mare/Tutor', 'Dni', 'Soci', 'Banc', 'Iban', 'Email', 'Telèfon',
        #                            'Fam. nombrosa', 'Import trimestral']
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
            shutil.copyfileobj(uploaded_file, tmp_in)
            input_path = tmp_in.name

        dfActivitats = read_file_CMS(fileName=os.path.split(input_path)[0] + "/" + os.path.split(input_path)[1],
                                     list_columns=list_columns_activitats)

        activitats_uniques = get_list_of_unique_activities(dfActivitats)
        totes = PRE_SELECTED_ACTIVITIES_NO_GESTIO_AMPA + activitats_uniques.tolist()
        unique_totes = np.unique(totes).tolist()
        selected_activities = st.multiselect(label="Selecciona les activitats que no cobra l'AFA i doncs no han d'aparéixer a la remesa",
                                             options=unique_totes,
                                             default=PRE_SELECTED_ACTIVITIES_NO_GESTIO_AMPA)
    except Exception as e:
        st.markdown(
            f'<div class="error-box">✗ Error: {str(e)}</div>',
            unsafe_allow_html=True,
        )
#st.divider()

if st.button("Crear remesa...",):
    with st.spinner("Processing your file…"):
        try:
            # Save upload to temp file
            uploaded_file.seek(0)
            print(uploaded_file.name)
            suffix = Path(uploaded_file.name).suffix
            print("here")
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
                shutil.copyfileobj(uploaded_file, tmp_in)
                input_path = tmp_in.name

            output_path = input_path.replace(suffix, f"_output{suffix}")

            if concept == "Quota Activitats 1T" or concept == "Quota Activitats 2T" or concept == "Quota Activitats 3T":
                tipus_remesa = "remesa_activitats"
            elif concept == "Quota Socis":
                tipus_remesa = "remesa_socis"

            dia_cobrament = data_cobrament.strftime("%Y-%m-%d")
            print(dia_cobrament)
            print(tipus_remesa)
            print(concept)
            print(input_path)


            [output_path_xml, output_path_excel] = run_crear_remeses(tipus_remesa=tipus_remesa,
                              dia_cobrament=dia_cobrament,
                              concepteRemesa=concept,
                              directoriFile=os.path.split(input_path)[0] + "/",
                              fileName=os.path.split(input_path)[1],
                              activitats_no_gestio_AMPA=selected_activities)



            # Read output into memory so we can clean up temp files
            with open(output_path_xml, "rb") as f:
                output_bytes_xml = f.read()

            # Read output into memory so we can clean up temp files
            with open(output_path_excel, "rb") as f:
                output_bytes_excel = f.read()

            os.unlink(input_path)
            os.unlink(output_path_xml)
            os.unlink(output_path_excel)

            output_filename_xml = f"remesa_{uploaded_file.name}.xml"
            output_filename_excel = f"output_verificacio_{uploaded_file.name}.xlsx"

            st.markdown(
                '<div class="status-box">✓ Remesa calculada. Pots baixar els fitxers...</div>',
                unsafe_allow_html=True,
            )

            st.download_button(
                label="⬇ Baixar el fitxer de remesa",
                data=output_bytes_xml,
                file_name=output_filename_xml,
                on_click="ignore",
                #mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            st.download_button(
                label="⬇ Baixar el fitxer de verificació en excel",
                data=output_bytes_excel,
                file_name=output_filename_excel,
                on_click="ignore",
                # mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.markdown(
                f'<div class="error-box">✗ Error: {str(e)}</div>',
                unsafe_allow_html=True,
            )
