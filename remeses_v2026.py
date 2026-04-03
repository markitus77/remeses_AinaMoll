__author__ = 'Marc'

import pandas as pd
import numpy as np
from datetime import datetime
from llibreria_xml import crear_fitxer_XML, reemplazar_texto_en_fichero, canviar_header_banca_march

#Remeses Soci
ID1 = 'DDAINASOCI'
MsgId = 'SDDAINASOCI'


now = datetime.now()
CreatedTime = now.strftime("%Y-%m-%dT%H:%M:%S")
print("Created Time:", CreatedTime)

#PREU_SOCI = 30
#DESCOMPTE_FAM_NOMBROSA = 0.15


#Remeses Activitats
ID1_activitats = 'DDAINAACT'
MsgId_activitats = 'SDDAINAACT'






# 'New Age (A)', 'New Age (B)', les fa exitim,
# New adventures també
# Dibuix i comic també
# Ball i ball modern també

def read_file_CMS(fileName, list_columns, skiprows = 1):
    print("Començant a llegir fitxer...")

    print("Print inicial amb totes les dades...")
    df = pd.read_excel(fileName, skiprows=skiprows)
    print(df.head(5))

    print("Print inicial només de les columnes seleccionades...")

    df2 = df[list_columns]
    print(df2.head(5))

    return df2

def get_list_of_unique_activities(df):
    return df.Activitat.unique()

def get_list_of_unique_child(df):
    return df.Alumne.unique()

def get_final_cost_per_child(df, childName, activitats_no_gestio_AMPA):

    df_result = df.loc[(df['Alumne'] == childName) & (pd.isnull(df['Dia baixa']))]
    print('Activitats EVITADES en Cobrament')
    print(df_result['Activitat'].loc[df_result['Activitat'].isin(activitats_no_gestio_AMPA)])
    df_result = df_result.loc[~df_result['Activitat'].isin(activitats_no_gestio_AMPA)]
    return df_result['Import trimestral'].sum()

def get_activitats(df, childName):

    df_result = df.loc[(df['Alumne'] == childName) & (pd.isnull(df['Dia baixa']))]
    return df_result['Activitat'].to_list()

def netejar_ibans(input_data_frame, column_to_clean = 'Iban', column_id = 'Pare/Mare/Tutor'):

    # Data frame to clean = input_data_frame
    # Column to clean = 'Iban'

    input_data_frame = input_data_frame.reset_index(drop=True)

    for index, element in enumerate(input_data_frame[column_to_clean]):
        if type(element) is str:
            element = element.replace(" ", "")
            element = element.strip()
            if len(element) != 24:
                print(
                    "Wrong IBAN - IBAN lenght not correct: Pare/Mare {} amb IBAN {}".format(
                        input_data_frame[column_id][index],
                        element))

                input_data_frame['Iban'][index] = "IBAN not correct"

                #raise Exception(
                    #"Wrong IBAN - IBAN lenght not correct: Pare/Mare {} amb IBAN {}".format(input_data_frame[column_id][index],element))
            else:
                input_data_frame['Iban'][index] = element
        else:
            print(
                "Wrong IBAN - IBAN not string in Pare/Mare: {} amb IBAN {}".
                    format(input_data_frame[column_id][index], element))

            input_data_frame['Iban'][index] = "IBAN not correct"

    return input_data_frame

def split_fills_cursos_naixements(fills_cursos_naixements):

    fills = []
    cursos = []
    naixements = []


    if type(fills_cursos_naixements) is str:
        x = fills_cursos_naixements.split(", ")

        for index, element in enumerate(x):
            first = element.split(" (")
            fill = first[0]
            second = first[1].split(" | ")
            curs = second[0]
            tercer = second[1].split(")")
            data = tercer[0]

            fills.append(fill)
            cursos.append(curs)
            naixements.append(data)



    return fills, cursos, naixements

