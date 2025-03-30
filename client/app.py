import streamlit as st
from datetime import datetime, timezone
import markdown
import asyncio
import logging
from services.auth_client import register, login
from services.social_graph_client import follow_user, unfollow_user, get_followers, get_following
from services.message_client import post_message, get_messages, repost_message
from config import SEPARATOR

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 40
MAX_MESSAGE_LENGTH = 3000  # Define the maximum length for messages

async def update_cache():
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None

    user = st.session_state.logged_in_user
    if not user:
        logging.info("No storage to update. No user found.")
        return

    if 'token' not in st.session_state:
        logging.error("Token not found in session state.")
        return

    token = st.session_state['token']

    try:
        await get_messages(user, token, request=True)
        await get_followers(user, token, request=True)
        users_following = await get_following(user, token, request=True)
        logging.info("cache updateada colega")  
        for user in users_following:
            await get_messages(user, token, request=True)
    except Exception as e:
        logging.error(f"Error updating storage: {str(e)}") 

# Initialize session state variables
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None  # None means the user is not logged in
if "current_view" not in st.session_state:
    st.session_state.current_view = "login"  # Default view is login/register

# Function to switch views
def switch_view(view):
    st.session_state.current_view = view

def navbar():
    with st.sidebar:
        st.image("logo.png", width=150)
        st.title("Tweety")
        st.markdown("---")
        if st.session_state.logged_in_user is None:
            option = st.radio("Navigate", ["Login/Register"])
        else:
            st.markdown(f"Welcome, {st.session_state.logged_in_user}")
            option = st.radio("Navigate", ["Relationships", "Messages", "Logout"])

        if option == "Login":
            switch_view("login")
        elif option == "Relationships":
            switch_view("relationships")
        elif option == "Messages":
            switch_view("messages")
        elif option == "Logout":
            st.session_state.logged_in_user = None
            switch_view("login")
            st.rerun()

