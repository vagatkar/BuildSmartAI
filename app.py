import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date
import sqlite3

st.set_page_config(page_title="BuildSmart AI | Construction Intelligence", page_icon="🏗️", layout="wide")
DATA = Path(__file__).parent

@st.cache_data
def load_data():
    t = pd.read_csv(DATA / "tasks.csv")
    c = pd.read_csv(DATA / "contractors.csv")
    r = pd.read_csv(DATA / "risks.csv")
    for col in ["Planned Start", "Planned Finish", "Actual Start", "Actual Finish"]:
        t[col] = pd.to_datetime(t[col], errors="coerce")
    r["Due Date"] = pd.to_datetime(r["Due Date"], errors="coerce")
    return t, c, r

tasks, contractors, risks = load_data()

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: #f5f7fb; padding: 14px 16px; border-radius: 10px; border: 1px solid #e7ebf2;}
.small-note {color:#6b7280;font-size:0.85rem;}
</style>
""", unsafe_allow_html=True)

st.title("🏗️ BuildSmart AI")
st.caption("Construction Project Intelligence & Automation Dashboard | Demonstration prototype")

with st.sidebar:
    st.header("Project controls")
    project_name = st.text_input("Project", "Hillview Residential Development")
    phase_filter = st.multiselect("Filter by phase", sorted(tasks["Phase"].unique()), default=sorted(tasks["Phase"].unique()))
    status_filter = st.multiselect("Filter by status", sorted(tasks["Status"].unique()), default=sorted(tasks["Status"].unique()))
    st.divider()
    st.caption("Demo data only · INR · Fictional project")
    st.caption("Prototype owner: Python / Automation portfolio")

filtered = tasks[tasks["Phase"].isin(phase_filter) & tasks["Status"].isin(status_filter)].copy()
total_budget = tasks["Budget (INR)"].sum()
actual_cost = tasks["Actual Cost (INR)"].sum()
weighted_progress = (tasks["Progress %"] * tasks["Budget (INR)"]).sum() / max(total_budget, 1)
open_risks = risks[risks["Status"].isin(["Open", "Monitoring"])]
overdue_like = tasks[(tasks["Status"] == "At risk") | ((tasks["Progress %"] < 100) & (tasks["Planned Finish"] < pd.Timestamp.today()))]

st.subheader(project_name)
st.caption("Illustrative project controls view — replace sample records with verified project data before operational use.")
m1,m2,m3,m4,m5 = st.columns(5)
m1.metric("Overall progress", f"{weighted_progress:.0f}%")
m2.metric("Approved budget", f"₹{total_budget/100000:.2f} L")
m3.metric("Actual cost to date", f"₹{actual_cost/100000:.2f} L")
variance = actual_cost - tasks["Budget (INR)"].sum() * (weighted_progress/100)
m4.metric("Cost vs earned progress", f"₹{variance/100000:+.2f} L")
m5.metric("Open risks", f"{len(open_risks)}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Schedule", "Cost control", "Contractors", "Risks & reports"])

with tab1:
    left,right = st.columns([1.4,1])
    with left:
        st.markdown("#### Work progress by phase")
        phase = tasks.groupby("Phase", as_index=False)["Progress %"].mean()
        fig = px.bar(phase, x="Progress %", y="Phase", orientation="h", range_x=[0,100], text_auto=".0f",
                     color="Progress %", color_continuous_scale="Blues")
        fig.update_layout(height=350, coloraxis_showscale=False, xaxis_title="Average completion (%)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("#### Activity status")
        status = tasks["Status"].value_counts().rename_axis("Status").reset_index(name="Activities")
        fig2 = px.pie(status, names="Status", values="Activities", hole=.55)
        fig2.update_layout(height=350, legend_title="")
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown("#### Priority attention")
    attention = tasks[tasks["Risk"].isin(["High","Medium"])][["Activity","Phase","Progress %","Status","Contractor","Risk"]]
    st.dataframe(attention, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("#### Baseline schedule")
    sched = filtered.copy()
    sched = sched.dropna(subset=["Planned Start","Planned Finish"])
    if len(sched):
        fig = px.timeline(sched, x_start="Planned Start", x_end="Planned Finish", y="Activity", color="Status",
                          hover_data=["Phase","Contractor","Progress %","Risk"])
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=480, xaxis_title="Timeline", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Schedule register")
    st.dataframe(filtered[["Phase","Activity","Planned Start","Planned Finish","Progress %","Status","Contractor"]], use_container_width=True, hide_index=True)

with tab3:
    st.markdown("#### Budget vs actual by work package")
    cost = tasks.groupby("Phase", as_index=False)[["Budget (INR)","Actual Cost (INR)"]].sum()
    cost_long = cost.melt(id_vars="Phase", var_name="Cost Type", value_name="Amount (INR)")
    fig = px.bar(cost_long, x="Phase", y="Amount (INR)", color="Cost Type", barmode="group")
    fig.update_layout(height=400, yaxis_title="INR")
    st.plotly_chart(fig, use_container_width=True)
    cost["Variance (INR)"] = cost["Actual Cost (INR)"] - cost["Budget (INR)"]
    st.dataframe(cost, use_container_width=True, hide_index=True)
    st.info("Cost variance here compares total actual cost to full package budget. For proper earned-value management, connect approved progress-weighted cost baselines and change orders.")

with tab4:
    st.markdown("#### Contractor performance")
    fig = px.bar(contractors, x="Contractor", y="Average Progress %", color="Trade", text="Average Progress %", range_y=[0,110])
    fig.update_layout(height=390, xaxis_title="", yaxis_title="Average progress (%)")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(contractors, use_container_width=True, hide_index=True)

with tab5:
    st.markdown("#### Risk register")
    st.dataframe(risks, use_container_width=True, hide_index=True)
    st.markdown("#### Rule-based project alerts")
    alerts = []
    for _, row in tasks.iterrows():
        if row["Risk"] == "High" and row["Progress %"] < 100:
            alerts.append(f"**High priority:** {row['Activity']} ({row['Contractor']}) is marked high risk at {row['Progress %']}% progress.")
        if row["Status"] == "At risk":
            alerts.append(f"**Schedule attention:** Review recovery actions for {row['Activity']}.")
    if alerts:
        for a in alerts: st.warning(a)
    else:
        st.success("No rule-based alerts from current sample data.")
    st.markdown("#### Generate weekly status summary")
    if st.button("Generate project summary"):
        summary = f"""# Weekly Project Status — {project_name}

**Overall weighted progress:** {weighted_progress:.0f}%

**Budget:** ₹{total_budget:,.0f}  
**Actual cost to date:** ₹{actual_cost:,.0f}  
**Open / monitored risks:** {len(open_risks)}

## Key attention areas
"""
        for a in alerts:
            summary += "- " + a.replace("**","") + "\n"
        summary += "\n*Generated from illustrative demo data. Validate all figures before external use.*"
        st.download_button("Download status report (.md)", summary, file_name="weekly_project_status.md")
        st.markdown(summary)

st.divider()
st.markdown('<p class="small-note">BuildSmart AI is an independent portfolio prototype. Sample project, contractors, costs and progress figures are fictional and do not represent Sanctuary or any actual client project. Current alerts are rule-based, not generated by an LLM.</p>', unsafe_allow_html=True)
