import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime
import re

def parse_habr_vacancies():
    vacancies = []
    seen_ids = set()

    search_terms = [
        "data scientist",
        "data analyst", 
        "data engineer",
        "analyst",
        "python developer",
        "devops",
        "machine learning"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for term in search_terms:
        if len(vacancies) >= 5000:
            break
            
        print(f"\n🔍 Поиск: '{term}'")
        
        for page in range(1, 30):
            if len(vacancies) >= 5000:
                break
                
            url = f"https://career.habr.com/vacancies?page={page}&q={term}"
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

                job_cards = soup.find_all('div', class_='vacancy-card')
                
                if not job_cards:
                    print(f"  Страница {page}: нет вакансий, завершаем")
                    break
                
                found = 0
                for card in job_cards:
                    try:
                        title_elem = card.find('a', class_='vacancy-card__title-link')
                        if not title_elem:
                            continue
                        title = title_elem.text.strip()

                        href = title_elem.get('href', '')
                        vacancy_id = href.split('/')[-1] if href else str(hash(title))
                        
                        if vacancy_id in seen_ids:
                            continue
                        seen_ids.add(vacancy_id)

                        company_elem = card.find('div', class_='vacancy-card__company')
                        company = company_elem.find('a').text.strip() if company_elem and company_elem.find('a') else "Не указана"

                        salary_elem = card.find('div', class_='vacancy-card__salary')
                        salary = None
                        if salary_elem:
                            salary_text = salary_elem.get_text(strip=True)
                            if 'от' in salary_text and '₽' in salary_text:
                                salary = salary_text
                            elif 'USD' in salary_text or '$' in salary_text:
                                salary = salary_text

                        meta_elem = card.find('div', class_='vacancy-card__meta')
                        city = "Не указан"
                        remote = False
                        if meta_elem:
                            chips = meta_elem.find_all('div', class_='basic-chip')
                            for chip in chips:
                                chip_text = chip.get_text(strip=True)
                                if 'Можно удалённо' in chip_text:
                                    remote = True
                                elif chip_text and not chip_text.startswith('Middle') and not chip_text.startswith('Senior') and not chip_text.startswith('Junior') and not chip_text.startswith('Lead') and not chip_text.startswith('Intern'):
                                    city = chip_text

                        skills_elem = card.find('div', class_='vacancy-card__skills')
                        skills = []
                        if skills_elem:
                            skill_chips = skills_elem.find_all('a', class_='basic-chip')
                            skills = [chip.get_text(strip=True) for chip in skill_chips]
                        
                        vacancies.append({
                            'id': vacancy_id,
                            'title': title,
                            'company': company,
                            'city': city,
                            'remote': remote,
                            'salary': salary,
                            'skills': ', '.join(skills),
                            'search_term': term,
                            'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        found += 1
                        
                        if len(vacancies) % 100 == 0:
                            print(f"     Собрано {len(vacancies)} вакансий...")
                            
                    except Exception as e:
                        continue

                
                if found == 0:
                    print(f"  На странице {page} нет вакансий, переходим к следующему запросу")
                    break

                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"  Ошибка: {e}")
                break
    
    return vacancies

result = parse_habr_vacancies()

df = pd.DataFrame(result)

if len(df) > 0:
    filename = f"habr_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
else:
    print("\n Не удалось собрать вакансии. Возможно, сайт изменил структуру.")
