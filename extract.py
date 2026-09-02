import pandas as pd
import sys

try:
    xls = pd.ExcelFile('d:/Casestudy/economy sim/Yarn_Economy.xlsx')
    with open('d:/Casestudy/economy sim/output.txt', 'w', encoding='utf-8') as f:
        for sheet in xls.sheet_names:
            f.write(f'\n--- {sheet} ---\n')
            f.write(pd.read_excel(xls, sheet).to_csv())
    print("Done")
except Exception as e:
    print(f"Error: {e}")