def crear_llista_remeses(df, concepteRemesa, type_remesa_soci_o_activitats = "soci",
                         preu_soci = 30):

    # listToTest = [("Nen 1", "Pare 1", "IBAN 1", "Quantitat 1"),
    #               ("Nen 2", "Pare 2", "IBAN 2", "Quantitat 2")]

    total_array = np.zeros((df['Pare/Mare/Tutor'].size, 1))
    flag_creat_array = np.zeros((df['Pare/Mare/Tutor'].size, 1))

    df['Total'] = total_array
    df['Flag creacio Remesa'] = flag_creat_array

    list_to_create = []
    total = 0
    countNo = 0
    countSi = 0
    for index, element in enumerate(df['Pare/Mare/Tutor']):

        if type_remesa_soci_o_activitats == 'soci':
            df['Total'][index] = preu_soci
        else:
            #if (df['Import trimestral'][index]*100) - round(df['Import trimestral'][index]*100,2)>0:
                #print('Problem occured {}'.format(df['Import trimestral'][index]))
            df['Total'][index] = round(df['Import trimestral'][index],2)

        titular = ""
        iban = ""
        fills = ""
        if type(df["Pare/Mare/Tutor"][index]) is str:
            titular = df["Pare/Mare/Tutor"][index]

        if type(df["Iban"][index]) is str:
            iban = df["Iban"][index]

        if type_remesa_soci_o_activitats == "soci":
            if type(df["Fills/Curs/Naixament"][index]) is str:
                fills_cursos_naixements = df["Fills/Curs/Naixament"][index]

                fills, cursos, naixements = split_fills_cursos_naixements(fills_cursos_naixements)
        else:
            if type(df["Alumne"][index]) is str:
                alumne = df["Alumne"][index]
                concepteRemesa = alumne


        # Eliminant aquí la condició de que per ser soci has de tenir fills:
        # La única condició per cobrar la quota de soci és tenir un IBAN vàlid i un nom de titular
        # Si la remesa es de 0 euros - no la creem
        if titular != "" and iban != "" and iban != "IBAN not correct" and df['Total'][index] != 0:
            countSi = countSi + 1

            # Crear llista
            print("Creant {} {} {} {}".format(concepteRemesa, titular, iban, df["Total"][index]))
            list_to_create.append((concepteRemesa, titular, iban,
                                   str(df["Total"][index])))
            total = round(total + round(df["Total"][index],2),2)
            df["Flag creacio Remesa"][index] = "Si"

        else:
            countNo = countNo + 1
            df["Flag creacio Remesa"][index] = "No"

        print('index = {}, total parcial = {}'.format(index,total))


    NumTxs = countSi

    #print('Total = {}'.format(total))

    return list_to_create, NumTxs, total, countNo







