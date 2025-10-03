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
# Invoice Analysis: Show only invoice details + particulars
# ---------------------------
if page == "Invoice Analysis":
    st.set_page_config(page_title="Invoice Analysis", layout="wide")
    st.title("📄 Invoice Analysis: Invoices Corresponding to POs")

    # Filter POs: Posted = Checked, Converted = Unchecked
    po_filtered = df[(df["Posted"] == "Checked") & (df["Converted"] == "Unchecked")].copy()

    # Ensure numeric
    po_filtered["Total"] = pd.to_numeric(po_filtered["Total"], errors="coerce")
    invoice_df["Total"] = pd.to_numeric(invoice_df["Total"], errors="coerce")

    # Function to find invoices for a PO
    def find_invoice_for_po(po_row, inv_df):
        matches = inv_df[(inv_df["Particulars"] == po_row["Particulars"]) &
                         (inv_df["Created Date"] > po_row["Created Date"])]
        if not matches.empty:
            return matches[["Tran No", "Created Date", "Total", "Particulars"]]
        else:
            return pd.DataFrame()

    # Collect all invoices corresponding to POs
    all_invoices_list = []
    for _, po_row in po_filtered.iterrows():
        matched_invoices = find_invoice_for_po(po_row, invoice_df)
        if not matched_invoices.empty:
            all_invoices_list.append(matched_invoices)

    if all_invoices_list:
        filtered_invoices = pd.concat(all_invoices_list).drop_duplicates().sort_values(by="Created Date", ascending=False)

        # ---------------------------
        # Summary metrics
        # ---------------------------
        st.subheader("Invoice Metrics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🧾 Total Invoices", len(filtered_invoices))
        with col2:
            st.metric("💳 Total Invoice Value", f"{filtered_invoices['Total'].sum():,.2f}")

        # ---------------------------
        # Display table
        # ---------------------------
        st.subheader("Invoices Corresponding to POs")
        st.dataframe(filtered_invoices, use_container_width=True, height=600)

    else:
        st.info("No invoices found corresponding to the filtered POs.")
