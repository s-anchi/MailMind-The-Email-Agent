import glob
import json
import os
import streamlit as st

from classifier import classify_email
from thread_summarizer import summarize_thread
from groq_client import GroqError
from actions import create_calendar_event, draft_followup


# =========================================================
# Configuration
# =========================================================

BASE_DIR = os.path.dirname(__file__)

EMAILS_DIR = os.path.join(BASE_DIR, "emails")
THREADS_DIR = os.path.join(BASE_DIR, "threads")


# =========================================================
# Page Configuration
# =========================================================

st.set_page_config(
    page_title="MailMind",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# Custom UI / CSS
# =========================================================

st.markdown(
    """
<style>

    /* ---------- Global ---------- */

    .stApp {
        background: #f7f8fc;
    }

    .main .block-container {
        max-width: 1400px;
        padding: 2rem 3rem 4rem 3rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.03em;
    }

    /* ---------- Sidebar ---------- */

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: none;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    .sidebar-brand {
        padding: 10px 4px 28px 4px;
    }

    .sidebar-brand-title {
        font-size: 24px;
        font-weight: 700;
        color: white;
        letter-spacing: -0.04em;
    }

    .sidebar-brand-subtitle {
        font-size: 12px;
        color: #9ca3af;
        margin-top: 3px;
    }

    .sidebar-section {
        color: #6b7280;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.12em;
        margin: 22px 4px 8px 4px;
        text-transform: uppercase;
    }

    /* ---------- Header ---------- */

    .page-eyebrow {
        color: #6366f1;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .page-title {
        font-size: 36px;
        font-weight: 750;
        color: #111827;
        letter-spacing: -0.045em;
        margin-bottom: 4px;
    }

    .page-subtitle {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 28px;
    }

    /* ---------- Metric Cards ---------- */

    .metric-card {
        background: white;
        border: 1px solid #e7e9ef;
        border-radius: 16px;
        padding: 20px;
        min-height: 110px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    }

    .metric-label {
        color: #6b7280;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .metric-value {
        color: #111827;
        font-size: 30px;
        font-weight: 750;
        margin-top: 6px;
    }

    .metric-description {
        color: #9ca3af;
        font-size: 12px;
        margin-top: 2px;
    }

    /* ---------- Section Titles ---------- */

    .section-title {
        color: #111827;
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin-top: 30px;
        margin-bottom: 14px;
    }

    .section-description {
        color: #6b7280;
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 18px;
    }

    /* ---------- Thread Cards ---------- */

    .thread-card {
        background: white;
        border: 1px solid #e7e9ef;
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.025);
    }

    .thread-card:hover {
        border-color: #c7c9f7;
    }

    .thread-subject {
        color: #111827;
        font-size: 16px;
        font-weight: 650;
        margin-bottom: 5px;
    }

    .thread-meta {
        color: #8a92a3;
        font-size: 12px;
    }

    /* ---------- Badges ---------- */

    .badge {
        display: inline-block;
        border-radius: 999px;
        padding: 4px 9px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .badge-high {
        background: #fef2f2;
        color: #dc2626;
    }

    .badge-medium {
        background: #fffbeb;
        color: #d97706;
    }

    .badge-low {
        background: #f0fdf4;
        color: #16a34a;
    }

    .badge-neutral {
        background: #f3f4f6;
        color: #6b7280;
    }

    /* ---------- Action Cards ---------- */

    .action-card {
        background: #fafaff;
        border: 1px solid #e3e4fb;
        border-radius: 14px;
        padding: 16px;
        margin: 8px 0;
    }

    .action-title {
        color: #111827;
        font-weight: 650;
        font-size: 14px;
    }

    .action-meta {
        color: #6b7280;
        font-size: 12px;
        margin-top: 7px;
    }

    /* ---------- Person ---------- */

    .person-card {
        background: #f8f9fc;
        border: 1px solid #eceef3;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }

    .person-name {
        color: #111827;
        font-weight: 650;
        font-size: 13px;
    }

    .person-role {
        color: #7b8494;
        font-size: 11px;
        margin-top: 2px;
    }

    /* ---------- Deadline ---------- */

    .deadline-card {
        border-left: 3px solid #6366f1;
        background: #f8f9ff;
        border-radius: 0 10px 10px 0;
        padding: 11px 14px;
        margin-bottom: 8px;
    }

    .deadline-title {
        font-size: 13px;
        font-weight: 650;
        color: #111827;
    }

    .deadline-meta {
        font-size: 11px;
        color: #6b7280;
        margin-top: 3px;
    }

    /* ---------- Summary Hero ---------- */

    .summary-hero {
        background: linear-gradient(
            135deg,
            #f5f3ff,
            #eef2ff
        );
        border: 1px solid #ddd6fe;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0 20px 0;
    }

    .summary-label {
        color: #6366f1;
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .summary-text {
        color: #27272a;
        font-size: 15px;
        line-height: 1.65;
    }

    /* ---------- Buttons ---------- */

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid #e5e7eb;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        border-color: #818cf8;
        color: #4f46e5;
    }

    /* ---------- Dialog ---------- */

    div[data-testid="stDialog"] {
        border-radius: 20px;
    }

    /* ---------- Hide Streamlit Branding ---------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# Data Loading
# =========================================================

@st.cache_data
def load_emails():

    paths = sorted(
        glob.glob(
            os.path.join(
                EMAILS_DIR,
                "*.json"
            )
        )
    )

    emails = []

    for path in paths:

        with open(
            path,
            encoding="utf-8"
        ) as f:

            emails.append(
                json.load(f)
            )

    return emails


@st.cache_data
def load_threads():

    if not os.path.exists(THREADS_DIR):
        return []

    paths = sorted(
        glob.glob(
            os.path.join(
                THREADS_DIR,
                "*.json"
            )
        )
    )

    threads = []

    for path in paths:

        with open(
            path,
            encoding="utf-8"
        ) as f:

            threads.append(
                json.load(f)
            )

    return threads


# =========================================================
# Helper Functions
# =========================================================

def priority_badge(priority):

    priority = priority or "Medium"

    if priority == "High":
        return (
            '<span class="badge badge-high">'
            'High priority'
            '</span>'
        )

    if priority == "Low":
        return (
            '<span class="badge badge-low">'
            'Low priority'
            '</span>'
        )

    return (
        '<span class="badge badge-medium">'
        'Medium priority'
        '</span>'
    )


def status_badge(status):

    status = (status or "pending").lower()

    if status == "completed":

        return (
            '<span class="badge badge-low">'
            'Completed'
            '</span>'
        )

    return (
        '<span class="badge badge-neutral">'
        'Pending'
        '</span>'
    )


# =========================================================
# Thread Summary Modal
# =========================================================

@st.dialog(
    "Thread Intelligence",
    width="large"
)
def show_thread_summary(thread):

    thread_id = thread.get(
        "thread_id",
        "thread"
    )

    subject = thread.get(
        "subject",
        "No subject"
    )

    messages = thread.get(
        "messages",
        []
    )

    st.markdown(
        f"### {subject}"
    )

    st.caption(
        f"AI analysis • {len(messages)} messages"
    )

    summary_key = (
        f"summary_data_{thread_id}"
    )

    if summary_key not in st.session_state:

        with st.spinner(
            "Analyzing conversation..."
        ):

            try:

                st.session_state[
                    summary_key
                ] = summarize_thread(
                    messages
                )

            except GroqError as e:

                st.error(
                    f"Groq error: {e}"
                )

                return

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )

                return

    summary = st.session_state[
        summary_key
    ]

    # =====================================================
    # Summary
    # =====================================================

    summary_text = summary.get(
        "summary",
        "No summary available."
    )

    st.markdown(
        f"""
        <div class="summary-hero">
            <div class="summary-label">
                AI Summary
            </div>
            <div class="summary-text">
                {summary_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # People + Priority
    # =====================================================

    people = summary.get(
        "people",
        []
    )

    priority = summary.get(
        "priority",
        "Medium"
    )

    left, right = st.columns(
        [2, 1]
    )

    with left:

        st.markdown(
            "#### 👥 People involved"
        )

        if people:

            for person in people:

                name = person.get(
                    "name",
                    "Unknown"
                )

                role = person.get(
                    "role",
                    ""
                )

                email = person.get(
                    "email",
                    ""
                )

                email_text = (
                    f"<br><small>{email}</small>"
                    if email
                    else ""
                )

                st.markdown(
                    f"""
                    <div class="person-card">
                        <div class="person-name">
                            {name}
                        </div>
                        <div class="person-role">
                            {role}
                            {email_text}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.caption(
                "No people identified."
            )

    with right:

        st.markdown(
            "#### Priority"
        )

        st.markdown(
            priority_badge(priority),
            unsafe_allow_html=True
        )

    st.divider()

    # =====================================================
    # Action Items
    # =====================================================

    st.markdown(
        "#### ✅ Action items"
    )

    action_items = summary.get(
        "action_items",
        []
    )

    if action_items:

        for index, item in enumerate(
            action_items
        ):

            task = item.get(
                "task",
                "Unknown task"
            )

            owner = item.get(
                "owner"
            ) or "Unassigned"

            deadline = item.get(
                "deadline"
            ) or "No deadline"

            status = item.get(
                "status",
                "pending"
            )

            st.markdown(
                f"""
                <div class="action-card">
                    <div class="action-title">
                        {task}
                    </div>
                    <div class="action-meta">
                        👤 {owner}
                        &nbsp;&nbsp;•&nbsp;&nbsp;
                        📅 {deadline}
                        &nbsp;&nbsp;•&nbsp;&nbsp;
                        {status_badge(status)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            action_col1, action_col2 = st.columns(
                2
            )

            # -------------------------------------------------
            # Calendar
            # -------------------------------------------------

            with action_col1:

                calendar_key = (
                    f"calendar_"
                    f"{thread_id}_"
                    f"{index}"
                )

                if st.button(
                    "📅 Add to Calendar",
                    key=calendar_key,
                    use_container_width=True
                ):

                    try:

                        ics_content = (
                            create_calendar_event(
                                task=task,
                                deadline=deadline,
                                owner=owner,
                                subject=subject
                            )
                        )

                        st.session_state[
                            f"calendar_content_"
                            f"{thread_id}_"
                            f"{index}"
                        ] = ics_content

                        st.success(
                            "Calendar event ready."
                        )

                    except ValueError as e:

                        st.error(
                            str(e)
                        )

                    except Exception as e:

                        st.error(
                            f"Calendar error: {e}"
                        )

            # -------------------------------------------------
            # Follow-up
            # -------------------------------------------------

            with action_col2:

                followup_key = (
                    f"followup_"
                    f"{thread_id}_"
                    f"{index}"
                )

                if st.button(
                    "✉️ Draft Follow-up",
                    key=followup_key,
                    use_container_width=True
                ):

                    with st.spinner(
                        "Drafting..."
                    ):

                        try:

                            draft = draft_followup(
                                thread,
                                item
                            )

                            st.session_state[
                                f"followup_data_"
                                f"{thread_id}_"
                                f"{index}"
                            ] = draft

                        except GroqError as e:

                            st.error(
                                f"Groq error: {e}"
                            )

                        except Exception as e:

                            st.error(
                                f"Couldn't create draft: {e}"
                            )

            # -------------------------------------------------
            # Calendar Download
            # -------------------------------------------------

            calendar_content = (
                st.session_state.get(
                    f"calendar_content_"
                    f"{thread_id}_"
                    f"{index}"
                )
            )

            if calendar_content:

                st.download_button(
                    "⬇️ Download .ics event",
                    data=calendar_content,
                    file_name=(
                        f"calendar_event_"
                        f"{index + 1}.ics"
                    ),
                    mime="text/calendar",
                    key=(
                        f"download_calendar_"
                        f"{thread_id}_"
                        f"{index}"
                    ),
                    use_container_width=True
                )

            # -------------------------------------------------
            # Follow-up Draft
            # -------------------------------------------------

            draft = st.session_state.get(
                f"followup_data_"
                f"{thread_id}_"
                f"{index}"
            )

            if draft:

                st.markdown(
                    "##### ✉️ Follow-up draft"
                )

                recipient = draft.get(
                    "recipient"
                )

                draft_subject = draft.get(
                    "subject",
                    ""
                )

                body = draft.get(
                    "body",
                    ""
                )

                if recipient:

                    st.caption(
                        f"To: {recipient}"
                    )

                st.text_input(
                    "Subject",
                    value=draft_subject,
                    key=(
                        f"draft_subject_"
                        f"{thread_id}_"
                        f"{index}"
                    )
                )

                st.text_area(
                    "Message",
                    value=body,
                    height=180,
                    key=(
                        f"draft_body_"
                        f"{thread_id}_"
                        f"{index}"
                    )
                )

                st.info(
                    "Draft only — nothing has been sent."
                )

    else:

        st.caption(
            "No action items identified."
        )

    st.divider()

    # =====================================================
    # Deadlines
    # =====================================================

    st.markdown(
        "#### ⏰ Deadlines"
    )

    deadlines = summary.get(
        "deadlines",
        []
    )

    if deadlines:

        for deadline in deadlines:

            description = deadline.get(
                "description",
                ""
            )

            date = deadline.get(
                "date",
                ""
            )

            owner = deadline.get(
                "owner"
            ) or "Unassigned"

            st.markdown(
                f"""
                <div class="deadline-card">
                    <div class="deadline-title">
                        {description}
                    </div>
                    <div class="deadline-meta">
                        📅 {date}
                        &nbsp;&nbsp;•&nbsp;&nbsp;
                        👤 {owner}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.caption(
            "No deadlines identified."
        )

    # =====================================================
    # Decisions
    # =====================================================

    decisions = summary.get(
        "decisions",
        []
    )

    if decisions:

        st.divider()

        st.markdown(
            "#### 🎯 Decisions"
        )

        for decision in decisions:

            st.markdown(
                f"• {decision}"
            )

    # =====================================================
    # Pending Questions
    # =====================================================

    questions = summary.get(
        "pending_questions",
        []
    )

    if questions:

        st.divider()

        st.markdown(
            "#### ❓ Pending questions"
        )

        for question in questions:

            st.markdown(
                f"• {question}"
            )


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">
                ✦ MailMind
            </div>
            <div class="sidebar-brand-subtitle">
                AI Email Workspace
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-section">Workspace</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "Inbox",
            "Threads",
        ],
        label_visibility="collapsed"
    )

    st.markdown(
        '<div class="sidebar-section">Agent</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "✦ Thread Intelligence"
    )

    st.caption(
        "✦ Action Extraction"
    )

    st.caption(
        "✦ Calendar Actions"
    )

    st.caption(
        "✦ Follow-up Drafting"
    )

    st.markdown(
        '<div class="sidebar-section">Status</div>',
        unsafe_allow_html=True
    )

    st.success(
        "Agent online"
    )


# =========================================================
# Load Data
# =========================================================

emails = load_emails()
threads = load_threads()


# =========================================================
# Main Header
# =========================================================

st.markdown(
    '<div class="page-eyebrow">AI EMAIL WORKSPACE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="page-title">Your inbox, understood.</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="page-subtitle">'
    'Let AI turn long conversations into clear actions, '
    'deadlines and decisions.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# Dashboard Metrics
# =========================================================

action_count = 0

for thread in threads:

    # We only count actions from already-generated summaries.
    thread_id = thread.get(
        "thread_id",
        "thread"
    )

    summary = st.session_state.get(
        f"summary_data_{thread_id}"
    )

    if summary:

        action_count += len(
            summary.get(
                "action_items",
                []
            )
        )


metric1, metric2, metric3 = st.columns(
    3
)

with metric1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Inbox
            </div>
            <div class="metric-value">
                {len(emails)}
            </div>
            <div class="metric-description">
                emails available
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with metric2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Threads
            </div>
            <div class="metric-value">
                {len(threads)}
            </div>
            <div class="metric-description">
                conversations ready for AI
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with metric3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Action items
            </div>
            <div class="metric-value">
                {action_count}
            </div>
            <div class="metric-description">
                extracted by the agent
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# Inbox
# =========================================================

if page == "Inbox":

    st.markdown(
        '<div class="section-title">Inbox</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Your individual messages at a glance.'
        '</div>',
        unsafe_allow_html=True
    )

    if not emails:

        st.info(
            "No emails found in the emails/ folder."
        )

    else:

        for email in emails:

            subject = email.get(
                "subject",
                "No subject"
            )

            sender = email.get(
                "from",
                "Unknown sender"
            )

            email_id = email.get(
                "id",
                "unknown"
            )

            with st.container(
                border=True
            ):

                col1, col2 = st.columns(
                    [7, 1]
                )

                with col1:

                    st.markdown(
                        f"**{subject}**"
                    )

                    st.caption(
                        f"From {sender}"
                    )

                with col2:

                    if st.button(
                        "Open",
                        key=f"open_{email_id}",
                        use_container_width=True
                    ):

                        st.session_state[
                            f"email_open_{email_id}"
                        ] = True

            if st.session_state.get(
                f"email_open_{email_id}",
                False
            ):

                with st.container(
                    border=True
                ):

                    st.caption(
                        f"Message ID: {email_id}"
                    )

                    st.write(
                        email.get(
                            "body",
                            "No email body."
                        )
                    )


# =========================================================
# Threads
# =========================================================

elif page == "Threads":

    st.markdown(
        '<div class="section-title">'
        'Thread Intelligence'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Analyze complete conversations instead of individual emails.'
        '</div>',
        unsafe_allow_html=True
    )

    if not threads:

        st.info(
            "No threads found."
        )

        st.code(
            "threads/\n"
            "└── thread_001.json"
        )

    else:

        for thread in threads:

            thread_id = thread.get(
                "thread_id",
                "thread"
            )

            subject = thread.get(
                "subject",
                "No subject"
            )

            messages = thread.get(
                "messages",
                []
            )

            summary = st.session_state.get(
                f"summary_data_{thread_id}"
            )

            priority = (
                summary.get(
                    "priority",
                    "Medium"
                )
                if summary
                else "Medium"
            )

            with st.container(
                border=True
            ):

                top_col, action_col = st.columns(
                    [7, 2]
                )

                with top_col:

                    st.markdown(
                        f"""
                        <div class="thread-subject">
                            {subject}
                        </div>
                        <div class="thread-meta">
                            🧵 {thread_id}
                            &nbsp;&nbsp;•&nbsp;&nbsp;
                            💬 {len(messages)} messages
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if summary:

                        st.markdown(
                            priority_badge(
                                priority
                            ),
                            unsafe_allow_html=True
                        )

                with action_col:

                    if st.button(
                        "✨ Summarize",
                        key=f"summary_{thread_id}",
                        use_container_width=True
                    ):

                        show_thread_summary(
                            thread
                        )