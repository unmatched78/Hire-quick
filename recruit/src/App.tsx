import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import LandingPage from '@/pages/LandingPage';
import Login from '@/components/Login';
import Navbar from '@/components/Navbar';
import { useAuthStore } from '@/stores/auth';

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function App() {
  const initializeAuth = useAuthStore((state) => state.initializeAuth);

  useEffect(() => {
    initializeAuth(); // Check auth state on mount
  }, [initializeAuth]);

  return (
    <Router>
      <Toaster richColors position="top-right" />
      <div className="min-h-screen">
        <Navbar />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          {/* Example protected route */}
          <Route
            path="/dashboard"
            element={<ProtectedRoute><div>Dashboard</div></ProtectedRoute>}
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;