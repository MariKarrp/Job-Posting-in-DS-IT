import requests
import pandas as pd
import time
from datetime import datetime

def parse_muse():
    keywords = ['data scientist', 'data analyst', 'software engineer', 'python', 'java']
    all_vacancies = []
    seen = set()
    
    for kw in keywords:
        if len(all_vacancies) >= 700:
            break
        
        for page in range(1, 15):
            url = f"https://www.themuse.com/api/public/jobs?page={page}&search={kw}"
            
            try:
                r = requests.get(url, timeout=10)
                data = r.json()
                
                jobs = data.get('results', [])
                if not jobs:
                    break
                
                for job in jobs:
                    title = job.get('name', '')
                    
                    if not title or title in seen:
                        continue
                    seen.add(title)
                    
                    company = job.get('company', {}).get('name', 'Unknown')
                    locations = job.get('locations', [])
                    city = locations[0].get('name', 'Unknown') if locations else 'Unknown'
                    
                    all_vacancies.append({
                        'title': title,
                        'company': company,
                        'city': city,
                        'salary': None,
                        'source': 'themuse.com',
                        'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                print(f"    Page {page}: +{len(jobs)} (total: {len(all_vacancies)})")
                time.sleep(0.3)
                
            except Exception as e:
                print(f"    Error: {e}")
                break
    
    return pd.DataFrame(all_vacancies)

df_muse = parse_muse()
print(f"\nCollected: {len(df_muse)}")
df_muse.to_csv('muse_vacancies.csv', index=False, encoding='utf-8-sig')