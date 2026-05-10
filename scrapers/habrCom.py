import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime

def parse_habr_vacancies():
    vacancies = []
    seen_titles = set()

    base_url = "https://career.habr.com/vacancies"
    search_terms = [
        "python", "java", "javascript", "golang", "rust", "c++", "c#",
        "data scientist", "data analyst", "data engineer", "machine learning",
        "devops", "backend", "frontend", "fullstack", "mobile", "ios", "android",
        "system administrator", "security", "qa", "testing", "analyst",
        "product manager", "project manager", "team lead", "tech lead"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for term in search_terms:
        if len(vacancies) >= 5000:
            break

        for page in range(1, 25):
            if len(vacancies) >= 5000:
                break
                
            url = f"{base_url}?page={page}&q={term}"
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

                job_cards = soup.find_all('div', class_='vacancy-card')
                
                if not job_cards and page == 1:
                    job_cards = soup.find_all('div', attrs={'class': lambda x: x and 'vacancy' in x})
                
                if not job_cards:
                    if page > 5:
                        break
                    continue
                
                found = 0
                for card in job_cards:
                    try:
                        title_elem = (card.find('a', class_='vacancy-card__title-link') or 
                                     card.find('a', href=lambda x: x and '/vacancies/' in x))
                        if not title_elem:
                            continue
                        
                        title = title_elem.text.strip()
                        if title in seen_titles:
                            continue
                        seen_titles.add(title)

                        company_elem = card.find('div', class_='vacancy-card__company')
                        company = company_elem.text.strip() if company_elem else "Не указана"

                        city_elem = card.find('div', class_='vacancy-card__meta')
                        city = "Не указан"
                        if city_elem:
                            meta_text = city_elem.text
                            cities = ['Москва', 'СПб', 'Санкт-Петербург', 'Новосибирск', 
                                     'Екатеринбург', 'Казань', 'Нижний Новгород', 'Краснодар']
                            for c in cities:
                                if c in meta_text:
                                    city = c
                                    break

                        salary_elem = card.find('div', class_='vacancy-card__salary')
                        salary = salary_elem.text.strip() if salary_elem else None

                        skills_elem = card.find('div', class_='vacancy-card__skills')
                        skills = []
                        if skills_elem:
                            skill_spans = skills_elem.find_all(['a', 'span'], class_='basic-chip')
                            skills = [s.text.strip() for s in skill_spans[:5]]
                        
                        vacancies.append({
                            'title': title,
                            'company': company,
                            'city': city,
                            'salary': salary,
                            'skills': ', '.join(skills),
                            'search_term': term,
                            'source': 'habr.com',
                            'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        found += 1
                        
                        if len(vacancies) % 200 == 0:
                            print(f"     Собрано {len(vacancies)} вакансий...")
                            
                    except Exception as e:
                        continue

                if found == 0 and page > 3:
                    break
                    
                time.sleep(random.uniform(0.5, 1))
                
            except Exception as e:
                print(f"  Ошибка: {e}")
                break
    
    return vacancies

result = parse_habr_vacancies()
df = pd.DataFrame(result)

if len(df) > 0:
    filename = f"habr_vacancies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