def crear_remesa_activitats(directory, filePath, concepteRemesa_activitats, collection_date, activitats_no_gestio_AMPA,
                            preu_matricula = 30,
                            descompte_fam_nombrosa = 0.15):

    directoriFileActivitats = directory
    fileNameActivitats = filePath


    list_columns_activitats = ['Dia alta', 'Dia baixa', 'Alumne Nom', 'Alumne Cognom', 'Curs', 'Activitat','Horari', 'Pare/Mare/Tutor', 'Dni', 'Soci', 'Banc', 'Iban', 'Email', 'Telèfon',
                               'Fam. nombrosa', 'Import trimestral' ]

    # list_columns_activitats = ['Dia alta', 'Dia baixa', 'Alumne', 'Curs', 'Activitat', 'Horari',
    #                            'Pare/Mare/Tutor', 'Dni', 'Soci', 'Banc', 'Iban', 'Email', 'Telèfon',
    #                            'Fam. nombrosa', 'Import trimestral']

    dfActivitats = read_file_CMS(fileName=directoriFileActivitats+fileNameActivitats,
                                 list_columns=list_columns_activitats)


    ############# CANVIS fets remesa 3r trimestre 2022

    # remove Linies Amb Nom NULL
    dfActivitats = dfActivitats.loc[~dfActivitats['Alumne Nom'].isnull()]

    #Ajuntar Alumne Nom amb Alumne Cognom
    dfActivitats['Alumne'] = dfActivitats['Alumne Nom'].astype(str) + " " +  dfActivitats['Alumne Cognom'].astype(str)

    ############# CANVIS fets remesa 3r trimestre 2022


    columns_activitats_single_child = ['Alumne', 'Activitat',
                                                     'Pare/Mare/Tutor', 'Dni',
                                                     'Soci', 'Banc', 'Iban',
                                                     'Email', 'Telèfon',
                               'Import trimestral']
    dfActivitats_singleChild = pd.DataFrame(columns=columns_activitats_single_child)

    print('Netejar ibans...')
    dfActivitats = netejar_ibans(dfActivitats)

    dfActivitats = dfActivitats.reset_index(drop=True)

    print(dfActivitats.head(5))

    # remove Eliminats
    dfActivitats = dfActivitats.loc[dfActivitats['Alumne'] != 'Eliminat'].reset_index(drop=True)

    # remove Baixes
    dfActivitats = dfActivitats.loc[dfActivitats['Dia baixa'].isnull()]



    print("Llista d'Alumnes unics")
    list_childs = get_list_of_unique_child(dfActivitats)
    print(list_childs)

    print("Llista Activitats úniques")
    list_activities = get_list_of_unique_activities(dfActivitats)
    print(list_activities)

    for name in list_childs:
        cost_child = get_final_cost_per_child(df = dfActivitats, childName=name, activitats_no_gestio_AMPA=activitats_no_gestio_AMPA)
        print("{}, {}€".format(name, cost_child))
        activitats = get_activitats(dfActivitats, childName = name)
        num_activitats = len(activitats)

        if (dfActivitats.loc[dfActivitats['Alumne']==name]['Soci']).values[0] == "No soci":
            if concepteRemesa_activitats == "Quota Activitats 1T":
                matricula = preu_matricula
            else:
                matricula = 0
        else:
            matricula = 0

        if (dfActivitats.loc[dfActivitats['Alumne'] == name]['Fam. nombrosa']).values[0] == "Si":
            descompte = descompte_fam_nombrosa
        else:
            descompte = 0

        # Es cobra només 1 matricula per aquell fill que NO sigui soci, pero no una matricular per activitat
        #cost_child = cost_child*(1-descompte) + matricula*num_activitats
        cost_child = cost_child * (1 - descompte) + matricula

        cost_child = round(cost_child, 2)

        values_to_append = [name, ",".join(activitats)]
        values_to_append.extend(dfActivitats.loc[dfActivitats['Alumne'] == name][['Pare/Mare/Tutor', 'Dni', 'Soci', 'Banc', 'Iban', 'Email', 'Telèfon']].values[0].tolist())
        values_to_append.extend([cost_child])
        df_to_append = pd.DataFrame([values_to_append],
                                    columns=columns_activitats_single_child)


        #dfActivitats_singleChild = dfActivitats_singleChild.append(df_to_append, ignore_index=True)
        dfActivitats_singleChild = pd.concat([dfActivitats_singleChild, df_to_append],
                                             ignore_index=True)

    list_to_create, NumTxs, total, countNo = crear_llista_remeses(dfActivitats_singleChild,
                                                                  concepteRemesa= "",
                                                                  type_remesa_soci_o_activitats='activitats')

    print("Remeses creades: {}, total = {}, Remeses NO creades: {}".format(NumTxs, total, countNo))

    # print to excel
    nom_fitxer_verificacio = directoriFileActivitats + "output_verificacio_{}".format(fileNameActivitats)
    dfActivitats_singleChild.to_excel(nom_fitxer_verificacio)

    # crearRemesa
    name_file_XML = directoriFileActivitats + "remesaXML_{}".format(fileNameActivitats)

    crear_fitxer_XML(llista_de_remeses=list_to_create,
                     name_file_XML=name_file_XML,
                     numTxs=NumTxs,
                     total=total,
                     ID1="{}".format(ID1_activitats),
                     MsgId="{}".format(MsgId_activitats),
                     COLLECTION_DATE=collection_date,
                     CreatedTime=CreatedTime,
                     Concepte=concepteRemesa_activitats)

    print("Remesa creada amb: Entrades: {}, TOTAL: {} €".format(NumTxs, total))

    canviar_header_banca_march(file=name_file_XML)

    return name_file_XML + '_modificado.xml', nom_fitxer_verificacio


