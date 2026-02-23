import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# 1. Page Config
st.set_page_config(page_title="Coffee_EDA", page_icon=":coffee:", layout="wide")
st.title("☕ Afficionado Coffee Roasters EDA")

# 2. File Uploader
fl = st.file_uploader(":file_folder: Upload your file", type="xlsx")

if fl is not None:
    ### --------------------------------------------- Read Data-------------------------------------------###
    df = pd.read_excel(fl)
    st.success("Data Loaded Successfully!")

    ### --------------- -------------------------- DATA PROCESSING -----------------------------------###
    # Convert to datetime and extract hour
    df['transaction_time'] = pd.to_datetime(df['transaction_time'], format='%H:%M:%S').dt.time
    # Helper to get the hour from the time objects
    df['hour'] = df['transaction_time'].apply(lambda x: x.hour)
    # Revenue Calculation
    df['total_bill'] = df['unit_price'] * df['transaction_qty']


    ### ------------------------------------- STREAMLIT DASHBOARD LAYOUT -------------------------------- ###

    # Sidebar for Filters
    st.sidebar.header("Dashboard Filters")
    top_n = st.sidebar.slider("Select number of top items to display", 5, 20, 5)

    # Unique Location for the multiselect
    locations = sorted(df['store_location'].unique())
    selected_locations = st.sidebar.multiselect(
        "Select Locations",
        options=locations,
        default=locations
    )

    # Apply filter to the dataframe
    main_df = df[ (df['store_location'].isin(selected_locations)) ]


    ##------------- Row 1: High-Level Metrics -------------##

    total_revenue = main_df['total_bill'].sum()
    total_qty = main_df['transaction_qty'].sum()
    avg_bill = main_df['total_bill'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Quantity Sold", f"{total_qty:,}")
    col3.metric("Average Transaction", f"${avg_bill:.2f}")

    st.markdown("---")

    ##------------- Row 2: High-Level Metrics -------------##

    st.header("📦 Product Inventory & Performance")

    # 1. Aggregate for the TABLE (Includes Unit Price)
    product_stats = main_df.groupby(['product_category', 'product_type', 'product_detail', 'unit_price']).agg({
        'transaction_qty': 'sum',
        'total_bill': 'sum'
    }).reset_index()
    product_stats.columns = ['Category', 'Type', 'Product Name', 'Unit Price', 'Units Sold', 'Total Revenue']
    # 1. Create a "Display Name" that includes the price to distinguish rows
    # This prevents Plotly from overlapping bars with the same name
    product_stats['Display Name'] = (
            product_stats['Product Name'] +
            " ($" + product_stats['Unit Price'].astype(str) + ")"
    )

    # 2. Sorting (keep your existing sort)
    product_stats = product_stats.sort_values(by='Units Sold', ascending=False)

    # --- Layout: Top vs Bottom ---
    col_top, col_bottom = st.columns(2)

    with col_top:
        st.subheader("🏆 Top 5 Performers (Volume)")
        top_5 = product_stats.head(5)

        fig_top = px.bar(
            top_5,
            x='Units Sold',
            y='Display Name',  # Use the unique display name here
            orientation='h',
            color_discrete_sequence=['#85BB65'],
            text='Units Sold',
            height=450
        )
        fig_top.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)

    with col_bottom:
        st.subheader("⚠️ Bottom 5 Performers (Volume)")
        # Sort ascending for the bottom chart
        bottom_5 = product_stats.tail(5).sort_values(by='Units Sold', ascending=True)

        fig_bottom = px.bar(
            bottom_5,
            x='Units Sold',
            y='Display Name',  # Use the unique display name here
            orientation='h',
            color_discrete_sequence=['#FF4B33'],
            text='Units Sold',
            height=450
        )
        fig_bottom.update_layout(showlegend=False, yaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig_bottom, use_container_width=True)

    # 3. Full Ranking Table (Stays the same - very clean)
    with st.expander("📄 View Full Product Ranking List"):
        # Drop the helper column before showing the table to keep it professional
        table_df = product_stats.drop(columns=['Display Name'])

        styled_df = table_df.style.background_gradient(
            subset=['Units Sold'], cmap='Greens'
        ).background_gradient(
            subset=['Total Revenue'], cmap='YlOrBr'
        ).background_gradient(
            subset=['Unit Price'], cmap='YlOrBr'
        ).format({
            'Total Revenue': '${:,.2f}',
            'Units Sold': '{:,}',
            'Unit Price': '${:,.2f}'
        })
        st.dataframe(styled_df, use_container_width=True)

    st.markdown("---")

    ##------ Row 3: Revenue Analysis (Your Aggregations) ------##

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader(f"Top {top_n} Categories by Revenue")
        category_revenue = main_df.groupby('product_category')['total_bill'].sum().reset_index()
        category_revenue = category_revenue.sort_values(by='total_bill', ascending=False)

        # Separate Top N from the rest
        top_slice = category_revenue.head(top_n)
        others_slice = category_revenue.iloc[top_n:]

        # Create 'Other' row if there are items remaining
        if not others_slice.empty:
            others_row = pd.DataFrame({
                'product_category': ['Other Products'],
                'total_bill': [others_slice['total_bill'].sum()]
            })
            plot_df = pd.concat([top_slice, others_row])
        else:
            plot_df = top_slice

        fig_type = px.pie(plot_df,
                          values='total_bill',
                          names='product_category',
                          hole=0.4,
                          color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig_type, use_container_width=True)

    with right_col:
        st.subheader("Unique Product Types by Category")

        # Unique categories for the multiselect
        categories = sorted(main_df['product_category'].unique())
        # Use selectbox for a single choice
        selected_categories = st.selectbox(
            "Select a Category to view details:",
            options=categories[2]
        )

        main_df_1 = main_df[main_df['product_category'] == selected_categories]

        # Grouping every unique type in the selected categories
        type_grouped = main_df_1.groupby(['product_category', 'product_type'])['total_bill'].sum().reset_index()
        type_grouped = type_grouped.sort_values(['product_category', 'total_bill'], ascending=[True, False])

        # Bar chart showing ALL unique types
        fig_type_bar = px.bar(
            type_grouped,
            x='total_bill',
            y='product_type',  # Focus on types
            color='total_bill',
            color_continuous_scale='Tealgrn',# Grouped by category color
            orientation='h',
            labels={'total_bill': 'Revenue ($)', 'product_type': 'Product Type'},
            height=300  # Height adjusted to fit many types
        )

        fig_type_bar.update_layout(
            showlegend=False,  # Removes the legend
            coloraxis_showscale=False,  # Removes the color bar on the right
            margin=dict(l=20, r=20, t=30, b=20),
            height=300,
            yaxis = {'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig_type_bar, use_container_width=True)

    st.markdown("---")

    ##------------ Row 4: Hourly Peak Analysis -------------##

    st.subheader("Peak Hour Analysis by Category")

        # 1. Local Multi-select for Categories
    selected_hour_cats = st.multiselect(
        "Select Categories to compare hourly trends:",
        options=category_revenue,
        default=category_revenue[:3]  # Defaulting to first 3 to keep it clean
    )

        # 2. Filter the data
    hour_df = main_df[main_df['product_category'].isin(selected_hour_cats)]

    if not hour_df.empty:
        # 3. Aggregate by Hour AND Category
        hourly_cat_rev = hour_df.groupby(['hour', 'product_category'])['transaction_qty'].sum().reset_index()

        # 4. Create the Multi-Line Chart
        fig_hour = px.line(
            hourly_cat_rev,
            x='hour',
            y='transaction_qty',
            color='product_category',  # This creates the separate lines
            markers=True,
            line_shape='spline',  # Makes the lines smooth/curvy
            labels={'transaction_qty': 'Total Sales', 'hour': 'Hour of Day (24h)', 'product_category': 'Category'},
            color_discrete_sequence=px.colors.qualitative.Bold
        )

        # 5. Clean up X-axis to show every hour
        fig_hour.update_layout(
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            hovermode="x unified"  # Shows all category values in one tooltip when hovering
        )

        st.plotly_chart(fig_hour, use_container_width=True)
    else:
        st.info("Select categories above to visualize hourly trends.")

    st.markdown("---")

    ##------------------- Row 5: Revenue Concentration & Menu Balance & Enginnering ------------------##

    st.header("⚖️ Revenue Concentration & Menu Balance")

    # 1. Prepare Data for Pareto

    product_stats['Display Name'] = (
            product_stats['Product Name'] +
            " ($" + product_stats['Unit Price'].astype(str) + ")"
    )

    pareto_df = product_stats.groupby('Display Name')['Total Revenue'].sum().reset_index()
    pareto_df = pareto_df.sort_values(by='Total Revenue', ascending=False)

    # 2. Calculate Cumulative Percentages
    pareto_df['Cumulative Revenue'] = pareto_df['Total Revenue'].cumsum()
    total_rev = pareto_df['Total Revenue'].sum()
    pareto_df['Cumulative %'] = (pareto_df['Cumulative Revenue'] / total_rev) * 100


    # 3. Categorize Products
    def categorize_pareto(pct):
        if pct <= 80: return "Revenue Anchor (Top 80%)"
        return "Long-tail (Remaining 20%)"


    pareto_df['Classification'] = pareto_df['Cumulative %'].apply(categorize_pareto)

    # --- Visualizing Concentration ---
    # Calculate metrics for the summary
    anchors_count = len(pareto_df[pareto_df['Classification'] == "Revenue Anchor (Top 80%)"])
    total_products = len(pareto_df)
    anchor_ratio = (anchors_count / total_products) * 100

    fig_tree = px.treemap(
        pareto_df,
        path=['Classification', 'Display Name'],
        values='Total Revenue',
        color='Classification',
        color_discrete_map={
            "Revenue Anchor (Top 80%)": "#2E7D32",  # Deeper green for better readability
            "Long-tail (Remaining 20%)": "#424242"  # Dark grey to signal "secondary importance"
        }
    )

    fig_tree.update_traces(
        textinfo="label+value",
        texttemplate="<b>%{label}</b><br>$%{value:,.0f}",  # Bold name and formatted currency
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<br>Contribution: %{percentParent:.1%}",
        marker_line_width=2,
        marker_line_color="#121212"  # Sharp borders between boxes
    )

    fig_tree.update_layout(
        margin=dict(t=30, l=10, r=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background to match Streamlit
        plot_bgcolor='rgba(0,0,0,0)',
        height=600
    )

    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    col1.metric("Revenue Anchors", f"{anchors_count} Products")
    col2.metric("Concentration Ratio", f"{anchor_ratio:.1f}%")

    st.markdown("---")

    # Risk Assessment
    if anchor_ratio < 15:
        st.error("⚠️ **High Risk**: Revenue is too concentrated in very few products.")
    elif anchor_ratio > 25:
        st.success("✅ **Balanced**: Revenue is healthy and spread across the menu.")
    else:
        st.warning("⚖️ **Moderate**: Standard 80/20 distribution.")

    st.markdown("---")

    # 4. Long-tail Detail
    with st.expander("🔍 Identify Long-tail Products (Candidates for Removal)"):
        long_tail = pareto_df[pareto_df['Classification'] == "Long-tail (Remaining 20%)"]
        st.write(f"These {len(long_tail)} products contribute to only 20% of your total revenue.")
        st.dataframe(long_tail[['Display Name', 'Total Revenue', 'Cumulative %']], use_container_width=True)

    st.markdown("---")

    st.header("🎯 Menu Engineering: Popularity vs. Revenue")

    # 1. Calculate Averages for the Quadrant Lines
    avg_units = product_stats['Units Sold'].mean()
    avg_rev = product_stats['Total Revenue'].mean()

    # 2. Create the Scatter Plot
    fig_scatter = px.scatter(
        product_stats,
        x='Units Sold',
        y='Total Revenue',
        color='Type',
        size='Total Revenue',
        hover_name='Display Name',
        template='plotly_dark',
        color_discrete_sequence=px.colors.qualitative.Dark2
    )

    # 3. Add Quadrant Lines
    fig_scatter.add_vline(x=avg_units, line_dash="dash", line_color="rgba(255,255,255,0.5)")
    fig_scatter.add_hline(y=avg_rev, line_dash="dash", line_color="rgba(255,255,255,0.5)")

    # 4. Add Quadrant Labels
    quadrant_labels = [
        dict(x=product_stats['Units Sold'].max() * 0.8, y=product_stats['Total Revenue'].max() * 0.9, text="⭐ STARS"),
        dict(x=product_stats['Units Sold'].min() * 1.2, y=product_stats['Total Revenue'].max() * 0.9, text="🧩 PUZZLES"),
        dict(x=product_stats['Units Sold'].max() * 0.8, y=product_stats['Total Revenue'].min() * 1.2,
             text="🐎 WORKHORSES"),
        dict(x=-300, y=2500, text="🐕 DOGS")
    ]

    for label in quadrant_labels:
        fig_scatter.add_annotation(
            x=label['x'], y=label['y'],
            text=label['text'],
            showarrow=False,
            font=dict(size=16, color="white", family="Arial Black"),
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="white",
            borderwidth=1
        )

    fig_scatter.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='White')))
    fig_scatter.update_layout(
        height=600,
        xaxis_title="Popularity (Units Sold)",
        yaxis_title="Profitability (Total Revenue $)",
        hovermode='closest'
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

else:
    st.info("Please upload an Excel file to generate the dashboard.")
