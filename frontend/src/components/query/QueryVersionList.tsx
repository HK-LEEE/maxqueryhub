import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { CheckCircle, Circle, Clock } from 'lucide-react';
import { queryVersionApi } from '../../api/queryVersions';
import type { QueryVersionResponse } from '../../types/queryVersion';

interface QueryVersionListProps {
  queryId: string;
}

export const QueryVersionList: React.FC<QueryVersionListProps> = ({ queryId }) => {
  const queryClient = useQueryClient();

  const { data: versions, isLoading } = useQuery({
    queryKey: ['query-versions', queryId],
    queryFn: () => queryVersionApi.getVersions(queryId),
  });

  const activateMutation = useMutation({
    mutationFn: (versionId: string) => 
      queryVersionApi.activateVersion(queryId, versionId),
    onSuccess: () => {
      toast.success('버전이 활성화되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['query-versions', queryId] });
      queryClient.invalidateQueries({ queryKey: ['query', queryId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '버전 활성화에 실패했습니다.');
    },
  });

  const handleActivate = (version: QueryVersionResponse) => {
    if (version.is_active) return;
    
    if (confirm(`"${version.name}" 버전을 활성화하시겠습니까?`)) {
      activateMutation.mutate(version.id);
    }
  };

  if (isLoading) {
    return <div className="text-center py-4 text-gray-500">로딩 중...</div>;
  }

  if (!versions || versions.items.length === 0) {
    return <div className="text-center py-4 text-gray-500">버전이 없습니다</div>;
  }

  return (
    <div className="space-y-2">
      {versions.items.map((version) => (
        <div
          key={version.id}
          className={`p-3 rounded border cursor-pointer transition-colors ${
            version.is_active
              ? 'border-black bg-gray-50'
              : 'border-gray-200 hover:bg-gray-50'
          }`}
          onClick={() => handleActivate(version)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                {version.is_active ? (
                  <CheckCircle size={16} className="text-green-500" />
                ) : (
                  <Circle size={16} className="text-gray-400" />
                )}
                <span className="font-medium">v{version.version_number}</span>
                <span className="text-sm">{version.name}</span>
              </div>
              {version.description && (
                <p className="text-sm text-gray-600 mt-1 ml-6">
                  {version.description}
                </p>
              )}
              <div className="flex items-center space-x-3 text-xs text-gray-500 mt-2 ml-6">
                <span>{version.created_by}</span>
                <span>•</span>
                <span className="flex items-center space-x-1">
                  <Clock size={12} />
                  <span>
                    {new Date(version.created_at).toLocaleDateString('ko-KR')}
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};