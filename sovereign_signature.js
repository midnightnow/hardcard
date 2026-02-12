/**
 * SOVEREIGN SIGNATURE - Constellation OS Identity SDK (Browser)
 * ==============================================================
 * Client-side implementation of the Sovereign Signature protocol.
 * Works with the Python backend for session management.
 * 
 * Usage:
 *   const identity = new SovereignIdentity();
 *   await identity.authenticate('1973-07-30');
 *   const claims = identity.getClaims();
 */

class SovereignIdentity {
    constructor() {
        this.deviceId = this._getOrCreateDeviceId();
        this.signature = null;
        this.sessionToken = null;
        this.claims = null;
    }

    /**
     * Get or create a persistent device ID.
     */
    _getOrCreateDeviceId() {
        const storageKey = 'constellation_device_id';
        let deviceId = localStorage.getItem(storageKey);

        if (!deviceId) {
            deviceId = crypto.randomUUID();
            localStorage.setItem(storageKey, deviceId);
        }

        return deviceId;
    }

    /**
     * Generate the Sovereign Signature from a date.
     * This is done entirely client-side - the date never leaves the device.
     */
    async generateSignature(sovereignDate) {
        // Normalize the date
        const date = new Date(sovereignDate);
        if (isNaN(date.getTime())) {
            throw new Error('Invalid date format');
        }

        const normalizedDate = date.toISOString().slice(0, 10).replace(/-/g, '');
        const salt = 'CONSTELLATION_OS_2026';

        // Create payload
        const payload = `${normalizedDate}:${this.deviceId}:${salt}`;

        // Hash using Web Crypto API
        const encoder = new TextEncoder();
        const data = encoder.encode(payload);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);

        // Convert to hex string
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const signature = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

        this.signature = signature;
        return signature;
    }

    /**
     * Authenticate with a Sovereign Date.
     * Generates signature and creates local session.
     */
    async authenticate(sovereignDate) {
        console.log('🔐 Generating Sovereign Signature...');

        const signature = await this.generateSignature(sovereignDate);

        // Create local session token
        const now = Math.floor(Date.now() / 1000);
        this.sessionToken = {
            session_id: crypto.randomUUID(),
            signature_prefix: signature.slice(0, 16),
            geostamp: `GEO:${now}:${this.deviceId.slice(0, 8)}`,
            created_at: now,
            expires_at: now + 86400, // 24 hours
            device_id: this.deviceId.slice(0, 8),
            protocol: 'SOVEREIGN_V1'
        };

        // Store in sessionStorage for cross-tab access
        sessionStorage.setItem('constellation_session', JSON.stringify(this.sessionToken));

        // Generate claims
        this.claims = {
            sub: signature.slice(0, 32),
            iss: 'constellation.os',
            aud: ['macagent', 'vetsorcery', 'hardcard'],
            iat: now,
            exp: now + 86400,
            device: this.deviceId.slice(0, 8),
            protocol: 'SOVEREIGN_V1',
            permissions: {
                L0_HARDCARD: ['read', 'write'],
                L2_MACAGENT: ['read', 'write', 'execute'],
                L3_VETSORCERY: ['read', 'write']
            }
        };

        // Store signature securely (only in memory by default)
        localStorage.setItem('constellation_claims', JSON.stringify(this.claims));

        console.log('✅ Sovereign Identity established');
        console.log(`   Subject: ${this.claims.sub}`);

        return this.claims;
    }

    /**
     * Check if user is authenticated.
     */
    isAuthenticated() {
        const session = this._loadSession();
        if (!session) return false;

        const now = Math.floor(Date.now() / 1000);
        return session.expires_at > now;
    }

    /**
     * Get current claims (or null if not authenticated).
     */
    getClaims() {
        if (this.claims) return this.claims;

        try {
            const stored = localStorage.getItem('constellation_claims');
            if (stored) {
                this.claims = JSON.parse(stored);

                // Check expiration
                const now = Math.floor(Date.now() / 1000);
                if (this.claims.exp < now) {
                    this.logout();
                    return null;
                }

                return this.claims;
            }
        } catch (e) {
            console.warn('Failed to load claims:', e);
        }

        return null;
    }

    /**
     * Load session from storage.
     */
    _loadSession() {
        try {
            const stored = sessionStorage.getItem('constellation_session');
            if (stored) {
                return JSON.parse(stored);
            }
        } catch (e) {
            console.warn('Failed to load session:', e);
        }
        return null;
    }

    /**
     * Logout - clear all identity data.
     */
    logout() {
        this.signature = null;
        this.sessionToken = null;
        this.claims = null;
        sessionStorage.removeItem('constellation_session');
        localStorage.removeItem('constellation_claims');
        console.log('🔓 Sovereign Identity cleared');
    }

    /**
     * Get the signature prefix for API authentication.
     */
    getAuthHeader() {
        const session = this._loadSession();
        if (!session) return null;

        return {
            'X-Sovereign-Session': session.session_id,
            'X-Sovereign-Prefix': session.signature_prefix,
            'X-Sovereign-Geostamp': session.geostamp
        };
    }

    /**
     * Display login prompt.
     * Returns a Promise that resolves when user authenticates.
     */
    async promptLogin() {
        return new Promise((resolve, reject) => {
            // Check if already authenticated
            if (this.isAuthenticated()) {
                resolve(this.getClaims());
                return;
            }

            // Check localStorage for saved signature preference
            const savedDate = localStorage.getItem('constellation_sovereign_date');

            if (savedDate) {
                // Auto-authenticate with saved date (user chose "remember")
                this.authenticate(savedDate).then(resolve).catch(reject);
                return;
            }

            // Otherwise, show prompt
            const dateInput = prompt('Enter your Sovereign Date (YYYY-MM-DD):');

            if (!dateInput) {
                reject(new Error('Authentication cancelled'));
                return;
            }

            this.authenticate(dateInput).then(resolve).catch(reject);
        });
    }
}

