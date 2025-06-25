import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import { useQuery } from '@tanstack/react-query';
import { Modal } from '../common/Modal';
import { workspaceApi } from '../../api/workspaces';
import { databaseApi } from '../../api/database';
import type { WorkspaceCreate, WorkspaceType } from '../../types/workspace';

interface CreateWorkspaceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const CreateWorkspaceModal: React.FC<CreateWorkspaceModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [formData, setFormData] = useState<WorkspaceCreate>({
    name: '',
    type: 'PERSONAL' as WorkspaceType,
    auto_close_days: 90,
    database_connection_id: null,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: connections } = useQuery({
    queryKey: ['database-connections'],
    queryFn: databaseApi.getConnections,
    enabled: isOpen,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await workspaceApi.createWorkspace(formData);
      toast.success('워크스페이스가 생성되었습니다.');
      onSuccess();
      onClose();
      // Reset form
      setFormData({
        name: '',
        type: 'PERSONAL' as WorkspaceType,
        auto_close_days: 90,
        database_connection_id: null,
      });
    } catch (error) {
      toast.error('워크스페이스 생성에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="새 워크스페이스 만들기">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium mb-2">
            워크스페이스 이름
          </label>
          <input
            id="name"
            type="text"
            className="input"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            maxLength={100}
          />
        </div>

        <div>
          <label htmlFor="type" className="block text-sm font-medium mb-2">
            유형
          </label>
          <select
            id="type"
            className="input"
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value as WorkspaceType })}
          >
            <option value="PERSONAL">개인 워크스페이스</option>
            <option value="GROUP">그룹 워크스페이스</option>
          </select>
        </div>

        <div>
          <label htmlFor="auto_close_days" className="block text-sm font-medium mb-2">
            비활성 쿼리 자동 종료 기간 (일)
          </label>
          <input
            id="auto_close_days"
            type="number"
            className="input"
            value={formData.auto_close_days || ''}
            onChange={(e) => 
              setFormData({ 
                ...formData, 
                auto_close_days: e.target.value ? parseInt(e.target.value) : null 
              })
            }
            min={1}
            max={365}
          />
          <p className="text-sm text-gray-500 mt-1">
            설정하지 않으면 자동 종료 기능이 비활성화됩니다.
          </p>
        </div>

        <div>
          <label htmlFor="database_connection" className="block text-sm font-medium mb-2">
            데이터베이스 연결
          </label>
          <select
            id="database_connection"
            className="input"
            value={formData.database_connection_id || ''}
            onChange={(e) => 
              setFormData({ 
                ...formData, 
                database_connection_id: e.target.value || null 
              })
            }
          >
            <option value="">선택하지 않음</option>
            {connections?.items
              .filter(conn => conn.is_active)
              .map(conn => (
                <option key={conn.id} value={conn.id}>
                  {conn.name} ({conn.database_type})
                </option>
              ))}
          </select>
          <p className="text-sm text-gray-500 mt-1">
            이 워크스페이스의 쿼리가 실행될 데이터베이스를 선택하세요.
          </p>
        </div>

        <div className="flex justify-end space-x-2 pt-4">
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
            disabled={isSubmitting || !formData.name}
          >
            {isSubmitting ? '생성 중...' : '생성'}
          </button>
        </div>
      </form>
    </Modal>
  );
};