import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Load dataset
# ---------------------------
df = pd.read_excel("transactions.xlsx")
df.columns = df.columns.str.strip().str.replace("\n", "").str.replace("\r", "")

# ---------------------------
# Dashboard Title
# ---------------------------
st.set_page_config(page_title="Transaction Dashboard", layout="wide")
st.title("📊 Transaction Dashboard")

# ---------------------------
# Sidebar Filters (Separate with All option)
# ---------------------------
st.sidebar.header("Filters")

# PO Status filter
po_status = st.sidebar.selectbox(
    "PO Status",
    options=["All"] + sorted(df["Posted"].dropna().unique().tolist()),
    index=0
)

# Converted Status filter
converted_status = st.sidebar.selectbox(
    "Converted Status",
    options=["All"] + sorted(df["Converted"].dropna().unique().tolist()),
    index=0
)

# ---------------------------
# Apply filters
# ---------------------------
df_filtered = df.copy()

if po_status != "All":
    df_filtered = df_filtered[df_filtered["Posted"] == po_status]

if converted_status != "All":
    df_filtered = df_filtered[df_filtered["Converted"] == converted_status]

# ---------------------------
# Metrics based on full dataset
# ---------------------------
total_sum_all = df["Total"].sum()
total_count_all = len(df)
total_qty_all = df["Total Qty"].sum() if "Total Qty" in df.columns else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Sum of Total", f"{total_sum_all:,.2f}")
with col2:
    st.metric("🧾 Number of Transactions", total_count_all)
with col3:
    st.metric("📦 Total Quantity", f"{total_qty_all:,.0f}")

# ---------------------------
# Top 30 transactions by Total for graph
# ---------------------------
df_top30 = df_filtered.sort_values(by="Total", ascending=False).head(30)

st.subheader("Top 30 Transactions by Total Value (Filtered)")

fig = px.bar(
    df_top30,
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
    yaxis=dict(autorange="reversed"),
    xaxis=dict(gridcolor="gray"),
    height=800,
    plot_bgcolor="#1e1e1e",
    paper_bgcolor="#1e1e1e",
    font=dict(color="white")
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Full Transactions Table
# ---------------------------
st.subheader("Filtered Transactions Table")

st.dataframe(
    df_filtered[
        ["Tran No", "Tran Date", "Particulars", "Total", "Discount", "Net Total", "Total Qty", "Posted", "Converted"]
    ],
    use_container_width=True,
    height=600
)
