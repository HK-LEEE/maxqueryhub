import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Plus, Settings } from 'lucide-react';
import { Layout } from '../components/common/Layout';
import { WorkspaceList } from '../components/workspace/WorkspaceList';
import { QueryList } from '../components/query/QueryList';
import { CreateWorkspaceModal } from '../components/workspace/CreateWorkspaceModal';
import { PermissionManageModal } from '../components/permission/PermissionManageModal';
import { workspaceApi } from '../api/workspaces';
import { useAuthStore } from '../stores/authStore';
import type { Workspace } from '../types/workspace';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [selectedWorkspace, setSelectedWorkspace] = useState<Workspace | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isPermissionModalOpen, setIsPermissionModalOpen] = useState(false);
  const user = useAuthStore((state) => state.user);
  const isAdmin = user?.is_admin || false;

  const { data: workspaces, isLoading, refetch } = useQuery({
    queryKey: ['workspaces'],
    queryFn: () => workspaceApi.getWorkspaces(),
  });

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Workspaces</h2>
              {isAdmin && (
                <button
                  onClick={() => setIsCreateModalOpen(true)}
                  className="p-2 hover:bg-gray-100 rounded"
                  title="새 워크스페이스 만들기"
                >
                  <Plus size={20} />
                </button>
              )}
            </div>
            {isLoading ? (
              <div className="text-gray-500">Loading workspaces...</div>
            ) : (
              <WorkspaceList
                workspaces={workspaces?.items || []}
                selectedWorkspace={selectedWorkspace}
                onSelectWorkspace={setSelectedWorkspace}
              />
            )}
          </div>
          <div className="lg:col-span-2">
            {selectedWorkspace ? (
              <>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-semibold">
                    Queries in {selectedWorkspace.name}
                  </h2>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => navigate(`/workspace/${selectedWorkspace.uuid}/query/new`)}
                      className="btn-primary flex items-center space-x-2"
                    >
                      <Plus size={16} />
                      <span>새 쿼리</span>
                    </button>
                    {isAdmin && selectedWorkspace.type === 'GROUP' && (
                      <button
                        onClick={() => setIsPermissionModalOpen(true)}
                        className="p-2 hover:bg-gray-100 rounded"
                        title="권한 관리"
                      >
                        <Settings size={20} />
                      </button>
                    )}
                  </div>
                </div>
                <QueryList workspaceId={selectedWorkspace.uuid} />
              </>
            ) : (
              <div className="text-gray-500 text-center py-12">
                Select a workspace to view queries
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Modals */}
      <CreateWorkspaceModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => {
          refetch();
          setIsCreateModalOpen(false);
        }}
      />
      
      <PermissionManageModal
        isOpen={isPermissionModalOpen}
        onClose={() => setIsPermissionModalOpen(false)}
        workspace={selectedWorkspace}
      />
    </Layout>
  );
};