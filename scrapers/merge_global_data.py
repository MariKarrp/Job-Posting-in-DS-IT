import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = current_dir
global_files = [
    "remotive_vacancies.csv",
    "muse_vacancies.csv",
    "linkedin_ds_it_vacancies.csv",
    "arbeitnow_vacancies.csv"
]

global_dfs = []

for file in global_files:
    file_path = os.path.join(data_folder, file)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        df['source_file'] = file
        global_dfs.append(df)
        print(f"Загружен {file}: {len(df)} строк")
    else:
        print(f" Файл не найден: {file}")
        print(f"   Искали тут: {file_path}")

if global_dfs:
    global_merged = pd.concat(global_dfs, ignore_index=True)

    output_path = os.path.join(data_folder, "global_all_vacancies.csv")
    global_merged.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"\nУспешно! Объединено {len(global_merged)} строк")
else:
    print("\n Нет данных для объединения")