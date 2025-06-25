import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './stores/authStore';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { QueryDetail } from './pages/QueryDetail';
import { DatabaseConnections } from './pages/DatabaseConnections';
import { QueryEditor } from './pages/QueryEditor';
import './styles/index.css';

console.log('App.tsx loaded');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

function App() {
  console.log('App component rendering');
  
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/workspace/:workspaceId/query/:queryId"
            element={
              <PrivateRoute>
                <QueryDetail />
              </PrivateRoute>
            }
          />
          <Route
            path="/database-connections"
            element={
              <PrivateRoute>
                <DatabaseConnections />
              </PrivateRoute>
            }
          />
          <Route
            path="/workspace/:workspaceId/query/new"
            element={
              <PrivateRoute>
                <QueryEditor />
              </PrivateRoute>
            }
          />
          <Route
            path="/workspace/:workspaceId/query/:queryId/edit"
            element={
              <PrivateRoute>
                <QueryEditor />
              </PrivateRoute>
            }
          />
        </Routes>
      </Router>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#000',
            color: '#fff',
          },
        }}
      />
    </QueryClientProvider>
  );
}

export default App;