import requests
import pandas as pd
import time
from datetime import datetime
def parse_trudvsem():
    keywords = [
        "data scientist", "data analyst", "data engineer",
        "python developer", "java developer", "sql developer",
        "аналитик данных", "инженер данных", "ml engineer",
        "machine learning", "big data", "bi analyst"
    ]
    
    all_vacancies = []
    seen = set()
    
    for keyword in keywords:
        if len(all_vacancies) >= 1000:
            break

        offset = 0
        
        while offset < 300:
            url = f"https://opendata.trudvsem.ru/api/v1/vacancies?text={keyword}&limit=100&offset={offset}"
            
            try:
                r = requests.get(url, timeout=15)
                data = r.json()
                
                vacancies = data.get('results', {}).get('vacancies', [])
                if not vacancies:
                    break
                
                for item in vacancies:
                    vac = item.get('vacancy', {})
                    title = vac.get('job-name', '')
                    
                    if not title or title in seen:
                        continue
                    seen.add(title)
                    
                    salary_from = vac.get('salary_from', '')
                    salary_to = vac.get('salary_to', '')
                    salary = None
                    if salary_from or salary_to:
                        salary = f"{salary_from} - {salary_to}" if salary_to else salary_from
                    
                    company = vac.get('company', {}).get('name', 'Не указана')
                    address = vac.get('address', {})
                    city = address.get('area', 'Не указан')
                    
                    all_vacancies.append({
                        'title': title,
                        'company': company,
                        'city': city,
                        'salary': salary,
                        'source': 'trudvsem.ru',
                        'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                print(f"    +{len(vacancies)} (всего: {len(all_vacancies)})")
                offset += 100
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Ошибка: {e}")
                break
    
    return pd.DataFrame(all_vacancies)

df_trud = parse_trudvsem()
df_trud.to_csv('trudvsem_vacancies.csv', index=False, encoding='utf-8-sig')