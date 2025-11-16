import streamlit as st
import json
import random
import os
import re
import ast
import io
import tokenize
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
        {"id": 7, "task": "Create a class Dog with attributes name and age", 
         "answer": "class Dog:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age"},
        {"id": 8, "task": "Write a program that fetches data from an API (mocked)", 
         "answer": "import requests; data = requests.get('https://api.example.com').json()"},
        {"id": 9, "task": "Implement a recursive factorial function", 
         "answer": "def fact(n): return 1 if n<=1 else n*fact(n-1)"}
    ]
}

PROGRESS_FILE = "progress.json"

# --- Utilities ---
def save_progress():
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.player, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Failed to save progress: {e}")


def load_progress() -> Optional[dict]:
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


# --- Code normalization and checking ---
def _strip_ast_positions(node):
    for n in ast.walk(node):
        for attr in ("lineno", "col_offset", "end_lineno", "end_col_offset"):
            if hasattr(n, attr):
                try:
                    setattr(n, attr, None)
                except Exception:
                    pass


def normalize_code_tokens(s: str) -> str:
    if s is None:
        return ""
    s = s.replace('"', "'")
    try:
        out_tokens = []
        sio = io.StringIO(s)
        for tok in tokenize.generate_tokens(sio.readline):
            toknum = tok.type
            tokval = tok.string
            if toknum == tokenize.COMMENT:
                continue
            out_tokens.append(tokval)
        s = "".join(out_tokens)
    except Exception:
        s = re.sub(r"#.*", "", s)

    # FIXED LINE (your original line was broken)
    s = re.sub(r"\s+", "", s)

    s = s.strip().rstrip(";")
    return s


def normalize_code_ast_or_tokens(s: str) -> str:
    if s is None:
        return ""
    try:
        tree = ast.parse(s)
        _strip_ast_positions(tree)
        return ast.dump(tree, include_attributes=False)
    except Exception:
        return normalize_code_tokens(s)


def is_correct_submission(submitted: str, expected: str) -> bool:
    sub_norm = normalize_code_ast_or_tokens(submitted)
    exp_norm = normalize_code_ast_or_tokens(expected)
    return sub_norm == exp_norm


# --- Initialize session state ---
if "player" not in st.session_state:
    st.session_state.player = {"name": "", "xp": 0, "completed": []}

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
    available = [c for c in challenges[level] if c["id"] not in player["completed"]]

    if available:
        challenge = random.choice(available)
        st.markdown(f"### {level} Challenge")
        st.write(challenge["task"])

        attempt = st.text_area("Enter your Python code here:", height=160)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit"):
                if is_correct_submission(attempt, challenge["answer"]):
                    st.success("✅ Correct! +10 XP")
                    player["xp"] += 10
                    player["completed"].append(challenge["id"])
                    save_progress()
                    st.experimental_rerun()
                else:
                    st.error("❌ Incorrect. Try again!")

        with col2:
            if st.button("Show Answer"):
                st.info("Correct answer:")
                st.code(challenge["answer"])

    else:
        st.info(f"All {level} challenges completed!")


elif page == "View Progress":
    st.markdown(f"### Progress for {player['name']}")
    st.write(f"**XP:** {player['xp']}")

    for level_name in challenges:
        total = len(challenges[level_name])
        done = len([c for c in challenges[level_name] if c["id"] in player.get("completed", [])])
        fraction = done / total if total else 0

        st.write(f"{level_name}: {done}/{total} completed")
        st.progress(fraction)

elif page == "Reset Progress":
    if st.button("Reset All Progress"):
        st.session_state.player = {"name": "", "xp": 0, "completed": []}
        save_progress()
        st.experimental_rerun()
