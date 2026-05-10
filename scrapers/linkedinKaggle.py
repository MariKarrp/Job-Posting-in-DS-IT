import kagglehub
import pandas as pd
import os
from datetime import datetime

path = kagglehub.dataset_download("arshkon/linkedin-job-postings")

file_postings = os.path.join(path, "postings.csv")
print("Загрузка postings.csv (1-2 минуты)...")

needed_cols = ['job_id', 'title', 'company_id', 'location', 
               'min_salary', 'max_salary', 'formatted_work_type', 
               'formatted_experience_level', 'remote_allowed']
df_postings = pd.read_csv(file_postings, usecols=needed_cols, low_memory=False)

file_companies = os.path.join(path, "companies", "companies.csv")
df_companies = pd.read_csv(file_companies, usecols=['company_id', 'name'])

keywords = 'data scientist|data analyst|data engineer|machine learning|' \
           'ml engineer|analytics|business intelligence|bi analyst|' \
           'python developer|sql developer|software engineer|' \
           'аналитик|разработчик python|инженер данных'

df_postings['title_lower'] = df_postings['title'].str.lower()

mask = df_postings['title_lower'].str.contains(keywords, na=False, regex=True)
df_filtered = df_postings[mask].copy()
df_filtered = df_filtered.drop(columns=['title_lower'])

df_merged = df_filtered.merge(df_companies, on='company_id', how='left')

df_clean = pd.DataFrame({
    'title': df_merged['title'].astype(str),
    'company': df_merged['name'].fillna('Не указана').astype(str),
    'city': df_merged['location'].fillna('Unknown').astype(str),
    'salary': df_merged['min_salary'].fillna('').astype(str) + ' - ' + df_merged['max_salary'].fillna('').astype(str),
    'work_type': df_merged['formatted_work_type'].fillna('').astype(str),
    'experience_level': df_merged['formatted_experience_level'].fillna('').astype(str),
    'remote_allowed': df_merged['remote_allowed'].fillna(False).astype(bool),
    'source': 'linkedin_kaggle',
    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
})

before = len(df_clean)
df_clean = df_clean.drop_duplicates(subset=['title', 'company'], keep='first')
df_clean = df_clean.dropna(subset=['title'])
df_clean = df_clean[df_clean['title'].str.len() > 3]

df_clean.to_csv('linkedin_ds_it_vacancies.csv', index=False, encoding='utf-8-sig')

