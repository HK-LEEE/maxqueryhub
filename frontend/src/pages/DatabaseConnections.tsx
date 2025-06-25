import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Edit2, Trash2, Database, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { Layout } from '../components/common/Layout';
import { Card } from '../components/common/Card';
import { DatabaseConnectionModal } from '../components/database/DatabaseConnectionModal';
import { databaseApi } from '../api/database';
import { useAuthStore } from '../stores/authStore';
import { Navigate } from 'react-router-dom';
import type { DatabaseConnection } from '../types/database';

export const DatabaseConnections: React.FC = () => {
  const [selectedConnection, setSelectedConnection] = useState<DatabaseConnection | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);
  const isAdmin = user?.is_admin || false;

  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  const { data: connections, isLoading } = useQuery({
    queryKey: ['database-connections'],
    queryFn: databaseApi.getConnections,
  });

  const deleteMutation = useMutation({
    mutationFn: databaseApi.deleteConnection,
    onSuccess: () => {
      toast.success('데이터베이스 연결이 삭제되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['database-connections'] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '삭제에 실패했습니다.');
    },
  });

  const handleEdit = (connection: DatabaseConnection) => {
    setSelectedConnection(connection);
    setIsModalOpen(true);
  };

  const handleDelete = async (connection: DatabaseConnection) => {
    if (confirm(`'${connection.name}' 연결을 삭제하시겠습니까?`)) {
      deleteMutation.mutate(connection.uuid);
    }
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setSelectedConnection(null);
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'MYSQL':
        return 'text-blue-600';
      case 'POSTGRESQL':
        return 'text-green-600';
      case 'MSSQL':
        return 'text-red-600';
      case 'ORACLE':
        return 'text-orange-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">데이터베이스 연결 관리</h1>
          <button
            onClick={() => setIsModalOpen(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus size={20} />
            <span>새 연결 추가</span>
          </button>
        </div>

        {isLoading ? (
          <div className="text-center py-8 text-gray-500">
            데이터베이스 연결 정보를 불러오는 중...
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {connections?.items.map((connection) => (
              <Card key={connection.uuid} className="hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center space-x-3">
                    <Database size={24} className={getTypeColor(connection.database_type)} />
                    <div>
                      <h3 className="font-semibold">{connection.name}</h3>
                      <p className="text-sm text-gray-500">{connection.database_type}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    {connection.is_active ? (
                      <CheckCircle size={16} className="text-green-500" />
                    ) : (
                      <XCircle size={16} className="text-red-500" />
                    )}
                  </div>
                </div>

                <div className="space-y-1 text-sm text-gray-600 mb-4">
                  <p>
                    <span className="font-medium">호스트:</span> {connection.host}:{connection.port}
                  </p>
                  <p>
                    <span className="font-medium">데이터베이스:</span> {connection.database_name}
                  </p>
                  <p>
                    <span className="font-medium">사용자:</span> {connection.username}
                  </p>
                </div>

                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => handleEdit(connection)}
                    className="p-2 hover:bg-gray-100 rounded"
                    title="편집"
                  >
                    <Edit2 size={16} />
                  </button>
                  <button
                    onClick={() => handleDelete(connection)}
                    className="p-2 hover:bg-gray-100 rounded text-red-500"
                    title="삭제"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </Card>
            ))}

            {connections?.items.length === 0 && (
              <div className="col-span-full text-center py-8 text-gray-500">
                아직 등록된 데이터베이스 연결이 없습니다.
              </div>
            )}
          </div>
        )}

        <DatabaseConnectionModal
          isOpen={isModalOpen}
          onClose={handleModalClose}
          connection={selectedConnection}
        />
      </div>
    </Layout>
  );
};