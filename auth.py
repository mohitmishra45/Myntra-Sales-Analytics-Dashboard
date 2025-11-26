import streamlit as st
import pandas as pd
import hashlib
import os
from datetime import datetime

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from CSV file"""
    try:
        if os.path.exists('users.csv'):
            return pd.read_csv('users.csv')
        return pd.DataFrame(columns=['username', 'password_hash', 'role', 'created_at'])
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")
        return pd.DataFrame(columns=['username', 'password_hash', 'role', 'created_at'])

def save_users(users_df):
    """Save users to CSV file"""
    try:
        users_df.to_csv('users.csv', index=False)
    except Exception as e:
        st.error(f"Error saving users: {str(e)}")

def create_user(username, password, role='merchant'):
    """Create a new user"""
    users_df = load_users()
    
    # Check if username already exists
    if username in users_df['username'].values:
        return False, "Username already exists"
    
    # Create new user
    new_user = pd.DataFrame({
        'username': [username],
        'password_hash': [hash_password(password)],
        'role': [role],
        'created_at': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    })
    
    users_df = pd.concat([users_df, new_user], ignore_index=True)
    save_users(users_df)
    return True, "User created successfully"

def verify_user(username, password):
    """Verify user credentials"""
    users_df = load_users()
    
    # Find user
    user = users_df[users_df['username'] == username]
    
    if user.empty:
        return False, None
    
    # Verify password
    if user['password_hash'].iloc[0] == hash_password(password):
        return True, user['role'].iloc[0]
    
    return False, None

def login_page():
    """Display login page"""
    # Add custom CSS for authentication pages with Myntra brand colors
    st.markdown("""
        <style>
        /* Main background with Myntra brand colors */
        .stApp {
            background: linear-gradient(135deg, #FF3F6C, #FF8E9E, #FF3F6C);
            background-size: 200% 200%;
            animation: gradient 10s ease infinite;
            perspective: 1000px;
            transform-style: preserve-3d;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Enhanced glass morphism effect */
        .auth-container {
            max-width: 400px;
            margin: 20px auto;
            padding: 2.5rem;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            box-shadow: 0 8px 32px 0 rgba(255, 63, 108, 0.2);
            border: 1px solid rgba(255, 63, 108, 0.1);
            transform-style: preserve-3d;
            transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            will-change: transform;
        }
        
        .auth-container:hover {
            transform: translateY(-10px) rotateX(5deg);
            box-shadow: 0 12px 40px 0 rgba(255, 63, 108, 0.3);
        }
        
        /* Floating logo with Myntra glow */
        .auth-header {
            text-align: center;
            margin-bottom: 1rem;
            padding: 1rem;
            transform-style: preserve-3d;
        }
        
        .auth-logo {
            width: 150px;
            height: auto;
            margin-bottom: 1.5rem;
            animation: float3D 3s ease-in-out infinite;
            filter: drop-shadow(0 0 20px rgba(255, 63, 108, 0.6));
            transform-style: preserve-3d;
        }
        
        @keyframes float3D {
            0% { transform: translateY(0px) rotateY(0deg); }
            50% { transform: translateY(-15px) rotateY(10deg); }
            100% { transform: translateY(0px) rotateY(0deg); }
        }
        
        /* Myntra brand title effect */
        .auth-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(120deg, #282C3F, #4A4E69);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.3);
            animation: title3D 1s ease-out;
            transform-style: preserve-3d;
        }
        
        @keyframes title3D {
            from {
                opacity: 0;
                transform: translateZ(-50px) scale(0.9);
            }
            to {
                opacity: 1;
                transform: translateZ(0) scale(1);
            }
        }
        
        /* Enhanced form styling */
        .stTextInput input {
            background: rgba(255, 255, 255, 0.95);
            border: 2px solid rgba(255, 63, 108, 0.2);
            border-radius: 10px;
            padding: 1rem;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            width: 100%;
            margin-bottom: 1rem;
            transform-style: preserve-3d;
            will-change: transform;
        }
        
        .stTextInput input:focus {
            border-color: #FF3F6C;
            box-shadow: 0 0 20px rgba(255, 63, 108, 0.3);
            transform: translateZ(10px);
        }
        
        /* Myntra brand button effect */
        .stButton button {
            background: linear-gradient(45deg, #282C3F, #4A4E69);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 1rem;
            transform-style: preserve-3d;
            will-change: transform;
            position: relative;
            overflow: hidden;
        }
        
        .stButton button:hover {
            transform: translateZ(20px) scale(1.05);
            box-shadow: 0 10px 20px rgba(40, 44, 63, 0.4);
            background: linear-gradient(45deg, #1A1D2B, #2D3142);
            color: #FF3F6C;
        }
        
        .stButton button:active {
            transform: translateZ(10px) scale(0.95);
        }
        
        .stButton button::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transform: translateX(-100%);
            transition: transform 0.6s;
        }
        
        .stButton button:hover::after {
            transform: translateX(100%);
        }
        
        /* Myntra brand tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background-color: transparent;
            transform-style: preserve-3d;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
            color: #282C3F;
            font-weight: 600;
            background-color: rgba(255, 255, 255, 0.9);
            border: none;
            border-radius: 10px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
            will-change: transform;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: #FF3F6C;
            background-color: rgba(255, 255, 255, 0.95);
            transform: translateZ(10px);
            box-shadow: 0 5px 15px rgba(40, 44, 63, 0.2);
        }
        
        .stTabs [aria-selected="true"] {
            color: #FF3F6C !important;
            background-color: rgba(255, 255, 255, 0.95) !important;
            transform: translateZ(20px);
            box-shadow: 0 5px 15px rgba(40, 44, 63, 0.2);
        }
        
        /* Myntra brand message styling */
        .success-message, .error-message {
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            text-align: center;
            animation: message3D 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
            will-change: transform;
        }
        
        .success-message {
            background: linear-gradient(45deg, #FF3F6C, #FF8E9E);
            color: white;
            box-shadow: 0 4px 15px rgba(255, 63, 108, 0.3);
        }
        
        .error-message {
            background: linear-gradient(45deg, #FF3F6C, #FF8E9E);
            color: white;
            box-shadow: 0 4px 15px rgba(255, 63, 108, 0.3);
        }
        
        @keyframes message3D {
            from {
                opacity: 0;
                transform: translateZ(-50px) scale(0.9);
            }
            to {
                opacity: 1;
                transform: translateZ(0) scale(1);
            }
        }
        
        /* Myntra brand floating elements */
        .floating-element {
            position: absolute;
            background: rgba(255, 63, 108, 0.1);
            border-radius: 50%;
            pointer-events: none;
            animation: floatElement 20s infinite linear;
            transform-style: preserve-3d;
            box-shadow: 0 0 20px rgba(255, 63, 108, 0.2);
        }
        
        @keyframes floatElement {
            0% {
                transform: translate(0, 0) rotate(0deg);
            }
            100% {
                transform: translate(100px, 100px) rotate(360deg);
            }
        }
        
        /* Performance optimizations */
        * {
            backface-visibility: hidden;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        /* Hardware acceleration */
        .auth-container, .auth-logo, .auth-title, .stTextInput input, 
        .stButton button, .stTabs [data-baseweb="tab"] {
            transform: translateZ(0);
            -webkit-transform: translateZ(0);
        }
        
        /* Myntra brand link styling */
        .auth-switch {
            text-align: center;
            margin-top: 1.5rem;
            color: #282C3F;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .auth-switch a {
            color: #282C3F;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.9);
        }
        
        .auth-switch a:hover {
            background: rgba(255, 255, 255, 0.95);
            color: #FF3F6C;
            box-shadow: 0 5px 15px rgba(40, 44, 63, 0.2);
            transform: translateY(-2px);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Add floating background elements with Myntra colors
    st.markdown("""
        <div class="floating-elements">
            <div class="floating-element" style="width: 100px; height: 100px; top: 10%; left: 10%;"></div>
            <div class="floating-element" style="width: 150px; height: 150px; top: 60%; right: 15%;"></div>
            <div class="floating-element" style="width: 80px; height: 80px; bottom: 20%; left: 30%;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Add Myntra logo and header with 3D effect
    st.markdown("""
        <div class="auth-header">
            <img src="https://logolook.net/wp-content/uploads/2023/01/Myntra-Emblem-2048x1152.png" class="auth-logo" alt="Myntra Logo">
        </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for login and register with 3D flip effect
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    with login_tab:
        st.markdown('<div class="auth-title">Welcome Back!</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                success, role = verify_user(username, password)
                if success:
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = username
                    st.session_state['role'] = role
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.markdown('<div class="auth-switch">Don\'t have an account? <a href="#" onclick="document.querySelector(\'[data-baseweb=\'tab-list\'] button:nth-child(2)\').click()">Register here</a></div>', unsafe_allow_html=True)
    
    with register_tab:
        st.markdown('<div class="auth-title">Create Account</div>', unsafe_allow_html=True)
        
        with st.form("register_form"):
            new_username = st.text_input("New Username", key="register_username")
            new_password = st.text_input("New Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = create_user(new_username, new_password)
                    if success:
                        st.success("Registration successful! Please login.")
                        st.markdown("""
                            <script>
                            setTimeout(function() {
                                document.querySelector('[data-baseweb="tab-list"] button:nth-child(1)').click();
                            }, 2000);
                            </script>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(message)
        
        st.markdown('<div class="auth-switch">Already have an account? <a href="#" onclick="document.querySelector(\'[data-baseweb=\'tab-list\'] button:nth-child(1)\').click()">Login here</a></div>', unsafe_allow_html=True)

def check_auth():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    if not st.session_state['authenticated']:
        login_page()
        return False
    
    return True

def logout():
    """Logout user"""
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None
    st.rerun() 