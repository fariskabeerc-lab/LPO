import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Load dataset
# ---------------------------
df = pd.read_excel("transactions.xlsx")  
# df = pd.read_csv("transactions.csv")

# ---------------------------
# Top 30 transactions by Total
# ---------------------------
df_sorted = df.sort_values(by="Total", ascending=False).head(30)

# ---------------------------
# Dashboard Title
# ---------------------------
st.set_page_config(page_title="Transaction Dashboard", layout="wide")
st.title("📊 Transaction Dashboard - Top 30 Transactions")

# ---------------------------
# Key Metrics
# ---------------------------
total_sum = df_sorted["Total"].sum()
total_count = len(df_sorted)
total_qty = df_sorted["Total Qty"].sum() if "Total Qty" in df_sorted.columns else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Sum of Total", f"{total_sum:,.2f}")

with col2:
    st.metric("🧾 Number of Transactions", total_count)

with col3:
    st.metric("📦 Total Quantity", f"{total_qty:,.0f}")

# ---------------------------
# Horizontal Bar Chart
# ---------------------------
st.subheader("Top 30 Transactions by Total Value")

fig = px.bar(
    df_sorted,
    x="Total",
    y="Particulars",
    orientation="h",
    text="Total",
    hover_data=["Tran No", "Tran Date", "Discount", "Net Total"],
    color_discrete_sequence=["teal"]
)

fig.update_traces(
    texttemplate="%{text:,.2f}",
    textposition="outside",
    marker=dict(line=dict(width=1, color="white"))
)

fig.update_layout(
    xaxis_title="Total Value",
    yaxis_title="Particulars",
    yaxis=dict(
        autorange="reversed",  # Largest total on top
        gridcolor="gray"
    ),
    xaxis=dict(gridcolor="gray"),
    height=800,
    plot_bgcolor="#1e1e1e",
    paper_bgcolor="#1e1e1e",
    font=dict(color="white")
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Top 30 Transactions Table
# ---------------------------
st.subheader("Top 30 Detailed Transactions Table")

st.dataframe(
    df_sorted[
        ["Tran No", "Tran Date", "Particulars", "Total", "Discount", "Net Total", "Total Qty"]
    ],
    use_container_width=True,
    height=500
)
