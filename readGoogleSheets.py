import gspread
from google.oauth2.service_account import Credentials
import random

def authenticate_gspread(credentials_path):
    # Cargar las credenciales desde el archivo JSON
    credentials = Credentials.from_service_account_file(credentials_path, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    
    # Crear una instancia de la clase gspread utilizando las credenciales
    gc = gspread.authorize(credentials)
    
    return gc

def read_google_sheets(gc, spreadsheet_id, sheet_name):
    # Abrir la hoja de cálculo y la hoja
    workbook = gc.open_by_key(spreadsheet_id)
    worksheet = workbook.worksheet(sheet_name)

    # Obtener todos los valores de la hoja
    values = worksheet.get_all_values()
    channels = values[1][2].split(";")
    random.shuffle(channels)
    print(channels)
    return channels
def main():
    # Ruta al archivo JSON de credenciales
    credentials_path = "automatizaciondonpodcast-6ffcae3433ee.json"

    # ID de la hoja de cálculo
    spreadsheet_id = '1QBl3XzKWWAZRlIAfURclabHQJr4PuMnClH8rbYrq-xY'

    # Nombre de la hoja dentro de la hoja de cálculo
    sheet_name = 'MasterData'

    # Autenticar con Google Sheets
    gc = authenticate_gspread(credentials_path)

    # Leer datos desde Google Sheets
    channels = read_google_sheets(gc, spreadsheet_id, sheet_name)
    return channels
    


if __name__ == "__main__":
    main()
