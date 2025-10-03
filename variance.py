import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# Load datasets
# ---------------------------
df = pd.read_excel("transactions.xlsx")      # PO dataset
invoice_df = pd.read_excel("invoice_list.xlsx")  # Invoice dataset

# ---------------------------
# Clean column names
# ---------------------------
df.columns = df.columns.str.strip().str.replace("\n", "").str.replace("\r", "")
invoice_df.columns = invoice_df.columns.str.strip().str.replace("\n", "").str.replace("\r", "")

# ---------------------------
# Sidebar Page Selection
# ---------------------------
page = st.sidebar.radio("📑 Select Page", ["Transactions Dashboard", "Invoice Analysis"])

# ---------------------------
# Transactions Dashboard
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

    # ---------------------------
    # Key Metrics
    # ---------------------------
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

    st.markdown(f"**Total Transactions in Dataset:** {len(df)} | **Filtered Transactions:** {total_count_filtered}")

    # ---------------------------
    # Top 30 transactions graph
    # ---------------------------
    df_top30 = df_filtered.sort_values(by="Total", ascending=False).head(30)
    st.subheader("Top 30 Transactions by Total Value")
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
    # Full table
    # ---------------------------
    st.subheader("Filtered Transactions Table")
    st.dataframe(
        df_filtered[["Tran No", "Tran Date", "Particulars", "Total", "Discount", "Net Total", "Total Qty", "Posted", "Converted"]],
        use_container_width=True,
        height=600
    )

# ---------------------------
# Invoice Analysis (PO details only, invoices received after PO)
# ---------------------------
if page == "Invoice Analysis":
    st.set_page_config(page_title="PO Details with Received Invoices", layout="wide")
    st.title("📄 PO Details with Invoices Received After PO Creation")

    # Filter POs: Posted = Checked, Converted = Unchecked
    po_filtered = df[(df["Posted"] == "Checked") & (df["Converted"] == "Unchecked")].copy()

    # Ensure numeric columns
    po_filtered["Total"] = pd.to_numeric(po_filtered["Total"], errors="coerce")
    invoice_df["Total"] = pd.to_numeric(invoice_df["Total"], errors="coerce")

    # Keep only POs that have invoices with same Particulars and Created Date after PO
    def po_has_invoice_after_creation(po_row, inv_df):
        matches = inv_df[(inv_df["Particulars"] == po_row["Particulars"]) & 
                         (inv_df["Created Date"] > po_row["Created Date"])]
        return not matches.empty

    # Apply filter
    po_with_invoice = po_filtered[po_filtered.apply(lambda r: po_has_invoice_after_creation(r, invoice_df), axis=1)]

    # Display PO details only
    display_cols = ["Tran No", "Particulars", "Total", "Created Date", "Posted", "Converted"]
    st.subheader("PO Details for which Invoices Were Received After Creation")
    st.dataframe(
        po_with_invoice[display_cols].sort_values(by="Created Date", ascending=False),
        use_container_width=True,
        height=600
    )
