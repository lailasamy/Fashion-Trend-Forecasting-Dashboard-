import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fashion Trend Intelligence Dashboard", layout="wide")

# --- Title & Description ---
st.title("Fashion Trend Intelligence Dashboard")
st.markdown("""
Welcome! This interactive dashboard helps you discover patterns in real-world fashion product data.
Use the sidebar to filter and visualize fashion trends by year, color, category, gender, and more.

**Why is this useful?**
- **Buyers:** Forecast demand for colors, categories, and genders by season/year.
- **Merchandisers:** Plan inventory and pricing for high- and low-performing styles.
- **Product Managers:** Spot emerging categories and optimize new product launches.

**Try grouping by “year” and “baseColour” or by “gender” and “masterCategory” for actionable retail insights.**
""")

# --- Data Loader ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/styles.csv", on_bad_lines='skip')
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    return df

df = load_data()

# --- Sidebar Filters & Guidance ---
st.sidebar.header("🔎 Explore the Data")
st.sidebar.markdown(
    """
    **How to use:**  
    1. Choose what to group and compare (X, Hue/Color).
    2. Filter by year and gender if you like.
    3. See instant charts and business insights!
    """
)

group1 = st.sidebar.selectbox(
    "Group by (X-axis):",
    ["year", "gender", "masterCategory", "subCategory", "articleType", "baseColour", "season", "usage"],
    index=0
)
group2 = st.sidebar.selectbox(
    "Compare by (color/group):",
    ["None", "year", "gender", "masterCategory", "subCategory", "articleType", "baseColour", "season", "usage"],
    index=5 if group1 == "year" else 0
)
if group2 == group1:
    group2 = "None"

year_min, year_max = df['year'].min(), df['year'].max()
year_range = st.sidebar.slider("Year Range", year_min, year_max, (year_min, year_max))
genders = df['gender'].dropna().unique().tolist()
selected_genders = st.sidebar.multiselect("Filter by Gender", genders, default=genders)

filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
filtered = filtered[filtered['gender'].isin(selected_genders)]

# --- Smart Chart Type Selection ---
def choose_chart_type(x, y, n_bars):
    # Line chart for year or sequential data, else bar/pie
    if x == "year" and (y == "None" or y in ["baseColour", "gender", "masterCategory"]):
        return "line"
    elif n_bars <= 8 and y == "None":
        return "pie"
    else:
        return "bar"

# --- Group and Visualize ---
if group2 == "None":
    counts = filtered.groupby(group1)['id'].count().sort_values(ascending=False)
    chart_type = choose_chart_type(group1, group2, len(counts))
    st.subheader(f"Product Counts by {group1.title()}")
    if chart_type == "line":
        st.line_chart(counts)
    elif chart_type == "pie":
        fig, ax = plt.subplots()
        counts.plot.pie(autopct='%1.1f%%', ax=ax, startangle=90, counterclock=False)
        ax.set_ylabel('')
        st.pyplot(fig)
    else:
        st.bar_chart(counts)
    main_insight = f"The most common {group1} is **{counts.idxmax()}** with {counts.max()} products."
else:
    counts = filtered.groupby([group1, group2])['id'].count().unstack(fill_value=0)
    chart_type = choose_chart_type(group1, group2, counts.shape[1])
    st.subheader(f"Product Counts by {group1.title()} and {group2.title()}")
    if chart_type == "line" and counts.shape[1] <= 8:
        st.line_chart(counts)
    else:
        st.bar_chart(counts)
    # Business insight example
    max_main = counts.sum(axis=1).idxmax()
    main_insight = f"The {group1} with the most diversity across {group2} is **{max_main}**."

# --- Show Table + Insight ---
st.markdown("### 📊 Business Insight")
st.info(main_insight)
with st.expander("Show Data Table for This View"):
    st.dataframe(filtered)

st.markdown("---")
st.caption("For interviewers: This dashboard demonstrates how to extract actionable, visual insights from retail/fashion data for business or product strategy. The code is modular and easily extensible to more advanced analytics (sales, forecasting, pricing, etc).")

# --- Optional: Sample Scenario for Hiring Managers ---
st.markdown("""
---
#### Example: Retail Use Case
- A merchandiser can use this tool to see which **baseColour** is rising in popularity year over year, or if certain **masterCategory** items are favored by a specific gender or season.
- This allows for smarter inventory buys, targeted marketing, and optimized launches—powered by clear, data-driven evidence.
""")
