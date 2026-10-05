import React, { useState, useEffect, useCallback, useRef } from 'react';
import { api, Project } from './services/api';
import { Navbar } from './components/Navbar';
import { StatusBadge } from './components/StatusBadge';
import { WorkflowSidebar } from './components/WorkflowSidebar';
import { ApprovalStation } from './components/ApprovalStation';
import { CompletedCelebration } from './components/CompletedCelebration';
import { AgentExecutionView } from './components/AgentExecutionView';
import { IterationMatrix } from './components/IterationMatrix';
import { EvaluationView } from './components/EvaluationView';
import { VersionTimeline } from './components/VersionTimeline';
import { CodeStudio } from './components/CodeStudio';
import { OverviewSection } from './components/OverviewSection';
import { CreateProjectModal } from './components/CreateProjectModal';
import { LiveAppPreview } from './components/LiveAppPreview';

import {
  Play,
  RotateCw,
  Trash2,
  Download,
  Bot,
  Search,
  FolderGit2,
  Zap,
} from 'lucide-react';

export default function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [showCreate, setShowCreate] = useState(false);

  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [activeTab, setActiveTab] = useState<
    'overview' | 'agents' | 'iterations' | 'evaluation' | 'versions' | 'code' | 'preview'
  >('overview');

  const [requirements, setRequirements] = useState<any>(null);
  const [plan, setPlan] = useState<any>(null);
  const [files, setFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');

  const [agentRuns, setAgentRuns] = useState<any[]>([]);
  const [, setIterations] = useState<any[]>([]);
  const [testResults, setTestResults] = useState<any[]>([]);
  const [reviewResults, setReviewResults] = useState<any[]>([]);
  const [debugResults, setDebugResults] = useState<any[]>([]);
  const [evaluation, setEvaluation] = useState<any>(null);
  const [documentation, setDocumentation] = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [packageInfo, setPackageInfo] = useState<any>(null);

  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState('');

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadProjects = useCallback(async () => {
    try {
      const data = await api.getProjects();
      setProjects(data);
      if (!selectedProjectId && data.length > 0) {
        setSelectedProjectId(data[0].id);
      }
    } catch {}
  }, [selectedProjectId]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const loadProjectData = useCallback(async (id: string) => {
    let currentProj: any = null;
    try {
      currentProj = await api.getProject(id);
      setSelectedProject(currentProj);
    } catch {}
    try {
      setRequirements(await api.getRequirements(id));
    } catch {
      setRequirements(null);
    }
    try {
      setPlan(await api.getPlan(id));
    } catch {
      setPlan(null);
    }
    try {
      const f = await api.getFiles(id);
      const fileList = f.files || [];
      setFiles(fileList);
      if (fileList.length > 0) {
        const defaultFile = fileList.find((x: any) => x.path === 'main.py' || x.path === 'index.html' || x.path === 'App.tsx' || x.path === 'README.md') || fileList[0];
        const targetPath = (selectedFile && fileList.some((x: any) => x.path === selectedFile)) ? selectedFile : defaultFile.path;
        setSelectedFile(targetPath);
        try {
          setFileContent(await api.getFileContent(id, targetPath));
        } catch {
          setFileContent('// File ready in workspace.');
        }
      } else {
        setSelectedFile(null);
        setFileContent('');
      }
    } catch {
      setFiles([]);
    }
    try {
      setIterations(await api.getIterations(id));
    } catch {
      setIterations([]);
    }
    try {
      setTestResults(await api.getTestResults(id));
    } catch {
      setTestResults([]);
    }
    try {
      setReviewResults(await api.getReviewResults(id));
    } catch {
      setReviewResults([]);
    }
    try {
      setDebugResults(await api.getDebugResults(id));
    } catch {
      setDebugResults([]);
    }
    try {
      setEvaluation(await api.getEvaluation(id));
    } catch {
      setEvaluation(null);
    }
    try {
      setDocumentation(await api.getDocumentation(id));
    } catch {
      setDocumentation(null);
    }
    try {
      setVersions(await api.getVersions(id));
    } catch {
      setVersions([]);
    }
    if (currentProj?.status === 'COMPLETED' || currentProj?.approval_status === 'APPROVED') {
      try {
        setPackageInfo(await api.getPackage(id));
      } catch {
        setPackageInfo(null);
      }
    } else {
      setPackageInfo(null);
    }
    try {
      setAgentRuns(await api.getProjectAgents(id));
    } catch {
      setAgentRuns([]);
    }
  }, [selectedFile]);

  const selectProject = useCallback(
    (id: string) => {
      setSelectedProjectId(id);
      setSelectedFile(null);
      setFileContent('');
      loadProjectData(id);
    },
    [loadProjectData]
  );

  useEffect(() => {
    if (selectedProjectId) {
      loadProjectData(selectedProjectId);
    }
  }, [selectedProjectId, loadProjectData]);

  // Auto-polling when workflow is actively running
  useEffect(() => {
    if (!selectedProjectId) return;
    if (!selectedProject) return;
    const isRunning = ['RUNNING', 'PACKAGING', 'EVALUATING', 'DOCUMENTING'].includes(
      selectedProject.status
    );
    if (isRunning) {
      pollRef.current = setInterval(() => {
        loadProjectData(selectedProjectId);
        loadProjects();
      }, 3500);
    } else {
      if (pollRef.current) clearInterval(pollRef.current);
    }
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [selectedProject?.status, selectedProjectId, loadProjectData, loadProjects]);

  const handleCreateProject = async (data: {
    name: string;
    description: string;
    max_iterations: number;
    experiment_type: string;
  }) => {
    try {
      const created = await api.createProject(data);
      setShowCreate(false);
      await loadProjects();
      if (created?.id) {
        selectProject(created.id);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create project');
    }
  };

  const handleStart = async (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setActionError('');
    setActionLoading(true);
    try {
      await api.startProject(id);
      await loadProjects();
      if (selectedProjectId === id) await loadProjectData(id);
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Start failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRetry = async (id: string) => {
    setActionError('');
    setActionLoading(true);
    try {
      await api.retryProject(id);
      await loadProjects();
      await loadProjectData(id);
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Retry failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this project?')) return;
    setActionError('');
    setActionLoading(true);
    try {
      await api.deleteProject(id);
      if (selectedProjectId === id) {
        setSelectedProjectId(null);
        setSelectedProject(null);
      }
      await loadProjects();
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'Delete failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleFileClick = async (path: string) => {
    setSelectedFile(path);
    setFileContent('Loading code...');
    try {
      setFileContent(await api.getFileContent(selectedProjectId!, path));
    } catch {
      setFileContent('// Error loading file contents from server.');
    }
  };

  const handleApprovalAction = async () => {
    if (selectedProjectId) {
      await loadProjects();
      await loadProjectData(selectedProjectId);
    }
  };

  const filteredProjects = projects.filter((p) => {
    const matchesSearch =
      !searchQuery ||
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || p.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const isWaiting = selectedProject?.status === 'WAITING_FOR_APPROVAL';
  const isCompleted = selectedProject?.status === 'COMPLETED';
  const isRunning =
    selectedProject?.status === 'RUNNING' ||
    selectedProject?.status === 'PACKAGING' ||
    selectedProject?.status === 'EVALUATING' ||
    selectedProject?.status === 'DOCUMENTING';
  const canStart = selectedProject?.status === 'CREATED';

  const TABS = [
    { key: 'overview', label: 'Overview & Requirements' },
    { key: 'agents', label: `Agent Log (${agentRuns.length})` },
    { key: 'iterations', label: `Loop Cycles (${testResults.length})` },
    { key: 'evaluation', label: 'Quality Evaluation' },
    { key: 'versions', label: `Versions (${versions.length})` },
    { key: 'code', label: `Code Studio (${files.length})` },
    { key: 'preview', label: '🚀 Live App Preview' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30">
      {/* Top Navbar */}
      <Navbar
        onNewProject={() => setShowCreate(true)}
        projectCount={projects.length}
        activeProject={selectedProject}
      />

      {/* Main Workspace Layout */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 w-full flex-1 flex flex-col lg:flex-row gap-6">
        {/* Left Sidebar: Projects List & LangGraph Flow */}
        <aside className="w-full lg:w-80 shrink-0 space-y-4">
          {/* Projects Control Panel */}
          <div className="glass-panel rounded-2xl p-4 border border-slate-800/80 shadow-subtle-card space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <FolderGit2 className="w-3.5 h-3.5 text-indigo-400" />
                Projects ({filteredProjects.length})
              </span>
              <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded-full border border-cyan-800/40">
                Workspace
              </span>
            </div>

            {/* Search & Filter */}
            <div className="space-y-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-3" />
                <input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search projects..."
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-8 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30 outline-none transition-all"
                />
              </div>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full bg-slate-900/90 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:border-indigo-500 outline-none transition-all"
              >
                <option value="ALL">All Statuses</option>
                {[
                  'CREATED',
                  'RUNNING',
                  'WAITING_FOR_APPROVAL',
                  'COMPLETED',
                  'FAILED',
                  'PACKAGING',
                ].map((s) => (
                  <option key={s} value={s}>
                    {s.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            </div>

            {/* Project List */}
            <div className="space-y-2 max-h-[320px] overflow-y-auto pr-1">
              {filteredProjects.map((p) => {
                const isSelected = selectedProjectId === p.id;
                return (
                  <div
                    key={p.id}
                    onClick={() => selectProject(p.id)}
                    className={`group relative p-3 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'border-indigo-500/50 bg-indigo-950/20 shadow-sm'
                        : 'border-slate-800/80 bg-slate-900/30 hover:border-slate-700 hover:bg-slate-900/60'
                    }`}
                  >
                    <button
                      onClick={(e) => handleDelete(p.id, e)}
                      disabled={actionLoading}
                      className="absolute top-2.5 right-2.5 text-slate-500 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-slate-800"
                      title="Delete Project"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>

                    <div className="font-semibold text-xs text-slate-200 truncate pr-6">
                      {p.name}
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono mt-0.5 truncate">
                      ID: {p.id.slice(0, 8)}...
                    </div>

                    <div className="flex items-center gap-2 mt-2">
                      <StatusBadge status={p.status} size="sm" />
                      <span className="text-[10px] font-mono text-slate-400 bg-slate-800/80 px-1.5 py-0.5 rounded border border-slate-700/50">
                        v{p.current_version}
                      </span>
                      {p.revision_count > 0 && (
                        <span className="text-[10px] font-mono text-amber-300 bg-amber-950/50 px-1.5 py-0.5 rounded border border-amber-800/30">
                          {p.revision_count} rev
                        </span>
                      )}
                    </div>

                    {isSelected && p.status === 'CREATED' && (
                      <button
                        onClick={(e) => handleStart(p.id, e)}
                        disabled={actionLoading}
                        className="mt-2.5 w-full flex items-center justify-center gap-1.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-sm transition-all"
                      >
                        <Play className="w-3.5 h-3.5" />
                        <span>Start Multi-Agent Loop</span>
                      </button>
                    )}
                  </div>
                );
              })}

              {filteredProjects.length === 0 && (
                <div className="text-center p-6 text-xs text-slate-500">No projects found.</div>
              )}
            </div>
          </div>

          {/* Workflow Sidebar */}
          {selectedProject && (
            <WorkflowSidebar
              project={selectedProject}
              agentRuns={agentRuns}
              activeTab={activeTab}
              onNavigateTab={(tab) => setActiveTab(tab as any)}
            />
          )}
        </aside>

        {/* Center / Main Content Area */}
        <main className="flex-1 min-w-0 space-y-5">
          {!selectedProjectId ? (
            /* Empty State Hero */
            <div className="glass-panel rounded-2xl border border-slate-800/80 p-12 text-center space-y-6 shadow-subtle-card">
              <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto text-indigo-400">
                <Bot className="w-7 h-7" />
              </div>

              <div className="space-y-2 max-w-lg mx-auto">
                <h2 className="text-xl font-bold text-slate-100">
                  Autonomous Multi-Agent Engineering Studio
                </h2>
                <p className="text-xs text-slate-400 leading-relaxed">
                  LangGraph orchestrates requirements analysis, system architecture, code generation, sandboxed test execution, reviewer auditing, and autonomous debugging until quality gates pass.
                </p>
              </div>

              <button
                onClick={() => setShowCreate(true)}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-sm transition-all"
              >
                <Zap className="w-3.5 h-3.5 text-indigo-200" />
                <span>Launch New Autonomous Project</span>
              </button>
            </div>
          ) : (
            <div className="space-y-5">
              {/* Project Header Banner */}
              {selectedProject && (
                <div className="glass-panel rounded-2xl border border-slate-800/80 p-5 shadow-subtle-card space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                    <div className="space-y-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2.5">
                        <h2 className="text-lg font-bold text-slate-100 truncate">
                          {selectedProject.name}
                        </h2>
                        <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono border border-slate-700">
                          {selectedProject.experiment_type}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed">
                        {selectedProject.description}
                      </p>
                    </div>

                    <div className="flex flex-col sm:items-end gap-1.5 shrink-0">
                      <StatusBadge status={selectedProject.status} size="md" />
                      <div className="text-[11px] font-mono text-slate-400">
                        Version v{selectedProject.current_version} · Revisions:{' '}
                        {selectedProject.revision_count}/{selectedProject.max_revisions ?? 3}
                      </div>
                    </div>
                  </div>

                  {/* Running Alert */}
                  {isRunning && (
                    <div className="flex items-center gap-2.5 p-3 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-xs text-cyan-200">
                      <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                      <span className="font-medium">
                        LangGraph loop executing stage: <strong className="font-mono text-cyan-100">[{selectedProject.current_stage || 'RUNNING'}]</strong>. State updates automatically.
                      </span>
                    </div>
                  )}

                  {actionError && (
                    <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/40 text-xs text-rose-300">
                      {actionError}
                    </div>
                  )}

                  {/* Action Bar */}
                  <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80">
                    {canStart && (
                      <button
                        onClick={(e) => handleStart(selectedProjectId, e)}
                        disabled={actionLoading}
                        className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-sm transition-all"
                      >
                        <Play className="w-3.5 h-3.5" />
                        <span>Start Workflow</span>
                      </button>
                    )}

                    <button
                      onClick={() => loadProjectData(selectedProjectId)}
                      className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs transition-all"
                    >
                      <RotateCw className="w-3.5 h-3.5" />
                      <span>Refresh</span>
                    </button>

                    <a
                      href={`http://localhost:8000/api/projects/${selectedProjectId}/report/export`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs transition-all"
                    >
                      <Download className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Export Report</span>
                    </a>

                    <button
                      onClick={(e) => handleDelete(selectedProjectId, e)}
                      disabled={actionLoading}
                      className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-rose-950/30 hover:bg-rose-900/40 text-rose-300 border border-rose-500/30 text-xs transition-all ml-auto"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Delete</span>
                    </button>
                  </div>
                </div>
              )}


              {/* Action State Panels */}
              {isWaiting && (
                <ApprovalStation
                  projectId={selectedProjectId}
                  project={selectedProject}
                  evaluation={evaluation}
                  documentation={documentation}
                  requirements={requirements}
                  testResults={testResults}
                  reviewResults={reviewResults}
                  onAction={handleApprovalAction}
                />
              )}

              {isCompleted && packageInfo && (
                <CompletedCelebration
                  projectId={selectedProjectId}
                  packageInfo={packageInfo}
                  onNavigateTab={(tab: any) => setActiveTab(tab)}
                />
              )}

              {/* Glassmorphic Tabs Navigation */}
              <div className="glass-panel rounded-2xl border border-slate-800/80 shadow-2xl overflow-hidden">
                <div className="flex border-b border-slate-800 overflow-x-auto p-1.5 bg-slate-950/40 gap-1">
                  {TABS.map((tab) => (
                    <button
                      key={tab.key}
                      onClick={() => setActiveTab(tab.key as any)}
                      className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                        activeTab === tab.key
                          ? 'bg-indigo-600/30 text-cyan-300 border border-indigo-500/40 shadow-[0_0_15px_rgba(99,102,241,0.25)]'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                <div className="p-5">
                  {activeTab === 'overview' && (
                    <OverviewSection
                      requirements={requirements}
                      plan={plan}
                      project={selectedProject}
                      onRetry={() => handleRetry(selectedProjectId)}
                    />
                  )}

                  {activeTab === 'agents' && (
                    <AgentExecutionView
                      agentRuns={agentRuns}
                      requirements={requirements}
                      plan={plan}
                      testResults={testResults}
                      reviewResults={reviewResults}
                      debugResults={debugResults}
                      evaluation={evaluation}
                      documentation={documentation}
                    />
                  )}

                  {activeTab === 'iterations' && (
                    <IterationMatrix
                      testResults={testResults}
                      reviewResults={reviewResults}
                      debugResults={debugResults}
                    />
                  )}

                  {activeTab === 'evaluation' && <EvaluationView evaluation={evaluation} />}

                  {activeTab === 'versions' && (
                    <VersionTimeline
                      versions={versions}
                      evaluations={versions.map((v) => ({
                        version: v.version,
                        ...v,
                      }))}
                    />
                  )}

                  {activeTab === 'code' && (
                    <CodeStudio
                      projectId={selectedProjectId}
                      files={files}
                      selectedFile={selectedFile}
                      fileContent={fileContent}
                      onFileClick={handleFileClick}
                    />
                  )}

                  {activeTab === 'preview' && (
                    <LiveAppPreview
                      projectId={selectedProjectId}
                      projectName={selectedProject?.name}
                    />
                  )}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Create Project Modal */}
      {showCreate && (
        <CreateProjectModal
          onClose={() => setShowCreate(false)}
          onCreate={handleCreateProject}
        />
      )}
    </div>
  );
}
