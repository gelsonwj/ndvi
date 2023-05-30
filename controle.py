import pymysql
import pandas as pd

def conecta_bd():
    conexao = pymysql.connect(
        host='localhost',
        port=3306,
        database='gelson',
        user='root',
        autocommit=True
    )
    poligonos = pd.read_sql('SELECT * FROM poligonos', con=conexao)
    conexao.close()
    return poligonos

#poligonos = conecta_bd()
#print(poligonos['roi_coords'])