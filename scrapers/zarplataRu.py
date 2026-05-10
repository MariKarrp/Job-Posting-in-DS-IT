from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(options=options)

keywords = ['python', 'java', 'data scientist', 'аналитик', 'разработчик', 'программист']
all_vacancies = []
seen = set()

for kw in keywords:
    if len(all_vacancies) >= 700:
        break
    
    print(f"\n🔍 {kw}")
    
    for page in range(0, 20):
        url = f"https://www.zarplata.ru/search/vacancy?text={kw}&page={page}"
        
        try:
            driver.get(url)
            time.sleep(2)
            
            items = driver.find_elements(By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy"]')
            
            if not items and page > 3:
                break
            
            for item in items:
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, '[data-qa="serp-item__title"]')
                    title = title_elem.text.strip()
                    
                    if not title or title in seen:
                        continue
                    seen.add(title)
                    
                    company_elem = item.find_elements(By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy-employer"]')
                    company = company_elem[0].text.strip() if company_elem else "Не указана"
                    
                    city_elem = item.find_elements(By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy-address"]')
                    city = city_elem[0].text.strip() if city_elem else "Не указан"
                    
                    salary_elem = item.find_elements(By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy-compensation"]')
                    salary = salary_elem[0].text.strip() if salary_elem else None
                    
                    all_vacancies.append({
                        'title': title,
                        'company': company,
                        'city': city,
                        'salary': salary,
                        'source': 'zarplata.ru',
                        'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                except Exception as e:
                    continue
            
            print(f"    Страница {page}: +{len(items)} (всего: {len(all_vacancies)})")
            time.sleep(1)
            
        except Exception as e:
            print(f"    Ошибка: {e}")
            break

driver.quit()

df_zarplata = pd.DataFrame(all_vacancies)
df_zarplata.to_csv('zarplata_selenium_vacancies.csv', index=False, encoding='utf-8-sig')