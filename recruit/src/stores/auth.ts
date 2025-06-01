import { jwtDecode } from 'jwt-decode'; // Use named import
// Rest of the file remains the same
interface JwtPayload {
  user_id: number;
  user_type: 'job_seeker' | 'company_rep';
  exp: number;
}

interface AuthState {
  isAuthenticated: boolean;
  user: { id: number; user_type: 'job_seeker' | 'company_rep' } | null;
  setTokens: (access: string, refresh: string) => void;
  clearAuth: () => void;
  initializeAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  setTokens: (access: string, refresh: string) => {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    const decoded: JwtPayload = jwtDecode(access); // Use named jwtDecode
    set({
      isAuthenticated: true,
      user: { id: decoded.user_id, user_type: decoded.user_type },
    });
  },
  clearAuth: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ isAuthenticated: false, user: null });
  },
  initializeAuth: () => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      try {
        const decoded: JwtPayload = jwtDecode(accessToken); // Use named jwtDecode
        const currentTime = Date.now() / 1000;
        if (decoded.exp > currentTime) {
          set({
            isAuthenticated: true,
            user: { id: decoded.user_id, user_type: decoded.user_type },
          });
        } else {
          set({ isAuthenticated: false, user: null });
          toast.info('Session expired. Please log in again.');
        }
      } catch (error) {
        set({ isAuthenticated: false, user: null });
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
  },
}));