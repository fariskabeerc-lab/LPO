import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Load your dataset
# ---------------------------
# Change this to your actual dataset file
# Example: Excel or CSV
df = pd.read_excel("transactions.xlsx")  
# df = pd.read_csv("transactions.csv")

# ---------------------------
# Filter only Unchecked (Converted = 0 / False / No / empty)
# ---------------------------
unchecked_df = df[
    (df["Converted"] == 0) | 
    (df["Converted"] == "No") | 
    (df["Converted"].isna())
]

# ---------------------------
# Sort by Total ascending
# ---------------------------
unchecked_df = unchecked_df.sort_values(by="Total", ascending=True)

# ---------------------------
# Page Title
# ---------------------------
st.title("Unchecked Transactions Dashboard")

# ---------------------------
# Quick Insights
# ---------------------------
st.subheader("Key Insights on Unchecked Transactions")

st.markdown(f"""
- **Total unchecked transactions:** {len(unchecked_df)}  
- **Lowest transaction value:** {unchecked_df['Total'].min()}  
- **Highest transaction value:** {unchecked_df['Total'].max()}  
- **Average transaction value:** {round(unchecked_df['Total'].mean(), 2)}  
""")

# ---------------------------
# Horizontal Bar Chart
# ---------------------------
fig = px.bar(
    unchecked_df,
    x="Total",
    y="Tran No",
    orientation="h",
    text="Total",
    hover_data=["Tran Date", "Particulars", "Discount", "Net Total"],
)

fig.update_traces(marker=dict(color="steelblue", line=dict(width=1, color="white")))
fig.update_layout(
    title="Unchecked Transactions by Total",
    xaxis_title="Total Value",
    yaxis_title="Transaction No",
    bargap=0.4,
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Show Detailed Table
# ---------------------------
st.subheader("Detailed Table")
st.dataframe(unchecked_df[["Tran No", "Tran Date", "Particulars", "Total", "Discount", "Net Total"]])