def crear_remesa_socis(directory, filePath, concepteRemesaSoci, collection_date, preu_soci = 30):

    #directoriFileSocis = 'Remeses2025-2026/RemesaSocis/'
    #fileNameSocis = 'LlistaSocis-04Oct2025_v2.xlsx'

    directoriFileSocis = directory
    fileNameSocis = filePath

    list_columns_socis = ['Alta',	'Baixa', 'Pare/Mare/Tutor', 'Dni',	'Banc', 'Iban', 'Email',	'Telèfon',
                          'Cònjuge',	'Email cònjuge',	'Telèfon cònjuge',	'DNI cònjuge',
                          'Fills/Curs/Naixament'	]


    dfSocis = read_file_CMS(fileName=directoriFileSocis+fileNameSocis,
                                  list_columns = list_columns_socis)

    dfSocisActius = dfSocis.loc[dfSocis['Baixa'] == 'Actiu']

    print('Netejar ibans...')
    dfSocisActius = netejar_ibans(dfSocisActius)

    dfSocisActius = dfSocisActius.reset_index(drop=True)

    print(dfSocisActius.head(5))

    list_to_create, NumTxs, total, countNo = crear_llista_remeses(dfSocisActius,
                                                                        concepteRemesa=concepteRemesaSoci,
                                                                  type_remesa_soci_o_activitats='soci',
                                                                  preu_soci=preu_soci)

    print("Remeses creades: {}, total = {}, Remeses NO creades: {}".format(NumTxs, total, countNo))

    # print to excel
    nom_fitxer_verificacio = directoriFileSocis + "output_verificacio_{}".format(fileNameSocis)
    dfSocisActius.to_excel(nom_fitxer_verificacio)

    # crearRemesa
    name_file_XML = directoriFileSocis + "remesaXML_{}".format(fileNameSocis)
    crear_fitxer_XML(llista_de_remeses=list_to_create,
                     name_file_XML=name_file_XML,
                     numTxs=NumTxs,
                     total=total,
                     ID1="{}".format(ID1),
                     MsgId="{}".format(MsgId),
                     COLLECTION_DATE=collection_date,
                     CreatedTime=CreatedTime,
                     Concepte=concepteRemesaSoci)

    print("Remesa creada amb: Entrades: {}, TOTAL: {} €".format(NumTxs, total))

    canviar_header_banca_march(file=name_file_XML)

    return name_file_XML + '_modificado.xml', nom_fitxer_verificacio




def run_crear_remeses(tipus_remesa, dia_cobrament, concepteRemesa, directoriFile, fileName, activitats_no_gestio_AMPA=None,
                      preu_matricula=30, descompte_fam_nombrosa = 0.15):

    if tipus_remesa == "remesa_activitats":

        [name_file_XML, nom_fitxer_verificacio] = crear_remesa_activitats(directory=directoriFile,
                                                filePath=fileName,
                                                concepteRemesa_activitats=concepteRemesa,
                                                collection_date=dia_cobrament,
                                                activitats_no_gestio_AMPA=activitats_no_gestio_AMPA,
                                                preu_matricula=preu_matricula,
                                                descompte_fam_nombrosa=descompte_fam_nombrosa)
    elif tipus_remesa == "remesa_socis":

        [name_file_XML, nom_fitxer_verificacio] = crear_remesa_socis(directory=directoriFile,
                                           filePath=fileName,
                                           concepteRemesaSoci=concepteRemesa,
                                           collection_date=dia_cobrament,
                                           preu_soci=preu_matricula)

    return name_file_XML, nom_fitxer_verificacio

