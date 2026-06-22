/**
 * Password Recovery Handlers
 * Wires the request (/auth/forgot) and redeem (/auth/reset) flows.
 */

document.addEventListener('DOMContentLoaded', () => {
    const forgotForm = document.getElementById('forgot-form');
    const resetForm = document.getElementById('reset-form');
    const tokenInput = document.getElementById('reset-token');

    // prefill the token if it arrived via the email link (?token=...)
    const tokenFromUrl = new URLSearchParams(window.location.search).get('token');
    if (tokenFromUrl && tokenInput) {
        tokenInput.value = tokenFromUrl;
    }

    // POST /auth/forgot -> matches ForgotPasswordRequest (204)
    forgotForm?.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = document.getElementById('forgot-email').value.trim();
        const submitButton = forgotForm.querySelector('button[type="submit"]');

        submitButton.disabled = true;
        submitButton.classList.add('loading');

        try {
            await apiRequest('/auth/forgot', {
                method: 'POST',
                body: JSON.stringify({ email }),
            });
            // server responds 204 regardless of whether the email exists
            alert('If that email is registered, a reset link is on its way.');
        } catch (error) {
            alert(error.message || 'Could not send reset link.');
        } finally {
            submitButton.disabled = false;
            submitButton.classList.remove('loading');
        }
    });

    // POST /auth/reset -> matches ResetPasswordRequest (204)
    resetForm?.addEventListener('submit', async (event) => {
        event.preventDefault();

        const token = document.getElementById('reset-token').value.trim();
        const newPassword = document.getElementById('reset-password').value;
        const submitButton = resetForm.querySelector('button[type="submit"]');

        submitButton.disabled = true;
        submitButton.classList.add('loading');

        try {
            await apiRequest('/auth/reset', {
                method: 'POST',
                body: JSON.stringify({ token, new_password: newPassword }),
            });
            alert('Password reset. You can now sign in.');
            window.location.href = '../index.html';
        } catch (error) {
            alert(error.message || 'Could not reset password.');
        } finally {
            submitButton.disabled = false;
            submitButton.classList.remove('loading');
        }
    });
});
