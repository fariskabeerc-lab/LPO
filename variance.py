import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Load datasets
# ---------------------------
df = pd.read_excel("transactions.xlsx")
invoice_df = pd.read_excel("invoice_list.xlsx")

# Clean column names
df.columns = df.columns.str.strip().str.replace("\n", "").str.replace("\r", "")
invoice_df.columns = invoice_df.columns.str.strip().str.replace("\n", "").str.replace("\r", "")

# ---------------------------
# Sidebar Page Selection
# ---------------------------
page = st.sidebar.radio("📑 Select Page", ["Transactions Dashboard", "Invoice Analysis"])

# ---------------------------
# Transactions Dashboard Page
# ---------------------------
if page == "Transactions Dashboard":
    st.set_page_config(page_title="Transaction Dashboard", layout="wide")
    st.title("📊 Transaction Dashboard")

    # Sidebar Filters
    st.sidebar.header("Filters")

    po_status = st.sidebar.selectbox(
        "PO Status",
        options=["All"] + sorted(df["Posted"].dropna().unique().tolist()),
        index=0
    )

    converted_status = st.sidebar.selectbox(
        "Converted Status",
        options=["All"] + sorted(df["Converted"].dropna().unique().tolist()),
        index=0
    )

    # Apply filters
    df_filtered = df.copy()
    if po_status != "All":
        df_filtered = df_filtered[df_filtered["Posted"] == po_status]
    if converted_status != "All":
        df_filtered = df_filtered[df_filtered["Converted"] == converted_status]

    # Metrics
    total_sum_filtered = df_filtered["Total"].sum()
    total_count_filtered = len(df_filtered)
    total_qty_filtered = df_filtered["Total Qty"].sum() if "Total Qty" in df_filtered.columns else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Sum of Total", f"{total_sum_filtered:,.2f}")
    with col2:
        st.metric("🧾 Number of Transactions", total_count_filtered)
    with col3:
        st.metric("📦 Total Quantity", f"{total_qty_filtered:,.0f}")

    # Top 30 transactions
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

    # Full table
    st.subheader("Filtered Transactions Table")
    st.dataframe(
        df_filtered[
            ["Tran No", "Tran Date", "Particulars", "Total", "Discount", "Net Total", "Total Qty", "Posted", "Converted"]
        ],
        use_container_width=True,
        height=600
    )

# ---------------------------
# Invoice Analysis Page
# ---------------------------
if page == "Invoice Analysis":
    st.set_page_config(page_title="Invoice Analysis", layout="wide")
    st.title("📄 Invoice Analysis")

    # Convert date columns to datetime
    df["Tran Date"] = pd.to_datetime(df["Tran Date"])
    invoice_df["Invoice Print Date"] = pd.to_datetime(invoice_df["Invoice Print Date"])

    # Merge invoice with transactions on 'Particulars' (change if needed)
    merged_df = pd.merge(
        invoice_df,
        df,
        on=["Particulars"],  # change to correct key if needed (Supplier or Reference)
        suffixes=("_inv", "_po")
    )

    # Filter: PO checked, Converted unchecked, Invoice after PO date
    filtered_invoice = merged_df[
        (merged_df["Posted_po"] == "Checked") &
        (merged_df["Converted_po"] == "Unchecked") &
        (merged_df["Invoice Print Date"] > merged_df["Tran Date_po"])
    ]

    st.subheader("Invoices Received after PO but Not Yet Converted")
    st.dataframe(
        filtered_invoice[
            ["Tran No_po", "Tran Date_po", "Particulars", "Total_po", 
             "Invoice Print Date", "Total_inv", "Net Total_po", "Remark"]
        ],
        use_container_width=True,
        height=600
    )
