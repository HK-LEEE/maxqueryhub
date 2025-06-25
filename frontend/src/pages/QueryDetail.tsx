import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/common/Layout';
import { Card } from '../components/common/Card';
import { QueryExecutor } from '../components/query/QueryExecutor';
import { queryApi } from '../api/queries';
import { QueryStatus } from '../types/query';
import { Copy, ArrowLeft, Code, Database, Globe, Lock } from 'lucide-react';
import { toast } from 'react-hot-toast';

export const QueryDetail: React.FC = () => {
  const { queryId } = useParams<{ queryId: string }>();
  const navigate = useNavigate();
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'curl' | 'python' | 'javascript'>('curl');

  const { data: query, isLoading } = useQuery({
    queryKey: ['query', queryId],
    queryFn: () => queryApi.getQuery(queryId!),
    enabled: !!queryId,
  });

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-gray-500">Loading query...</div>
        </div>
      </Layout>
    );
  }

  if (!query) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-gray-500">Query not found</div>
        </div>
      </Layout>
    );
  }

  const apiEndpoint = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8006'}/api/v1/execute/${query.id}`;
  
  // Generate curl example with actual parameters
  const generateCurlExample = () => {
    const params: Record<string, any> = {};
    if (query.params_info) {
      Object.entries(query.params_info).forEach(([name, info]: [string, any]) => {
        if (info.type === 'integer') {
          params[name] = 123;
        } else if (info.type === 'float') {
          params[name] = 123.45;
        } else if (info.type === 'date') {
          params[name] = '2025-01-01';
        } else {
          params[name] = `example_${name}`;
        }
      });
    }
    
    return `curl -X POST "${apiEndpoint}" \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify({ params }, null, 2)}'`;
  };

  const curlExample = generateCurlExample();

  // Generate Python example
  const pythonExample = `import requests

url = "${apiEndpoint}"
${query.params_info && Object.keys(query.params_info).length > 0 ? `params = ${JSON.stringify(generateSampleParams(), null, 4)}` : 'params = {}'}

response = requests.post(url, json={"params": params})
data = response.json()
print(f"Rows returned: {data['row_count']}")`;

  // Generate JavaScript example  
  const jsExample = `fetch("${apiEndpoint}", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    params: ${JSON.stringify(generateSampleParams(), null, 4)}
  })
})
.then(response => response.json())
.then(data => console.log(data));`;

  function generateSampleParams() {
    const params: Record<string, any> = {};
    if (query.params_info) {
      Object.entries(query.params_info).forEach(([name, info]: [string, any]) => {
        if (info.type === 'integer') {
          params[name] = 123;
        } else if (info.type === 'float') {
          params[name] = 123.45;
        } else if (info.type === 'date') {
          params[name] = '2025-01-01';
        } else {
          params[name] = `example_${name}`;
        }
      });
    }
    return params;
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6">
          <button
            onClick={() => navigate('/')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft size={20} />
            <span>Back to Dashboard</span>
          </button>
        </div>

        <div className="space-y-6">
          <Card>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-4">
                  <Database size={24} />
                  <h1 className="text-2xl font-bold">{query.name}</h1>
                  <span
                    className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                      query.status === QueryStatus.AVAILABLE
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {query.status === QueryStatus.AVAILABLE ? (
                      <>
                        <Globe size={14} className="mr-1" />
                        Public API
                      </>
                    ) : (
                      'Private'
                    )}
                  </span>
                </div>
                {query.description && (
                  <p className="text-gray-600 mb-4">{query.description}</p>
                )}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Created by:</span> {query.created_by}
                  </div>
                  <div>
                    <span className="text-gray-500">Created at:</span>{' '}
                    {new Date(query.created_at).toLocaleString()}
                  </div>
                  {query.last_executed_at && (
                    <div>
                      <span className="text-gray-500">Last executed:</span>{' '}
                      {new Date(query.last_executed_at).toLocaleString()}
                    </div>
                  )}
                </div>
              </div>
              <button
                onClick={() => navigate(`/workspace/${query.workspace_id}/query/${query.id}/edit`)}
                className="btn-secondary"
              >
                Edit Query
              </button>
            </div>
          </Card>

          {query.status === QueryStatus.AVAILABLE && (
            <Card>
              <div className="flex items-center space-x-2 mb-6">
                <Code size={20} />
                <h2 className="text-lg font-semibold">Public API Documentation</h2>
              </div>
              
              <div className="space-y-6">
                {/* API Endpoint */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">API Endpoint</h3>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 flex items-center space-x-2 p-3 bg-gray-50 border border-gray-200 rounded">
                      <span className="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-1 rounded">POST</span>
                      <code className="text-sm">{apiEndpoint}</code>
                    </div>
                    <button
                      onClick={() => copyToClipboard(apiEndpoint)}
                      className="p-2 hover:bg-gray-100 rounded"
                      title="Copy to clipboard"
                    >
                      <Copy size={16} />
                    </button>
                  </div>
                </div>

                {/* Parameters */}
                {query.params_info && Object.keys(query.params_info).length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Parameters</h3>
                    <div className="bg-gray-50 border border-gray-200 rounded p-4">
                      <table className="min-w-full">
                        <thead>
                          <tr className="text-left text-xs text-gray-500 uppercase">
                            <th className="pb-2">Parameter</th>
                            <th className="pb-2">Type</th>
                            <th className="pb-2">Required</th>
                            <th className="pb-2">Description</th>
                          </tr>
                        </thead>
                        <tbody className="text-sm">
                          {Object.entries(query.params_info).map(([name, info]: [string, any]) => (
                            <tr key={name} className="border-t border-gray-200">
                              <td className="py-2 font-mono">{name}</td>
                              <td className="py-2">{info.type || 'string'}</td>
                              <td className="py-2">
                                {info.required !== false ? (
                                  <span className="text-red-600">Yes</span>
                                ) : (
                                  <span className="text-gray-400">No</span>
                                )}
                              </td>
                              <td className="py-2">{info.label || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Code Examples */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Code Examples</h3>
                  <div className="border border-gray-200 rounded">
                    {/* Tabs */}
                    <div className="flex border-b border-gray-200">
                      <button
                        onClick={() => setActiveTab('curl')}
                        className={`px-4 py-2 text-sm font-medium ${
                          activeTab === 'curl'
                            ? 'text-gray-900 border-b-2 border-black'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                      >
                        cURL
                      </button>
                      <button
                        onClick={() => setActiveTab('python')}
                        className={`px-4 py-2 text-sm font-medium ${
                          activeTab === 'python'
                            ? 'text-gray-900 border-b-2 border-black'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                      >
                        Python
                      </button>
                      <button
                        onClick={() => setActiveTab('javascript')}
                        className={`px-4 py-2 text-sm font-medium ${
                          activeTab === 'javascript'
                            ? 'text-gray-900 border-b-2 border-black'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                      >
                        JavaScript
                      </button>
                    </div>
                    
                    {/* Tab Content */}
                    <div className="relative">
                      <pre className="p-4 bg-gray-900 text-gray-100 overflow-x-auto text-sm">
                        <code>
                          {activeTab === 'curl' && curlExample}
                          {activeTab === 'python' && pythonExample}
                          {activeTab === 'javascript' && jsExample}
                        </code>
                      </pre>
                      <button
                        onClick={() => copyToClipboard(
                          activeTab === 'curl' ? curlExample :
                          activeTab === 'python' ? pythonExample : jsExample
                        )}
                        className="absolute top-2 right-2 p-2 hover:bg-gray-800 rounded text-gray-400 hover:text-white"
                        title="Copy to clipboard"
                      >
                        <Copy size={16} />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Response Format */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Response Format</h3>
                  <pre className="p-4 bg-gray-50 border border-gray-200 rounded overflow-x-auto text-sm">
                    <code>{`{
  "query_id": ${query.id},
  "query_name": "${query.name}",
  "executed_at": "2025-01-01T00:00:00",
  "row_count": 10,
  "data": [
    {
      // Result rows
    }
  ],
  "execution_time_ms": 50
}`}</code>
                  </pre>
                </div>
              </div>
            </Card>
          )}

          {query.status === QueryStatus.UNAVAILABLE && (
            <Card className="bg-yellow-50 border-yellow-200">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <Lock className="h-5 w-5 text-yellow-600" />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-yellow-800">Private Query</h3>
                  <p className="text-sm text-yellow-700 mt-1">
                    This query is currently private and cannot be accessed via the public API. 
                    To make it publicly available, publish the query from the dashboard.
                  </p>
                </div>
              </div>
            </Card>
          )}

          <Card>
            <h2 className="text-lg font-semibold mb-4">Test Query Execution</h2>
            <QueryExecutor
              query={query}
              onExecute={setExecutionResult}
            />
          </Card>

          {executionResult && (
            <Card>
              <h2 className="text-lg font-semibold mb-4">Execution Result</h2>
              <div className="space-y-2 text-sm">
                <p>
                  <span className="text-gray-500">Rows returned:</span> {executionResult.row_count}
                </p>
                <p>
                  <span className="text-gray-500">Execution time:</span> {executionResult.execution_time_ms}ms
                </p>
              </div>
              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {executionResult.data.length > 0 &&
                        Object.keys(executionResult.data[0]).map((column) => (
                          <th
                            key={column}
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            {column}
                          </th>
                        ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {executionResult.data.map((row: any, index: number) => (
                      <tr key={index}>
                        {Object.values(row).map((value: any, cellIndex: number) => (
                          <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {String(value)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
};