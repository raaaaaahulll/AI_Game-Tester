// Authentication utility functions

export const getAuth = () => {
    // Check localStorage first (remember me)
    const localAuth = localStorage.getItem('auth');
    if (localAuth) {
        try {
            return JSON.parse(localAuth);
        } catch (e) {
            localStorage.removeItem('auth');
        }
    }

    // Check sessionStorage (temporary session)
    const sessionAuth = sessionStorage.getItem('auth');
    if (sessionAuth) {
        try {
            return JSON.parse(sessionAuth);
        } catch (e) {
            sessionStorage.removeItem('auth');
        }
    }

    return null;
};

export const isAuthenticated = () => {
    const auth = getAuth();
    return auth && auth.isAuthenticated === true;
};

export const logout = () => {
    localStorage.removeItem('auth');
    sessionStorage.removeItem('auth');
};

export const setAuth = (authData, rememberMe = false) => {
    if (rememberMe) {
        localStorage.setItem('auth', JSON.stringify(authData));
    } else {
        sessionStorage.setItem('auth', JSON.stringify(authData));
    }
};

