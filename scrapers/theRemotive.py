import requests
import pandas as pd
import time
from datetime import datetime
def parse_remotive():

    all_vacancies = []
    seen = set()
    
    categories = ['software-dev', 'data-science', 'devops-sysadmin', 'product', 'design']
    
    for cat in categories:
        if len(all_vacancies) >= 600:
            break

        
        url = f"https://remotive.com/api/remote-jobs?category={cat}"
        
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            
            jobs = data.get('jobs', [])
            
            for job in jobs:
                title = job.get('title', '')
                
                if not title or title in seen:
                    continue
                seen.add(title)
                
                company = job.get('company_name', 'Unknown')
                
                all_vacancies.append({
                    'title': title,
                    'company': company,
                    'city': 'Remote',
                    'salary': job.get('salary', None),
                    'source': 'remotive.com',
                    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Error: {e}")
    
    return pd.DataFrame(all_vacancies)

df_remotive = parse_remotive()
df_remotive.to_csv('remotive_vacancies.csv', index=False, encoding='utf-8-sig')