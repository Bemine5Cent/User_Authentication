import gspread
from google.oauth2.service_account import Credentials

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
client = gspread.authorize(creds)
sheet = client.open('UserDatabase').sheet1

print("Connected!")
print("Headers:", sheet.row_values(1))