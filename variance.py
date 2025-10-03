import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Load your dataset
# ---------------------------
# Change file path if needed
df = pd.read_excel("transactions.xlsx")  
# df = pd.read_csv("transactions.csv")

# ---------------------------
# Sort by Total (ascending)
# ---------------------------
df_sorted = df.sort_values(by="Total", ascending=True)

# ---------------------------
# Big Insights at Top
# ---------------------------
st.title("Transaction Insights")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Transactions", len(df_sorted))

with col2:
    st.metric("Lowest Total", f"{df_sorted['Total'].min():,.2f}")

with col3:
    st.metric("Highest Total", f"{df_sorted['Total'].max():,.2f}")

with col4:
    st.metric("Average Total", f"{df_sorted['Total'].mean():,.2f}")

# ---------------------------
# Horizontal Bar Chart
# ---------------------------
st.subheader("Transactions by Total (Ascending)")

fig = px.bar(
    df_sorted,
    x="Total",
    y="Tran No",
    orientation="h",
    text="Total",
    hover_data=["Tran Date", "Particulars", "Discount", "Net Total"],
)

fig.update_traces(marker=dict(color="steelblue", line=dict(width=1, color="white")))
fig.update_layout(
    xaxis_title="Total Value",
    yaxis_title="Transaction No",
    bargap=0.4,
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Show Sorted Table
# ---------------------------
st.subheader("Detailed Transactions Table (Sorted by Total)")
st.dataframe(df_sorted[["Tran No", "Tran Date", "Particulars", "Total", "Discount", "Net Total"]])
