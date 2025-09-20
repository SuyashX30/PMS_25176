import streamlit as st
import Backend_pms as be
from datetime import date

st.set_page_config(page_title="Performance Management System", layout="wide")

def main():
    """Main function to run the Streamlit app."""
    # --- Initialize Database ---
    be.setup_database()
    be.seed_data()

    st.title("Performance Management System")

    # --- User Selection ---
    st.sidebar.header("Select User")
    employees = be.get_employees()
    employee_dict = {name: eid for eid, name in employees}
    
    # Simple user switching for demo purposes
    if employee_dict:
        selected_user_name = st.sidebar.selectbox("Select your user profile", options=list(employee_dict.keys()))
        selected_user_id = employee_dict[selected_user_name]
        is_manager = "Manager" in selected_user_name
        st.sidebar.info(f"Logged in as: **{selected_user_name}**")
    else:
        st.sidebar.error("No users found in the database.")
        st.error("Application cannot start. No employee data found. Please check the database connection and seed data.")
        return

    # --- Sidebar for Navigation ---
    st.sidebar.title("Navigation")
    
    # Define navigation options based on user role
    nav_options = ["Goal & Task Setting", "Progress Tracking", "Feedback", "Reporting"]
    if is_manager:
        nav_options.append("Business Insights")
        
    app_mode = st.sidebar.selectbox("Choose a section", nav_options)


    # --- Page Content based on Navigation ---

    if app_mode == "Goal & Task Setting":
        st.header("Goal & Task Setting")

        if is_manager:
            st.subheader("Set a New Goal for an Employee")
            team_members = {name: eid for eid, name in employees if "Manager" not in name}
            if team_members:
                selected_employee_name = st.selectbox("Select Employee", options=list(team_members.keys()))
                goal_desc = st.text_area("Goal Description")
                due_date = st.date_input("Due Date", min_value=date.today())

                if st.button("Create Goal"):
                    if goal_desc:
                        employee_id = team_members[selected_employee_name]
                        be.create_goal(employee_id, goal_desc, due_date)
                        st.success(f"Goal created for {selected_employee_name}")
                        st.rerun()
                    else:
                        st.warning("Goal description cannot be empty.")
            else:
                st.info("No employees found to assign goals to.")

        st.subheader("My Assigned Goals")
        my_goals = be.get_goals_for_employee(selected_user_id)

        if not my_goals:
            st.info("You have no goals assigned.")
        
        for goal_id, desc, due, status in my_goals:
            with st.expander(f"Goal: {desc} (Status: {status})"):
                st.write(f"**Due Date:** {due}")
                
                # --- Task Management ---
                st.markdown("---")
                st.markdown("**Tasks to achieve this goal:**")
                
                tasks = be.get_tasks_for_goal(goal_id)
                if tasks:
                    for task_id, task_desc, is_approved in tasks:
                        approval_status = "Approved" if is_approved else "Pending Approval"
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"- {task_desc}")
                        with col2:
                            st.write(f"_{approval_status}_")
                        with col3:
                             if is_manager and not is_approved:
                                if st.button("Approve", key=f"approve_{task_id}"):
                                    be.approve_task(task_id)
                                    st.rerun()
                else:
                    st.text("No tasks yet.")

                if not is_manager:
                    st.markdown("**Log a new task:**")
                    new_task_desc = st.text_input("Task Description", key=f"task_{goal_id}")
                    if st.button("Add Task", key=f"add_task_{goal_id}"):
                        if new_task_desc:
                            be.create_task(goal_id, new_task_desc)
                            st.success("Task added and awaiting manager approval.")
                            st.rerun()
                        else:
                            st.warning("Task description cannot be empty.")


    elif app_mode == "Progress Tracking":
        st.header("Progress Tracking")
        
        target_employee_id = selected_user_id
        display_name = selected_user_name
        if is_manager:
             team_members = {name: eid for eid, name in employees if "Manager" not in name}
             if team_members:
                 selected_employee_name = st.selectbox("View progress for:", options=[selected_user_name] + list(team_members.keys()))
                 target_employee_id = employee_dict[selected_employee_name]
                 display_name = selected_employee_name
             else:
                 st.info("No employees to track.")
        
        st.subheader(f"Progress for: {display_name}")
        goals = be.get_goals_for_employee(target_employee_id)
        if not goals:
            st.info("No goals to track for this user.")

        for goal_id, desc, due, status in goals:
            st.subheader(f"Goal: {desc}")
            st.write(f"**Status:** {status} | **Due Date:** {due}")

            if is_manager:
                new_status = st.selectbox(
                    "Update Goal Status",
                    options=['Draft', 'In Progress', 'Completed', 'Cancelled'],
                    index=['Draft', 'In Progress', 'Completed', 'Cancelled'].index(status),
                    key=f"status_{goal_id}"
                )
                if st.button("Save Status", key=f"save_{goal_id}"):
                    be.update_goal_status(goal_id, new_status)
                    st.success("Status updated!")
                    st.rerun()
            
            # Progress visualization
            tasks = be.get_tasks_for_goal(goal_id)
            total_tasks = len(tasks)
            approved_tasks = sum(1 for _, _, is_approved in tasks if is_approved)
            progress = (approved_tasks / total_tasks) * 100 if total_tasks > 0 else 0
            
            st.progress(int(progress))
            st.write(f"Task Completion: {approved_tasks} of {total_tasks} approved tasks.")
            st.markdown("---")

    elif app_mode == "Feedback":
        st.header("Feedback")
        
        target_employee_id = selected_user_id
        display_name = selected_user_name
        if is_manager:
            team_members = {name: eid for eid, name in employees if "Manager" not in name}
            if team_members:
                selected_employee_name = st.selectbox("Select Employee for Feedback", options=[selected_user_name] + list(team_members.keys()))
                target_employee_id = employee_dict[selected_employee_name]
                display_name = selected_employee_name
            
        st.subheader(f"Feedback for: {display_name}")
        goals = be.get_goals_for_employee(target_employee_id)
        if not goals:
            st.info("This employee has no goals to provide feedback on.")

        for goal_id, desc, _, status in goals:
            with st.expander(f"Goal: {desc} (Status: {status})"):
                st.subheader("Existing Feedback")
                feedback_list = be.get_feedback_for_goal(goal_id)
                if feedback_list:
                    for fb_text, manager_name, created_at in feedback_list:
                        st.info(f"**From {manager_name} on {created_at.strftime('%Y-%m-%d %H:%M')}:**\n\n{fb_text}")
                else:
                    st.text("No feedback has been given for this goal yet.")

                if is_manager:
                    st.subheader("Provide New Feedback")
                    feedback_text = st.text_area("Your Feedback", key=f"feedback_{goal_id}")
                    if st.button("Submit Feedback", key=f"submit_fb_{goal_id}"):
                        if feedback_text:
                            be.create_feedback(goal_id, selected_user_id, feedback_text)
                            st.success("Feedback submitted.")
                            st.rerun()
                        else:
                            st.warning("Feedback cannot be empty.")

    elif app_mode == "Reporting":
        st.header("Performance History Report")
        
        target_employee_id = selected_user_id
        if is_manager:
             team_members = {name: eid for eid, name in employees if "Manager" not in name}
             if team_members:
                selected_employee_name = st.selectbox("Generate report for:", options=list(team_members.keys()))
                target_employee_id = team_members[selected_employee_name]
                st.subheader(f"Showing report for: {selected_employee_name}")
             else:
                st.info("No employees available for reporting.")
                return
        else:
            st.subheader(f"Showing your performance history")

        goals = be.get_goals_for_employee(target_employee_id)
        if not goals:
            st.warning("No performance data available for this user.")
        
        for goal_id, desc, due, status in goals:
            st.markdown(f"### Goal: {desc}")
            st.write(f"**Status:** {status} | **Due:** {due}")
            
            st.markdown("**Associated Tasks:**")
            tasks = be.get_tasks_for_goal(goal_id)
            if tasks:
                for _, task_desc, is_approved in tasks:
                    st.write(f"- {task_desc} `{'Approved' if is_approved else 'Pending'}`")
            else:
                st.write("_No tasks logged for this goal._")

            st.markdown("**Associated Feedback:**")
            feedback = be.get_feedback_for_goal(goal_id)
            if feedback:
                for fb_text, manager_name, ts in feedback:
                    st.text(f"[{ts.strftime('%Y-%m-%d')}] from {manager_name}: {fb_text}")
            else:
                st.write("_No feedback recorded for this goal._")
            st.markdown("---")

    elif app_mode == "Business Insights":
        st.header("Business Insights Dashboard")
        insights = be.get_performance_insights()

        if insights:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Goals Set", value=insights.get("total_goals", 0))
            with col2:
                st.metric(label="Avg Goals Per Employee", value=insights.get("average_goals_per_employee", 0))
            
            st.subheader("Goals by Status")
            st.bar_chart(insights.get("goals_by_status", {}))

            st.subheader("Top & Lowest Performers")
            col1, col2 = st.columns(2)
            with col1:
                 st.success(f"**Top Performer (most goals completed):**\n\n## {insights.get('top_performer', 'N/A')}")
            with col2:
                st.warning(f"**Lowest Performer (least goals completed):**\n\n## {insights.get('lowest_performer', 'N/A')}")

        else:
            st.warning("Could not retrieve business insights.")

if __name__ == "__main__":
    main()

