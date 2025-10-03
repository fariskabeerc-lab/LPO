import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Load your dataset
# ---------------------------
df = pd.read_excel("transactions.xlsx")  
# df = pd.read_csv("transactions.csv")

# ---------------------------
# Sort by Total (ascending)
# ---------------------------
df_sorted = df.sort_values(by="Total", ascending=True)

# ---------------------------
# Dashboard Title
# ---------------------------
st.set_page_config(page_title="Transaction Dashboard", layout="wide")
st.title("📊 Transaction Dashboard")

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
# Horizontal Bar Chart (Dark Mode)
# ---------------------------
st.subheader("Transactions by Total (Ascending)")

fig = px.bar(
    df_sorted,
    x="Total",
    y="Tran No",
    orientation="h",
    text="Total",
    hover_data=["Tran Date", "Particulars", "Discount", "Net Total"],
    color="Total",  # Gradient based on Total
    color_continuous_scale="Viridis"
)

fig.update_traces(
    marker=dict(line=dict(width=1, color="black")),
    texttemplate="%{text:,.2f}",
    textposition="outside"
)

fig.update_layout(
    xaxis_title="Total Value",
    yaxis_title="Transaction No",
    bargap=0.25,
    height=600,
    plot_bgcolor="#1e1e1e",  # Dark background
    paper_bgcolor="#1e1e1e",
    font=dict(color="white"),  # White font for dark background
    xaxis=dict(gridcolor="gray"),
    yaxis=dict(gridcolor="gray"),
    coloraxis_colorbar=dict(title="Total")
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Sorted Transactions Table
# ---------------------------
st.subheader("Detailed Transactions Table (Sorted by Total)")

st.dataframe(
    df_sorted[
        ["Tran No", "Tran Date", "Particulars", "Total", "Discount", "Net Total", "Total Qty"]
    ],
    use_container_width=True,
    height=500
)
