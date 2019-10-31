#Importamos librerias necesarias
import pandas as pd
import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def f_bf_confirmacion(df_datos, paridad):
    
    """
    param df_datos: Dataframe que contiene toda la informacion sobre la que trabajaremos
    param paridad: La que el usuario escoja
    
    :return: Resultado con dos diccionarios que contienen el comportamiento del trader, gráfica, explicación y escala
    """
    
    #Convertir formatos de columnas a flotantes
    df_datos[['profit','size']] = df_datos[['profit','size']].astype(float) 

    lista1 =[]
    lista2 =[]
    h=list(df_datos.loc[:,'instrument'].unique()) #Aqui tomamos los elementos unicos de la columna de instrumentos - list
    h2=df_datos.loc[:,'instrument'].unique() #Lo mismo de arriba pero sin convertirla en lista
    
    #Creamos DataFrame
    x=[]
    for i in range(len(h)): # Ciclo for que recorra toda la lista h
        a=df_datos.where(df_datos.instrument == h[i]).dropna()[['instrument','size','profit']] # Quitamos los NA
        
        # Rezagamos la columna "profit" y "size"
        a['sizet1']=a[['size']].shift(1)
        a['profit']=a[['profit']].shift(1)

        # Determinamos condicion con base a "profit" para saber si gano o perdio   
        condiciones = [a.profit<0,a.profit>0]
        elecciones =['perdió','ganó']
        # Este comando regresa un arreglo de elementos de la lista de eleccion, dependiendo de las condiciones
        b=np.select(condiciones,elecciones)
        a['gano_perdio']=b
    
        # Ciclo para determinar la variacion en "size"
        c=[]
        for i in range(len(a[['size']])):
            if a.iloc[i,1] > a.iloc[i,3]:
                d = 'aumentó'
            elif a.iloc[i,1] < a.iloc[i,3]:
                d = 'disminuyó'
            elif a.iloc[i,1] == a.iloc[i,3]:
                d = 'mantuvo'
            else:
                d = 'na'
            c.append(d)

        a['com_size']=c


        # Juntamos las condiciones de "profit" y "size" para saber el comportamiento del trader 
        condiciones = [(a.gano_perdio=='ganó') & (a.com_size=='mantuvo'),(a.gano_perdio=='ganó') & (a.com_size=='aumentó'),
                      (a.gano_perdio=='ganó') & (a.com_size=='disminuyó'),(a.gano_perdio=='perdió') & (a.com_size=='aumentó'),
                      (a.gano_perdio=='perdió') & (a.com_size=='mantuvo'),(a.gano_perdio=='perdió') & (a.com_size=='disminuyó')]
        elecciones =['Razonable','Razonable','Sesgado','Sesgado','Sesgado','Razonable']

        b=np.select(condiciones,elecciones)

        a['Comportamiento']=b
        a=a.iloc[1:]    

        # Ordenamos la info en dos tablas
        tabla1 = a.pivot_table(index='gano_perdio', columns=['instrument','com_size'], aggfunc={'com_size':len})
        tabla2 = a.pivot_table(index='instrument',columns=['Comportamiento'], aggfunc={'Comportamiento':len})

        # Las mostramos como listas
        lista1.append(tabla1)
        lista2.append(tabla2)
        
        # Las convertimos en diccionarios
    final1 = {h[i]: lista1[i] for i in range(0, len(lista1))}
    final2 = {h[i]: lista2[i] for i in range(0, len(lista2))}
    
    
    #AQUI EMPIEZA LO DE LA GRAFICA
    labels = ['aumento','disminuyo','mantuvo']

        #Aqui creamos subplots
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
        #Para cuando gano 
    fig.add_trace(go.Pie(labels=labels, values=[final1[paridad].iloc[0,0], final1[paridad].iloc[0,1],
                                                    final1[paridad].iloc[0,2]], name='Cuando Gana'),1, 1)
        #Para cuando perdio
    fig.add_trace(go.Pie(labels=labels, values=[final1[paridad].iloc[1,0], final1[paridad].iloc[1,1],
                                                    final1[paridad].iloc[1,2]], name="Cuando pierde"),1, 2)

    # Usamos "hole" para hacer la forma de una dona
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(
    title_text="Comportamiento del size después de haber ganado o perdido ",
        
        #Agregamos anotaciones
    annotations=[dict(text='Cuando ganó', x=0.13, y=0.5, font_size=20, showarrow=False),
                     dict(text='Cuando perdió', x=0.88, y=0.5, font_size=20, showarrow=False)])
    
    
    
    salida = {'datos': {'df_1':final1[paridad], 'df_2':final2[paridad]},
              'grafica': fig,
              'explicacion':'SESGO DE CONFIRMACIÓN: Implica la tendencia a buscar y considerar de forma más intensa y selectiva ' +
              'aquella información que confirme lo que ya pensamos al momento de selección y retención de activos.',
              'escala': {'texto': 'El porcentaje de sesgo del trader en la paridad seleccionada fue:',
              'valor':(pd.DataFrame.from_dict(final2[paridad]).iloc[0,1]/(pd.DataFrame.from_dict(final2[paridad]).iloc[0,1] + 
                                                                          pd.DataFrame.from_dict(final2[paridad]).iloc[0,0])*100)}}

    return salida