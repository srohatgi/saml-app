// static/js/app.js

// DOM elements
const loginButton = document.getElementById('login-button');
const logoutButton = document.getElementById('logout-button');
const callApiButton = document.getElementById('call-api-button');
const unauthenticatedDiv = document.getElementById('unauthenticated');
const authenticatedDiv = document.getElementById('authenticated');
const apiResultDiv = document.getElementById('api-result');
const apiResultContent = document.getElementById('api-result-content');
const userName = document.getElementById('user-name');
const userEmail = document.getElementById('user-email');
const userPicture = document.getElementById('user-picture');

// Check for authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check if we have just been redirected from Auth0 with tokens
    handleAuth0Redirect();
    
    // Check if we already have tokens stored
    const accessToken = localStorage.getItem('access_token');
    const idToken = localStorage.getItem('id_token');
    
    if (accessToken && idToken) {
        // We have tokens, so the user is authenticated
        showAuthenticatedState();
        fetchUserInfo(accessToken);
    } else {
        // User is not authenticated
        showUnauthenticatedState();
    }
});

// Add event listeners
loginButton.addEventListener('click', login);
logoutButton.addEventListener('click', logout);
callApiButton.addEventListener('click', callProtectedApi);

function login() {
    // Redirect to the backend login route, which will redirect to Auth0
    window.location.href = '/login';
}

function logout() {
    // Clear stored tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
    
    // Redirect to the backend logout route
    window.location.href = '/logout';
}

function showAuthenticatedState() {
    unauthenticatedDiv.classList.add('hidden');
    authenticatedDiv.classList.remove('hidden');
}

function showUnauthenticatedState() {
    unauthenticatedDiv.classList.remove('hidden');
    authenticatedDiv.classList.add('hidden');
    apiResultDiv.classList.add('hidden');
}

function handleAuth0Redirect() {
    // Check if we have tokens in the URL hash (from Auth0 redirect)
    if (window.location.hash) {
        // Parse the hash
        const urlParams = new URLSearchParams(window.location.hash.substring(1));
        const accessToken = urlParams.get('access_token');
        const idToken = urlParams.get('id_token');
        
        if (accessToken && idToken) {
            // Store tokens in localStorage
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('id_token', idToken);
            
            // Clean the URL
            window.history.replaceState({}, document.title, window.location.pathname);
            
            // Update UI
            showAuthenticatedState();
            fetchUserInfo(accessToken);
        }
    }
}

async function fetchUserInfo(accessToken) {
    try {
        const response = await fetch('/api/user-info', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch user info');
        }
        
        const userInfo = await response.json();
        
        // Update the UI with user information
        userName.textContent = userInfo.name || userInfo.nickname || 'User';
        userEmail.textContent = userInfo.email || '';
        if (userInfo.picture) {
            userPicture.src = userInfo.picture;
            userPicture.alt = `${userName.textContent}'s profile picture`;
        } else {
            userPicture.src = 'https://via.placeholder.com/150';
        }
    } catch (error) {
        console.error('Error fetching user info:', error);
        // If we can't fetch user info, the token might be invalid
        logout();
    }
}

async function callProtectedApi() {
    const accessToken = localStorage.getItem('access_token');
    
    if (!accessToken) {
        console.error('No access token found');
        return;
    }
    
    try {
        const response = await fetch('/api/protected', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        
        const result = await response.json();
        
        // Display the API response
        apiResultDiv.classList.remove('hidden');
        apiResultContent.textContent = JSON.stringify(result, null, 2);
    } catch (error) {
        console.error('Error calling protected API:', error);
        apiResultDiv.classList.remove('hidden');
        apiResultContent.textContent = `Error: ${error.message}`;
    }
}