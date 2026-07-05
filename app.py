import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="The Enterprise Economics Engine",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed" # Hide sidebar by default
)

# ==========================================
# UTILITY: DOCUMENTATION LOADER
# ==========================================
def load_docs(file_names):
    """Safely loads and concatenates markdown files."""
    content = ""
    for file_name in file_names:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                content += f.read() + "\n\n---\n\n"
        else:
            content += f"> ⚠️ **File Not Found:** Could not locate `{file_name}` in the root directory.\n\n"
    return content

# ==========================================
# MODULE 1: OPERATING LEVERAGE SIMULATOR
# ==========================================
def render_operating_leverage():
    st.header("1. The Operating Leverage Simulator")
    
    # Nested tabs for Engine vs Theory
    tab_engine, tab_docs = st.tabs(["⚙️ Simulation Engine", "📚 Financial Theory"])
    
    with tab_engine:
        with st.expander("⚙️ Simulation Parameters", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                revenue = st.number_input("Initial Revenue (₹)", min_value=100.0, value=1000.0, step=100.0)
                gm_pct = st.slider("Gross Margin (%)", 10.0, 100.0, 60.0, 1.0) / 100
            with col2:
                base_gross_profit = revenue * gm_pct
                total_opex = st.number_input("Total Operating Expenses (₹)", min_value=0.0, value=float(base_gross_profit * 0.5), step=10.0)
                fixed_share_pct = st.slider("Fixed Share of OpEx (%)", 0.0, 100.0, 50.0, 1.0) / 100
            with col3:
                rev_shift_pct = st.slider("Revenue Change Shift (%)", -50.0, 100.0, 20.0, 5.0) / 100

        fixed_costs = total_opex * fixed_share_pct
        variable_cost_rate = (total_opex - fixed_costs) / revenue if revenue > 0 else 0
        base_ebit = base_gross_profit - total_opex
        
        shifted_revenue = revenue * (1 + rev_shift_pct)
        shifted_ebit = (shifted_revenue * gm_pct) - fixed_costs - (shifted_revenue * variable_cost_rate)
        dol = base_gross_profit / base_ebit if base_ebit != 0 else np.nan

        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Base EBIT", f"₹{base_ebit:,.2f}")
        m2.metric("Shifted EBIT", f"₹{shifted_ebit:,.2f}", f"{((shifted_ebit/base_ebit)-1)*100:.1f}%" if base_ebit > 0 else None)
        m3.metric("Degree of Operating Leverage", f"{dol:.2f}x" if not np.isnan(dol) else "N/A")
        
        if dol > 3:
            st.info("💡 **High Operating Leverage:** Operating leverage amplifies both success and failure. Because fixed costs dominate, once they are covered, additional revenue requires comparatively little incremental expenditure.")
        elif dol > 0 and dol <= 3:
            st.success("💡 **Moderate/Low Operating Leverage:** The business must incur additional expenses on almost every incremental sale. Profit grows modestly alongside revenue, offering stability but less explosive upside.")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Revenue', x=['Base State', 'Shifted State'], y=[revenue, shifted_revenue], marker_color='#2E86AB'))
        fig.add_trace(go.Bar(name='EBIT', x=['Base State', 'Shifted State'], y=[base_ebit, shifted_ebit], marker_color='#F24236'))
        fig.update_layout(barmode='group', margin=dict(t=40, b=0, l=0, r=0), height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    with tab_docs:
        # Loading both Gross Profit and Operating Profit theses here
        st.markdown(load_docs([
            "Gross Profit — The Economics of Competitive Advantage.md", 
            "Operating Profit — The Economics of Operating Leverage.md"
        ]))

# ==========================================
# MODULE 2: WORKING CAPITAL & CCC
# ==========================================
def render_working_capital():
    st.header("2. Working Capital & Cash Conversion")
    
    tab_engine, tab_docs = st.tabs(["⚙️ Simulation Engine", "📚 Financial Theory"])
    
    with tab_engine:
        with st.expander("⚙️ Operating Cycle Assumptions", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            dso = col1.number_input("Days Sales (DSO)", 0, value=45)
            dio = col2.number_input("Days Inventory (DIO)", 0, value=60)
            dpo = col3.number_input("Days Payables (DPO)", 0, value=30)
            target_rev_growth = col4.number_input("Target Rev Growth (₹)", 0.0, value=1000.0, step=100.0)

        ccc = dso + dio - dpo
        wc_intensity = ccc / 365.0
        hidden_cash_required = target_rev_growth * wc_intensity
        
        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Cash Conversion Cycle (CCC)", f"{ccc} Days")
        m2.metric("Hidden Cash Funding Required", f"₹{hidden_cash_required:,.2f}")
        
        if ccc > 0:
            st.warning(f"⚠️ **The Growth Trap:** A CCC of {ccc} days indicates growth itself becomes a financing challenge. To grow revenue by ₹{target_rev_growth:,.0f}, you must permanently trap ₹{hidden_cash_required:,.2f} in working capital.")
        elif ccc <= 0:
            st.success(f"🔥 **Supplier Financed Growth:** A negative cash conversion cycle is a competitive advantage. Your suppliers finance your inventory while customers provide cash before supplier payments become due.")
            
    with tab_docs:
        st.markdown(load_docs(["Working Capital — The Economics of Cash.md"]))

# ==========================================
# MODULE 3: CAPITAL STRUCTURE & RETURNS
# ==========================================
def render_capital_structure():
    st.header("3. Capital Structure & Returns")
    
    tab_engine, tab_docs = st.tabs(["⚙️ Simulation Engine", "📚 Financial Theory"])
    
    with tab_engine:
        with st.expander("⚙️ Financing Parameters", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                invested_capital = st.number_input("Total Invested Capital (₹)", 100.0, value=1000.0, step=100.0)
                ebit = st.number_input("Operating Earnings (EBIT) (₹)", -500.0, value=150.0, step=10.0)
            with col2:
                debt_ratio = st.slider("Debt Ratio (%)", 0.0, 100.0, 40.0, 5.0) / 100
                cost_of_debt = st.slider("Pre-Tax Cost of Debt (%)", 1.0, 20.0, 8.0, 0.5) / 100

        debt_amount = invested_capital * debt_ratio
        equity_amount = invested_capital - debt_amount
        interest_expense = debt_amount * cost_of_debt
        
        net_income = (ebit - interest_expense) * 0.70 
        nopat = ebit * 0.70
        
        roic = nopat / invested_capital if invested_capital > 0 else 0
        roe = net_income / equity_amount if equity_amount > 0 else 0
        interest_coverage = ebit / interest_expense if interest_expense > 0 else np.inf
        
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("ROIC (Operating Economics)", f"{roic*100:.1f}%")
        m2.metric("ROE (Financing Economics)", f"{roe*100:.1f}%" if equity_amount > 0 else "N/A")
        m3.metric("Interest Coverage", f"{interest_coverage:.1f}x" if interest_coverage != np.inf else "No Debt")
        
        if equity_amount == 0:
            st.error("⚠️ Capital structure is 100% Debt. Financial risk is absolute.")
        elif roe > roic and interest_coverage > 1.5:
            st.success(f"📈 **Positive Leverage:** Debt acts as a magnifying glass. Because the business earns a return on capital that exceeds its cost of capital, the surplus accrues entirely to the equity shareholders.")
        elif roe < roic and ebit > 0:
            st.error(f"📉 **Negative Leverage:** The rigid nature of debt has now triggered negative leverage. The business must effectively subsidize the shortfall using cash that belongs to the shareholders, consuming their capital.")

    with tab_docs:
        st.markdown(load_docs(["Capital Structure — The Economics of Financing - Copy.md"]))

# ==========================================
# MODULE 4: REVENUE QUALITY VALIDATOR
# ==========================================
def render_revenue_quality():
    st.header("4. Revenue Quality Validator")
    
    tab_engine, tab_docs = st.tabs(["⚙️ Simulation Engine", "📚 Financial Theory"])
    
    with tab_engine:
        with st.expander("⚙️ Financial Statements Data", expanded=True):
            col1, col2 = st.columns(2)
            prior_rev = col1.number_input("Prior Year Revenue (₹)", 1.0, value=1000.0)
            curr_rev = col2.number_input("Current Year Revenue (₹)", 0.0, value=1200.0)
            prior_ar = col1.number_input("Prior Year Accounts Receivable (₹)", 1.0, value=200.0)
            curr_ar = col2.number_input("Current Year Accounts Receivable (₹)", 0.0, value=350.0)
            curr_ocf = st.number_input("Current Year Operating Cash Flow (₹)", value=100.0)

        rev_growth = ((curr_rev - prior_rev) / prior_rev) * 100
        ar_growth = ((curr_ar - prior_ar) / prior_ar) * 100
        ocf_margin = (curr_ocf / curr_rev) * 100 if curr_rev > 0 else 0
        
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Revenue Growth", f"{rev_growth:.1f}%")
        m2.metric("Receivables Growth", f"{ar_growth:.1f}%")
        m3.metric("OCF Margin", f"{ocf_margin:.1f}%")
        
        if curr_ocf < 0 and rev_growth > 0:
            st.error("🚨 **Red Flag (Earnings Manipulation):** If revenue and profits continue rising while operating cash flow stagnates or declines, the reported growth may not reflect the underlying economics of the business.")
        elif ar_growth > (rev_growth + 5.0):
            st.warning(f"⚠️ **Aggressive Recognition Risk:** Receivables grew at {ar_growth:.1f}%, drastically outpacing revenue. This may indicate weakening collections, aggressive credit terms, or premature revenue recognition like channel stuffing.")
        elif ar_growth <= (rev_growth + 5.0) and curr_ocf > 0:
            st.success("✅ **High-Quality Growth:** Receivables should generally grow in line with revenue. This top-line expansion is financially real and supported by cash.")

    with tab_docs:
        st.markdown(load_docs(["Revenue — The Economics of Growth.md"]))

# ==========================================
# MODULE 5: THE COMPOUNDING ENGINE
# ==========================================
def render_compounding_engine():
    st.header("5. The Compounding Engine")
    
    tab_engine, tab_docs = st.tabs(["⚙️ Simulation Engine", "📚 Financial Theory"])
    
    with tab_engine:
        with st.expander("⚙️ Reinvestment Parameters", expanded=True):
            col1, col2, col3 = st.columns(3)
            init_capital = col1.number_input("Initial Invested Capital (₹)", 10.0, value=100.0, step=10.0)
            roic = col2.slider("ROIC (%)", 5.0, 50.0, 25.0, 1.0) / 100
            reinvest_rate = col3.slider("Reinvestment Rate (%)", 0.0, 100.0, 60.0, 5.0) / 100
            horizon = st.slider("Time Horizon (Years)", 1, 15, 10, 1)

        data = []
        current_capital = init_capital
        
        for year in range(1, horizon + 1):
            nopat = current_capital * roic
            capital_reinvested = nopat * reinvest_rate
            fcf = nopat - capital_reinvested
            data.append({"Year": year, "NOPAT": nopat, "FCF": fcf})
            current_capital += capital_reinvested
            
        df = pd.DataFrame(data)
        yr1_nopat = df.iloc[0]["NOPAT"]
        final_nopat = df.iloc[-1]["NOPAT"]
        
        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Year 1 Operating Profit", f"₹{yr1_nopat:,.2f}")
        m2.metric(f"Year {horizon} Operating Profit", f"₹{final_nopat:,.2f}", f"{(final_nopat/yr1_nopat - 1)*100:.1f}% Total Growth")
        
        if roic >= 0.25 and reinvest_rate <= 0.20:
            st.info("🐮 **The Cash Cow:** This business generates substantial cash but has limited opportunities to compound because most of its earnings must be distributed to shareholders.")
        elif roic >= 0.25 and reinvest_rate >= 0.70:
            st.success("🚀 **The Ultimate Compounder:** This business combines high returns with high reinvestment, allowing both its earnings and capital base to compound over time.")
        elif roic < 0.10 and reinvest_rate >= 0.50:
            st.error("📉 **Value Destroyer:** A company with abundant investment opportunities but poor returns will destroy value despite growing rapidly.")
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Year'], y=df['NOPAT'], mode='lines+markers', name='Operating Profit', line=dict(color='#329F5B', width=3)))
        fig.add_trace(go.Scatter(x=df['Year'], y=df['FCF'], mode='lines+markers', name='Free Cash Flow', line=dict(color='#2E86AB', width=3)))
        fig.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=400, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

    with tab_docs:
        st.markdown(load_docs(["Capital Allocation — The Economics of Compounding.md"]))

# ==========================================
# MAIN ROUTING
# ==========================================
def main():
    # Page Header
    st.title("The Enterprise Economics Engine")
    st.caption("Architected for high-signal financial modeling. Evaluate business quality by testing fundamental economics.")
    st.divider()
    
    # Main Body Navigation replacing the sidebar
    engine_tabs = st.tabs([
        "1. Operating Leverage",
        "2. Working Capital",
        "3. Capital Structure",
        "4. Revenue Quality",
        "5. Compounding Engine"
    ])
    
    with engine_tabs[0]:
        render_operating_leverage()
    with engine_tabs[1]:
        render_working_capital()
    with engine_tabs[2]:
        render_capital_structure()
    with engine_tabs[3]:
        render_revenue_quality()
    with engine_tabs[4]:
        render_compounding_engine()

if __name__ == "__main__":
    main()