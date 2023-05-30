from function_ndvi import *
import ast
from controle import *

def main():
    poligonos = conecta_bd()

    farm = str(input("Digite o nome da fazenda para obter o NDVI: "))
    poligonos = poligonos.loc[(poligonos['fazenda'] == farm)] #& (poligonos['talhao'] == 'T2')]
    
    print("Digite o intervalo de data de que a imagem seja (mínimo de 10 dias), no formato aaaa-mm-dd")
    data_ini = str(input("Digite a data inicial, no formato aaaa-mm-dd: "))
    data_final = str(input("Digite a data final, no formato aaaa-mm-dd: "))

    for index, row in poligonos.iterrows():
        roi_coords_str= row['roi_coords']
        roi_coords = ast.literal_eval(roi_coords_str) #biblioteca necessária para converter str para lista sem perder a formatação da coordenada (ee.geometry.polygon não aceita string)
        fazenda = row['fazenda']
        talhao = row['talhao']
        proprietario = row['proprietario']
        processor = SentinelImageProcessor(roi_coords, data_ini, data_final, fazenda, talhao, proprietario)
        image_roi = processor.process_images()

        processor.export_image(image_roi)
    
if __name__ == "__main__":
    main()

    input("Pressione Enter para fechar o programa...")
'''
roi_coords = [[-54.48707864894492,-21.73660745069606],[-54.48436529569182,-21.73708612766352],[-54.48279945411046,-21.73735021301333],[-54.48158601256098,-21.73674759944548],[-54.48098925004302,-21.73635896833387],[-54.47959688990941,-21.734558500359],[-54.47757850143851,-21.7315917751563],[-54.48198141914839,-21.72971447365351],[-54.48584171818774,-21.72808633032107],[-54.48600718380892,-21.72948018458605],[-54.48650189180762,-21.73282315958958],[-54.48667203986014,-21.73489702752682]]
fazenda = 'Pão e Mel'
talhao = 'LOTE P11'
'''