def user_stats():
    token = st.session_state['token']
    
    # Ejecutar la corrutina get_followers
    response_followers = asyncio.run(get_followers(st.session_state.logged_in_user, token))
    
    if response_followers is not None:
        followers = len(response_followers)
    else:
        followers = "error"
        st.error("Failed to retrieve followers.")

    # Si get_following también es async, debes usar asyncio.run para ella también
    response_following = asyncio.run(get_following(st.session_state.logged_in_user, token))  # ← Ajusta si es async
    if response_following is not None:
        following = len(response_following)
    else:
        following = "error"
        st.error("Failed to retrieve following.")

    st.markdown(f"""
                <div style="background-color:rgb(25, 30, 41);padding:5px 20px;margin:10px 0;border-radius:10px;">
                    <h3>📊 Stats</h3>
                    <div style="display:flex;">
                        <p><strong>Followers<strong>: {followers}</p>
                        <p style="margin-left:30px"><strong>Following<strong>: {following}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,)

# Function to handle login
def handle_login(username, password):
    if SEPARATOR in username:
        st.error(f"Username cannot contain '{SEPARATOR}'.")
        return
    token = login(username, password)
    if token:
        st.session_state.logged_in_user = username  # Store the logged-in user
        st.session_state['token'] = token
        asyncio.run(update_cache())
        switch_view("relationships")  # Change to relationships view
        st.rerun()
    else:
        st.error("Invalid username or password!")

# Function to handle registration
def handle_register(username, email, name, password):
    if SEPARATOR in username:
        st.error(f"Username cannot contain '{SEPARATOR}'.")
        return
    if len(username) < MIN_USERNAME_LENGTH:
        st.error(f"Username must have at least {MIN_USERNAME_LENGTH} characters.")
        return
    if len(username) > MAX_USERNAME_LENGTH:
        st.error(f"Username can have at most {MAX_USERNAME_LENGTH} characters.")
        return
    response = register(username, email, name, password)
    if response and response.success:
        st.success("Registration successful! Please log in.")
        switch_view("login")  # Redirect to login view
    else:
        st.error("Registration failed. Try again.")

# Login/Register View
def login_register_view():
    st.title("🔐 Auth")
    option = st.selectbox("Choose an option", ["Login", "Register"])
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    
    if option == "Login":
        if st.button("Login"):
            handle_login(username, password)
    elif option == "Register":
        email = st.text_input("E-mail")
        name = st.text_input("Name")

        if st.button("Register"):
            handle_register(username, email, name, password)

# Relationships Graph View
def relationships_view():
    st.title(f"🤝 Relationships")
    user_stats()
    
    # Actions for the relationships graph
    option = st.selectbox("Choose an action", ["Follow a User", "View Followers", "View Following"])
    if option == "Follow a User":
        user_to_follow = st.text_input("Enter username to follow")
        token = st.session_state['token']
        if st.button("👉 Follow"):
            if SEPARATOR in user_to_follow:
                st.error(f"Username cannot contain '{SEPARATOR}'.")
            else:
                response = follow_user(st.session_state.logged_in_user, user_to_follow, token)
                if response and response.success:
                    st.success(f"You are now following {user_to_follow}.")
                    asyncio.run(update_cache()) 
                    st.rerun()
                else:
                    st.error(f"Failed to follow the user. {response.message}")
    elif option == "View Followers":
        token = st.session_state['token']
        response = asyncio.run(get_followers(st.session_state.logged_in_user, token))
        if response is not None:
            st.markdown("### Your followers:")
            for follower in response:
                st.markdown(f"👥 **{follower}**")
        else:
            st.error("Failed to retrieve followers.")
    elif option == "View Following":
        token = st.session_state['token']
        response = asyncio.run(get_following(st.session_state.logged_in_user, token))
        if response is not None:
            st.markdown("### You are following:")
            for following in response:
                st.markdown(f"👥 **{following}**")
        else:
            st.error("Failed to retrieve following list.")

def format_date_time(iso_timestamp):
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        now = datetime.now(timezone.utc)

        if dt.date() == now.date():
            return f"Today · {dt.strftime('%H:%M')}"
        elif (now.date() - dt.date()).days == 1:
            return f"Yesterday · {dt.strftime('%H:%M')}"
        else:
            return dt.strftime('%b %d, %Y · %H:%M')  # e.g., Mar 21, 2025 · 14:35
    except Exception as e:
        return iso_timestamp  # fallback in case of error

def display_message(msg):
    # Convertir el contenido markdown a HTML
    msg_html = markdown.markdown(msg.content)
    
    if msg.is_repost:
        repost_time = format_date_time(msg.timestamp)
        original_time = format_date_time(msg.original_message_timestamp)
        html = f"""
        <div style="background-color:#2a2f3a; padding:16px; margin:12px 0; border-radius:12px; border-left:4px solid #888; font-family:sans-serif;">
            <div style="font-size:1.1em; color:gray; margin-bottom:8px;">
                🔁 <strong>{msg.user_id}</strong>
            </div>
            <div style="background-color:#1c1f27; padding:12px; border-radius:8px;">
                <table style="width:100%; border-collapse: collapse; border: none;">
                    <tr style="border: none;">
                        <td style="border: none; padding: 0; margin: 0; color:white; font-weight:bold; font-size:1.0em;">{msg.original_message_user_id}</td>
                        <td style="border: none; padding: 0; margin: 0; text-align:right; color:gray;">
                            <small>from {original_time}</small>
                        </td>
                    </tr>
                </table>
                <div style="margin-top: 12px;">{msg_html}</div>
            </div>
            <div style="text-align:right; margin-top:8px;">
                <small style="color:gray;">{repost_time}</small>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
    else:
        timestamp = format_date_time(msg.timestamp)
        html = f"""
        <div style="background-color:#1e222b; padding:16px; margin:12px 0; border-radius:12px; font-family:sans-serif;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h5 style="margin:0; color:white;">{msg.user_id}</h5>
                <span style="font-size:0.85em; color:gray;">{timestamp}</span>
            </div>
            <div style="margin-top: 12px;">{msg_html}</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

def refresh_messages():
    token = st.session_state['token']
    response = asyncio.run(get_following(st.session_state.logged_in_user, token))
    users = [st.session_state.logged_in_user]
    if response is not None:
        for following in response:
            users.append(following)
    else:
        st.error("Failed to retrieve following list.")

    messages = []
    for user in users:
        response = asyncio.run(get_messages(user, token))
        if response:
            # Store the messages in session state to persist them across renders
            for msg in response.messages:
                messages.append(msg)
        else:
            st.error(f"Failed to load messages of user {user}.")

    # Ordenar mensajes por fecha de más reciente a más antiguo
    from datetime import datetime
    messages.sort(key=lambda msg: datetime.fromisoformat(msg.timestamp), reverse=True)

    st.session_state.messages = messages

# Message Posting View
def message_view():
    st.title(f"💬 Posts")
    refresh_messages()

    token = st.session_state['token']
    response_followers = asyncio.run(get_followers(st.session_state.logged_in_user, token))
    
    if response_followers is not None:
        followers = len(response_followers)
    else:
        followers = 0
        st.error("Failed to retrieve amount of followers.")
    
    # Text area for writing a new message
    with st.form("post_form"):
        content = st.text_area(
            "Write a message:",
            max_chars = min(MAX_MESSAGE_LENGTH, (followers + 1) * 300),
            placeholder="What's on your mind?",
        )
        submitted = st.form_submit_button("Post 🚀")
        if submitted:
            response = post_message(st.session_state.logged_in_user, content, token)

            if response and response.success:
                refresh_messages()
                asyncio.run(update_cache())
                st.success(response.message)
            else:
                msg = ""
                if response:
                    msg = response.message
                st.error(f"Failed to post the message. {msg}")

    if st.button("🔄 Refresh Messages"):
        refresh_messages()
        asyncio.run(update_cache())
    
    # Ensure session state has a list of messages
    if "messages" in st.session_state:
        st.markdown("#### 📧 Messages:")
        for idx, msg in enumerate(st.session_state.messages):
            display_message(msg)
            
            # Create a unique key for each button
            button_key = f"repost_button_{idx}"
            
            # If the button is clicked, update session state
            if st.button("🔁 Repost", key=button_key):
                st.session_state.repost_message_id = msg.message_id
                st.session_state.repost_clicked = True
            st.markdown("---")

    # Handle repost functionality after all buttons are rendered
    if st.session_state.get("repost_clicked", False):
        original_message_id = st.session_state.repost_message_id
        repost_response = repost_message(st.session_state.logged_in_user, original_message_id, token)

        if repost_response and repost_response.success:
            st.success("Message reposted successfully!")
            st.session_state.repost_clicked = False
            asyncio.run(update_cache())
            st.rerun()
        else:
            msg = ""
            if repost_response:
                msg = repost_response.message
            st.error(f"Failed to repost the message. {msg}")
        # Reset repost state after handling
        st.session_state.repost_clicked = False

# Render the appropriate view based on session state
navbar()
if st.session_state.current_view == "login":
    login_register_view()
elif st.session_state.current_view == "relationships":
    relationships_view()
elif st.session_state.current_view == "messages":
    message_view()