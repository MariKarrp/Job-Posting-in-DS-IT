import requests
import pandas as pd
import time
from datetime import datetime

def parse_arbeitnow():
    all_vacancies = []
    seen = set()
    
    keywords = ['data', 'python', 'java', 'javascript', 'devops']
    
    for kw in keywords:
        if len(all_vacancies) >= 800:
            break
            
        print(f"\n🔍 {kw}")
        
        for page in range(1, 10):
            url = f"https://www.arbeitnow.com/api/job-board-api?search={kw}&page={page}"
            
            try:
                r = requests.get(url, timeout=10)
                data = r.json()
                
                jobs = data.get('data', [])
                
                if not jobs:
                    break
                
                for job in jobs:
                    title = job.get('title', '')
                    
                    if not title or title in seen:
                        continue
                    seen.add(title)
                    
                    company = job.get('company_name', 'Unknown')
                    location = job.get('location', 'Unknown')
                    
                    all_vacancies.append({
                        'title': title,
                        'company': company,
                        'city': location,
                        'salary': job.get('salary', None),
                        'source': 'arbeitnow.com',
                        'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                print(f"    Page {page}: +{len(jobs)} (total: {len(all_vacancies)})")
                time.sleep(0.3)
                
            except Exception as e:
                print(f"    Error: {e}")
                break
    
    return pd.DataFrame(all_vacancies)

df_arbeitnow = parse_arbeitnow()
df_arbeitnow.to_csv('arbeitnow_vacancies.csv', index=False, encoding='utf-8-sig')