import React from 'react';
import { Folder, Users, Database } from 'lucide-react';
import type { Workspace } from '../../types/workspace';
import { WorkspaceType } from '../../types/workspace';

interface WorkspaceItemProps {
  workspace: Workspace;
  isSelected: boolean;
  onClick: () => void;
}

export const WorkspaceItem: React.FC<WorkspaceItemProps> = ({
  workspace,
  isSelected,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className={`p-4 rounded cursor-pointer transition-colors ${
        isSelected
          ? 'bg-black text-white'
          : 'bg-white border border-gray-200 hover:bg-gray-50'
      }`}
    >
      <div className="flex items-center space-x-3">
        {workspace.type === WorkspaceType.PERSONAL ? (
          <Folder size={20} />
        ) : (
          <Users size={20} />
        )}
        <div className="flex-1">
          <h3 className="font-medium">{workspace.name}</h3>
          <p className={`text-sm ${isSelected ? 'text-gray-300' : 'text-gray-500'}`}>
            {workspace.query_count} queries
          </p>
          {workspace.database_connection_name && (
            <div className={`flex items-center space-x-1 text-xs ${isSelected ? 'text-gray-300' : 'text-gray-500'} mt-1`}>
              <Database size={12} />
              <span>{workspace.database_connection_name}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};