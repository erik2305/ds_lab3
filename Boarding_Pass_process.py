import pandas as pd

# Load the Excel file
file_path = 'src/YourBoardingPassDotAero/YourBoardingPassDotAero-2017-08-24.xlsx'
excel_data = pd.ExcelFile(file_path)

# Helper function to extract data from a sheet with resilience to missing data
def extract_flight_info_resilient(sheet_df):
    def get_cell_value(row, col):
        # Helper function to get cell value or return NaN if out of bounds
        try:
            return str(sheet_df.iloc[row, col])
        except IndexError:
            return 'NaN((('
    
    # Extracting all specified fields with corrected references and handling potential missing values
    flight_info = {
        'Flight Number': get_cell_value(3, 0),  # A4 (Flight Number)
        'Full Name': get_cell_value(2, 1),  # B3 (Full name)
        'Departure': get_cell_value(3, 3),  # D5 (Departure)
        'Arrival': get_cell_value(3, 7),  # H5 (Arrival)
        'Departure Code': get_cell_value(6, 3),  # D7 (Departure code)
        'Arrival Code': get_cell_value(6, 7),  # H7 (Arrival code)
        'Gate': get_cell_value(5, 1),  # D6 (Gate)
        'Flight Date': get_cell_value(7, 0),  # A9 (Flight Date)
        'Airline': get_cell_value(8, 4),  # E9 (Airline)
        'Unknown Time': get_cell_value(8, 2),  # C9 (Unknown time)
        'PNR': get_cell_value(11, 1),  # A12 (PNR)
        'E-Ticket': get_cell_value(11, 4),  # E13 (E-Ticket)
        'Seat': get_cell_value(9, 5),  # G10 (Seat)
        'Unknown Number': get_cell_value(0, 7),  # H1 (Unknown number)
        'Sequence': get_cell_value(3, 5)  # F3 (Sequence)
    }
    return flight_info

# Extract flight info from all sheets
structured_data_resilient = [extract_flight_info_resilient(excel_data.parse(sheet)) for sheet in excel_data.sheet_names]
structured_df_resilient = pd.DataFrame(structured_data_resilient)

# Save to Excel if needed
structured_df_resilient.to_excel('resilient_structured_flight_data.xlsx', index=False)