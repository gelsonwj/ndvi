import os
import pymysql
import pandas as pd
from dotenv import load_dotenv

def conecta_bd():
    load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
    host = os.getenv('DATABASE_HOST')
    user = os.getenv('DATABASE_USER')

    conexao = pymysql.connect(
        host=host,
        port=3306,
        database='gelson',
        user=user,
        autocommit=True
    )

    poligonos = pd.read_sql('SELECT * FROM poligonos', con=conexao)
    conexao.close()
    return poligonos

#poligonos = conecta_bd()
#print(poligonos['roi_coords'])