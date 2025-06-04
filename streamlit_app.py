import os, datetime
import streamlit as st
import pandas as pd
import plotly.express as px

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ──────────  UI  ──────────
st.set_page_config(page_title="🌟 Goal Creator", layout="centered")
st.title("🌟 Goal Creator Chat Assistant")

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
os.environ["OPENAI_API_KEY"] = openai_api_key

# ──────────  STATE  ──────────
s = st.session_state
s.setdefault("chat", [])
s.setdefault("step", 1)
s.setdefault("goal_focus", "")
s.setdefault("booted", False)

# ──────────  HELPERS  ──────────
def llm():
    return init_chat_model(
        "gpt-4o-mini",
        model_provider="openai",
        openai_api_key=openai_api_key,
    )

def ai(text: str):
    st.chat_message("assistant").write(text)
    s.chat.append(AIMessage(content=text))

def user(text: str):
    st.chat_message("user").write(text)
    s.chat.append(HumanMessage(content=text))

# ──────────  REPLAY  ──────────
for msg in s.chat:
    st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant").write(msg.content)

# ──────────  FLOW  ──────────
def handle(inp: str):
    user(inp)
    model = llm()

    # 1️⃣  area
    if s.step == 1:
        s.step = 2
        area = inp.strip().lower()
        ai(f"Great — focusing on **{area}** is a powerful step 💪")
        ai("**Step 1 of 6: Define the Focus 🎯**")
        ai(f"What specific thing would you like to improve in **{area}**?")
        return

    # 2️⃣  goal + first why
    if s.step == 2:
        s.goal_focus = inp.strip()
        s.step = 3
        ai("**Step 2 of 6: Explore Your Why 🪄**")
        ai(f"Why is this goal — *{s.goal_focus}* — important to you?")
        return

    # 3️⃣ second why
    if s.step == 3:
        s.step = 4
        ai("**Step 3 of 6: Uncover Your Values 💖**")
        ai("And why does that matter to you at a deeper level?")
        return

    # 4️⃣ third why + obstacles
    if s.step == 4:
        s.step = 5
        ai("**Step 4 of 6: Identify Challenges 🚧**")
        ai("What obstacles or patterns usually make this goal hard to achieve?")
        return

    # 5️⃣ ask to summarise
    if s.step == 5:
        s.step = 6
        ai(
            "Thanks for sharing openly. ✨\n\n"
            "Would you like a concise analysis before we craft some goal ideas?\n"
            "Type **yes** to continue."
        )
        return

    # 6️⃣ simplified consultant+psychologist analysis
    if s.step == 6 and "yes" in inp.lower():
        s.step = 7
        summary_prompt = """
You are a consultant (strategy) + psychologist (behaviour).  
Write a SIMPLE analysis anyone can understand. 4 sections only:

🌟 Core Motivation  
🔍 Hidden Patterns  
🪜 Leverage Points  
⚠️ Possible Risks  

Each section: max 2 short sentences, plain language, emojis as headers.  
Finish with:  
“Does this feel accurate? 😊  If so, I'll suggest 4 goal ideas.”"""
        resp = model.invoke([SystemMessage(content=summary_prompt)] + s.chat)
        ai(resp.content)
        return

    # 7️⃣ suggest 4 strategic goals
    if s.step == 7 and "yes" in inp.lower():
        s.step = 8
        suggest_prompt = """
Act like a top-tier strategy consultant. Suggest **exactly 4** inspiring but realistic goals that align with the analysis.  
Each goal: • start with emoji • ≤18 words • clear outcome.  
Finish with: "Which goal feels right for you to pursue first?" """
        resp = model.invoke([SystemMessage(content=suggest_prompt)] + s.chat)
        ai(resp.content)
        return

    # 8️⃣ SMART summary + ask for roadmap
    if s.step == 8:
        chosen = inp.strip()
        s.chosen_goal = chosen
        s.step = 9
        smart_prompt = f"""
Create a SMART breakdown (Specific • Measurable • Achievable • Relevant • Time-bound) for this goal:

**{chosen}**

One short bullet per SMART letter, plain language, emoji headers.  
End with: "Shall I draft a friendly 4-week roadmap?" """
        resp = model.invoke([SystemMessage(content=smart_prompt)] + s.chat)
        ai(resp.content)
        return

    # 9️⃣ roadmap (on yes)
    if s.step == 9 and "yes" in inp.lower():
        s.step = 10
        ai("Great! Here's a doable 4-week roadmap ⬇️")

        # dynamic Gantt
        today = datetime.date.today()
        one_week = datetime.timedelta(days=7)
        tasks = [
            {"Task": "Week 1 – Lay the foundation",   "Start": today,                 "Finish": today + one_week - datetime.timedelta(days=1)},
            {"Task": "Week 2 – First key action",     "Start": today + one_week,      "Finish": today + 2*one_week - datetime.timedelta(days=1)},
            {"Task": "Week 3 – Review & iterate",     "Start": today + 2*one_week,    "Finish": today + 3*one_week - datetime.timedelta(days=1)},
            {"Task": "Week 4 – Consolidate & reflect","Start": today + 3*one_week,    "Finish": today + 4*one_week - datetime.timedelta(days=1)},
        ]
        df = pd.DataFrame(tasks)
        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Task",
                          title="4-Week Roadmap (starts today)")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig)

        ai("If you'd like a vivid picture of success, type **show me**.")
        return

    # 🔟 vision
    if s.step == 10 and "show me" in inp.lower():
        vision_prompt = "Write a vivid, sensory scene of the user succeeding at their goal."
        vision = model.invoke([SystemMessage(content=vision_prompt)] + s.chat)
        ai("Here’s what success could feel like:")
        ai(vision.content)
        s.step = 11
        return

# ────────── welcome ──────────
if openai_api_key.startswith("sk-") and not s.booted:
    ai(
        "Hi! I'm your **Goal Creator Assistant** 🌟\n\n"
        "Which life area would you like to improve?\n"
        "_E.g. Health · Relationships · Career · Finances · Self-development_\n\n"
        "**Tell me your focus area to start.**"
    )
    s.booted = True

# ────────── input ──────────
if openai_api_key.startswith("sk-"):
    msg = st.chat_input("Your response…")
    if msg:
        handle(msg)
else:
    st.warning("Please enter your OpenAI API key to start.", icon="⚠️")