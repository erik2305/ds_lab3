#скрипт для обработки и слияния посадочных талонов
import pandas as pd
import os

directory = '../src/YourBoardingPassDotAero'

def extract_flight_info_resilient(sheet_df):
    def get_cell_value(row, col):
        try:
            return str(sheet_df.iloc[row, col])
        except IndexError:
            return 'NaN(((('
    
    def get_gender(value):
        if value.strip().upper() == "MR":
            return "Male"
        elif value.strip().upper() == "MRS":
            return "Female"
        else:
            return "Unknown"
    

    flight_info = {
        'Flight Number': get_cell_value(3, 0),
        'Full Name': get_cell_value(1, 1),  
        'Departure': get_cell_value(3, 3),  
        'Arrival': get_cell_value(3, 7),
        'Departure Code': get_cell_value(5, 3),  
        'Arrival Code': get_cell_value(5, 7),
        'Gate': get_cell_value(5, 1),
        'Flight Date': get_cell_value(7, 0),  
        'Airline': get_cell_value(7, 4),
        'Unknown Time': get_cell_value(7, 2),  
        'PNR': get_cell_value(11, 1),
        'E-Ticket': get_cell_value(11, 4),
        'Seat': get_cell_value(9, 7), 
        'Unknown Number': sheet_df.columns[7],
        'Unknown Letter': get_cell_value(1, 7),
        'Gender': get_gender(get_cell_value(1, 0)),
        'Sequence': get_cell_value(1, 5),
    }
    return flight_info

all_data = []
counter = 0

for filename in os.listdir(directory):
    if filename.endswith(".xlsx"):
        file_path = os.path.join(directory, filename)
        excel_data = pd.ExcelFile(file_path)
        print(f"opening {filename}")
        for sheet in excel_data.sheet_names:
            sheet_df = excel_data.parse(sheet)
            flight_info = extract_flight_info_resilient(sheet_df)
            all_data.append(flight_info)
            counter += 1

structured_df_resilient = pd.DataFrame(all_data)

output_file = 'Boarding_pass_merged.xlsx'
structured_df_resilient.to_excel(output_file, index=False)

print(f"Successfully merged data into {output_file}")
print(f"processed {counter} files")