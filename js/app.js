/**
 * Global Configuration & Base API Client
 */

// 1. Dynamic Environment Base URL Setup
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000' 
    : 'https://'; 

/**
 * 2. Authenticated HTTP Client Wrapper
 * Automatically appends the JWT bearer token and content-type headers.
 * * @param {string} endpoint - The API path (e.g., '/api/v1/inventory')
 * @param {object} options - Fetch options (method, body, headers, etc.)
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // Initialize headers object safely
    options.headers = options.headers || {};
    
    // Set Default Content-Type to JSON if sending a body and it's not FormData
    if (options.body && !(options.body instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
    }

    // Inject JWT access token if it exists in localStorage
    const token = localStorage.getItem('access_token');
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, options);
        
        // Handle HTTP regular error codes
        if (!response.ok) {
            // Handle automatic token expiration or unauthorized access
            if (response.status === 401 || response.status === 403) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                if (window.location.pathname !== '/index.html' && window.location.pathname !== '/') {
                    // root-absolute so it resolves from any depth (e.g. /views/*)
                    window.location.href = '/index.html';
                }
            }
            
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Request failed with status ${response.status}`);
        }

        // Return JSON payload if content exists
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            return await response.json();
        }
        
        return null;
    } catch (error) {
        console.error(`[API Error] ${options.method || 'GET'} to ${endpoint}:`, error.message);
        throw error;
    }
}

/**
 * 3. Role helpers (read from the access token)
 * The backend embeds the user's roles as a `roles` claim in the JWT access
 * token. These helpers decode that claim client-side so the UI can gate
 * content. NOTE: this is for UI gating only — the backend still enforces
 * access via permissions, so a tampered token grants nothing.
 */

// Canonical role names — mirror of SYSTEM_ROLES in management/app/core/constants.
const ROLES = Object.freeze({
    ADMIN: 'admin',
    EMPLOYEE: 'employee',
    CLIENT: 'client',
});

// Decode a base64url JWT segment into an object (no signature check).
function decodeJwtPayload(token) {
    try {
        let part = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
        part += '='.repeat((4 - (part.length % 4)) % 4); // restore padding
        return JSON.parse(atob(part));
    } catch {
        return null;
    }
}

// Roles of the currently logged-in user, e.g. ['admin']. Empty if no session.
function getRoles() {
    const token = localStorage.getItem('access_token');
    if (!token) return [];
    const payload = decodeJwtPayload(token);
    return payload && Array.isArray(payload.roles) ? payload.roles : [];
}

// True if the user holds at least one of the given roles.
function hasAnyRole(...roles) {
    const mine = getRoles();
    return roles.some((role) => mine.includes(role));
}

/**
 * Reveal/hide elements tagged with `data-roles="admin,manager"`.
 * Gated elements are hidden by default (see the inline CSS in each page head)
 * and only revealed once their role matches — so nothing flashes before the
 * role is known. Elements without `data-roles` are unaffected.
 */
function applyRoleVisibility(root = document) {
    const mine = getRoles();
    root.querySelectorAll('[data-roles]').forEach((el) => {
        const allowed = el.dataset.roles
            .split(',')
            .map((r) => r.trim())
            .filter(Boolean);
        el.classList.toggle('role-ok', allowed.some((r) => mine.includes(r)));
    });
}

// Resolve role-gated content on every page as soon as the DOM is ready.
document.addEventListener('DOMContentLoaded', () => applyRoleVisibility());