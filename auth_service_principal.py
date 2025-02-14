
from flask import Flask, redirect, request, session, url_for
from msal import ConfidentialClientApplication

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key

# Azure AD Configuration
CLIENT_ID = 'SPN ID'
CLIENT_SECRET = 'SPN SECRET'
AUTHORITY = "https://login.microsoftonline.com/TENANT_ID"  # Replace with your Tenant ID
REDIRECT_URI = "http://localhost:5000/callback"  # Must match the Redirect URI in Azure AD
SCOPE = ["User.Read"]  # Permissions requested for the token (e.g., User.Read)

# MSAL App
msal_app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

@app.route('/')
def index():
    return 'Welcome to the OAuth Flow with Azure! <a href="/login">Login</a>'

@app.route('/login')
def login():
    # Generate the authorization URL
    auth_url = msal_app.get_authorization_request_url(
        SCOPE,
        redirect_uri=REDIRECT_URI
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Get the authorization code from the callback URL
    code = request.args.get('code')
    if not code:
        return "No authorization code found.", 400

    # Exchange the authorization code for an access token
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI
    )

    if "access_token" in result:
        # Store the access token in the session
        session["access_token"] = result["access_token"]
        return "Login successful! Access token acquired."
    else:
        return f"Error acquiring token: {result.get('error_description')}", 400



@app.route('/profile')
def profile():
    # Use the access token to call Microsoft Graph API
    token = session.get("access_token")
    if not token:
        return redirect(url_for('login'))

    import requests
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)

    if response.status_code == 200:
        return f"User Profile: {response.json()}"
    else:
        return f"Failed to fetch profile: {response.status_code}, {response.text}"

if __name__ == '__main__':
    app.run(debug=True)
