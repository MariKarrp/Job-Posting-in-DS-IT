import kagglehub
import pandas as pd
import os
from datetime import datetime

path = "/kaggle/input/hhru-it-vacancies-from-20211025-to-20211202"

csv_file = os.path.join(path, "IT_vacancies_full.csv")
df = pd.read_csv(csv_file)

df_clean = pd.DataFrame({
    'title': df['Name'].astype(str),
    'company': df['Employer'].astype(str),
    'city': df['Area'].astype(str),
    'salary': df['From'].fillna('').astype(str) + ' - ' + df['To'].fillna('').astype(str),
    'skills': df['Keys'].fillna('').astype(str),
    'experience': df['Experience'].fillna('').astype(str),
    'schedule': df['Schedule'].fillna('').astype(str),
    'source': 'hh_kaggle_47k',
    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
})

df_clean = df_clean.dropna(subset=['title'])
df_clean = df_clean[df_clean['title'].str.len() > 3]
df_clean = df_clean.drop_duplicates(subset=['title', 'company'], keep='first')

df_clean.to_csv('hh_it_vacancies_47k.csv', index=False, encoding='utf-8-sig')
print("\nСОХРАНЕНО: hh_it_vacancies_47k.csv")
