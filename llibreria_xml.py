__author__ = 'Marc'

import xml.etree.ElementTree as ET

import os
#levels = ["CstmrDrctDbtInitn",
#                    ["GrpHdr","PmtInf"]]

#Fields PmtInf


EMPTY = "EMPTY"

#TO BE INVESTIGATED
# MsgId = 'SDDAINA20190816SOCI'
# CreatedTime = '2019-10-16T14:04:43'

# ID1 = 'DDAINA20190816'
ID2 = 'DD'
##NUMBER_TRANSFERS = '287'
##CTRL_SUM = '23456'
# COLLECTION_DATE = '2019-10-21'

Nm = 'AMPA CEIP AINA MOLL I MARQUES'
IBAN_AINAMOLL = 'ES4000610119610055340115'

BIC_AINAMOLL = 'BMARES2MXXX'

IdNumberOrdenante = 'ES35000G07083751'

IdNumberPresentador = 'ES1500047769657Z'

listToTest = [("Nen 1", "Pare 1", "IBAN 1", "Quantitat 1"),
              ("Nen 2", "Pare 2", "IBAN 2", "Quantitat 2")]


# Structure Cdtr
structureCdtr = [("Nm", Nm),
                 ("PstlAdr", [("Ctry", "ES"), ("AdrLine", "Placa Bisbe Berenguer de Palou, 6")])]

# Structure CdtrAcct
structureCdtrAcct = [("Id", [("IBAN", IBAN_AINAMOLL)])]

# Structure CdtrAgt
structureCdtrAgt = [("FinInstnId", [("BIC", BIC_AINAMOLL)])]

# Structure CdtrSchemeId
structureCdtrSchemeId = [("Id", [("PrvtId", [("Othr", [("Id", IdNumberOrdenante), ("SchmeNm", [("Prtry", "SEPA")])])])])]

# Estructure DrctDbtTxInf
structureDrctDbtTxInf = [
    ("PmtId", EMPTY, ("EndToEndId", ""))
    ]



def initialiseFields(numTxs, total, ID1, MsgId, COLLECTION_DATE, CreatedTime):

    fields_GrpHdr = [("MsgId", MsgId),
                 ("CreDtTm", CreatedTime),
                 ("NbOfTxs", str(numTxs)),
                 ("CtrlSum", str(total)),
                 ("InitgPty", [("Nm", Nm), ("Id", [("OrgId", [("Othr", [("Id", IdNumberPresentador)])])])])]


    fields_PmtInf = [("PmtInfId",ID1),
                 ("PmtMtd",ID2),
                 ("NbOfTxs",str(numTxs)),
                 ("CtrlSum",str(total)),
                 ("PmtTpInf",[("SvcLvl", [("Cd", "SEPA")]), ("LclInstrm", [("Cd", "CORE")]), ("SeqTp", "RCUR")]),
                 ("ReqdColltnDt",COLLECTION_DATE),
                 ("Cdtr", structureCdtr),
                 ("CdtrAcct",structureCdtrAcct),
                 ("CdtrAgt",structureCdtrAgt),
                 ("CdtrSchmeId",structureCdtrSchemeId)]

    return fields_GrpHdr, fields_PmtInf




def create_structure():

    string= 'Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'

    string = "Document"


    top = ET.Element(string)
    tree = ET.ElementTree(top)

    return top, tree


def add_subElement(title, text, node):

    item = ET.SubElement(node, title)
    item.text = text

    return item

def add_name_to_node(node, name, text):
    node.set(name, text)

# def process_list(node, input):
#
#     lastNode = node
#
#     for index, element in enumerate(input):
#         if type(element) is not list:
#             lastNode = add_subElement(title = element,
#                                       text = "hola",
#                                       node=lastNode)
#         else:
#             lastNode = process_list(node = lastNode,
#                          input = element)
#
#     return lastNode


def add_list_to_node(input_list, node):

    output_list = []

    parentNode = node

    for index, element in enumerate(input_list):
        # Element is a tuple
        if type(element[1]) is str:
            output_list.append(add_subElement(title=element[0],
                       text = element[1],
                       node = parentNode))
        else:
            lastNode = add_subElement(title=element[0],
                                              text="",
                                              node=parentNode)
            output_list.append(lastNode)
            sub_output_list = add_list_to_node(input_list = element[1],
                             node = lastNode)

            output_list.append(sub_output_list)
            #print("Substructure for {}".format(element[0]))


    return output_list

