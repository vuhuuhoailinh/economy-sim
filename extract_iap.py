import pandas as pd
import sys

try:
    file_path = 'd:/Casestudy/economy sim/Economy + IAP Design  (1).xlsx'
    xls = pd.ExcelFile(file_path)
    with open('d:/Casestudy/economy sim/iap_preview.txt', 'w', encoding='utf-8') as f:
        f.write(f"Sheets: {xls.sheet_names}\n\n")
        for sheet in xls.sheet_names:
            f.write(f'\n--- {sheet} (First 15 rows) ---\n')
            df = pd.read_excel(xls, sheet, nrows=15)
            f.write(df.to_csv())
    print("Extraction successful.")
except Exception as e:
    print(f"Error: {e}")
