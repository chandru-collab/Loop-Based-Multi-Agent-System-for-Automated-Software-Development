export const WORKFLOW_STAGES = [
  { key: 'requirement', label: 'Requirements Analysis', shortLabel: 'Requirements', icon: '📋', stage: 'requirement', desc: 'Analyzes functional scope, user stories & ambiguities' },
  { key: 'planner', label: 'System Planning', shortLabel: 'Planning', icon: '🗺️', stage: 'planner', desc: 'Architects modules, endpoints & database schemas' },
  { key: 'coder', label: 'Code Generation', shortLabel: 'Coder', icon: '⚙️', stage: 'coder', desc: 'Generates full project implementation files' },
  { key: 'tester', label: 'Sandbox Testing', shortLabel: 'Testing', icon: '🧪', stage: 'tester', loop: true, desc: 'Executes automated test suites & collects logs' },
  { key: 'reviewer', label: 'Code Review', shortLabel: 'Review', icon: '🔍', stage: 'reviewer', loop: true, desc: 'Audits code security, bugs, logic & performance' },
  { key: 'debugger', label: 'Auto Debugger', shortLabel: 'Debugger', icon: '🔧', stage: 'debugger', loop: true, desc: 'Fixes test failures & quality gate blockers in a loop' },
  { key: 'evaluator', label: 'Evaluation Metrics', shortLabel: 'Evaluation', icon: '📊', stage: 'evaluator', desc: 'Computes test pass rates, coverage & gate decisions' },
  { key: 'documentor', label: 'Documentation', shortLabel: 'Documentation', icon: '📝', stage: 'documentor', desc: 'Generates README, API specs & deployment guides' },
  { key: 'approval', label: 'User Approval Gate', shortLabel: 'Approval', icon: '✅', stage: 'WAITING_FOR_APPROVAL', desc: 'Human-in-the-loop review and revision gating' },
  { key: 'packaging', label: 'Release Packaging', shortLabel: 'Packaging', icon: '📦', stage: 'PACKAGING', desc: 'Packages deliverable ZIP archive with SHA-256' },
];

export function getStageStatus(
  stageKey: string,
  project: any,
  agentRuns: any[]
): 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'WAITING' {
  if (!project) return 'PENDING';
  const status = project.status;
  const currentStage = project.current_stage;

  const stageNames: Record<string, string[]> = {
    requirement: ['requirement', 'REQUIREMENT_ANALYSIS'],
    planner: ['planner', 'PLANNING'],
    coder: ['coder', 'CODE_GENERATING'],
    tester: ['tester', 'TESTING'],
    reviewer: ['reviewer', 'REVIEWING'],
    debugger: ['debugger', 'DEBUGGING'],
    evaluator: ['evaluator', 'EVALUATING'],
    documentor: ['documentor', 'DOCUMENTING'],
    approval: ['WAITING_FOR_APPROVAL'],
    packaging: ['PACKAGING'],
  };

  const names = stageNames[stageKey] || [];

  if (status === 'COMPLETED') {
    return 'COMPLETED';
  }

  if (status === 'FAILED' && names.some((n) => currentStage?.includes(n.toUpperCase()) || currentStage === n)) {
    return 'FAILED';
  }

  if (status === 'WAITING_FOR_APPROVAL' && stageKey === 'approval') {
    return 'WAITING';
  }

  if (status === 'PACKAGING' && stageKey === 'packaging') {
    return 'RUNNING';
  }

  if (names.some((n) => currentStage === n)) {
    return 'RUNNING';
  }

  // Determine if completed by progression sequence
  const stageOrder = WORKFLOW_STAGES.map((s) => s.key);
  const thisIdx = stageOrder.indexOf(stageKey);
  const currentIdx = stageOrder.findIndex((k) => stageNames[k]?.some((n) => n === currentStage));

  if (currentIdx > thisIdx) return 'COMPLETED';

  const agentNameMap: Record<string, string> = {
    requirement: 'RequirementAgent',
    planner: 'PlannerAgent',
    coder: 'CodeGenerationAgent',
    tester: 'TestingAgent',
    reviewer: 'ReviewerAgent',
    debugger: 'DebuggerAgent',
    evaluator: 'EvaluationMetricsAgent',
    documentor: 'DocumentationAgent',
  };

  const agentName = agentNameMap[stageKey];
  if (agentName && agentRuns.some((r) => r.agent_name === agentName && r.status === 'completed')) {
    return 'COMPLETED';
  }

  return 'PENDING';
}