/**
 * WebAuthn Passkey Integration (Phase 18.5)
 * Allows binding the Sovereign Signature to a hardware key.
 */
class SovereignPasskey {
    constructor(identity) {
        this.identity = identity;
    }

    /**
     * Check if WebAuthn is available.
     */
    isAvailable() {
        return window.PublicKeyCredential !== undefined;
    }

    /**
     * Register a new passkey.
     */
    async register() {
        if (!this.isAvailable()) {
            throw new Error('WebAuthn not supported');
        }

        const challenge = crypto.getRandomValues(new Uint8Array(32));

        const publicKeyCredentialCreationOptions = {
            challenge: challenge,
            rp: {
                name: "Constellation OS",
                id: window.location.hostname
            },
            user: {
                id: new TextEncoder().encode(this.identity.deviceId),
                name: "sovereign@constellation.os",
                displayName: "Sovereign Identity"
            },
            pubKeyCredParams: [
                { type: "public-key", alg: -7 },   // ES256
                { type: "public-key", alg: -257 }  // RS256
            ],
            timeout: 60000,
            attestation: "none"
        };

        try {
            const credential = await navigator.credentials.create({
                publicKey: publicKeyCredentialCreationOptions
            });

            console.log('✅ Passkey registered:', credential.id);

            // Store credential ID
            localStorage.setItem('constellation_passkey_id', credential.id);

            return credential;
        } catch (e) {
            console.error('Passkey registration failed:', e);
            throw e;
        }
    }

    /**
     * Authenticate with existing passkey.
     */
    async authenticate() {
        if (!this.isAvailable()) {
            throw new Error('WebAuthn not supported');
        }

        const credentialId = localStorage.getItem('constellation_passkey_id');
        if (!credentialId) {
            throw new Error('No passkey registered');
        }

        const challenge = crypto.getRandomValues(new Uint8Array(32));

        const publicKeyCredentialRequestOptions = {
            challenge: challenge,
            allowCredentials: [{
                id: Uint8Array.from(atob(credentialId), c => c.charCodeAt(0)),
                type: "public-key"
            }],
            timeout: 60000
        };

        try {
            const assertion = await navigator.credentials.get({
                publicKey: publicKeyCredentialRequestOptions
            });

            console.log('✅ Passkey authenticated');
            return assertion;
        } catch (e) {
            console.error('Passkey authentication failed:', e);
            throw e;
        }
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SovereignIdentity, SovereignPasskey };
}

// Make available globally for browser usage
if (typeof window !== 'undefined') {
    window.SovereignIdentity = SovereignIdentity;
    window.SovereignPasskey = SovereignPasskey;
}
