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