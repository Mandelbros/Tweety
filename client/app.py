import streamlit as st
from datetime import datetime, timezone
import pytz
from services.auth_client import register, login
from services.social_graph_client import follow_user, unfollow_user, get_followers, get_following
from services.message_client import post_message, get_messages, repost_message

MAX_MESSAGE_LENGTH = 300  # Define the maximum length for messages

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
    response_followers = get_followers(st.session_state.logged_in_user)
    if response_followers:
        followers = len(response_followers.followers)
    else:
        followers = "error"
        st.error("Failed to retrieve followers.")

    response_following = get_following(st.session_state.logged_in_user)
    if response_following:
        following = len(response_following.following)
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
    token = login(username, password)
    if token:
        st.session_state.logged_in_user = username  # Store the logged-in user
        st.session_state['token'] = token
        st.success("Logueado Correctamente")
        switch_view("relationships")  # Change to relationships view
    else:
        st.error("Invalid username or password!")

# Function to handle registration
def handle_register(username, email, name, password):
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
        if st.button("👉 Follow"):
            response = follow_user(st.session_state.logged_in_user, user_to_follow)
            if response and response.success:
                st.success(f"You are now following {user_to_follow}.")
            else:
                st.error("Failed to follow the user.")
    elif option == "View Followers":
        response = get_followers(st.session_state.logged_in_user)
        if response:
            st.markdown("### Your followers:")
            for follower in response.followers:
                st.markdown(f"👥 **{follower}**")
        else:
            st.error("Failed to retrieve followers.")
    elif option == "View Following":
        response = get_following(st.session_state.logged_in_user)
        if response:
            st.markdown("### You are following:")
            for following in response.following:
                st.markdown(f"👥 **{following}**")
        else:
            st.error("Failed to retrieve following list.")

def format_date_time(iso_timestamp):
    # Assume Havana time (Cuba Standard Time - CST)
    havana_tz = pytz.timezone('America/Havana')
    naive_dt = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    aware_dt = havana_tz.localize(naive_dt)
    return aware_dt.strftime("%d/%m/%Y %H:%M:%S %Z%z")

def display_message(msg):
    if msg.is_repost:
        st.markdown(
            f"""
            <div style="background-color:rgb(28, 33, 44);padding:10px;margin:10px 0;border-radius:10px;">
                <h5><strong>{msg.username}</strong> <small>reposted from <strong>{msg.original_username}</strong></small></h5>
                <p style="color:#ddd;">“{msg.content}”</p>
                <small style="color:gray;">{format_date_time(msg.timestamp)}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="background-color:rgb(20, 24, 32);padding:10px;margin:10px 0;border-radius:10px;">
                <h5><strong>{msg.username}</strong></h5>
                <p style="color:#ddd;">“{msg.content}”</p>
                <small style="color:gray;">{format_date_time(msg.timestamp)}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Message Posting View
def message_view():
    st.title(f"💬 Posts")

    token = st.session_state['token']
    
    # Text area for writing a new message
    with st.form("post_form"):
        content = st.text_area(
            "Write a message:",
            max_chars=MAX_MESSAGE_LENGTH,
            placeholder="What's on your mind?",
        )
        submitted = st.form_submit_button("Post 🚀")
        if submitted:
            response = post_message(st.session_state.logged_in_user, content, token)
            if response and response.success:
                st.success(response.message)
            else:
                st.error("Failed to post the message.")

    if st.button("🔄 Refresh Messages"):
        response = get_messages(st.session_state.logged_in_user, token)
        if response:
            # Store the messages in session state to persist them across renders
            st.session_state.messages = response.messages
        else:
            st.error("Failed to load messages.")
    
    # Ensure session state has a list of messages
    if "messages" in st.session_state:
        st.markdown("#### 📧 Messages:")
        for idx, msg in enumerate(st.session_state.messages):
            display_message(msg)
            
            # Create a unique key for each button
            button_key = f"repost_button_{idx}"
            
            # If the button is clicked, update session state
            if st.button("🔁 Repost", key=button_key):
                st.session_state.repost_message_id = idx
                st.session_state.repost_clicked = True
            st.markdown("---")

    # Handle repost functionality after all buttons are rendered
    if st.session_state.get("repost_clicked", False):
        original_message_id = st.session_state.repost_message_id
        repost_response = repost_message(st.session_state.logged_in_user, original_message_id, token)
        if repost_response and repost_response.success:
            st.success("Message reposted successfully!")
        else:
            st.error("Failed to repost the message.")
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