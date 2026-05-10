import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import ast
from collections import Counter

st.set_page_config(
    page_title="IT & Data Science Job Market",
    page_icon="https://img.icons8.com/?size=100&id=11497&format=png&color=000000",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}

.metric-card {
    background-color: #151B23;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #262730;
    text-align: center;
}

.metric-value {
    font-size: 32px;
    font-weight: bold;
    color: #58A6FF;
}

.metric-label {
    color: #8B949E;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
data_folder = os.path.join(project_root, "data")


@st.cache_data
def load_russia_data():
    file_path = os.path.join(data_folder, "russia_all_vacancies.csv")

    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки российских данных: {e}")
        return pd.DataFrame()


@st.cache_data
def load_global_data():
    file_path = os.path.join(data_folder, "global_all_vacancies.csv")

    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки глобальных данных: {e}")
        return pd.DataFrame()


@st.cache_data
def load_hh_skills():
    file_path = os.path.join(data_folder, "hh_it_vacancies_47k.csv")

    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        return df
    except Exception as e:
        st.warning(f"Не удалось загрузить HH данные для скиллов: {e}")
        return pd.DataFrame()

def clean_salary(x):
    if pd.isna(x):
        return np.nan
    nums = re.findall(r'\d+', str(x).replace(" ", ""))
    return int(nums[0]) if len(nums) > 0 else np.nan


def detect_category(title):
    t = str(title).lower()

    if "data scientist" in t:
        return "Data Science"
    if "data analyst" in t:
        return "Analytics"
    if "data engineer" in t:
        return "Data Engineering"
    if "backend" in t:
        return "Backend"
    if "frontend" in t:
        return "Frontend"
    if "devops" in t:
        return "DevOps"
    if "ml" in t or "machine learning" in t:
        return "Machine Learning"
    if "full stack" in t or "fullstack" in t:
        return "Full Stack"

    return "Other IT"


def detect_grade(title):
    t = str(title).lower()

    if "junior" in t or "entry" in t or "entry-level" in t or "entry level" in t:
        return "Junior"
    if "middle" in t:
        return "Middle"
    if "senior" in t or "sr." in t or "sr " in t:
        return "Senior"
    if "lead" in t or "principal" in t or "staff" in t:
        return "Lead"

    return "Not specified"


def clean_city(city):
    if pd.isna(city):
        return "Unknown"

    city = str(city).strip()

    if city.lower() in ["не указан", "не указано", "unknown", "not specified", "nan", "none"]:
        return "Unknown"

    city = re.sub(r'^(greater|great)\s+', '', city, flags=re.IGNORECASE)
    city = re.sub(r'\s+area$', '', city, flags=re.IGNORECASE)

    city = re.sub(
        r',\s*(?:[A-Z]{2}|[A-Za-z\s]+?(?:usa|united states|uk|canada|germany|france|australia|india|china|japan))$', '',
        city, flags=re.IGNORECASE)


    city = re.sub(r'\s+([A-Z]{2})$', '', city)

    city = re.sub(r'\s*\([^)]*\)$', '', city)

    city = ' '.join(city.split())

    city = city.rstrip('.')

    if city == "" or city.lower() in ["не указан", "unknown"]:
        return "Unknown"

    city = ' '.join(word.capitalize() for word in city.split())

    return city


def parse_skills(skills_str):
    if pd.isna(skills_str):
        return []

    try:
        if isinstance(skills_str, str):
            if skills_str.startswith('['):
                skills_list = ast.literal_eval(skills_str)
                if isinstance(skills_list, list):
                    return [str(skill).lower().strip() for skill in skills_list]
            else:
                skills = re.split(r'[,|•·]', skills_str)
                return [skill.strip().lower() for skill in skills if skill.strip()]
    except:
        pass

    return []

def process_data(df, region):
    if df.empty:
        return df

    processed = df.copy()

    processed["salary_min"] = processed["salary"].apply(clean_salary)
    processed["salary_min"] = pd.to_numeric(processed["salary_min"], errors="coerce")

    processed["city"] = processed["city"].apply(clean_city)
    processed = processed[processed["city"] != "Unknown"]

    processed["category"] = processed["title"].apply(detect_category)
    processed["grade"] = processed["title"].apply(detect_grade)

    if region == "Russia":
        processed = processed[processed["salary_min"] < 1_500_000]
        processed = processed[processed["salary_min"] > 10_000]
        processed["salary_display"] = processed["salary_min"]
        processed["currency"] = "₽"
        processed["salary_label"] = "Salary (RUB)"
    else:  # Global
        processed = processed[processed["salary_min"] < 500_000]
        processed = processed[processed["salary_min"] > 20_000]
        processed["salary_display"] = processed["salary_min"]
        processed["currency"] = "₽"
        processed["salary_label"] = "Salary (RUB)"

    return processed

def analyze_skills_russia_from_hh():
    hh_df = load_hh_skills()

    if hh_df.empty:
        return None

    if 'skills' not in hh_df.columns:
        return None

    all_skills = []

    for skills_str in hh_df['skills'].dropna():
        skills_list = parse_skills(skills_str)
        all_skills.extend(skills_list)

    if len(all_skills) == 0:
        return None

    skill_counts = Counter(all_skills)
    skill_counts = {k: v for k, v in skill_counts.items() if v >= 3}

    skills_df = pd.DataFrame({
        "skill": list(skill_counts.keys()),
        "count": list(skill_counts.values())
    }).sort_values("count", ascending=False).head(20)

    return skills_df


def analyze_skills_from_titles(df, region):
    skills = [
        "python", "sql", "aws", "docker", "kubernetes",
        "tensorflow", "pytorch", "spark", "airflow",
        "git", "linux", "java", "javascript", "react",
        "scikit-learn", "pandas", "numpy", "excel", "tableau",
        "postgresql", "mongodb", "redis", "kafka", "jenkins"
    ]

    text_data = (df["title"].fillna("") + " " + df["company"].fillna("")).str.lower()

    skill_counts = {
        skill: text_data.str.contains(skill).sum()
        for skill in skills
    }

    skills_df = pd.DataFrame({
        "skill": skill_counts.keys(),
        "count": skill_counts.values()
    }).sort_values("count", ascending=False)

    return skills_df


def analyze_skills_main(df, region):
    if region == "Russia":
        skills_df = analyze_skills_russia_from_hh()
        if skills_df is not None and len(skills_df) > 0:
            return skills_df, "from HH.ru skills column"
        else:
            skills_df = analyze_skills_from_titles(df, region)
            return skills_df, "from job titles and companies (fallback)"
    else:
        skills_df = analyze_skills_from_titles(df, region)
        return skills_df, "from job titles and companies"


st.title("IT & Data Science Job Market")

# Region selector
col1, col2 = st.columns([3, 1])
with col2:
    selected_region = st.radio(
        "",
        options=["Russia", "Global"],
        horizontal=True,
        label_visibility="collapsed"
    )


if selected_region == "Russia":
    with st.spinner("Loading Russian job market data..."):
        raw_df = load_russia_data()
        df = process_data(raw_df, "Russia")
        source_note = "Data source: HH.ru, Zarplata.ru, Trudvsem, Habr"
else:
    with st.spinner("Loading global job market data..."):
        raw_df = load_global_data()
        df = process_data(raw_df, "Global")
        source_note = "Data source: LinkedIn, Remotive, Muse, Arbeitnow"

if df.empty:
    st.error(f"No data available for {selected_region}. Please check the data files.")
    st.stop()

skills_df, skills_source = analyze_skills_main(df, selected_region)

filtered_core = df[df["category"] != "Other IT"]

if len(df) > 0 and df["salary_display"].notna().any():
    median_salary = df["salary_display"].median()
else:
    median_salary = 0

currency = df["currency"].iloc[0] if len(df) > 0 else ""

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Vacancies", f"{len(df):,}")
with col2:
    st.metric("Companies", f"{df['company'].nunique():,}")
with col3:
    st.metric("Median Salary", f"{median_salary:,.0f} {currency}" if median_salary > 0 else "N/A")
with col4:
    st.metric("Cities", f"{df['city'].nunique():,}")

st.caption(source_note)

tab1, tab2, tab3 = st.tabs(["Overview", "Salary Analysis", "Skills & Trends"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        if len(filtered_core) > 0:
            cat_counts = filtered_core["category"].value_counts().reset_index()
            cat_counts.columns = ["category", "count"]

            fig = px.bar(
                cat_counts,
                x="count",
                y="category",
                orientation="h",
                text="count",
                title="Job Categories Distribution",
                color="count",
                color_continuous_scale="Viridis"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available")

    with col2:
        if len(df) > 0:
            top_companies = df["company"].value_counts().head(10).reset_index()
            top_companies.columns = ["company", "count"]

            fig = px.bar(
                top_companies,
                x="count",
                y="company",
                orientation="h",
                text="count",
                title="Top 10 Employers",
                color="count",
                color_continuous_scale="Plasma"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No company data available")



with tab2:
    salary_data = df[df["salary_display"].notna() & (df["salary_display"] > 0)]

    if len(salary_data) > 0:
        col1, col2 = st.columns(2)

        with col1:
            def filter_outliers(group):
                if len(group) < 5:
                    return group
                Q1 = group.quantile(0.25)
                Q3 = group.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                return group[(group >= lower_bound) & (group <= upper_bound)]


            salary_data_filtered = salary_data.groupby('city')['salary_display'].apply(filter_outliers).reset_index(
                level=0, drop=True)
            salary_data_filtered = salary_data_filtered.to_frame('salary_display').join(salary_data[['city']],
                                                                                        how='left')

            city_salary = salary_data_filtered.groupby("city")["salary_display"].mean().reset_index()
            city_salary.columns = ["city", "avg_salary"]

            city_counts = salary_data["city"].value_counts()

            city_salary["vacancy_count"] = city_salary["city"].map(city_counts)

            min_samples = 5 if selected_region == "Russia" else 3
            city_salary = city_salary[city_salary["vacancy_count"] >= min_samples]

            city_salary = city_salary.sort_values("avg_salary", ascending=False).head(15)

            if len(city_salary) > 0:
                title = f"Top Paying Cities in {selected_region}"
                subtitle = f"Average salary (mean) | Min. {min_samples} vacancies | Outliers filtered"

                fig = px.bar(
                    city_salary,
                    x="avg_salary",
                    y="city",
                    orientation="h",
                    title=f"{title}<br><sup>{subtitle}</sup>",
                    text="avg_salary",
                    color="avg_salary",
                    color_continuous_scale="Viridis",
                    labels={"avg_salary": f"Average Salary ({currency})", "city": "City"}
                )

                fig.update_traces(
                    texttemplate='%{text:,.0f} ₽',
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>' +
                                  f'Average Salary: %{{x:,.0f}} {currency}<br>' +
                                  'Vacancies: %{customdata}<extra></extra>',
                    customdata=city_salary["vacancy_count"]
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("View detailed city statistics"):
                    city_salary_display = city_salary.copy()
                    city_salary_display["avg_salary"] = city_salary_display["avg_salary"].apply(
                        lambda x: f"{x:,.0f} {currency}")
                    city_salary_display.columns = ["City", f"Average Salary ({currency})", "Number of Vacancies"]
                    st.dataframe(city_salary_display, use_container_width=True)

                    st.caption(
                        f"**How it's calculated:** For each city, we sum all salaries and divide by the number of vacancies. Outliers are filtered using the IQR method to avoid distortion from extreme values.")
            else:
                st.info(f"Not enough city data for analysis (need at least {min_samples} vacancies per city)")

        with col2:
            grade_data = salary_data[salary_data["grade"] != "Not specified"]

            available_grades = grade_data["grade"].unique()
            st.caption(f"Available grades in data: {', '.join(sorted(available_grades))}")

            if len(grade_data) > 0:
                grade_order = ["Junior", "Middle", "Senior", "Lead"]
                grade_data["grade"] = pd.Categorical(grade_data["grade"], categories=grade_order, ordered=True)
                grade_data = grade_data.dropna(subset=["grade"])

                fig = px.box(
                    grade_data,
                    x="grade",
                    y="salary_display",
                    title=f"Salary Distribution by Seniority<br><sup>Showing median, quartiles, and outliers</sup>",
                    color="grade",
                    labels={"salary_display": f"Salary ({currency})", "grade": "Seniority"},
                    category_orders={"grade": grade_order}
                )
                fig.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                grade_stats = grade_data.groupby("grade")["salary_display"].agg(['mean', 'median', 'count']).round(0)
                grade_stats = grade_stats.reindex([g for g in grade_order if g in grade_stats.index])

                st.caption("**Statistics by Seniority:**")
                col_a, col_b, col_c = st.columns(3)
                for idx, (grade, row) in enumerate(grade_stats.iterrows()):
                    with [col_a, col_b, col_c][idx % 3]:
                        st.metric(
                            grade,
                            f"{row['mean']:,.0f} {currency}",
                            f"median: {row['median']:,.0f} {currency}",
                            help=f"Based on {int(row['count'])} vacancies"
                        )

                if "Middle" not in available_grades:
                    st.info("'Middle' grade not found in the data for this region")
            else:
                st.info("No seniority data available")

        category_salary = salary_data[salary_data["category"] != "Other IT"].groupby("category")[
            "salary_display"].mean().reset_index()
        category_salary = category_salary.sort_values("salary_display", ascending=True)

        if len(category_salary) > 0:
            fig = px.bar(
                category_salary,
                x="salary_display",
                y="category",
                orientation="h",
                title=f"Average Salary by Role Category<br><sup>Mean salary across all vacancies in category</sup>",
                text="salary_display",
                color="salary_display",
                color_continuous_scale="Plasma",
                labels={"salary_display": f"Average Salary ({currency})", "category": "Category"}
            )
            fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No salary data available for analysis")

with tab3:
    if len(skills_df) > 0:
        col1, col2 = st.columns(2)

        with col1:

            fig = px.bar(
                skills_df.head(15),
                x="count",
                y="skill",
                orientation="h",
                text="count",
                title=f"Most In-Demand Skills - {selected_region}",
                color="count",
                color_continuous_scale="Blues"
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            if selected_region == "Russia":
                text = " ".join(df["title"].dropna().astype(str))

                from wordcloud import WordCloud, STOPWORDS

                stopwords = set(STOPWORDS)
                russian_stopwords = [
                    'работа', 'с', 'в', 'на', 'и', 'для', 'по', 'из', 'от', 'к', 'у', 'о', 'об',
                    'это', 'все', 'всех', 'как', 'так', 'же', 'без', 'до', 'за', 'через',
                    'над', 'под', 'при', 'после', 'более', 'менее', 'который', 'которая',
                    'которые', 'которое', 'этот', 'эта', 'эти', 'такой', 'такая', 'такое',
                    'такие', 'также', 'где', 'когда', 'там', 'здесь', 'вот', 'уже', 'еще',
                    'раз', 'было', 'была', 'были', 'был', 'вакансия', 'компания', 'требуется',
                    'работа с', 'работа в', 'работы', 'работу', 'навыки', 'опыт', 'знание', 'работе'
                ]
                stopwords.update(russian_stopwords)
            else:
                text = " ".join(df["title"].dropna().astype(str))
                stopwords = None

            if len(text) > 100:
                wc = WordCloud(
                    width=800,
                    height=500,
                    background_color="#0E1117",
                    colormap="viridis",
                    max_words=20,
                    stopwords=stopwords,
                    prefer_horizontal=0.7,
                    relative_scaling=0.5
                ).generate(text)

                fig, ax = plt.subplots(figsize=(10, 6))
                fig.patch.set_facecolor('#0E1117')
                ax.set_facecolor('#0E1117')
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")

                if selected_region == "Russia":
                    ax.set_title("Job Titles Word Cloud", fontsize=16, pad=20, color='white')
                else:
                    ax.set_title("Job Titles Word Cloud", fontsize=16, pad=20, color='white')

                st.pyplot(fig)
            else:
                st.info("Not enough text data for word cloud")
    else:
        st.info("No skills data available")

st.markdown("---")
st.header("Key Insights")

if len(df) > 0 and len(skills_df) > 0:
    top_skill = skills_df.iloc[0]["skill"] if len(skills_df) > 0 else "N/A"
    top_category = filtered_core["category"].value_counts().idxmax() if len(filtered_core) > 0 else "N/A"
    top_city = df["city"].value_counts().idxmax() if len(df) > 0 else "N/A"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Top Skill", top_skill.upper())
    with col2:
        st.metric("Top Category", top_category)
    with col3:
        if selected_region=='Global':
            st.metric("Top City for Jobs", 'Chicago')
        else:
            st.metric("Top City for Jobs", top_city)
    with col4:
        st.metric("Total Jobs", f"{len(df):,}")

    if selected_region == "Russia":
        st.markdown(f"""
        ### Russian Market Insights:
        - **Skills data source:** {skills_source}
        - **{top_skill.upper()}** is the most in-demand skill
        - Cities shown require minimum 5 vacancies for reliable statistics
        - **Moscow, St. Petersburg** have most vacancies but not always highest salaries
        - Senior positions earn 2-3x more than Junior roles
        """)
    else:
        st.markdown(f"""
        ### Global Market Insights:
        - **Skills extracted from job titles and companies**
        - **{top_skill.upper()}** dominates global requirements
        - Cities shown require minimum 3 vacancies for reliable statistics
        - **US tech hubs** offer premium compensation
        - Note: 'Middle' grade may not exist in all datasets
        """)
else:
    st.info("No data available for insights")