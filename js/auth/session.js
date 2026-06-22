/**
 * Dashboard Session Handlers
 * Wires logout, token refresh and change-password against the /auth endpoints.
 */

document.addEventListener('DOMContentLoaded', () => {
    // guard: no session means back to the login page
    if (!localStorage.getItem('access_token')) {
        window.location.href = '../index.html';
        return;
    }

    const logoutBtn = document.getElementById('logout-btn');
    const refreshBtn = document.getElementById('refresh-btn');
    const changeForm = document.getElementById('change-password-form');

    // clear local tokens and return to login
    function clearSession() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '../index.html';
    }

    // POST /auth/logout -> revokes the refresh token (204)
    logoutBtn?.addEventListener('click', async () => {
        const refreshToken = localStorage.getItem('refresh_token');
        try {
            if (refreshToken) {
                await apiRequest('/auth/logout', {
                    method: 'POST',
                    body: JSON.stringify({ refresh_token: refreshToken }),
                });
            }
        } catch (error) {
            // even if the server rejects the token, drop the local session
            console.warn('[logout]', error.message);
        } finally {
            clearSession();
        }
    });

    // POST /auth/refresh -> rotates the token pair (TokenResponse)
    refreshBtn?.addEventListener('click', async () => {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return clearSession();

        try {
            const tokens = await apiRequest('/auth/refresh', {
                method: 'POST',
                body: JSON.stringify({ refresh_token: refreshToken }),
            });
            localStorage.setItem('access_token', tokens.access_token);
            localStorage.setItem('refresh_token', tokens.refresh_token);
            // the new token may carry updated roles -> re-resolve gated content
            applyRoleVisibility();
            alert('Session refreshed.');
        } catch (error) {
            // expired/invalid refresh token -> force re-login
            clearSession();
        }
    });

    // POST /auth/change-password -> matches ChangePasswordRequest (204)
    changeForm?.addEventListener('submit', async (event) => {
        event.preventDefault();

        const oldPassword = document.getElementById('old_password').value;
        const newPassword = document.getElementById('new_password').value;
        const submitButton = changeForm.querySelector('button[type="submit"]');

        submitButton.disabled = true;
        submitButton.classList.add('loading');

        try {
            await apiRequest('/auth/change-password', {
                method: 'POST',
                body: JSON.stringify({
                    old_password: oldPassword,
                    new_password: newPassword,
                }),
            });

            // backend revokes all refresh tokens on change -> re-login
            alert('Password updated. Please sign in again.');
            clearSession();
        } catch (error) {
            alert(error.message || 'Could not change password.');
        } finally {
            submitButton.disabled = false;
            submitButton.classList.remove('loading');
        }
    });
});
