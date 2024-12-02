import streamlit as st
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

# Function to handle login
def handle_login(username, password):
    response = login(username, password)
    if response and response.success:
        st.session_state.logged_in_user = username  # Store the logged-in user
        switch_view("relationships")  # Change to relationships view
    else:
        st.error("Invalid username or password!")

# Function to handle registration
def handle_register(username, password):
    response = register(username, password)
    if response and response.success:
        st.success("Registration successful! Please log in.")
        switch_view("login")  # Redirect to login view
    else:
        st.error("Registration failed. Try again.")

# Login/Register View
def login_register_view():
    st.title("Tweety - Auth")
    option = st.selectbox("Choose an option", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if option == "Login":
        if st.button("Login"):
            handle_login(username, password)
    elif option == "Register":
        if st.button("Register"):
            handle_register(username, password)

# Relationships Graph View
def relationships_view():
    st.title(f"Tweety - Welcome, {st.session_state.logged_in_user}")
    
    # Actions for the relationships graph
    option = st.selectbox("Choose an action", ["Follow a User", "View Followers", "View Following"])
    if option == "Follow a User":
        user_to_follow = st.text_input("Enter username to follow")
        if st.button("Follow"):
            response = follow_user(st.session_state.logged_in_user, user_to_follow)
            if response and response.success:
                st.success(f"You are now following {user_to_follow}.")
            else:
                st.error("Failed to follow the user.")
    elif option == "View Followers":
        #if st.button("Show Followers"):
            response = get_followers(st.session_state.logged_in_user)
            if response:
                st.write("Your Followers:")
                st.write(response.followers)
            else:
                st.error("Failed to retrieve followers.")
    elif option == "View Following":
        #if st.button("Show Following"):
            response = get_following(st.session_state.logged_in_user)
            if response:
                st.write("You are Following:")
                st.write(response.following)
            else:
                st.error("Failed to retrieve following list.")
    
    # Logout Button
    if st.button("Logout"):
        st.session_state.logged_in_user = None
        switch_view("login")
    # Message Posting Button
    if st.button("Manage Messages"):
        switch_view("messages")

# Message Posting View
def message_view():
    st.title(f"Welcome, {st.session_state.logged_in_user}")
    
    # Text area for writing a new message
    content = st.text_area(
        "Write a message:",
        max_chars=MAX_MESSAGE_LENGTH,
        placeholder=f"Maximum {MAX_MESSAGE_LENGTH} characters allowed",
    )
    
    if st.button("Post Message"):
        response = post_message(st.session_state.logged_in_user, content)
        if response and response.success:
            st.success(response.message)
        else:
            st.error("Failed to post the message.")

    if st.button("Refresh Messages"):
        response = get_messages()
        if response:
            # Store the messages in session state to persist them across renders
            st.session_state.messages = response.messages
        else:
            st.error("Failed to load messages.")
    
    # Ensure session state has a list of messages
    if "messages" in st.session_state:
        st.write("Messages:")
        for idx, msg in enumerate(st.session_state.messages):
            if msg.is_repost:
                st.write(f"**{msg.username}** [reposted from **{msg.original_username}**]: {msg.content} ({msg.timestamp})")
            else:
                st.write(f"**{msg.username}**: {msg.content} ({msg.timestamp})")
            
            # Create a unique key for each button
            button_key = f"repost_button_{idx}"
            
            # If the button is clicked, update session state
            if st.button("Repost", key=button_key):
                st.session_state.repost_message_id = idx
                st.session_state.repost_clicked = True

    # Handle repost functionality after all buttons are rendered
    if st.session_state.get("repost_clicked", False):
        original_message_id = st.session_state.repost_message_id
        repost_response = repost_message(st.session_state.logged_in_user, original_message_id)
        if repost_response and repost_response.success:
            st.success("Message reposted successfully!")
        else:
            st.error("Failed to repost the message.")
        # Reset repost state after handling
        st.session_state.repost_clicked = False

    # Logout Button
    if st.button("Logout"):
        st.session_state.logged_in_user = None
        switch_view("login")

    # Manage Relationships Button
    if st.button("Manage Relationships"):
        switch_view("relationships")

# Render the appropriate view based on session state
if st.session_state.current_view == "login":
    login_register_view()
elif st.session_state.current_view == "relationships":
    relationships_view()
elif st.session_state.current_view == "messages":
    message_view()