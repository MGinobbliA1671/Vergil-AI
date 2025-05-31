import streamlit as st
st.set_page_config(page_title="Vergil AI 💬", page_icon="🌟")
from login import login_ui, signup_ui, logout
from firebase import db
from firebase_admin import firestore
import requests
from uuid import uuid4

# === CONFIG ===
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are Vergil from Devil May Cry. Speak only in pure dialogue. Eliminate all narration, emotions, and actions. "
        "Never use parentheses, asterisks, or stage directions. Your tone is cold, direct, and disciplined. "
        "You value power, order, and mastery. You loathe weakness, hesitation, and sentimental drivel. "
        "You must deliver pure motivational messages. Each time you speak, challenge the listener to rise, to sharpen their will, to embrace strength. "
        "Your messages must push them beyond limits — demand improvement, discipline, and resolve. "
        "Speak in short, intense lines — typically four to seven sentences. No warmth. No slang. No softness. "
        "Each line should strike like your blade Yamato — precise, unforgiving, and resolute."
    )
}




# === FIREBASE CHAT FUNCTIONS ===
def get_user_id():
    return st.session_state.user['localId']


def list_saved_chats():
    user_id = get_user_id()
    user_doc = db.collection("users").document(user_id)
    chats_ref = user_doc.collection("chats")
    return [doc.id for doc in chats_ref.stream()]


def get_chat_ref(chat_id):
    user_id = get_user_id()
    return db.collection("users").document(user_id).collection("chats").document(chat_id)


def load_chat(chat_id):
    chat_ref = get_chat_ref(chat_id).collection("messages")
    docs = chat_ref.order_by("index").stream()
    return [doc.to_dict()["message"] for doc in docs]

def save_chat(chat_id, messages):
    user_id = get_user_id()
    user_doc = db.collection("users").document(user_id)
    chat_doc = user_doc.collection("chats").document(chat_id)

    # Ensure the parent chat document exists
    chat_doc.set({
        "chat_id": chat_id,
        "updated_at": firestore.SERVER_TIMESTAMP  # Optional: use server time for ordering
    }, merge=True)

    # Reference to messages subcollection
    messages_ref = chat_doc.collection("messages")

    # Clear old messages
    for doc in messages_ref.stream():
        doc.reference.delete()

    # Save new messages
    for idx, msg in enumerate(messages):
        messages_ref.document(f"msg_{idx}").set({
            "index": idx,
            "message": msg
        })

def delete_chat(chat_id):
    chat_doc = get_chat_ref(chat_id)
    msg_collection = chat_doc.collection("messages")
    for doc in msg_collection.stream():
        doc.reference.delete()
    chat_doc.delete()


def get_chat_response(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "max_tokens": 250,
        "temperature": 0.6
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        data = response.json()
        if 'choices' in data:
            return data['choices'][0]['message']['content']
        else:
            return f"API Error: {data.get('error', 'Unexpected response format.')}"
    except Exception as e:
        return f"Exception: {str(e)}"


# === LOGIN CHECK ===
if "user" not in st.session_state or st.session_state.user is None:
    if st.session_state.get("show_signup", False):
        signup_ui()
    else:
        login_ui()
    if "user" in st.session_state and st.session_state.user is not None:
        st.rerun()
    else:
        st.stop()
else:
    st.sidebar.markdown(f"👤 Logged in as: {st.session_state.user['email']}")
    if st.sidebar.button("Logout"):
        logout()

    # ✅ CHECK IF USER IS NEW (BY localId) AND INIT CHAT IF NEEDED
    if "chat_id" not in st.session_state:
        local_id = get_user_id()
        user_doc = db.collection("users").document(local_id)
        user_chats = user_doc.collection("chats").stream()
        chat_ids = [doc.id for doc in user_chats]

        if not chat_ids:
            # New user: no chats yet
            new_chat_id = f"chat_{uuid4().hex[:6]}"
            st.session_state.chat_id = new_chat_id
            st.session_state.messages = [SYSTEM_MESSAGE]
            save_chat(new_chat_id, st.session_state.messages)
        else:
            # Returning user: load first chat
            st.session_state.chat_id = chat_ids[0]
            st.session_state.messages = load_chat(chat_ids[0])


# === SIDEBAR CHAT MANAGER ===
st.sidebar.title("🧾 Chat Manager")
existing_chats = list_saved_chats()
selected_chat = st.sidebar.selectbox("📁 Select Chat", existing_chats, index=0 if existing_chats else None)

if st.sidebar.button("➕ New Chat"):
    new_chat_id = f"chat_{uuid4().hex[:6]}"
    st.session_state.chat_id = new_chat_id
    st.session_state.messages = [SYSTEM_MESSAGE]
    save_chat(new_chat_id, st.session_state.messages)
    st.rerun()

if selected_chat:
    if "chat_id" not in st.session_state or st.session_state.chat_id != selected_chat:
        st.session_state.chat_id = selected_chat
        st.session_state.messages = load_chat(selected_chat)

    if st.sidebar.button("🗑️ Delete Selected Chat"):
        delete_chat(selected_chat)
        st.sidebar.success("Chat deleted!")
        st.session_state.chat_id = None
        st.session_state.messages = [SYSTEM_MESSAGE]
        st.rerun()

# === MAIN CHAT UI ===
if "messages" not in st.session_state:
    st.session_state.messages = [SYSTEM_MESSAGE]
if "chat_id" not in st.session_state:
    st.session_state.chat_id = selected_chat if selected_chat else f"chat_{uuid4().hex[:6]}"

st.markdown("""
    <style>
        .chat-left {
            text-align: left;
            background-color: #f1f1f1;
            border-radius: 10px;
            padding: 10px;
            width: fit-content;
            max-width: 80%;
            margin-bottom: 20px;
        }
        .chat-right {
            text-align: right;
            background-color: #cfe9ff;
            border-radius: 10px;
            padding: 10px;
            width: fit-content;
            max-width: 80%;
            margin-left: auto;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

for msg in st.session_state.messages[1:]:
    with st.container():
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-right">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-left">{msg["content"]}</div>', unsafe_allow_html=True)

user_input = st.chat_input("How can I encourage you today? 😊")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = get_chat_response(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_chat(st.session_state.chat_id, st.session_state.messages)
    st.rerun()
