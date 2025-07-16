import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fashion Trend Forecast: See the Future!", layout="wide")

st.title("çFashion Trend Forecaster")
st.markdown("""
Forecast future product trends based on historical data.
Select any filters, then pick a group and value to see both past counts and extrapolated forecasts from the year after your last data point.
""")

@st.cache_data
def load_data():
    df = pd.read_csv("data/styles.csv", on_bad_lines='skip')
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    return df

df = load_data()

# Sidebar: Filters
filter_cols = ['id','gender','masterCategory','subCategory','articleType','baseColour','season','year','usage','productDisplayName']
st.sidebar.header("Filter Data")
filtered = df.copy()
for col in filter_cols:
    vals = sorted(filtered[col].dropna().unique())
    if len(vals) > 30:
        continue  # skip huge fields for UI sanity
    selected = st.sidebar.multiselect(f"{col}:", vals, default=vals)
    filtered = filtered[filtered[col].isin(selected)]

groupby_col = st.sidebar.selectbox(
    "Forecast by:",
    ['gender','masterCategory','subCategory','articleType','baseColour','season','year','usage'],
    index=4
)
possible_values = sorted(filtered[groupby_col].dropna().unique())
selected_value = st.sidebar.selectbox(f"Value for {groupby_col}:", possible_values)

future_years = st.sidebar.slider("Forecast how many years ahead:", 1, 5, 3)

# Historical data for selected value
hist = filtered[filtered[groupby_col] == selected_value].groupby('year')['id'].count().sort_index()
if len(hist) == 0:
    st.error("No data for this selection. Change filters or value.")
    st.stop()
years_available = list(hist.index)

# Forecast always starts after the latest data year
forecast_start = years_available[-1] + 1
forecast_years = [forecast_start + i for i in range(future_years)]

if (hist != 0).sum() > 1:
    x = np.array(hist.index)
    y = np.array(hist.values)
    coeffs = np.polyfit(x, y, deg=1)
    trend = np.poly1d(coeffs)
    forecast = pd.Series([max(0, int(trend(fy))) for fy in forecast_years], index=forecast_years)
else:
    forecast = pd.Series([0] * len(forecast_years), index=forecast_years)

# Combine for Data Table
combined = pd.concat([hist, forecast])
combined.name = 'Product Count'
combined.index.name = 'Year'

# Visualization
st.subheader(f"Forecast for {selected_value} ({groupby_col.title()})")
fig, ax = plt.subplots(figsize=(8,4))
ax.plot(hist.index, hist.values, marker='o', label='Historical', color='#4286f4', linewidth=2)
ax.plot(forecast.index, forecast.values, marker='x', linestyle='dashed', label=f'Forecast ({forecast_start} +)', color='#e6ad28', linewidth=2)
ax.set_xlabel("Year")
ax.set_ylabel("Product Count")
ax.set_title(f"{selected_value} Trend Forecast", fontsize=15, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(axis='y', color="#eee", linewidth=1)
st.pyplot(fig)

st.markdown("#### Data Table (Historical & Forecasted)")
st.dataframe(combined.astype(int))

# Insight
trend_dir = "increasing 📈" if forecast.mean() > hist.mean() else "decreasing 📉"
st.markdown(f"""
**Business Insight:**  
From {forecast_start} onward, '{selected_value}' ({groupby_col}) is projected to be **{trend_dir}**.
""")

st.markdown("---")
st.caption("This dashboard uses linear trends. For advanced analytics, ask about ARIMA/Prophet forecasting.")
