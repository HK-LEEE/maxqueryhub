import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { queryApi } from '../../api/queries';
import { QueryItem } from './QueryItem';

interface QueryListProps {
  workspaceId: string;
}

export const QueryList: React.FC<QueryListProps> = ({ workspaceId }) => {
  const { data: queries, isLoading, refetch } = useQuery({
    queryKey: ['queries', workspaceId],
    queryFn: () => queryApi.getQueries(workspaceId),
  });

  if (isLoading) {
    return <div className="text-gray-500">Loading queries...</div>;
  }

  if (!queries?.items.length) {
    return <div className="text-gray-500 text-center py-8">No queries found</div>;
  }

  return (
    <div className="space-y-4">
      {queries.items.map((query) => (
        <QueryItem key={query.uuid} query={query} onStatusChange={() => refetch()} />
      ))}
    </div>
  );
};