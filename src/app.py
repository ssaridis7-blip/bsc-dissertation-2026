"""
Streamlit Chat Interface — v5
==============================
NexusFlow CRM Intelligence Assistant
Deep Sea & Intelligence Violet design system.
"""

import streamlit as st
import time
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.rag_pipeline import initialize_rag_system, query_rag

# ─── Page Configuration ──────────────────────────────────────────
st.set_page_config(
    page_title="NexusFlow CRM Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Load CRM data for activity feed ─────────────────────────────
CRM_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_crm_data.json")
with open(CRM_DATA_PATH, "r", encoding="utf-8") as f:
    CRM_DATA = json.load(f)

# ─── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-base: #080A0F;
        --bg-surface: #111622;
        --bg-elevated: #161D2E;
        --border-subtle: #1F2937;
        --border-accent: #2D3748;
        --accent-violet: #8B5CF6;
        --accent-cyan: #06B6D4;
        --accent-green: #10B981;
        --accent-amber: #F59E0B;
        --accent-rose: #F43F5E;
        --text-primary: #F9FAFB;
        --text-secondary: #9CA3AF;
        --text-muted: #4B5563;
    }

    .stApp {
        background: var(--bg-base) !important;
        font-family: 'DM Sans', sans-serif;
    }
    .block-container { padding-top: 1rem !important; }

    /* ── Sidebar Toggle Button ── */
    button[data-testid="stSidebarCollapsedControl"] {
        color: white !important;
        background: rgba(139, 92, 246, 0.3) !important;
        border: 1px solid rgba(139, 92, 246, 0.5) !important;
    }

    /* ── Status Bar ── */
    .status-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(17, 22, 34, 0.7);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 0.55rem 1.2rem;
        margin-bottom: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
    }
    .status-left {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        color: var(--text-muted);
    }
    .status-dot {
        width: 7px; height: 7px;
        background: var(--accent-green);
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
        animation: pulse-dot 2s ease-in-out infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { box-shadow: 0 0 6px rgba(16, 185, 129, 0.5); }
        50% { box-shadow: 0 0 12px rgba(16, 185, 129, 0.8); }
    }
    .status-right {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        color: var(--text-muted);
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: var(--bg-surface) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text-secondary) !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent;
        border: none;
        border-left: 2px solid transparent;
        color: var(--text-secondary);
        font-family: 'DM Sans', sans-serif;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 0.55rem 0.9rem;
        border-radius: 0 6px 6px 0;
        transition: all 0.2s ease;
        text-align: left;
        width: 100%;
        margin-bottom: 4px;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(139, 92, 246, 0.06);
        border-left: 2px solid var(--accent-violet);
        color: var(--text-primary);
    }

    /* ── Header ── */
    .header-block {
        background: linear-gradient(135deg, var(--bg-surface) 0%, var(--bg-elevated) 100%);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.8rem 2.2rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    .header-block::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-violet), var(--accent-cyan), var(--accent-violet));
        background-size: 200% 100%;
        animation: gradient-shift 4s ease infinite;
    }
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    .header-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.03em;
    }
    .header-sub {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.88rem;
        color: var(--text-muted);
        margin: 0.3rem 0 0 0;
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: rgba(17, 22, 34, 0.6);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1rem 1rem 0.8rem;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-violet), var(--accent-cyan));
    }
    .metric-number {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
    }
    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.35rem;
    }
    .metric-trend-up {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: var(--accent-green);
        margin-top: 0.25rem;
    }
    .metric-trend-neutral {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: var(--accent-amber);
        margin-top: 0.25rem;
    }

    /* ── Chat Messages ── */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 0.6rem 0 !important;
    }
    .stChatMessage [data-testid="chatAvatarIcon-user"] {
        background: linear-gradient(135deg, var(--accent-violet), #6D28D9) !important;
    }
    .stChatMessage [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, var(--accent-cyan), #0891B2) !important;
    }
    .stChatMessage .stMarkdown p,
    .stChatMessage .stMarkdown li {
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.9rem;
        line-height: 1.75;
    }
    .stChatMessage .stMarkdown strong {
        color: #E5E7EB !important;
    }

    /* ── Source Pills ── */
    .source-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(6, 182, 212, 0.06);
        border: 1px solid rgba(6, 182, 212, 0.18);
        color: var(--accent-cyan);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.68rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        margin: 2px 3px;
    }
    .sources-row {
        margin-top: 0.5rem;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 2px;
    }
    .sources-label {
        color: var(--text-muted);
        font-size: 0.65rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        margin-right: 4px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    /* ── Response Time ── */
    .resp-time {
        color: var(--text-muted);
        font-size: 0.65rem;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 0.25rem;
        opacity: 0.7;
    }

    /* ── Chat Input ── */
    .stChatInput > div {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
    }
    .stChatInput > div:focus-within {
        border-color: rgba(139, 92, 246, 0.4) !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.06) !important;
    }
    .stChatInput textarea {
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    .stSpinner > div { color: var(--accent-violet) !important; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: var(--border-subtle); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem;">
        <div style="font-family: 'DM Sans', sans-serif; font-size: 1.3rem; font-weight: 700; color: #F9FAFB; letter-spacing: -0.02em;">
            💼 NexusFlow
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; color: #4B5563; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 2px;">
            CRM Intelligence Assistant
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### Quick Queries")
    example_queries = [
        ("👤", "Who is James Mitchell?"),
        ("📋", "What invoices are pending?"),
        ("📊", "Show me deals in negotiation"),
        ("💰", "What pricing tiers are available?"),
        ("🔄", "Latest interactions with GreenLeaf Energy"),
        ("🏢", "Tell me about David Okafor's account"),
        ("⚠️", "Which contacts have churned?"),
        ("📖", "What is the onboarding process?"),
        ("🤖", "How does the AI Analytics module work?"),
        ("🎯", "What is our win-back strategy?"),
    ]
    for icon, query in example_queries:
        if st.button(f"{icon}  {query}", key=f"ex_{query}", use_container_width=True):
            st.session_state.pending_query = query

    st.markdown("---")
    st.markdown("""
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #4B5563; line-height: 2.2;">
        <div style="color: #9CA3AF; font-weight: 600; font-size: 0.6rem; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 4px;">SYSTEM CONFIG</div>
        <span style="color: #10B981;">●</span> LLM → GPT-4o-mini<br>
        <span style="color: #10B981;">●</span> Embed → text-embedding-3-small<br>
        <span style="color: #10B981;">●</span> VectorDB → ChromaDB<br>
        <span style="color: #10B981;">●</span> Framework → LangChain
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    if st.button("↻  Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chain = None
        st.rerun()

    st.markdown("")
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem;">
        <span style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.15); color: #7C3AED; padding: 3px 10px; border-radius: 4px; font-size: 0.58rem; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.1em; text-transform: uppercase; opacity: 0.7;">🔬 Research Prototype · MSc 2026</span>
    </div>
    """, unsafe_allow_html=True)

# ─── Initialize RAG System ───────────────────────────────────────
@st.cache_resource
def get_rag_chain():
    return initialize_rag_system(force_rebuild=False)

if "chain" not in st.session_state or st.session_state.chain is None:
    with st.spinner("Initializing RAG system..."):
        st.session_state.chain = get_rag_chain()

# ─── Status Bar ──────────────────────────────────────────────────
st.markdown("""
<div class="status-bar">
    <div class="status-left">
        <span class="status-dot"></span>
        <span>System Online</span>
        <span style="color: #2D3748;">|</span>
        <span>RAG Pipeline Active</span>
        <span style="color: #2D3748;">|</span>
        <span>97 vectors indexed</span>
    </div>
    <div class="status-right">
        <span>MSc Thesis 2026</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Main Layout ─────────────────────────────────────────────────
col_main, col_activity = st.columns([3, 1])

with col_main:
    st.markdown("""
    <div class="header-block">
        <div class="header-title">NexusFlow CRM Assistant</div>
        <div class="header-sub">Retrieval-Augmented Generation · Business Intelligence · CRM Data Integration</div>
    </div>
    """, unsafe_allow_html=True)

    total_pipeline = sum(d["value"] for d in CRM_DATA["deals"] if d["stage"] != "Lost")
    pending_invoices = sum(1 for i in CRM_DATA["invoices"] if i["status"] == "Pending")
    avg_score = round(sum(c["lead_score"] for c in CRM_DATA["contacts"]) / len(CRM_DATA["contacts"]), 1)

    st.markdown(f"""
    <div style="display: flex; gap: 0.7rem; margin-bottom: 1.2rem;">
        <div style="flex: 3; display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.7rem;">
            <div class="metric-card">
                <div class="metric-number">{len(CRM_DATA["contacts"])}</div>
                <div class="metric-label">Contacts</div>
                <div class="metric-trend-up">↑ 4 active customers</div>
            </div>
            <div class="metric-card">
                <div class="metric-number">£{total_pipeline:,.0f}</div>
                <div class="metric-label">Pipeline Value</div>
                <div class="metric-trend-up">↑ 7 active deals</div>
            </div>
            <div class="metric-card">
                <div class="metric-number">{pending_invoices}</div>
                <div class="metric-label">Pending Invoices</div>
                <div class="metric-trend-neutral">⬡ awaiting payment</div>
            </div>
        </div>
        <div style="width: 1px; background: #1F2937; margin: 0 0.2rem;"></div>
        <div style="flex: 2; display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.7rem;">
            <div class="metric-card">
                <div class="metric-number">{avg_score}</div>
                <div class="metric-label">Avg Lead Score</div>
                <div class="metric-trend-up">↑ healthy pipeline</div>
            </div>
            <div class="metric-card">
                <div class="metric-number">97</div>
                <div class="metric-label">Vector Chunks</div>
                <div class="metric-trend-neutral">⬡ 4 knowledge docs</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_activity:
    st.markdown("#### ⚡ Recent Activity")
    sorted_interactions = sorted(CRM_DATA["interactions"], key=lambda x: x["date"], reverse=True)

    for interaction in sorted_interactions[:8]:
        contact = next((c for c in CRM_DATA["contacts"] if c["id"] == interaction["contact_id"]), None)
        name = f"{contact['first_name']} {contact['last_name']}" if contact else "Unknown"
        company = contact["company"] if contact else ""
        type_icon = {"Email": "✉️", "Call": "📞", "Meeting": "🤝"}.get(interaction["type"], "📌")
        sentiment_color = {"Positive": "🟢", "Neutral": "🔵", "Negative": "🔴"}.get(interaction["sentiment"], "⚪")

        st.markdown(f"{sentiment_color} {type_icon} **{name}**  \n{interaction['subject']}  \n`{interaction['date']} · {company}`")

# ─── Chat Section ────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            pills = "".join([f'<span class="source-pill">⬡ {s}</span>' for s in message["sources"]])
            st.markdown(
                f'<div class="sources-row"><span class="sources-label">Retrieved from:</span>{pills}</div>',
                unsafe_allow_html=True
            )
        if "response_time" in message:
            st.markdown(
                f'<div class="resp-time">⏱ {message["response_time"]:.2f}s · gpt-4o-mini · top-5 retrieval</div>',
                unsafe_allow_html=True
            )

# Input handling
if "pending_query" in st.session_state:
    prompt = st.session_state.pending_query
    del st.session_state.pending_query
else:
    prompt = st.chat_input("Ask about contacts, deals, invoices, or company knowledge...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        start_time = time.time()

        with st.spinner("Searching knowledge base..."):
            result = query_rag(st.session_state.chain, prompt)

        response_time = time.time() - start_time

        st.markdown(result["answer"])

        source_names = [s["source"] for s in result["sources"]]
        if source_names:
            pills = "".join([f'<span class="source-pill">⬡ {s}</span>' for s in source_names])
            st.markdown(
                f'<div class="sources-row"><span class="sources-label">Retrieved from:</span>{pills}</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div class="resp-time">⏱ {response_time:.2f}s · gpt-4o-mini · top-5 retrieval</div>',
            unsafe_allow_html=True
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": source_names,
        "response_time": response_time
    })