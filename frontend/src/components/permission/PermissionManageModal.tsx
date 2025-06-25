import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { Modal } from '../common/Modal';
import { X, Plus, User, Users } from 'lucide-react';
import type { Workspace } from '../../types/workspace';
import type { PermissionCreate, PrincipalType } from '../../types/permission';

interface PermissionManageModalProps {
  isOpen: boolean;
  onClose: () => void;
  workspace: Workspace | null;
}

export const PermissionManageModal: React.FC<PermissionManageModalProps> = ({
  isOpen,
  onClose,
  workspace,
}) => {
  const [permissions, setPermissions] = useState<PermissionCreate[]>([]);
  const [newPermission, setNewPermission] = useState<PermissionCreate>({
    principal_type: 'USER' as PrincipalType,
    principal_id: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (workspace && isOpen) {
      loadPermissions();
    }
  }, [workspace, isOpen]);

  const loadPermissions = async () => {
    if (!workspace) return;
    
    setIsLoading(true);
    try {
      // TODO: API call to get permissions
      // const response = await permissionApi.getPermissions(workspace.id);
      // setPermissions(response);
      setPermissions([]); // Placeholder
    } catch (error) {
      toast.error('권한 정보를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const addPermission = () => {
    if (!newPermission.principal_id) {
      toast.error('사용자 ID 또는 그룹 ID를 입력해주세요.');
      return;
    }

    if (permissions.some(p => 
      p.principal_type === newPermission.principal_type && 
      p.principal_id === newPermission.principal_id
    )) {
      toast.error('이미 추가된 권한입니다.');
      return;
    }

    setPermissions([...permissions, { ...newPermission }]);
    setNewPermission({
      principal_type: 'USER' as PrincipalType,
      principal_id: '',
    });
  };

  const removePermission = (index: number) => {
    setPermissions(permissions.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    if (!workspace) return;

    setIsSaving(true);
    try {
      // TODO: API call to save permissions
      // await permissionApi.updatePermissions(workspace.id, permissions);
      toast.success('권한이 저장되었습니다.');
      onClose();
    } catch (error) {
      toast.error('권한 저장에 실패했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  if (!workspace) return null;

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      title={`${workspace.name} - 권한 관리`}
    >
      <div className="space-y-4">
        {isLoading ? (
          <div className="text-center py-8 text-gray-500">
            권한 정보를 불러오는 중...
          </div>
        ) : (
          <>
            {/* 현재 권한 목록 */}
            <div>
              <h3 className="text-sm font-medium mb-2">현재 권한</h3>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {permissions.length === 0 ? (
                  <p className="text-sm text-gray-500 py-2">
                    아직 추가된 권한이 없습니다.
                  </p>
                ) : (
                  permissions.map((permission, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-gray-50 rounded"
                    >
                      <div className="flex items-center space-x-2">
                        {permission.principal_type === 'USER' ? (
                          <User size={16} />
                        ) : (
                          <Users size={16} />
                        )}
                        <span className="text-sm">
                          {permission.principal_id}
                        </span>
                        <span className="text-xs text-gray-500">
                          ({permission.principal_type === 'USER' ? '사용자' : '그룹'})
                        </span>
                      </div>
                      <button
                        onClick={() => removePermission(index)}
                        className="text-gray-400 hover:text-red-500"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* 새 권한 추가 */}
            <div>
              <h3 className="text-sm font-medium mb-2">권한 추가</h3>
              <div className="flex space-x-2">
                <select
                  className="input"
                  value={newPermission.principal_type}
                  onChange={(e) =>
                    setNewPermission({
                      ...newPermission,
                      principal_type: e.target.value as PrincipalType,
                    })
                  }
                >
                  <option value="USER">사용자</option>
                  <option value="GROUP">그룹</option>
                </select>
                <input
                  type="text"
                  className="input flex-1"
                  placeholder={
                    newPermission.principal_type === 'USER'
                      ? '사용자 이메일'
                      : '그룹 ID'
                  }
                  value={newPermission.principal_id}
                  onChange={(e) =>
                    setNewPermission({
                      ...newPermission,
                      principal_id: e.target.value,
                    })
                  }
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addPermission();
                    }
                  }}
                />
                <button
                  onClick={addPermission}
                  className="btn-primary"
                  disabled={!newPermission.principal_id}
                >
                  <Plus size={16} />
                </button>
              </div>
            </div>
          </>
        )}

        {/* 액션 버튼 */}
        <div className="flex justify-end space-x-2 pt-4 border-t">
          <button
            onClick={onClose}
            className="btn-secondary"
            disabled={isSaving}
          >
            취소
          </button>
          <button
            onClick={handleSave}
            className="btn-primary"
            disabled={isSaving || isLoading}
          >
            {isSaving ? '저장 중...' : '저장'}
          </button>
        </div>
      </div>
    </Modal>
  );
};