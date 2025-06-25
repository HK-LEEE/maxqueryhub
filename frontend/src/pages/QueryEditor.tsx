import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { Save, Play, Plus, History, ArrowLeft } from 'lucide-react';
import { Layout } from '../components/common/Layout';
import { Card } from '../components/common/Card';
import { Modal } from '../components/common/Modal';
import { QueryVersionList } from '../components/query/QueryVersionList';
import { queryApi } from '../api/queries';
import { queryVersionApi } from '../api/queryVersions';
import { workspaceApi } from '../api/workspaces';
import type { QueryCreate, Query, QueryExecuteResponse } from '../types/query';
import type { QueryVersionCreate } from '../types/queryVersion';

export const QueryEditor: React.FC = () => {
  const { workspaceId, queryId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isNewQuery = !queryId || queryId === 'new';
  const [showVersionModal, setShowVersionModal] = useState(false);
  const [showVersionsPanel, setShowVersionsPanel] = useState(false);
  const [showTestPanel, setShowTestPanel] = useState(false);
  const [testParams, setTestParams] = useState<Record<string, any>>({});
  const [testResult, setTestResult] = useState<QueryExecuteResponse | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const [formData, setFormData] = useState<QueryCreate>({
    name: '',
    description: '',
    sql_template: '',
    params_info: {},
  });

  const [paramFields, setParamFields] = useState<Array<{
    name: string;
    type: string;
    label: string;
    required: boolean;
  }>>([]);

  // Fetch workspace
  const { data: workspace, isLoading: isLoadingWorkspace } = useQuery({
    queryKey: ['workspace', workspaceId],
    queryFn: () => workspaceApi.getWorkspace(workspaceId!),
    enabled: !!workspaceId,
  });

  // Fetch existing query if editing
  const { data: existingQuery, isLoading: isLoadingQuery } = useQuery({
    queryKey: ['query', queryId],
    queryFn: () => queryApi.getQuery(queryId),
    enabled: !isNewQuery && !!queryId,
  });

  // Update form when existing query is loaded
  useEffect(() => {
    if (existingQuery) {
      setFormData({
        name: existingQuery.name,
        description: existingQuery.description || '',
        sql_template: existingQuery.sql_template,
        params_info: existingQuery.params_info || {},
      });

      // Parse params_info to paramFields
      if (existingQuery.params_info) {
        const fields = Object.entries(existingQuery.params_info).map(([name, info]: [string, any]) => ({
          name,
          type: info.type || 'string',
          label: info.label || name,
          required: info.required !== false,
        }));
        setParamFields(fields);
        
        // Initialize test params with empty values
        const initialTestParams: Record<string, any> = {};
        fields.forEach(field => {
          initialTestParams[field.name] = '';
        });
        setTestParams(initialTestParams);
      }
    }
  }, [existingQuery]);

  // Create query mutation
  const createMutation = useMutation({
    mutationFn: (data: QueryCreate) => queryApi.createQuery(workspaceId!, data),
    onSuccess: (newQuery) => {
      toast.success('쿼리가 생성되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['queries', workspaceId] });
      navigate(`/workspace/${workspaceId}/query/${newQuery.id}/edit`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '쿼리 생성에 실패했습니다.');
    },
  });

  // Create version mutation
  const createVersionMutation = useMutation({
    mutationFn: (data: QueryVersionCreate) => 
      queryVersionApi.createVersion(queryId!, data),
    onSuccess: () => {
      toast.success('새 버전이 생성되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['query-versions', queryId] });
      setShowVersionModal(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '버전 생성에 실패했습니다.');
    },
  });

  const handleSave = () => {
    // Convert paramFields to params_info format
    const params_info = paramFields.reduce((acc, field) => {
      if (field.name) {
        acc[field.name] = {
          type: field.type,
          label: field.label,
          required: field.required,
        };
      }
      return acc;
    }, {} as Record<string, any>);

    const dataToSave = {
      ...formData,
      params_info,
    };

    if (isNewQuery) {
      createMutation.mutate(dataToSave);
    } else {
      // Create new version
      setShowVersionModal(true);
    }
  };

  const handleCreateVersion = (versionName: string, description: string) => {
    const params_info = paramFields.reduce((acc, field) => {
      if (field.name) {
        acc[field.name] = {
          type: field.type,
          label: field.label,
          required: field.required,
        };
      }
      return acc;
    }, {} as Record<string, any>);

    createVersionMutation.mutate({
      name: versionName,
      description,
      sql_template: formData.sql_template,
      params_info,
    });
  };

  const handleTestQuery = async () => {
    if (!queryId || isNewQuery) {
      toast.error('쿼리를 먼저 저장해주세요.');
      return;
    }

    // Validate required parameters
    for (const field of paramFields) {
      if (field.required && !testParams[field.name]) {
        toast.error(`필수 파라미터 "${field.label || field.name}"를 입력해주세요.`);
        return;
      }
    }

    setIsExecuting(true);
    setTestResult(null);

    try {
      const result = await queryApi.executeQuery(queryId, {
        params: testParams,
      });
      setTestResult(result);
      toast.success('쿼리 실행 완료');
    } catch (error: any) {
      console.error('Query execution error:', error);
      console.error('Response data:', error.response?.data);
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else if (error.message) {
        toast.error(`Error: ${error.message}`);
      } else {
        toast.error('쿼리 실행에 실패했습니다.');
      }
    } finally {
      setIsExecuting(false);
    }
  };

  const addParamField = () => {
    setParamFields([
      ...paramFields,
      { name: '', type: 'string', label: '', required: true },
    ]);
  };

  const updateParamField = (index: number, field: any) => {
    const updated = [...paramFields];
    updated[index] = field;
    setParamFields(updated);
  };

  const removeParamField = (index: number) => {
    setParamFields(paramFields.filter((_, i) => i !== index));
  };

  // Show loading state
  if (isLoadingWorkspace || (!isNewQuery && isLoadingQuery)) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-gray-500">로딩 중...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/')}
              className="p-2 hover:bg-gray-100 rounded"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold">
                {isNewQuery ? '새 쿼리 작성' : '쿼리 편집'}
              </h1>
              {workspace && (
                <p className="text-sm text-gray-500">
                  워크스페이스: {workspace.name}
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {!isNewQuery && (
              <>
                <button
                  onClick={() => setShowTestPanel(!showTestPanel)}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Play size={16} />
                  <span>테스트</span>
                </button>
                <button
                  onClick={() => setShowVersionsPanel(!showVersionsPanel)}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <History size={16} />
                  <span>버전 관리</span>
                </button>
              </>
            )}
            <button
              onClick={handleSave}
              className="btn-primary flex items-center space-x-2"
              disabled={!formData.name || !formData.sql_template}
            >
              <Save size={16} />
              <span>{isNewQuery ? '저장' : '새 버전 저장'}</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className={`lg:col-span-${showVersionsPanel ? '2' : '3'}`}>
            <Card className="mb-6">
              <h2 className="text-lg font-semibold mb-4">쿼리 정보</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    쿼리 이름
                  </label>
                  <input
                    type="text"
                    className="input"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="예: 월별 매출 리포트"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    설명 (선택사항)
                  </label>
                  <textarea
                    className="input"
                    rows={2}
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="이 쿼리에 대한 설명을 입력하세요"
                  />
                </div>
              </div>
            </Card>

            <Card className="mb-6">
              <h2 className="text-lg font-semibold mb-4">SQL 쿼리</h2>
              <textarea
                className="input font-mono text-sm"
                rows={10}
                value={formData.sql_template}
                onChange={(e) => setFormData({ ...formData, sql_template: e.target.value })}
                placeholder="SELECT * FROM table WHERE date = :date"
              />
              <p className="text-sm text-gray-500 mt-2">
                파라미터는 :parameter_name 형식으로 작성하세요
              </p>
            </Card>

            <Card>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">쿼리 파라미터</h2>
                <button
                  onClick={addParamField}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Plus size={16} />
                  <span>파라미터 추가</span>
                </button>
              </div>
              {paramFields.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  파라미터가 없습니다
                </p>
              ) : (
                <div className="space-y-4">
                  {paramFields.map((field, index) => (
                    <div key={index} className="border-b pb-4 last:border-0">
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-1">
                            파라미터 이름
                          </label>
                          <input
                            type="text"
                            className="input"
                            value={field.name}
                            onChange={(e) =>
                              updateParamField(index, { ...field, name: e.target.value })
                            }
                            placeholder="start_date"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-1">
                            타입
                          </label>
                          <select
                            className="input"
                            value={field.type}
                            onChange={(e) =>
                              updateParamField(index, { ...field, type: e.target.value })
                            }
                          >
                            <option value="string">문자열</option>
                            <option value="date">날짜</option>
                            <option value="integer">정수</option>
                            <option value="float">실수</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-1">
                            라벨
                          </label>
                          <input
                            type="text"
                            className="input"
                            value={field.label}
                            onChange={(e) =>
                              updateParamField(index, { ...field, label: e.target.value })
                            }
                            placeholder="시작일"
                          />
                        </div>
                        <div className="flex items-end space-x-2">
                          <label className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              checked={field.required}
                              onChange={(e) =>
                                updateParamField(index, { ...field, required: e.target.checked })
                              }
                            />
                            <span className="text-sm">필수</span>
                          </label>
                          <button
                            onClick={() => removeParamField(index)}
                            className="p-2 text-red-500 hover:bg-red-50 rounded"
                          >
                            삭제
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* Test Execution Panel */}
            {showTestPanel && !isNewQuery && (
              <Card className="mt-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-semibold">쿼리 테스트</h2>
                  <button
                    onClick={handleTestQuery}
                    disabled={isExecuting}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <Play size={16} />
                    <span>{isExecuting ? '실행 중...' : '쿼리 실행'}</span>
                  </button>
                </div>

                {paramFields.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-medium mb-3">파라미터 입력</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {paramFields.map((field) => (
                        <div key={field.name}>
                          <label className="block text-sm font-medium mb-1">
                            {field.label || field.name}
                            {field.required && <span className="text-red-500 ml-1">*</span>}
                          </label>
                          <input
                            type={field.type === 'date' ? 'date' : field.type === 'integer' || field.type === 'float' ? 'number' : 'text'}
                            step={field.type === 'float' ? '0.01' : undefined}
                            className="input"
                            value={testParams[field.name] || ''}
                            onChange={(e) => setTestParams({
                              ...testParams,
                              [field.name]: field.type === 'integer' ? parseInt(e.target.value) || 0
                                : field.type === 'float' ? parseFloat(e.target.value) || 0
                                : e.target.value
                            })}
                            placeholder={`${field.type} 값 입력`}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Query Results */}
                {testResult && (
                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-sm font-medium">실행 결과</h3>
                      <div className="text-sm text-gray-500">
                        {testResult.row_count}개 행 | {testResult.execution_time_ms}ms
                      </div>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            {testResult.data.length > 0 &&
                              Object.keys(testResult.data[0]).map((key) => (
                                <th
                                  key={key}
                                  className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                >
                                  {key}
                                </th>
                              ))}
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {testResult.data.map((row, idx) => (
                            <tr key={idx}>
                              {Object.values(row).map((value: any, cellIdx) => (
                                <td key={cellIdx} className="px-4 py-2 text-sm text-gray-900">
                                  {value === null ? 'NULL' : String(value)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {testResult.data.length === 0 && (
                      <div className="text-center py-4 text-gray-500">
                        결과가 없습니다
                      </div>
                    )}
                  </div>
                )}
              </Card>
            )}
          </div>

          {showVersionsPanel && !isNewQuery && (
            <div className="lg:col-span-1">
              <Card>
                <h2 className="text-lg font-semibold mb-4">버전 히스토리</h2>
                <QueryVersionList queryId={queryId} />
              </Card>
            </div>
          )}
        </div>

        {/* Version Creation Modal */}
        <Modal
          isOpen={showVersionModal}
          onClose={() => setShowVersionModal(false)}
          title="새 버전 생성"
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              handleCreateVersion(
                formData.get('versionName') as string,
                formData.get('description') as string
              );
            }}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium mb-2">
                버전 이름
              </label>
              <input
                name="versionName"
                type="text"
                className="input"
                required
                placeholder="예: v1.1 - 성능 개선"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                변경사항 설명
              </label>
              <textarea
                name="description"
                className="input"
                rows={3}
                placeholder="이 버전에서 변경된 내용을 설명하세요"
              />
            </div>
            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setShowVersionModal(false)}
                className="btn-secondary"
              >
                취소
              </button>
              <button type="submit" className="btn-primary">
                버전 생성
              </button>
            </div>
          </form>
        </Modal>
      </div>
    </Layout>
  );
};