import pandas as pd

#Load the Excel file and target all sheets
excel_file= "Hormuz.xlsx"
all_sheets= pd.read_excel(excel_file, sheet_name=None)

for sheet_name, data in all_sheets.items():
    data.to_csv(f" {sheet_name}.csv", index=False)

# code to redirect files that created into the data/raw folder
