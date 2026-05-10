import pandas as pd
import glob
import re
from datetime import datetime

all_files = glob.glob('*.csv')
dfs = []

for file in all_files:
    try:
        df = pd.read_csv(file)
        print(f" {file}: {len(df)} записей")
        dfs.append(df)
    except Exception as e:
        print(f"Ошибка при чтении {file}: {e}")

df_all = pd.concat(dfs, ignore_index=True)

before = len(df_all)
df_all = df_all.drop_duplicates(subset=['title', 'company'], keep='first')

df_all = df_all.dropna(subset=['title'])
df_all = df_all[df_all['title'].str.len() > 3]

df_all['city'] = df_all['city'].astype(str).str.replace(r'[^\w\s\-]', '', regex=True)
df_all['city'] = df_all['city'].str.replace('nan', 'Не указан', case=False)

def extract_min_salary(salary_str):
    if pd.isna(salary_str) or salary_str == '':
        return None
    numbers = re.findall(r'\d+', str(salary_str))
    if numbers:
        return int(numbers[0])
    return None

df_all['salary_min'] = df_all['salary'].apply(extract_min_salary)

def detect_grade(title):
    title_lower = str(title).lower()
    if 'junior' in title_lower or 'младший' in title_lower:
        return 'Junior'
    elif 'senior' in title_lower or 'lead' in title_lower:
        return 'Senior'
    elif 'middle' in title_lower:
        return 'Middle'
    else:
        return 'Not specified'

df_all['grade'] = df_all['title'].apply(detect_grade)

def detect_category(title):
    title_lower = str(title).lower()
    if 'data scientist' in title_lower or 'data science' in title_lower:
        return 'Data Scientist'
    elif 'data analyst' in title_lower or 'analyst' in title_lower:
        return 'Data Analyst'
    elif 'data engineer' in title_lower:
        return 'Data Engineer'
    elif 'python' in title_lower or 'java' in title_lower or 'developer' in title_lower:
        return 'Developer/Engineer'
    elif 'machine learning' in title_lower or 'ml' in title_lower:
        return 'Machine Learning'
    else:
        return 'Other IT'

df_all['category'] = df_all['title'].apply(detect_category)

df_all.to_csv('final_dashboard_data.csv', index=False, encoding='utf-8-sig')