def crear_fitxer_XML(llista_de_remeses, name_file_XML, numTxs, total, ID1,
                        MsgId,
                        COLLECTION_DATE,
                        CreatedTime,
                        Concepte):

    top, tree = create_structure()

    fields_GrpHdr, fields_PmtInf = initialiseFields(numTxs, total, ID1, MsgId, COLLECTION_DATE, CreatedTime)

    lastNode = top

    #process_list(node = lastNode,
    #             input = levels)

    secondField = add_subElement(title = 'CstmrDrctDbtInitn',
                    text = "",
                    node = lastNode)

    GrpHdrField = add_subElement(title='GrpHdr',
                   text="",
                   node=secondField)

    outputNodes = add_list_to_node(input_list=fields_GrpHdr,
                                   node=GrpHdrField)

    PmtInfField = add_subElement(title='PmtInf',
                                 text="",
                                 node=secondField)

    outputNodes = add_list_to_node(input_list=fields_PmtInf,
                     node = PmtInfField)

    DrctDbtTxInfNode = outputNodes[len(outputNodes)-1]

    # Add transaction by transactions

    for element in llista_de_remeses:
        structureDrctDbtTxInf = [("PmtId", [("EndToEndId", element[0][0:34])]),
                                 ("InstdAmt", element[3]),
                                 ("DrctDbtTx", [("MndtRltdInf", [("MndtId", element[1][0:34]), ("DtOfSgntr", COLLECTION_DATE), ("AmdmntInd", "false"),
                                                                 ("AmdmntInfDtls",[("OrgnlCdtrSchmeId","")])])]),
                                 ("DbtrAgt", [("FinInstnId", "")]),
                                 ("Dbtr", [("Nm", element[1]), ("PstlAdr", [("Ctry", "ES")])]),
                                 ("DbtrAcct", [("Id", [("IBAN", element[2])])]),
                                 ("UltmtDbtr", ""),
                                 ("RmtInf", [("Ustrd", Concepte)])
                                           ]

        info_alumne = [("DrctDbtTxInf", structureDrctDbtTxInf)]

        output = add_list_to_node(input_list = info_alumne,
                                  node = PmtInfField)

        # add name to Currency
        add_name_to_node(node = output[1][2],
                         name = "Ccy",
                         text = "EUR")



    myfile = open("{}.xml".format(name_file_XML), "w")
    tree.write(myfile, encoding='unicode')

# def crear_fitxer_XML():
#     print("Començant a crear fitxer XML")
#
#
#
#     # create the file structure
#     data = ET.Element('data')
#     tree = ET.ElementTree(data)
#     items = ET.SubElement(data, 'items')
#     item1 = ET.SubElement(items, 'item')
#     item2 = ET.SubElement(items, 'item')
#     item1.set('name', 'item1')
#     item2.set('name', 'item2')
#     item1.text = 'item1abc'
#     item2.text = 'item2abc'
#
#     # create a new XML file with the results
#
#     myfile = open("items2.xml", "w")
#     tree.write(myfile, encoding='unicode')


def canviar_header_banca_march(file):

    print("Afegint Node Document amb el nou format")

    cambio_document = '<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'

    original_document = "<Document>"

    reemplazar_texto_en_fichero(ruta_fichero=file + ".xml",
                                texto_buscar=original_document,
                                texto_reemplazo=cambio_document)

    print("Node Document amb el nou format -- modificat correctament")


def reemplazar_texto_en_fichero(ruta_fichero, texto_buscar, texto_reemplazo):
    """
    Lee un fichero de texto, reemplaza todas las ocurrencias de 'texto_buscar'
    por 'texto_reemplazo', y guarda el resultado en un nuevo fichero de salida
    con el mismo nombre y formato, añadiendo '_modificado' al nombre.

    Parámetros:
        ruta_fichero (str): Ruta completa del fichero de entrada.
        texto_buscar (str): Texto que se desea buscar.
        texto_reemplazo (str): Texto que reemplazará al anterior.
    """

    # Verificar que el fichero existe
    if not os.path.isfile(ruta_fichero):
        print(f"❌ El fichero '{ruta_fichero}' no existe.")
        return

    # Leer el contenido original
    with open(ruta_fichero, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Reemplazar el texto
    contenido_modificado = contenido.replace(texto_buscar, texto_reemplazo)

    # Crear nombre del fichero de salida
    directorio, nombre_fichero = os.path.split(ruta_fichero)
    nombre, extension = os.path.splitext(nombre_fichero)
    ruta_salida = os.path.join(directorio, f"{nombre}_modificado{extension}")

    # Escribir el nuevo fichero
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write(contenido_modificado)

    print(f"✅ Fichero procesado con éxito. Nuevo fichero: {ruta_salida}")




if __name__ == '__main__':
    crear_fitxer_XML(llista_de_remeses = listToTest)