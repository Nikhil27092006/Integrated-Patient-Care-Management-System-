import re

# Read the file
with open('pages/admin_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the old and new sections
old_section = '''        else:
            st.info("No appointments found.")

    # ════════════════════════════════════════════════════════════════════════════
    # PAGE: AI CARE
    # ════════════════════════════════════════════════════════════════════════════
    elif page == "ai_care":'''

new_section = '''        else:
            st.info("No appointments found.")

    # PAGE: MEDICINES
    elif page == "medicines":
        page_header("💊 Medicines", "Manage pharmacy inventory")
        medicines = db.fetch_all_medicines()

        col_search1, col_search2, col_search3 = st.columns([2, 1, 1])
        with col_search1:
            search_term = st.text_input("Search medicines", placeholder="e.g., Paracetamol...")
        with col_search2:
            category_filter = st.selectbox("Category", ["All"] + list(set(m.get("category", "General") for m in medicines)))
        with col_search3:
            stock_filter = st.selectbox("Stock", ["All", "In Stock", "Low Stock", "Out of Stock"])

        filtered_meds = medicines
        if search_term:
            filtered_meds = [m for m in filtered_meds if search_term.lower() in m.get("name", "").lower()]
        if category_filter != "All":
            filtered_meds = [m for m in filtered_meds if m.get("category") == category_filter]
        if stock_filter == "In Stock":
            filtered_meds = [m for m in filtered_meds if m.get("stock_quantity", 0) > 10]
        elif stock_filter == "Low Stock":
            filtered_meds = [m for m in filtered_meds if 0 < m.get("stock_quantity", 0) <= 10]
        elif stock_filter == "Out of Stock":
            filtered_meds = [m for m in filtered_meds if m.get("stock_quantity", 0) == 0]

        total_meds = len(filtered_meds)
        total_value = sum(m.get("unit_price", 0) * m.get("stock_quantity", 0) for m in filtered_meds)
        low_stock = sum(1 for m in filtered_meds if 0 < m.get("stock_quantity", 0) <= 10)

        stat_cards([
            ("💊", "Medicines", str(total_meds)),
            ("₹", "Total Value", f"₹{total_value:,.0f}"),
            ("⚠️", "Low Stock", str(low_stock)),
        ])

        st.markdown("---")

        with st.expander("➕ Add New Medicine", expanded=False):
            col_new1, col_new2, col_new3, col_new4 = st.columns(4)
            with col_new1:
                new_name = st.text_input("Medicine Name")
            with col_new2:
                new_category = st.selectbox("Category", ["General", "Pain Relief", "Antibiotics", "Cardiac", "Diabetes", "Respiratory", "Gastrointestinal", "Neurological", "Dermatology", "Other"])
            with col_new3:
                new_unit = st.selectbox("Unit", ["tablet", "capsule", "syrup", "injection", "cream", "ointment", "drops", "inhaler"])
            with col_new4:
                new_price = st.number_input("Price (₹)", min_value=0.0, step=1.0)

            col_new5, col_new6 = st.columns(2)
            with col_new5:
                new_stock = st.number_input("Stock Quantity", min_value=0, step=10)
            with col_new6:
                new_expiry = st.date_input("Expiry Date (optional)")

            if st.button("Add Medicine", type="primary"):
                if new_name:
                    success, msg = db.add_medicine(new_name, new_category, new_unit, new_price, new_stock, str(new_expiry) if new_expiry else None)
                    if success:
                        st.success("Medicine added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error: {msg}")
                else:
                    st.warning("Please enter medicine name")

        st.markdown(f"**Found {len(filtered_meds)} medicines**")

        if not filtered_meds:
            st.warning("No medicines found matching your criteria.")
        else:
            for i in range(0, len(filtered_meds), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(filtered_meds):
                        m = filtered_meds[i + j]
                        stock = m.get("stock_quantity", 0)
                        stock_color = "#10b981" if stock > 50 else "#f59e0b" if stock > 10 else "#ef4444"
                        stock_icon = "✅" if stock > 50 else "⚠️" if stock > 10 else "❌"
                        with col:
                            st.markdown(f"""
                            <div style="background: linear-gradient(145deg, rgba(30,41,59,0.9), rgba(15,23,42,0.8));
                                        border: 1px solid rgba(139,92,246,0.2); border-radius: 14px;
                                        padding: 1rem; margin-bottom: 0.8rem;">
                                <div style="font-size: 1rem; font-weight: 700; color: #fff; margin-bottom: 0.3rem;">
                                    💊 {m.get('name', 'Unknown')}
                                </div>
                                <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.5rem;">
                                    {m.get('category', 'General')} | {m.get('unit', 'tablet')}
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 0.9rem; font-weight: 600; color: #0ea5e9;">₹{m.get('unit_price', 0)}</span>
                                    <span style="font-size: 0.8rem; font-weight: 700; color: {stock_color};">
                                        {stock_icon} {stock}
                                    </span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

    elif page == "ai_care":'''

# Replace
if old_section in content:
    content = content.replace(old_section, new_section)
    with open('pages/admin_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Admin dashboard updated!")
else:
    print("ERROR: Could not find the section to replace")
    # Try to find something similar
    if 'elif page == "ai_care":' in content:
        print("Found 'elif page == \"ai_care\":' in file")
