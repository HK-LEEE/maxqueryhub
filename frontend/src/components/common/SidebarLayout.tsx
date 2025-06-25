import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Home, 
  Database, 
  LogOut, 
  ChevronRight,
  ChevronDown,
  Folder,
  Users,
  Menu,
  X
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import type { Workspace } from '../../types/workspace';

interface SidebarLayoutProps {
  children: React.ReactNode;
  workspaces?: Workspace[];
  onWorkspaceSelect?: (workspace: Workspace) => void;
  selectedWorkspaceId?: string;
}

export const SidebarLayout: React.FC<SidebarLayoutProps> = ({ 
  children, 
  workspaces = [],
  onWorkspaceSelect,
  selectedWorkspaceId
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const isAdmin = user?.is_admin || false;
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [expandedWorkspaces, setExpandedWorkspaces] = useState<Set<string>>(new Set());

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleWorkspace = (workspaceId: string) => {
    const newExpanded = new Set(expandedWorkspaces);
    if (newExpanded.has(workspaceId)) {
      newExpanded.delete(workspaceId);
    } else {
      newExpanded.add(workspaceId);
    }
    setExpandedWorkspaces(newExpanded);
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${isSidebarOpen ? 'w-64' : 'w-16'} bg-white border-r border-gray-200 transition-all duration-200 flex flex-col`}>
        {/* Header */}
        <div className="h-16 border-b border-gray-200 flex items-center justify-between px-4">
          {isSidebarOpen && (
            <h1 className="text-xl font-bold">MAX QueryHub</h1>
          )}
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 hover:bg-gray-100 rounded"
          >
            {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4">
          {/* Dashboard */}
          <Link
            to="/"
            className={`flex items-center px-3 py-2 rounded mb-2 transition-colors ${
              isActive('/') ? 'bg-black text-white' : 'hover:bg-gray-100'
            }`}
          >
            <Home size={20} />
            {isSidebarOpen && <span className="ml-3">Dashboard</span>}
          </Link>

          {/* Workspaces */}
          {isSidebarOpen && (
            <div className="mt-6">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Workspaces
              </h3>
              <div className="space-y-1">
                {workspaces.map((workspace) => (
                  <div key={workspace.uuid} className="mb-1">
                    <button
                      onClick={() => {
                        toggleWorkspace(workspace.uuid);
                        onWorkspaceSelect?.(workspace);
                      }}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded transition-colors ${
                        selectedWorkspaceId === workspace.uuid
                          ? 'bg-gray-100'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center">
                        {workspace.type === 'PERSONAL' ? (
                          <Folder size={16} />
                        ) : (
                          <Users size={16} />
                        )}
                        <span className="ml-2 text-sm">{workspace.name}</span>
                      </div>
                      {expandedWorkspaces.has(workspace.uuid) ? (
                        <ChevronDown size={16} />
                      ) : (
                        <ChevronRight size={16} />
                      )}
                    </button>
                    {expandedWorkspaces.has(workspace.uuid) && (
                      <div className="ml-6 mt-1 space-y-1">
                        <Link
                          to={`/workspace/${workspace.uuid}/queries`}
                          className="block px-3 py-1 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded"
                        >
                          Queries
                        </Link>
                        <Link
                          to={`/workspace/${workspace.uuid}/query/new`}
                          className="block px-3 py-1 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded"
                        >
                          New Query
                        </Link>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </nav>

        {/* Bottom section */}
        <div className="border-t border-gray-200 p-4">
          {/* Database Connections (Admin only) */}
          {isAdmin && (
            <Link
              to="/database-connections"
              className={`flex items-center px-3 py-2 rounded mb-2 transition-colors ${
                isActive('/database-connections') ? 'bg-black text-white' : 'hover:bg-gray-100'
              }`}
            >
              <Database size={20} />
              {isSidebarOpen && <span className="ml-3">Database Connections</span>}
            </Link>
          )}

          {/* User info and logout */}
          <div className="flex items-center justify-between mt-4">
            {isSidebarOpen && (
              <div className="text-sm">
                <p className="font-medium">{user?.user_name}</p>
                <p className="text-gray-500">{user?.user_id}</p>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-gray-100 rounded"
              title="Logout"
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-6">
          <h2 className="text-lg font-semibold">
            {location.pathname === '/' && 'All Queries'}
            {location.pathname === '/database-connections' && 'Database Connections'}
            {location.pathname.includes('/workspace/') && 'Workspace Queries'}
          </h2>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};