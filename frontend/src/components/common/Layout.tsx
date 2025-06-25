import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { LogOut, Home, Database } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-semibold">Query Hub</h1>
              {user && (
                <nav className="flex items-center space-x-6">
                  <Link 
                    to="/" 
                    className="flex items-center space-x-2 text-sm text-gray-600 hover:text-black"
                  >
                    <Home size={16} />
                    <span>Dashboard</span>
                  </Link>
                  {user.is_admin && (
                    <Link 
                      to="/database-connections" 
                      className="flex items-center space-x-2 text-sm text-gray-600 hover:text-black"
                    >
                      <Database size={16} />
                      <span>Database Connections</span>
                    </Link>
                  )}
                </nav>
              )}
            </div>
            {user && (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">{user.email}</span>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 text-sm text-gray-600 hover:text-black"
                >
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
};