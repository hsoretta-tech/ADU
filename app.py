import streamlit as st
import json
import random
import os
import re
from typing import Optional

st.set_page_config(page_title="Python Challenge Wall", layout="centered")

# --- Challenge data ---
challenges = {
    "Easy": [
        {"id": 1, "task": "Print 'Hello, World!'", "answer": "print('Hello, World!')"},
        {"id": 2, "task": "Create a variable x with value 10", "answer": "x = 10"},
        {"id": 3, "task": "Write a loop that prints numbers 1 to 5", "answer": "for i in range(1,6): print(i)"}
    ],
    "Intermediate": [
        {"id": 4, "task": "Write a function that returns the square of a number", "answer": "def square(n): return n*n"},
        {"id": 5, "task": "Create a list of 5 fruits and print the second one", "answer": "fruits = ['apple','banana','cherry','date','fig']; print(fruits[1])"},
        {"id": 6, "task": "Write a program that counts vowels in a string", "answer": "s=input(); print(sum(1 for c in s if c.lower() in 'aeiou'))"}
    ],
    "Advanced": [
        {"id": 7, "task": "Create a class Dog with attributes name and age", "answer": "class Dog:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age"},
        {"id": 8, "task": "Write a program that fetches data from an API (mocked)", "answer": "import requests; data = requests.get('https://api.example.com').json()"},
        {"id": 9, "task": "Implement a recursive factorial function", "answer": "def fact(n): return 1 if n<=1 else n*fact(n-1)"}
    ]
}

PROGRESS_FILE = "progress.json"

# --- Utilities ---
def save_progress():
    """Save current player state to disk (progress.json)."""
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.player, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Failed to save progress: {e}")


def load_progress() -> Optional[dict]:
    """Load player state from disk if available."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def normalize_code(s: str) -> str:
    """
    Normalize code/text for comparison:
    - remove all whitespace (spaces, tabs, newlines)
    - collapse semicolons and optional trailing spaces
    - normalize quote types
    """
    if s is None:
        return ""
    # unify quotes (double -> single)
    s = s.replace('"', '"')
    # remove comments (simple inline # comments)
    s = re.sub(r"#.*", "", s)
    # remove whitespace
    s = re.sub(r"\s+", "", s)
    # remove optional trailing semicolons
    s = s.strip().rstrip(";")
    return s


def is_correct_submission(submitted: str, expected: str) -> bool:
    """Check if a submitted answer matches the expected one after normalization."""
    return normalize_code(submitted) == normalize_code(expected)

# --- Initialize session state ---
if "player" not in st.session_state:
    # default
    st.session_state.player = {"name": "", "xp": 0, "completed": []}
# load persisted progress if available and session has no name
if not st.session_state.player.get("name"):
    data = load_progress()
    if data and isinstance(data, dict):
        st.session_state.player.update(data)

player = st.session_state.player

# --- UI ---
st.title("🐍 Python Challenge Wall")
st.subheader("A differentiated coding challenge experience")

# Player setup
if not player.get("name"):
    name = st.text_input("Enter your name to begin:")
    if st.button("Start"):
        if not name or name.strip() == "":
            st.warning("Please enter a valid name.")
        else:
            player["name"] = name.strip()
            save_progress()
            st.experimental_rerun()
    st.stop()
else:
    st.success(f"Welcome, {player['name']}! XP: {player['xp']}")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Choose Challenge", "View Progress", "Reset Progress"])

if page == "Choose Challenge":
    level = st.selectbox("Select difficulty level:", ["Easy", "Intermediate", "Advanced"])
    # choose an available challenge (not completed)
    available = [c for c in challenges[level] if c["id"] not in player["completed"]]
    if available:
        challenge = random.choice(available)
        st.markdown(f"### {level} Challenge")
        st.write(challenge["task"])
        attempt = st.text_area("Enter your Python code here (textual submission):", height=160)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit"):
                if is_correct_submission(attempt, challenge["answer"]):
                    st.success("✅ Correct! +10 XP")
                    player["xp"] = player.get("xp", 0) + 10
                    player.setdefault("completed", []).append(challenge["id"])
                    save_progress()
                    st.experimental_rerun()
                else:
                    st.error("❌ Incorrect. Try again!")
        with col2:
            if st.button("Show Answer"):
                st.info("Correct answer (for reference):")
                st.code(challenge["answer"])
    else:
        st.info(f"All {level} challenges completed!")

elif page == "View Progress":
    st.markdown(f"### Progress for {player.get('name')}")
    st.write(f"**XP:** {player.get('xp', 0)}")
    for level_name in challenges:
        total = len(challenges[level_name])
        done = len([c for c in challenges[level_name] if c["id"] in player.get("completed", [])])
        fraction = done / total if total > 0 else 0.0
        st.write(f"{level_name}: {done}/{total} completed")
        st.progress(fraction)

elif page == "Reset Progress":
    if st.button("Reset All Progress"):
        st.session_state.player = {"name": "", "xp": 0, "completed": []}
        save_progress()
        st.experimental_rerun()