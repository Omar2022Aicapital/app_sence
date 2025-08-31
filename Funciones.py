#Para mayor estructura, esta función procesara el excel descargado de "DEDICACION AL CURSO"
import os
import pandas as pd
import re
def normalizar_nombre(nombre):
    #Eliminar espacios adicionales al inicio y al final, era lo que pasaba con sasha
    nombre = nombre.strip()
    #Reemplazar espacios internos por un solo espacio
    nombre = re.sub(r'\s+', ' ', nombre)
    return nombre

def dedicacion(excel):
    #df =pd.read_excel(excel)
    df=excel
    '''df.columns = df.iloc[0]
    df=df.drop(index=0)
    informacion_primera_fila= pd.read_excel(excel, nrows=1, header=None)
    inf_inicio= informacion_primera_fila.iloc[0,1]'''
    #Unir nombre y apellido
    df['Nombre Completo'] = df['Nombre'] + ' ' + df['Apellido(s)']
    #df['Horas'] = df['Dedicación al curso'].str.extract('(\d+) horas').astype(float)
    columnas=['Nombre Completo','Dedicación al curso']
    df_final_dedicacion=df[columnas]
    #df_final_dedicacion.to_excel("Excel-dedicacion.xlsx")
    return df_final_dedicacion

def unir_porcentajeYhoras(excel_porcentaje,df_dedi):
    #Nombre estudiante
    df_porcentaje=pd.read_excel(excel_porcentaje)
    #Nombre Completo
    df_dedicacion= df_dedi
    print(df_dedicacion)
    df_dedicacion['Nombre Completo'] = df_dedicacion['Nombre Completo']
    df_porcentaje['Nombre estudiante'] = df_porcentaje['Nombre estudiante'].astype(str)
    df_dedicacion['Nombre Normalizado'] = df_dedicacion['Nombre Completo']
    df_porcentaje['Nombre Normalizado'] = df_porcentaje['Nombre estudiante'].apply(normalizar_nombre)
    #Unir los DataFrames en base a los nombres normalizados
    #casefold: comparación de cadenas sin considerar las diferencias de mayúsculas y minúsculas
    df_merged = df_porcentaje.merge(df_dedicacion, left_on='Nombre Normalizado', 
                                right_on='Nombre Normalizado', how="inner")
    columnas_interesan=['Nombre Completo', 'Dedicación al curso','Porcentaje Progreso']
    df_final_p_h=df_merged[columnas_interesan]
    #df_merged.to_excel("union.xlsx")
    #df_final.to_excel("Union-porcentaje-dedicacion.xlsx")
    return df_final_p_h

def procesamiento_notas(df_notas):
    # Verifica si el DataFrame está vacío
    if df_notas.empty:
        print("El DataFrame está vacío.")
        return None
    columnas_interesan = ['Nombre / Apellido(s)','Prueba Modulo 1','Prueba Modulo 2','Prueba Modulo 3','Prueba Modulo 4','Prueba Modulo 5','Evaluación Final']
    df_final=df_notas[columnas_interesan]
    print(df_final)
    return df_final

def unir_notas(excel, excel_notas):
    #df_p_d=pd.read_excel(excel)
    df_p_d=excel
    #df_notas=pd.read_excel(excel_notas)
    df_notas = excel_notas
    df_p_d['Nombre Normalizado'] = df_p_d['Nombre Completo'].astype(str).apply(normalizar_nombre)
    df_notas['Nombre Normalizado'] = df_notas['Nombre / Apellido(s)'].astype(str).apply(normalizar_nombre)
    #Unir los DataFrames en base a los nombres normalizados
    #merge: es como un joins 
    df_merged = df_p_d.merge(df_notas, left_on='Nombre Normalizado', 
                                right_on='Nombre Normalizado', how="inner")
    columnas_finales=['Nombre Normalizado','Dedicación al curso','Porcentaje Progreso','Prueba Modulo 1','Prueba Modulo 2','Prueba Modulo 3','Prueba Modulo 4','Prueba Modulo 5','Evaluación Final']
    df_final = df_merged[columnas_finales]
    return df_final

def resultado(df_resultado, nombre_resultado):
    df=pd.DataFrame(df_resultado)
    df.to_excel(nombre_resultado)

# Función para extraer horas y verificar si son menores a 65
def color_horas(row):
    horas = int(row['Dedicación al curso'].split()[0])  # Extrae el número de horas
    if horas < 65:
        return ['background-color: red'] * len(row)
    return [''] * len(row) 

def colorear(df_anterior):
    #df=pd.read_excel("DMIPE-24-01-01-0158-1 INFORME.xlsx")
    # Aplicar el estilo
    styled_df = df_anterior.style.apply(color_horas,subset=['Dedicación al curso'], axis=1)
    # Mostrar el DataFrame estilizado
    return styled_df
def borrar_excel(excel):
    # Verificar si el archivo existe antes de intentar eliminarlo
    if os.path.exists(excel):
        os.remove(excel)  # Eliminar el archivo
        print(f"El archivo {excel} ha sido eliminado.")
    else:
        print(f"El archivo {excel} no existe.")



