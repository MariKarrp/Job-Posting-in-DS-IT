# IT & Data Science Job Market Dashboard

Interactive dashboard for analyzing IT and Data Science job vacancies in Russia and worldwide.

## Features

- **Two regions**: Russia (HH.ru, Zarplata.ru, Trudvsem, Habr) and Global (LinkedIn, Remotive, Muse, Arbeitnow)
- **Salary analysis**: By cities, seniority levels, job categories
- **Skills tracking**: Most in-demand skills with beautiful visualizations
- **Interactive charts**: Powered by Plotly with zoom and hover details
- **Word Cloud**: Visualizing most frequent terms in job titles

## Demo

![Dashboard Preview](/visualization/img.png)
### Link
https://job-posting-in-ds-it-ocbqcjzjqznhehnkbxjswd.streamlit.app/

## Project Structure

```bash
Job-Posting-in-DS-IT/
│
├── data/                    
│   ├── russia_all_vacancies.csv   
│   ├── global_all_vacancies.csv   
│   └── [other CSV files] 
│
├── visualization/   
│   ├── dashboard.py                
│   └── img.png      
│
├── scripts/                    
│   ├── merge_russia_data.py 
│   ├── merge_global_data.py 
│   └── [other scraping scripts]  
│
└── README.md 
```

## Data

### Raw Data Sources

| Source | Region | Records |
|--------|--------|-------|
| hh_it_vacancies_47k.csv | Russia | 43,990 |
| zarplata_selenium_vacancies.csv | Russia | 1,053 |
| trudvsem_vacancies.csv | Russia | 192 |
| habr_vacancies_*.csv | Russia | 536 |
| habr_jobs_*.csv | Russia | 382 |
| linkedin_ds_it_vacancies.csv | Global | 2,700 |
| remotive_vacancies.csv | Global | 20 |
| muse_vacancies.csv | Global | 262 | 
| arbeitnow_vacancies.csv | Global | 834 |

## Limitations
- **City ranking formula**: 
  - Cities are ranked using a **weighted score**: `avg_salary × (0.7 + 0.3 × (vacancies / max_vacancies))`
  - This gives advantage to cities with more vacancies (more statistical confidence)
  - Small cities with few high-paying jobs may rank lower than their actual average suggests
  - This is intentional: we prioritize statistical reliability over theoretical maximums
- **Skill detection**: 
  - Russia: Uses HH.ru `skills` column (most accurate)
  - Global: Extracted from job titles (less precise)
- **Seniority detection**:
  - Keyword-based (Junior/Middle/Senior/Lead), Middle in region Global is absent 