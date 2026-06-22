/**
 * Login Page Handler
 * Submits credentials to POST /auth/login and persists the returned tokens.
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    if (!form) return;

    const submitButton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        // Disable the button to prevent duplicate submissions
        submitButton.disabled = true;
        submitButton.classList.add('loading');

        try {
            // matches LoginRequest (email, password) -> TokenResponse
            const tokens = await apiRequest('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            });

            // persist tokens for the authenticated apiRequest wrapper
            localStorage.setItem('access_token', tokens.access_token);
            localStorage.setItem('refresh_token', tokens.refresh_token);

            // redirect to the main dashboard on success
            window.location.href = 'views/dashboard.html';
        } catch (error) {
            // apiRequest already logged the details, surface a message to the user
            alert(error.message || 'Login failed. Please try again.');
        } finally {
            submitButton.disabled = false;
            submitButton.classList.remove('loading');
        }
    });
});
