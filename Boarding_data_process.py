#скрипт для обработки посадочных данных
import pandas as pd

file_path = '../src/BoardingData.csv'

df = pd.read_csv(file_path, delimiter=';', engine='python')

df.to_excel('cleaned_boarding_data.xlsx', index=False)
