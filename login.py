import streamlit as st
import pyrebase

# Your Firebase config here
firebase_config = {
    "apiKey": "AIzaSyBZUxN2z93UzFYqOkvifhWbNnP3aOY0YfE",
    "authDomain": "vergilbot-2274c.firebaseapp.com",
    "databaseURL": "https://vergilbot-2274c-default-rtdb.firebaseio.com/",
    "projectId": "vergilbot-2274c",
    "storageBucket": "vergilbot-2274c.firebasestorage.app",
    "messagingSenderId": "268423869959",
    "appId": "1:268423869959:web:32ab60933ef81042c09ca2",
    "measurementId": "G-3578QXS9SK"
}
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False

def login_ui():
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", key="login_btn"):
       try:
           user = auth.sign_in_with_email_and_password(email, password)
           st.session_state.user = user
           st.success("Logged in!") 
           return
       except:
           st.error("Login failed.")
    st.write("Don't have an account?")
    if st.button("Sign up here", key="go_signup"):
        st.session_state.show_signup = True
        st.rerun()

def signup_ui():
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
    if st.button("Sign up", key="signup_btn"):
        if password != confirm:
            st.error("Passwords do not match.")
            return
        try:
            user = auth.create_user_with_email_and_password(email, password)
            st.success("Account created. Please log in.")
            st.session_state.show_signup = False
            st.rerun()
        except Exception as e:
            st.error(f"Signup failed: {e}")
    if st.button("Back to Login", key="back_to_login"):
        st.session_state.show_signup = False
        st.rerun()

def logout():
    st.session_state.user = None
    st.session_state.show_signup = False
    st.rerun()
