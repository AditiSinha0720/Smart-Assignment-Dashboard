import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="CHRIST | Assignment Dashboard", page_icon="📚", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1250px; padding-top: 2.2rem; padding-bottom: 2rem;}
[data-testid="stSidebar"] {border-right: 1px solid #94a3b833;}
/* Explicit card colours keep the text readable in both Streamlit themes. */
[data-testid="stMetric"] {
    background: #10233f !important; color: #ffffff !important;
    border: 1px solid #33516d; border-top: 3px solid #2dd4bf;
    padding: 16px; border-radius: 10px;
}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
    color: #cbd5e1 !important;
}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
    color: #ffffff !important; font-weight: 750;
}
[data-testid="stProgress"] div[role="progressbar"] > div {
    background-color: #0f766e;
}
.banner {background: linear-gradient(110deg, #10233f, #173d60); color: white;
    padding: 26px 30px; border-radius: 12px; margin-bottom: 24px;}
.banner small {color: #91ded5; font-weight: 700; letter-spacing: 2px;}
.banner h1 {color: white; font-size: 1.85rem; margin: 7px 0; padding: 0;}
.banner p {color: #dbeafe; margin: 0;}
.stButton > button, .stFormSubmitButton > button {border-radius: 8px;}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"]
    {background: #0f766e; border-color: #0f766e; color: white;}
</style>
""", unsafe_allow_html=True)

FILE = "christ_assignments.csv"
COLUMNS = ["ID", "Assignment", "Subject", "Due Date", "Priority", "Status", "Notes"]
PRIORITIES = ["High", "Medium", "Low"]
STATUSES = ["Pending", "In Progress", "Completed"]
TODAY = pd.Timestamp.now(tz="Asia/Kolkata").normalize().tz_localize(None)

def load_data():
    try:
        data = pd.read_csv(FILE, dtype=str, keep_default_na=False)[COLUMNS]
        data["ID"] = data["ID"].astype(int)
        data["Due Date"] = pd.to_datetime(data["Due Date"], format="%Y-%m-%d").dt.strftime("%Y-%m-%d")
        if (data["ID"].duplicated().any() or data["Due Date"].isna().any()
                or not data["Priority"].isin(PRIORITIES).all()
                or not data["Status"].isin(STATUSES).all()):
            raise ValueError("Invalid dates, IDs, priorities or statuses.")
        return data
    except FileNotFoundError:
        return pd.DataFrame(columns=COLUMNS)
    except (OSError, ValueError, KeyError) as error:
        st.error(f"Cannot read {FILE}: {error}. Check the CSV before continuing.")
        st.stop()

def save_data(data, message):
    try:
        data[COLUMNS].to_csv(FILE, index=False)
    except OSError as error:
        st.error(f"Could not save assignments: {error}")
        return
    st.session_state["message"] = message
    st.rerun()

def deadline_data(data):
    result = data.copy()
    days = (pd.to_datetime(result["Due Date"]) - TODAY).dt.days
    result["Days Left"] = days.astype("Int64")
    result["Deadline"] = np.select(
        [result["Status"].eq("Completed"), days.lt(0), days.eq(0), days.le(3)],
        ["Completed", "Overdue", "Due Today", "Due Soon"], default="Upcoming")
    result.loc[result["Status"].eq("Completed"), "Days Left"] = pd.NA
    result["Priority Rank"] = result["Priority"].map({"High": 0, "Medium": 1, "Low": 2})
    return result.sort_values(["Due Date", "Priority Rank", "ID"])

def show_table(data):
    if data.empty:
        st.info("No assignments to display.")
        return
    st.dataframe(data[["Assignment", "Subject", "Due Date", "Priority", "Status",
                       "Deadline", "Days Left", "Notes"]],
                 hide_index=True, use_container_width=True)

def assignment_form(key, task=None):
    editing = task is not None
    with st.form(key, clear_on_submit=not editing):
        left, right = st.columns(2)
        title = left.text_input("Assignment title *", value=task["Assignment"] if editing else "")
        subject = right.text_input("Subject *", value=task["Subject"] if editing else "",
                                   placeholder="e.g. Python, DSA, Java")
        left, middle, right = st.columns(3)
        due = left.date_input("Submission deadline", value=pd.Timestamp(task["Due Date"]).date()
                              if editing else TODAY.date())
        priority = middle.selectbox("Priority", PRIORITIES,
                                    index=PRIORITIES.index(task["Priority"]) if editing else 1)
        status = right.selectbox("Status", STATUSES,
                                 index=STATUSES.index(task["Status"]) if editing else 0)
        notes = st.text_area("Notes / submission instructions", value=task["Notes"] if editing else "")
        submitted = st.form_submit_button("Save changes" if editing else "Add assignment", type="primary")
    if submitted:
        if not title.strip() or not subject.strip():
            st.warning("Enter both the assignment title and subject.")
        else:
            return [title.strip(), subject.strip(), str(due), priority, status, notes.strip()]
    return None

df = load_data()
tasks = deadline_data(df)
active = tasks[tasks["Status"] != "Completed"]
total = len(tasks)
completed = int(tasks["Status"].eq("Completed").sum())
overdue = active[active["Deadline"] == "Overdue"]
due_today = active[active["Deadline"] == "Due Today"]
due_soon = active[active["Deadline"] == "Due Soon"]
percent = round(completed / total * 100, 1) if total else 0

# Sidebar navigation
st.sidebar.title("CHRIST")
st.sidebar.caption("UNIVERSITY  /  STUDENT WORKSPACE")
st.sidebar.divider()
page = st.sidebar.radio("WORKSPACE", ["Overview", "Manage assignments", "Analytics"])
st.sidebar.divider()
st.sidebar.caption(TODAY.strftime("%A, %d %B %Y"))
st.sidebar.progress(float(percent / 100))
st.sidebar.write(f"{completed} of {total} assignments completed")
st.sidebar.download_button("Export assignments (CSV)", df.to_csv(index=False),
                           file_name="christ_assignments_export.csv", mime="text/csv")

st.markdown("""
<div class="banner"><small>CHRIST UNIVERSITY  •  ACADEMIC PRODUCTIVITY</small>
<h1>Smart Assignment &amp; Deadline Management Dashboard</h1>
<p>Plan your workload. Track your progress. Meet every deadline.</p></div>
""", unsafe_allow_html=True)
if "message" in st.session_state:
    st.success(st.session_state.pop("message"))

if page == "Overview":
    st.subheader("Academic overview")
    a, b, c, d, e = st.columns(5)
    a.metric("Total tasks", total)
    b.metric("Open tasks", len(active))
    c.metric("Completed", completed)
    d.metric("Overdue", len(overdue))
    e.metric("Due in 3 days", len(due_today) + len(due_soon))
    st.write("")
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Deadline alerts")
        if len(overdue):
            st.error(f"{len(overdue)} overdue assignment(s). Prioritize these now.")
        if len(due_today):
            st.warning(f"{len(due_today)} assignment(s) due today.")
        if len(due_soon):
            st.info(f"{len(due_soon)} assignment(s) due in the next 3 days.")
        if not (len(overdue) + len(due_today) + len(due_soon)):
            st.success("No urgent deadlines. You are all caught up on immediate tasks.")
    with right:
        st.subheader("Completion rate")
        st.metric("Overall progress", f"{percent:g}%")
        st.progress(float(percent / 100))
        st.caption(f"{len(active)} assignment(s) remaining")
    st.divider()
    st.subheader("Priority task list")
    st.caption("Open assignments, ordered by deadline and then priority.")
    show_table(active)

#demonstration data, useful for an academic presentation.
    if total == 0:
        if st.button("Load sample assignments"):
            samples = [
                [1, "NumPy practical", "Python", -2, "High", "Pending", "Practice arrays"],
                [2, "Sorting algorithms", "DSA", 0, "High", "In Progress", "Submit code"],
                [3, "SQL lab report", "DBMS", 2, "Medium", "Pending", "Include queries"],
                [4, "OOP case study", "Java", 5, "Medium", "In Progress", "Add examples"],
                [5, "Statistics worksheet", "Mathematics", -1, "Low", "Completed", "Submitted"],
                [6, "Data visualization", "Python", 7, "Low", "Pending", "Create plots"]]
            demo = pd.DataFrame(samples, columns=COLUMNS)
            demo["Due Date"] = (TODAY + pd.to_timedelta(demo["Due Date"], unit="D")).dt.strftime("%Y-%m-%d")
            save_data(demo, "Sample assignments loaded. You can edit or delete them.")

elif page == "Manage assignments":
    st.subheader("Assignment manager")
    add_tab, list_tab, edit_tab = st.tabs(["Add assignment", "View & filter", "Edit or delete"])
    with add_tab:
        values = assignment_form("add_form")
        if values is not None:
            new_id = int(df["ID"].max()) + 1 if len(df) else 1
            new = pd.DataFrame([[new_id] + values], columns=COLUMNS)
            save_data(pd.concat([df, new], ignore_index=True), "Assignment added successfully.")
    with list_tab:
        a, b, c = st.columns(3)
        search = a.text_input("Search assignments")
        subjects = b.multiselect("Subjects", sorted(df["Subject"].unique()))
        statuses = c.multiselect("Status", STATUSES)
        filtered = tasks[tasks["Assignment"].str.contains(search, case=False, regex=False)
                         | tasks["Subject"].str.contains(search, case=False, regex=False)]
        if subjects:
            filtered = filtered[filtered["Subject"].isin(subjects)]
        if statuses:
            filtered = filtered[filtered["Status"].isin(statuses)]
        st.caption(f"Showing {len(filtered)} of {total} assignments")
        show_table(filtered)
    with edit_tab:
        if df.empty:
            st.info("Add an assignment before editing or deleting.")
        else:
            labels = {row.ID: f"{row.Assignment} — {row.Subject} (#{row.ID})"
                      for row in df.itertuples(index=False)}
            selected = st.selectbox("Select assignment", list(labels), format_func=labels.get)
            task = df[df["ID"] == selected].iloc[0]
            if task["Status"] != "Completed" and st.button("Mark as completed", type="primary"):
                df.loc[df["ID"] == selected, "Status"] = "Completed"
                save_data(df, "Assignment marked as completed.")
            values = assignment_form(f"edit_{selected}", task)
            if values is not None:
                df.loc[df["ID"] == selected, COLUMNS[1:]] = values
                save_data(df, "Assignment updated successfully.")
            confirm = st.checkbox("Confirm deletion", key=f"confirm_{selected}")
            if st.button("Delete assignment", disabled=not confirm):
                save_data(df[df["ID"] != selected], "Assignment deleted.")

else:
    st.subheader("Academic performance analytics")
    st.caption("Understand your workload and assignment completion patterns.")
    if df.empty:
        st.info("Add assignments to unlock your analytics.")
    else:
        # Matplotlib charts: a consistent navy, teal and amber palette.
        left, right = st.columns([1, 1.4])
        with left:
            st.markdown("**Assignment status**")
            counts = df["Status"].value_counts().reindex(STATUSES, fill_value=0)
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor="white")
            ax.pie(counts, colors=["#d97706", "#24476b", "#0f766e"], startangle=90,
                   wedgeprops={"width": 0.32, "edgecolor": "white"})
            ax.text(0, 0, f"{percent:g}%\nComplete", ha="center", va="center",
                    fontsize=14, fontweight="bold", color="#10233f")
            ax.legend([f"{s}: {n}" for s, n in counts.items()], loc="lower center",
                      bbox_to_anchor=(0.5, -0.15), frameon=False, ncol=1, fontsize=9)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        with right:
            st.markdown("**Subject-wise workload**")
            workload = pd.crosstab(df["Subject"], df["Status"]).reindex(columns=STATUSES, fill_value=0)
            fig, ax = plt.subplots(figsize=(6, max(3.2, 0.45 * len(workload) + 1.5)), facecolor="white")
            workload.plot.barh(stacked=True, color=["#d97706", "#24476b", "#0f766e"], ax=ax)
            ax.set_xlabel("Assignments")
            ax.set_ylabel("")
            ax.xaxis.get_major_locator().set_params(integer=True)
            ax.spines[["top", "right"]].set_visible(False)
            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=False, fontsize=8)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        st.divider()
        st.markdown("**Upcoming deadlines — next 7 days including today**")
        dates = pd.date_range(TODAY, periods=7)
        daily = pd.to_datetime(active["Due Date"]).value_counts().reindex(dates, fill_value=0)
        fig, ax = plt.subplots(figsize=(10, 2.8), facecolor="white")
        bars = ax.bar(dates.strftime("%a %d %b"), daily, color="#0f766e", width=0.55)
        ax.bar_label(bars, padding=3, fontsize=9)
        ax.set_ylim(0, max(1, int(daily.max()) + 1))
        ax.set_ylabel("Open tasks")
        ax.yaxis.get_major_locator().set_params(integer=True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="x", labelsize=9)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)


        st.divider()
        left, right = st.columns(2)
        with left:
            st.markdown("**Deadline distribution (Histogram)**")
            st.caption("Negative days are overdue; zero means due today.")
            if active.empty:
                st.info("No open assignments to display in the histogram.")
            else:
                days = active["Days Left"].astype(int).to_numpy()
                # Group remaining days into at most 10 intervals.
                bins = min(10, int(days.max() - days.min()) + 1)
                fig, ax = plt.subplots(figsize=(6, 3.5), facecolor="white")
                ax.hist(days, bins=bins, range=(days.min() - 0.5, days.max() + 0.5),
                        color="#24476b", edgecolor="white")
                ax.axvline(0, color="#d97706", linestyle="--", label="Today")
                ax.set_xlabel("Days until deadline")
                ax.set_ylabel("Open assignments")
                ax.xaxis.get_major_locator().set_params(integer=True)
                ax.yaxis.get_major_locator().set_params(integer=True)
                ax.spines[["top", "right"]].set_visible(False)
                ax.legend(frameon=False)
                fig.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
        with right:
            st.markdown("**Deadline trend (Line graph)**")
            st.caption("Open assignments due each day over the next 14 days, including today.")
            dates = pd.date_range(TODAY, periods=14)
            daily = pd.to_datetime(active["Due Date"]).value_counts().reindex(dates, fill_value=0)
            fig, ax = plt.subplots(figsize=(6, 3.5), facecolor="white")
            ax.plot(dates, daily, color="#0f766e", marker="o", linewidth=2)
            ax.fill_between(dates, daily.to_numpy(), alpha=0.12, color="#0f766e")
            ax.set_xticks(dates[::3], dates[::3].strftime("%d %b"))
            ax.set_ylim(0, max(1, int(daily.max()) + 1))
            ax.set_ylabel("Open assignments")
            ax.set_xlabel("Due date")
            ax.yaxis.get_major_locator().set_params(integer=True)
            ax.spines[["top", "right"]].set_visible(False)
            ax.grid(axis="y", alpha=0.2)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

st.divider()
st.caption("CHRIST Smart Assignment Dashboard  |  Student academic planning tool")