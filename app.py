import json
import os
import shutil
from pathlib import Path

import streamlit as st

from assistant import draft_reply

st.set_page_config(page_title="Ridgeline Inbox Assistant", page_icon="🔧")
st.title("Ridgeline Plumbing & Drain")
st.caption("AI inbox assistant demo. Paste a customer email and get a draft reply. Fictional company, fake data.")

if not (shutil.which("claude") or os.environ.get("ANTHROPIC_API_KEY")):
    st.error("Install the Claude Code CLI (or set ANTHROPIC_API_KEY), then restart the app.")
    st.stop()

tests = json.loads((Path(__file__).parent / "test_emails.json").read_text(encoding="utf-8"))
samples = {t["subject"]: t["email"] for t in tests}
pick = st.selectbox("Load a sample email", ["(write your own)", *samples])
email = st.text_area("Customer email", samples.get(pick, ""), height=180)

if st.button("Draft reply", type="primary", disabled=not email.strip()):
    with st.spinner("Drafting..."):
        r = draft_reply(email)
    if r["category"] == "emergency":
        st.error("🚨 URGENT: emergency. Call the customer now.")
    if r["flags"]:
        st.warning("**Needs a person:**\n" + "\n".join(f"- {f}" for f in r["flags"]))
    else:
        st.success("Routine: give it a quick read and send.")
    st.caption(f"Category: {r['category']}")
    st.text_area("Draft reply (edit before sending)", r["draft_reply"], height=320)
