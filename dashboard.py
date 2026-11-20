
"""Streamlit analytics dashboard (Plotly + Pandas)."""
import pandas as pd
import plotly.express as px
import streamlit as st

import config
import storage

PRIORITY_COLORS = {"High": "#d9534f", "Medium": "#f0ad4e", "Low": "#5cb85c"}


STATUS_COLORS = {"Pending": "#ef4444", "In Progress": "#f59e0b", "Resolved": "#10b981"}


def render():
    st.header("Analytics Dashboard")

    # Real-time auto-sync: detect changes in data_editor immediately
    if "editor" in st.session_state and isinstance(st.session_state["editor"], dict):
        changes = st.session_state["editor"].get("edited_rows", {})
        if changes:
            curr_df = storage.load()
            view_sorted = curr_df.sort_values("timestamp", ascending=False).reset_index(drop=True)
            to_update = {}
            for row_idx, diff in changes.items():
                if "status" in diff:
                    idx = int(row_idx)
                    if idx < len(view_sorted):
                        cid = view_sorted.iloc[idx]["id"]
                        to_update[cid] = diff["status"]
            if to_update:
                storage.update_statuses(to_update)
                st.session_state["editor"]["edited_rows"] = {}

    df = storage.load()

    if df.empty:
        st.info(
            "No complaints yet. Submit one on the Report Issue page, "
            "or load demo data to preview the dashboard."
        )
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total complaints", len(df))
        c2.metric("Pending", int((df["status"] == "Pending").sum()))
        c3.metric("In Progress", int((df["status"] == "In Progress").sum()))
        c4.metric("Resolved", int((df["status"] == "Resolved").sum()))

        c_left, c_right = st.columns(2)

        cat = df["category"].value_counts().reset_index()
        cat.columns = ["category", "count"]

        c_left.plotly_chart(
            px.pie(
                cat,
                names="category",
                values="count",
                hole=0.45,
                title="Complaints by category",
            ),
            width="stretch",
        )

        st_df = (
            df["status"]
            .value_counts()
            .reindex(["Pending", "In Progress", "Resolved"])
            .fillna(0)
            .reset_index()
        )
        st_df.columns = ["status", "count"]

        c_right.plotly_chart(
            px.bar(
                st_df,
                x="status",
                y="count",
                color="status",
                color_discrete_map=STATUS_COLORS,
                title="Resolved vs pending",
            ),
            width="stretch",
        )

        b_left, b_right = st.columns(2)

        loc = (
            df[df["location"] != "Not specified"]["location"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        loc.columns = ["location", "count"]

        b_left.plotly_chart(
            px.bar(
                loc,
                x="count",
                y="location",
                orientation="h",
                title="Most reported locations",
            ).update_yaxes(autorange="reversed"),
            width="stretch",
        )

        daily = df.groupby(df["timestamp"].dt.date).size().reset_index(name="count")
        daily.columns = ["date", "count"]

        b_right.plotly_chart(
            px.bar(
                daily,
                x="date",
                y="count",
                title="Complaints over time",
            ),
            width="stretch",
        )

        st.subheader("Manage complaints")

        view = df[
            [
                "id",
                "timestamp",
                "category",
                "issue_type",
                "location",
                "status",
                "source",
            ]
        ].sort_values("timestamp", ascending=False)

        edited = st.data_editor(
            view,
            hide_index=True,
            width="stretch",
            key="editor",
            disabled=[c for c in view.columns if c != "status"],
            column_config={
                "status": st.column_config.SelectboxColumn(
                    "status",
                    options=config.STATUSES,
                    required=True,
                )
            },
        )

        if st.button("Save status changes"):
            storage.update_statuses(
                dict(zip(edited["id"], edited["status"]))
            )
            st.success("Saved.")
            st.rerun()


