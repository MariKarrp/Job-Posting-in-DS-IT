import pandas as pd
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = current_dir

russian_files = [
    "zarplata_selenium_vacancies.csv",
    "trudvsem_vacancies.csv",
    "hh_it_vacancies_47k.csv",
    "habr_vacancies_20260509_145533 (1).csv",
    "habr_jobs_20260509_144554 (1).csv"
]

russian_dfs = []

for file in russian_files:
    file_path = os.path.join(data_folder, file)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        df['source_file'] = file
        russian_dfs.append(df)
    else:
        print(f" Файл не найден: {file}")

if russian_dfs:
    russia_merged = pd.concat(russian_dfs, ignore_index=True)

    output_path = os.path.join(data_folder, "russia_all_vacancies.csv")
    russia_merged.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"\n Успешно! Объединено {len(russia_merged)} строк")
else:
    print("\n Нет данных для объединения")