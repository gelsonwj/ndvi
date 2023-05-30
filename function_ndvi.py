from ee import Geometry, ImageCollection, Filter, Feature, Image, Initialize, Authenticate
Authenticate()
Initialize()
from os import listdir, path, rename, remove
from requests import get
from zipfile import ZipFile
from datetime import datetime


class SentinelImageProcessor:
    def __init__(self, roi_coords, start_date, end_date, fazenda, talhao, proprietario): 
        self.roi_coords = roi_coords
        self.roi = Geometry.Polygon(roi_coords)
        self.start_date = start_date
        self.end_date = end_date
        self.fazenda = fazenda
        self.talhao = talhao
        self.data_images_list = None
        self.data_image = None
        self.proprietario = proprietario
        
    def get_sentinel_collection(self): #obtém uma coleção (lista) de imagens do sentinel-2a e sentinel-1c
        sentinel_harmonized = (
            ImageCollection("COPERNICUS/S2_HARMONIZED")
            .filterDate(self.start_date, self.end_date)
            .filterBounds(self.roi)
            .filter(Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 99))
        )

        sentinel_sr_harmonized = (
            ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterDate(self.start_date, self.end_date)
            .filterBounds(self.roi)
            .filter(Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 99))
        )

        return sentinel_harmonized, sentinel_sr_harmonized
    
    def get_date(self, image): #obtém a da imagem
        id = image.get("system:id")
        date = image.date().format("yyyy-MM-dd")
        return Feature(None, {"ID": id, "date": date})

    def calculate_ndvi(self, image): #faz o cálculo do NDVI
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return image.addBands(ndvi)

    def process_images(self): #chama as funções para obter as imagens dos sentinel, compara qual tem a data mais recente e fica com ela, caso tenha data igual, fica com o S2_SR
        sentinel_harmonized, sentinel_sr_harmonized = self.get_sentinel_collection()
        sentinel_harmonized_data = sentinel_harmonized.map(self.get_date)
        sentinel_sr_harmonized_data = sentinel_sr_harmonized.map(self.get_date)

        sentinel_harmonized_images = sentinel_harmonized_data.aggregate_array("ID").getInfo()
        sentinel_sr_harmonized_images = sentinel_sr_harmonized_data.aggregate_array("ID").getInfo()

        sentinel_harmonized_dates = sentinel_harmonized_data.aggregate_array("date").getInfo()
        sentinel_sr_harmonized_dates = sentinel_sr_harmonized_data.aggregate_array("date").getInfo()

        latest_date_harmonized = datetime.strptime(sentinel_harmonized_dates[-1], "%Y-%m-%d")
        latest_date_sr_harmonized = datetime.strptime(sentinel_sr_harmonized_dates[-1], "%Y-%m-%d")

        if latest_date_harmonized > latest_date_sr_harmonized:
            selected_images = sentinel_harmonized_images
            selected_date = sentinel_harmonized_dates[-1]
        else:
            selected_images = sentinel_sr_harmonized_images
            selected_date = sentinel_sr_harmonized_dates[-1]

        selected_image = Image(selected_images[-1])
        selected_image = selected_image.select(['B4', 'B8'])
        selected_image_with_ndvi = self.calculate_ndvi(selected_image)
        image_roi = selected_image_with_ndvi.clip(self.roi)

        self.data_image = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%d-%m-%Y")
        print("Data da imagem 📅:", self.data_image)

        #cloud_percentage = image_roi.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()

        #print("☁ Percentual de Nuvem ☁:", cloud_percentage, "%")
        #DATATAKE_IDENTIFIER	
        return image_roi


    def get_last_archive(self): #seleciona o último arquivo da pasta para que ele seja selecionado pra ser renomeado dentro da pasta onde foi baixado.
        pasta = 'Y:\\DADOS\\TEMP\\T. I\\NDVI_novo\\{}\\{}\\{}\\{}' .format(self.data_image.split('-')[-1], self.proprietario, self.fazenda, self.talhao) #self.data_image.split('')[-1] seleciona o ano
        arquivos = listdir(pasta)

        # Remove pastas da lista
        arquivos = [arquivo for arquivo in arquivos if path.isfile(path.join(pasta, arquivo))]

        # Ordena a lista de arquivos com base na data de modificação
        arquivos = sorted(arquivos, key=lambda x: path.getmtime(path.join(pasta, x)), reverse=True)

        # Obtém o nome do arquivo mais recente
        if len(arquivos) > 0:
            arquivo_recente = arquivos[0]
            print("Arquivo mais recente:", arquivo_recente)
            return arquivo_recente
        else:
            print("A pasta está vazia.")
        

    def export_image(self, image_roi): #baixa a imagem do polígono
        #masked_image = image_roi.updateMask(image_roi.select('NDVI').gt(0))
        ano = self.data_image.split('-')[-1]
        url = image_roi.select('NDVI').getDownloadUrl({
            'scale': 10,
            'crs': 'EPSG:4326',
            'region': self.roi
        })

        response = get(url)
    
        if response.status_code == 200:
            output_zip_path = 'Y:\\DADOS\\TEMP\\T. I\\NDVI_novo\\zipfile.zip' 
            output_tif_path = 'Y:\\DADOS\\TEMP\\T. I\\NDVI_novo\\{}\\{}\\{}\\{}' .format(ano, self.proprietario, self.fazenda, self.talhao) #local onde a imagem ndvi será extraída

            with open(output_zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extrair o arquivo TIFF do zip
            with ZipFile(output_zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_tif_path)
            
            # Renomear o arquivo TIFF extraído
            arquivo = self.get_last_archive()
            extracted_tif_path = output_tif_path + "\\{}" .format(arquivo)
            renamed_tif_path = output_tif_path + "\\{}_{}.tif" .format(self.data_image, self.talhao) #dd_mm_aaaa_talhao

            try:#caso o arquivo com o nome já existe, então exclui ele e atualiza com o mais novo.
                rename(extracted_tif_path, renamed_tif_path)
            except FileExistsError:
                remove(renamed_tif_path)  # Remove o arquivo existente
                rename(extracted_tif_path, renamed_tif_path)
            
            # Remover o arquivo zip
            remove(output_zip_path)
            
            print("Imagem exportada com sucesso para:", renamed_tif_path)
        else:
            print("Falha ao exportar a imagem. Status de resposta:", response.status_code)  
    