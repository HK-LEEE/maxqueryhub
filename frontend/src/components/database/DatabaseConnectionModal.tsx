import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { Play, Loader } from 'lucide-react';
import { Modal } from '../common/Modal';
import { databaseApi } from '../../api/database';
import { DatabaseType } from '../../types/database';
import type { DatabaseConnection, DatabaseConnectionCreate } from '../../types/database';

interface DatabaseConnectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  connection?: DatabaseConnection | null;
}

const defaultPorts: Record<DatabaseType, number> = {
  [DatabaseType.MYSQL]: 3306,
  [DatabaseType.POSTGRESQL]: 5432,
  [DatabaseType.MSSQL]: 1433,
  [DatabaseType.ORACLE]: 1521,
  [DatabaseType.SQLITE]: 0,
};

export const DatabaseConnectionModal: React.FC<DatabaseConnectionModalProps> = ({
  isOpen,
  onClose,
  connection,
}) => {
  const queryClient = useQueryClient();
  const [isTesting, setIsTesting] = useState(false);
  const [formData, setFormData] = useState<DatabaseConnectionCreate>({
    name: '',
    database_type: DatabaseType.MYSQL,
    host: 'localhost',
    port: defaultPorts[DatabaseType.MYSQL],
    database_name: '',
    username: '',
    password: '',
    is_active: true,
  });

  useEffect(() => {
    if (connection) {
      setFormData({
        name: connection.name,
        database_type: connection.database_type,
        host: connection.host,
        port: connection.port,
        database_name: connection.database_name,
        username: connection.username,
        password: '', // Password is not returned from API
        is_active: connection.is_active,
      });
    } else {
      setFormData({
        name: '',
        database_type: DatabaseType.MYSQL,
        host: 'localhost',
        port: defaultPorts[DatabaseType.MYSQL],
        database_name: '',
        username: '',
        password: '',
        is_active: true,
      });
    }
  }, [connection]);

  const createMutation = useMutation({
    mutationFn: databaseApi.createConnection,
    onSuccess: () => {
      toast.success('데이터베이스 연결이 추가되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['database-connections'] });
      onClose();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '연결 추가에 실패했습니다.');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      databaseApi.updateConnection(id, data),
    onSuccess: () => {
      toast.success('데이터베이스 연결이 수정되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['database-connections'] });
      onClose();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '연결 수정에 실패했습니다.');
    },
  });

  const handleDatabaseTypeChange = (type: DatabaseType) => {
    setFormData({
      ...formData,
      database_type: type,
      port: defaultPorts[type],
    });
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    try {
      const result = await databaseApi.testConnection({
        database_type: formData.database_type,
        host: formData.host,
        port: formData.port,
        database_name: formData.database_name,
        username: formData.username,
        password: formData.password,
      });

      if (result.success) {
        toast.success(`연결 성공! ${result.version || ''}`);
      } else {
        toast.error(result.message);
      }
    } catch (error) {
      toast.error('연결 테스트에 실패했습니다.');
    } finally {
      setIsTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (connection) {
      const updateData: any = { ...formData };
      if (!updateData.password) {
        delete updateData.password;
      }
      updateMutation.mutate({ id: connection.id, data: updateData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={connection ? '데이터베이스 연결 수정' : '새 데이터베이스 연결'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">연결 이름</label>
          <input
            type="text"
            className="input"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            maxLength={100}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">데이터베이스 타입</label>
          <select
            className="input"
            value={formData.database_type}
            onChange={(e) => handleDatabaseTypeChange(e.target.value as DatabaseType)}
          >
            <option value={DatabaseType.MYSQL}>MySQL</option>
            <option value={DatabaseType.POSTGRESQL}>PostgreSQL</option>
            <option value={DatabaseType.MSSQL}>MSSQL</option>
            <option value={DatabaseType.ORACLE}>Oracle</option>
            <option value={DatabaseType.SQLITE}>SQLite</option>
          </select>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium mb-2">호스트</label>
            <input
              type="text"
              className="input"
              value={formData.host}
              onChange={(e) => setFormData({ ...formData, host: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">포트</label>
            <input
              type="number"
              className="input"
              value={formData.port}
              onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
              required
              min={1}
              max={65535}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">데이터베이스명</label>
          <input
            type="text"
            className="input"
            value={formData.database_name}
            onChange={(e) => setFormData({ ...formData, database_name: e.target.value })}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">사용자명</label>
          <input
            type="text"
            className="input"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            비밀번호 {connection && <span className="text-gray-500">(변경시에만 입력)</span>}
          </label>
          <input
            type="password"
            className="input"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required={!connection}
          />
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="is_active"
            checked={formData.is_active}
            onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
          />
          <label htmlFor="is_active" className="text-sm">
            활성화
          </label>
        </div>

        <div className="flex justify-between items-center pt-4 border-t">
          <button
            type="button"
            onClick={handleTestConnection}
            className="btn-secondary flex items-center space-x-2"
            disabled={isTesting || !formData.host || !formData.database_name || !formData.username}
          >
            {isTesting ? (
              <>
                <Loader size={16} className="animate-spin" />
                <span>테스트 중...</span>
              </>
            ) : (
              <>
                <Play size={16} />
                <span>연결 테스트</span>
              </>
            )}
          </button>

          <div className="flex space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
              disabled={isSubmitting}
            >
              취소
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? '저장 중...' : connection ? '수정' : '추가'}
            </button>
          </div>
        </div>
      </form>
    </Modal>
  );
};