if __name__ == '__main__':

    tipus_remesa = "remesa_activitats"
    directoriFile = 'Remeses2025-2026/Remesa3T/'
    fileName = 'LlistaActivitats-02Abril-2026.xlsx'
    dia_cobrament = '2026-04-15'
    concepteRemesa = "Quota Activitats 3T"



    #tipus_remesa = "remesa_socis"
    # directoriFile = 'Remeses2025-2026/RemesaSocis/'
    # fileName = 'LlistaSocis-04Oct2025_v2.xlsx'
    # dia_cobrament = '2025-10-09'
    # concepteRemesa = "Quota Soci AFA"

    # ACTIVITATS_NO_GESTIO_AMPA = ['Anglès I (A)', 'Anglès I (B)', 'Anglès I (C)', 'Anglès I (D)',
    #                             'Anglès II (A)', 'Anglès II (B)', 'Anglès II (C)', 'Anglès II (D)',
    #                             'Anglès III (A)', 'Anglès III (B)', 'Anglès III (C)', 'Anglès III (D)',
    #                              'Càlcul Aloha (A)', 'Càlcul Aloha  (A)', 'Càlcul Aloha (B)',
    #                              'Lego Robotix I', 'Lego Robotix II', 'Lego Robotix III',
    #                              'Natació (A)', 'Natació (B) - comença 11.45h',
    #                              'Arts &amp; Crafts', 'Arts &amp; Crafts + Kitsune', 'Kitsune',
    #                              'Brain games', 'Brain games + Ciència divertida', 'Ciència divertida',
    #                              'Cook&amp;Kids', 'Cook&amp;Kids + Ciència divertida', 'Ciència divertida',
    #                              'Pre-Aloha',
    #                              'Arts &amp; Crafts', 'Arts &amp; Crafts + Pre-Aloha',
    #                              'Robòtica I', 'Robòtica II', 'Robòtica III',]

    # run_crear_remeses(tipus_remesa=tipus_remesa,
    #                   dia_cobrament=dia_cobrament,
    #                   concepteRemesa=concepteRemesa,
    #                   directoriFile=directoriFile,
    #                   fileName=fileName,
    #                   activitats_no_gestio_AMPA = ACTIVITATS_NO_GESTIO_AMPA)


    #-----------------------------------------
    # Test valors d'activitats a no cobrar
    # list_columns_activitats = ['Dia alta', 'Dia baixa', 'Alumne Nom', 'Alumne Cognom', 'Curs', 'Activitat', 'Horari',
    #                            'Pare/Mare/Tutor', 'Dni', 'Soci', 'Banc', 'Iban', 'Email', 'Telèfon',
    #                            'Fam. nombrosa', 'Import trimestral']
    #
    # # list_columns_activitats = ['Dia alta', 'Dia baixa', 'Alumne', 'Curs', 'Activitat', 'Horari',
    # #                            'Pare/Mare/Tutor', 'Dni', 'Soci', 'Banc', 'Iban', 'Email', 'Telèfon',
    # #                            'Fam. nombrosa', 'Import trimestral']
    #
    # dfActivitats = read_file_CMS(fileName=directoriFile + fileName,
    #                              list_columns=list_columns_activitats)
    #
    # activitats_uniques = get_list_of_unique_activities(dfActivitats)
    # pre_selected_activitats = ACTIVITATS_NO_GESTIO_AMPA
    #
    # print("activitats uniques")
    # print(activitats_uniques)
    # print("pre_selected_activitats")
    # print(pre_selected_activitats)
    #
    #
    # totes = pre_selected_activitats + activitats_uniques.tolist()
    # print("full_options")
    # print(pre_selected_activitats)
    #
    # unique_totes = np.unique(totes).tolist()
    # print(unique_totes)

