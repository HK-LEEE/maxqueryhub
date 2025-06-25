import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, Globe, Lock, Edit, Play } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { type Query, QueryStatus } from '../../types/query';
import { queryApi } from '../../api/queries';
import { Card } from '../common/Card';
import { Modal } from '../common/Modal';

interface QueryItemProps {
  query: Query;
  onStatusChange: () => void;
}

export const QueryItem: React.FC<QueryItemProps> = ({ query, onStatusChange }) => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const handleStatusToggle = async () => {
    if (query.status === QueryStatus.UNAVAILABLE) {
      setIsModalOpen(true);
    } else {
      await updateStatus(QueryStatus.UNAVAILABLE);
    }
  };

  const updateStatus = async (status: QueryStatus) => {
    setIsUpdating(true);
    try {
      await queryApi.updateQueryStatus(query.uuid, status);
      toast.success(`Query ${status === QueryStatus.AVAILABLE ? 'published' : 'unpublished'}`);
      onStatusChange();
    } catch (error) {
      toast.error('Failed to update query status');
    } finally {
      setIsUpdating(false);
      setIsModalOpen(false);
    }
  };

  return (
    <>
      <Card className="hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <Database size={20} />
              <h3 className="font-medium">{query.name}</h3>
            </div>
            {query.description && (
              <p className="text-sm text-gray-600 mb-2">{query.description}</p>
            )}
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>Created by: {query.created_by}</span>
              {query.last_executed_at && (
                <span>Last executed: {new Date(query.last_executed_at).toLocaleDateString()}</span>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate(`/workspace/${query.workspace_uuid || query.workspace_id}/query/${query.uuid}`)}
              className="p-2 hover:bg-gray-100 rounded"
              title="실행"
            >
              <Play size={16} />
            </button>
            <button
              onClick={() => navigate(`/workspace/${query.workspace_uuid || query.workspace_id}/query/${query.uuid}/edit`)}
              className="p-2 hover:bg-gray-100 rounded"
              title="편집"
            >
              <Edit size={16} />
            </button>
            <div className="flex items-center space-x-1 ml-2">
              {query.status === QueryStatus.AVAILABLE ? (
                <>
                  <Globe size={16} className="text-green-600" />
                  <span className="text-sm font-medium text-green-600">Public</span>
                </>
              ) : (
                <>
                  <Lock size={16} className="text-gray-400" />
                  <span className="text-sm font-medium text-gray-400">Private</span>
                </>
              )}
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={query.status === QueryStatus.AVAILABLE}
                onChange={handleStatusToggle}
                disabled={isUpdating}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-black"></div>
            </label>
          </div>
        </div>
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Publish Query"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Warning: Publishing this query will create a public API that can be executed by anyone
            without authentication. Are you sure you want to continue?
          </p>
          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setIsModalOpen(false)}
              className="btn-secondary"
              disabled={isUpdating}
            >
              Cancel
            </button>
            <button
              onClick={() => updateStatus(QueryStatus.AVAILABLE)}
              className="btn-primary"
              disabled={isUpdating}
            >
              {isUpdating ? 'Publishing...' : 'Publish'}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
};