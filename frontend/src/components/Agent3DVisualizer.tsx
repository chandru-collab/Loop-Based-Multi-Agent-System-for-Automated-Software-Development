import React, { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';
import { WORKFLOW_STAGES, getStageStatus } from '../utils/workflowUtils';
import {
  GitCommit,
  CheckCircle2,
  Clock,
  AlertCircle,
  RefreshCw,
  Repeat,
  Sparkles,
  Bot,
  Terminal,
  ShieldCheck,
  PackageCheck,
  ChevronRight,
  Workflow,
  Orbit,
  Maximize2,
  Minimize2,
  Rotate3d,
} from 'lucide-react';

interface Agent3DVisualizerProps {
  project: any;
  agentRuns: any[];
  activeAgentKey?: string;
  onSelectStage?: (stageKey: string) => void;
}

export const Agent3DVisualizer: React.FC<Agent3DVisualizerProps> = ({
  project,
  agentRuns,
  onSelectStage,
}) => {
  const [viewMode, setViewMode] = useState<'3d' | 'dag'>('3d');
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const canvasContainerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  const isExpA = project?.experiment_type === 'A';
  const stages = WORKFLOW_STAGES.filter((s) => !(isExpA && s.loop));

  // Three.js 3D Central Galaxy Sphere Setup
  useEffect(() => {
    if (viewMode !== '3d' || !canvasContainerRef.current) return;

    const container = canvasContainerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight || 380;

    // 1. Scene & Camera
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 4.5, 17);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // 2. WebGL Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    rendererRef.current = renderer;

    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    container.appendChild(renderer.domElement);

    // 3. Lighting
    const ambientLight = new THREE.AmbientLight(0x818cf8, 0.9);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x38bdf8, 2.5, 60);
    pointLight.position.set(6, 12, 10);
    scene.add(pointLight);

    const blueLight = new THREE.PointLight(0x6366f1, 2.5, 60);
    blueLight.position.set(-8, -6, -5);
    scene.add(blueLight);

    // 4. Central Galaxy Sphere Group
    const galaxyGroup = new THREE.Group();
    scene.add(galaxyGroup);

    // Inner Core Holographic Wireframe Sphere
    const coreGeo = new THREE.IcosahedronGeometry(2.6, 2);
    const coreMat = new THREE.MeshStandardMaterial({
      color: 0x6366f1,
      wireframe: true,
      transparent: true,
      opacity: 0.45,
      emissive: 0x4338ca,
      emissiveIntensity: 0.8,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    galaxyGroup.add(coreMesh);

    // Inner Solid Luminous Core Sphere
    const innerGeo = new THREE.SphereGeometry(1.7, 32, 32);
    const innerMat = new THREE.MeshStandardMaterial({
      color: 0x1e1b4b,
      emissive: 0x3b82f6,
      emissiveIntensity: 0.8,
      roughness: 0.25,
      metalness: 0.85,
    });
    const innerSphere = new THREE.Mesh(innerGeo, innerMat);
    galaxyGroup.add(innerSphere);

    // Primary Rotating Orbital Ring
    const ringGeo = new THREE.RingGeometry(6.0, 6.08, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x818cf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.35,
    });
    const orbitalRing = new THREE.Mesh(ringGeo, ringMat);
    orbitalRing.rotation.x = Math.PI / 2.3;
    galaxyGroup.add(orbitalRing);

    // Secondary Tilted Orbital Ring
    const ringGeo2 = new THREE.RingGeometry(6.8, 6.86, 64);
    const ringMat2 = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.25,
    });
    const orbitalRing2 = new THREE.Mesh(ringGeo2, ringMat2);
    orbitalRing2.rotation.x = Math.PI / 1.7;
    orbitalRing2.rotation.y = Math.PI / 4.5;
    galaxyGroup.add(orbitalRing2);

    // Background Particle Starfield
    const starGeo = new THREE.BufferGeometry();
    const starCount = 400;
    const starPositions = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount * 3; i += 3) {
      starPositions[i] = (Math.random() - 0.5) * 50;
      starPositions[i + 1] = (Math.random() - 0.5) * 50;
      starPositions[i + 2] = (Math.random() - 0.5) * 50;
    }
    starGeo.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
    const starMat = new THREE.PointsMaterial({
      size: 0.14,
      color: 0xa5b4fc,
      transparent: true,
      opacity: 0.75,
    });
    const starField = new THREE.Points(starGeo, starMat);
    scene.add(starField);

    // 5. Orbiting 3D Agent Spheres
    const agentMeshes: { mesh: THREE.Mesh; halo: THREE.Mesh; stageKey: string; angle: number; radius: number }[] = [];
    const radius = 6.4;
    const totalStages = stages.length;

    stages.forEach((stage, idx) => {
      const angle = (idx / totalStages) * Math.PI * 2;
      const status = getStageStatus(stage.key, project, agentRuns);

      let color = 0x475569;
      let emissive = 0x1e293b;
      let emissiveIntensity = 0.2;

      if (status === 'COMPLETED') {
        color = 0x10b981;
        emissive = 0x059669;
        emissiveIntensity = 0.9;
      } else if (status === 'RUNNING') {
        color = 0x38bdf8;
        emissive = 0x0284c7;
        emissiveIntensity = 1.3;
      } else if (status === 'WAITING') {
        color = 0xf59e0b;
        emissive = 0xd97706;
        emissiveIntensity = 1.0;
      } else if (status === 'FAILED') {
        color = 0xf43f5e;
        emissive = 0xe11d48;
        emissiveIntensity = 1.1;
      }

      // Orbiting Sphere Mesh
      const agentGeo = new THREE.SphereGeometry(0.58, 24, 24);
      const agentMat = new THREE.MeshStandardMaterial({
        color,
        emissive,
        emissiveIntensity,
        roughness: 0.2,
        metalness: 0.7,
      });
      const agentMesh = new THREE.Mesh(agentGeo, agentMat);

      // Glowing Halo Shell
      const haloGeo = new THREE.SphereGeometry(0.78, 16, 16);
      const haloMat = new THREE.MeshBasicMaterial({
        color: emissive,
        transparent: true,
        opacity: status === 'RUNNING' ? 0.6 : 0.25,
        wireframe: true,
      });
      const haloMesh = new THREE.Mesh(haloGeo, haloMat);
      agentMesh.add(haloMesh);

      // 3D Orbital Coordinates
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const y = Math.sin(angle * 2) * 1.3;
      agentMesh.position.set(x, y, z);
      (agentMesh as any).stageKey = stage.key;

      galaxyGroup.add(agentMesh);
      agentMeshes.push({ mesh: agentMesh, halo: haloMesh, stageKey: stage.key, angle, radius });
    });

    // Connecting Orbital Line Spline
    const linePoints: THREE.Vector3[] = [];
    agentMeshes.forEach((item) => {
      linePoints.push(item.mesh.position.clone());
    });
    if (agentMeshes.length > 0) {
      linePoints.push(agentMeshes[0].mesh.position.clone());
    }
    const lineCurve = new THREE.CatmullRomCurve3(linePoints, true);
    const lineGeo = new THREE.BufferGeometry().setFromPoints(lineCurve.getPoints(120));
    const lineMat = new THREE.LineBasicMaterial({
      color: 0x6366f1,
      transparent: true,
      opacity: 0.4,
    });
    const orbitLine = new THREE.Line(lineGeo, lineMat);
    galaxyGroup.add(orbitLine);

    // 6. Interactive Mouse Drag Controls
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const deltaX = e.clientX - previousMousePosition.x;
      const deltaY = e.clientY - previousMousePosition.y;

      galaxyGroup.rotation.y += deltaX * 0.006;
      galaxyGroup.rotation.x += deltaY * 0.006;

      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    const domElement = renderer.domElement;
    domElement.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);

    // Raycaster Click Handler
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onClick = (e: MouseEvent) => {
      const rect = domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(agentMeshes.map((m) => m.mesh));

      if (intersects.length > 0) {
        const hitMesh = intersects[0].object as any;
        if (hitMesh.stageKey) {
          setSelectedNode(hitMesh.stageKey);
          if (onSelectStage) onSelectStage(hitMesh.stageKey);
        }
      }
    };
    domElement.addEventListener('click', onClick);

    // Resize Handler
    const handleResize = () => {
      if (!container || !camera || !renderer) return;
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight || 380;
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    };
    window.addEventListener('resize', handleResize);

    // 7. Animation Loop
    const clock = new THREE.Clock();
    const animate = () => {
      animationFrameRef.current = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const elapsedTime = clock.getElapsedTime();

      // Auto rotation
      if (!isDragging) {
        galaxyGroup.rotation.y += delta * 0.28;
        galaxyGroup.rotation.x = Math.sin(elapsedTime * 0.3) * 0.15;
      }

      // Central core pulsation
      coreMesh.rotation.y -= delta * 0.45;
      coreMesh.rotation.z += delta * 0.25;
      const pulse = 1 + Math.sin(elapsedTime * 2.8) * 0.05;
      coreMesh.scale.set(pulse, pulse, pulse);

      // Orbiting agent halo pulses
      agentMeshes.forEach((item) => {
        const itemPulse = 1 + Math.sin(elapsedTime * 4 + item.angle) * 0.18;
        item.halo.scale.set(itemPulse, itemPulse, itemPulse);
      });

      // Starfield slow background drift
      starField.rotation.y -= delta * 0.06;

      renderer.render(scene, camera);
    };
    animate();

    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      domElement.removeEventListener('mousedown', onMouseDown);
      domElement.removeEventListener('click', onClick);
      renderer.dispose();
    };
  }, [viewMode, project?.status, project?.experiment_type, agentRuns.length, stages.length, onSelectStage]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3" />
            Done
          </span>
        );
      case 'RUNNING':
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-cyan-300 bg-cyan-950/80 px-2 py-0.5 rounded-full border border-cyan-400/40 animate-pulse">
            <RefreshCw className="w-3 h-3 animate-spin text-cyan-400" />
            Running
          </span>
        );
      case 'WAITING':
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-amber-300 bg-amber-950/70 px-2 py-0.5 rounded-full border border-amber-500/40 animate-pulse">
            <Clock className="w-3 h-3 text-amber-400" />
            Action Req.
          </span>
        );
      case 'FAILED':
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-rose-300 bg-rose-950/70 px-2 py-0.5 rounded-full border border-rose-500/40">
            <AlertCircle className="w-3 h-3 text-rose-400" />
            Failed
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-[11px] text-slate-500 bg-slate-900/60 px-2 py-0.5 rounded-full border border-slate-800">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-600" />
            Queued
          </span>
        );
    }
  };

  const getStageIcon = (key: string) => {
    switch (key) {
      case 'requirement':
        return <Bot className="w-4 h-4 text-indigo-400" />;
      case 'planner':
        return <Workflow className="w-4 h-4 text-sky-400" />;
      case 'coder':
        return <Terminal className="w-4 h-4 text-emerald-400" />;
      case 'tester':
        return <Sparkles className="w-4 h-4 text-teal-400" />;
      case 'reviewer':
        return <ShieldCheck className="w-4 h-4 text-amber-400" />;
      case 'debugger':
        return <Repeat className="w-4 h-4 text-rose-400" />;
      case 'evaluator':
        return <GitCommit className="w-4 h-4 text-purple-400" />;
      case 'documentor':
        return <Terminal className="w-4 h-4 text-blue-400" />;
      case 'approval':
        return <Clock className="w-4 h-4 text-yellow-400" />;
      case 'packaging':
        return <PackageCheck className="w-4 h-4 text-green-400" />;
      default:
        return <Bot className="w-4 h-4 text-indigo-400" />;
    }
  };

  return (
    <div
      className={`glass-panel rounded-2xl border border-slate-800/80 shadow-subtle-card overflow-hidden transition-all ${
        isFullscreen ? 'fixed inset-4 z-50 flex flex-col bg-slate-950/95 backdrop-blur-2xl' : ''
      }`}
    >
      {/* Visualizer Header */}
      <div className="p-4 sm:p-5 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-3 bg-slate-900/40">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Orbit className="w-4 h-4 animate-spin-slow" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-slate-100 font-display">
                Agent Orbital Sphere & Flow
              </h2>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-950/60 text-cyan-300 font-mono border border-cyan-800/40">
                Interactive 3D Galaxy
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Drag to rotate 3D sphere · Click nodes to inspect agent telemetry
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View Switcher: 3D Galaxy vs DAG Flow */}
          <div className="flex items-center bg-slate-900/90 border border-slate-800 p-1 rounded-xl">
            <button
              onClick={() => setViewMode('3d')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                viewMode === '3d'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Rotate3d className="w-3.5 h-3.5" />
              <span>3D Sphere</span>
            </button>
            <button
              onClick={() => setViewMode('dag')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                viewMode === 'dag'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Workflow className="w-3.5 h-3.5" />
              <span>DAG Flow</span>
            </button>
          </div>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-900/80 hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-all"
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen Visualizer'}
          >
            {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Main Visualizer Body */}
      {viewMode === '3d' ? (
        <div className="relative w-full h-[360px] sm:h-[400px] bg-gradient-to-b from-slate-950 via-[#070d1e] to-slate-950 flex flex-col justify-between overflow-hidden">
          {/* 3D WebGL Canvas Viewport */}
          <div
            ref={canvasContainerRef}
            className="absolute inset-0 w-full h-full cursor-grab active:cursor-grabbing z-0"
          />

          {/* Top HUD overlay */}
          <div className="relative z-10 p-3.5 flex items-center justify-between pointer-events-none">
            <div className="flex items-center gap-2 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-800/80 pointer-events-auto shadow-lg">
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <span className="text-[11px] font-mono text-slate-300">
                Core State: <strong className="text-cyan-300">{project?.status || 'IDLE'}</strong>
              </span>
            </div>

            <div className="text-[11px] text-slate-400 bg-slate-900/80 backdrop-blur-md px-2.5 py-1 rounded-xl border border-slate-800/80 pointer-events-auto">
              {stages.length} Nodes in Orbit
            </div>
          </div>

          {/* Bottom Interactive Stage Pills */}
          <div className="relative z-10 p-3.5 flex items-center gap-2 overflow-x-auto bg-slate-950/70 backdrop-blur-md border-t border-slate-800/60 scrollbar-thin">
            {stages.map((stage) => {
              const status = getStageStatus(stage.key, project, agentRuns);
              const isSelected = selectedNode === stage.key;

              return (
                <button
                  key={stage.key}
                  onClick={() => {
                    setSelectedNode(stage.key);
                    if (onSelectStage) onSelectStage(stage.key);
                  }}
                  className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs whitespace-nowrap transition-all ${
                    isSelected
                      ? 'bg-indigo-600/30 border-indigo-500 text-cyan-200'
                      : status === 'RUNNING'
                      ? 'bg-cyan-950/60 border-cyan-500/50 text-cyan-300 animate-pulse'
                      : status === 'COMPLETED'
                      ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300'
                      : 'bg-slate-900/80 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {getStageIcon(stage.key)}
                  <span className="font-medium text-[11px]">{stage.name}</span>
                  {status === 'COMPLETED' && <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
                  {status === 'RUNNING' && <RefreshCw className="w-3 h-3 text-cyan-400 animate-spin" />}
                </button>
              );
            })}
          </div>
        </div>
      ) : (
        /* DAG Pipeline Mode */
        <div className="p-4 sm:p-5 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {stages.map((stage, idx) => {
              const status = getStageStatus(stage.key, project, agentRuns);
              const run = agentRuns?.find((r) => r.agent_name?.toLowerCase().includes(stage.key));
              const isSelected = selectedNode === stage.key;

              return (
                <div
                  key={stage.key}
                  onClick={() => {
                    setSelectedNode(stage.key);
                    if (onSelectStage) onSelectStage(stage.key);
                  }}
                  className={`relative p-3.5 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'border-indigo-500/80 bg-indigo-950/20 shadow-sm ring-1 ring-indigo-500/30'
                      : status === 'RUNNING'
                      ? 'border-cyan-500/40 bg-cyan-950/20'
                      : status === 'COMPLETED'
                      ? 'border-emerald-500/30 bg-emerald-950/10'
                      : 'border-slate-800/80 bg-slate-900/30 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-lg bg-slate-800/90 border border-slate-700/60 flex items-center justify-center">
                        {getStageIcon(stage.key)}
                      </div>
                      <span className="text-xs font-bold text-slate-200">{stage.name}</span>
                    </div>
                    {getStatusBadge(status)}
                  </div>

                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed mb-2.5">
                    {stage.description}
                  </p>

                  <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] font-mono text-slate-500">
                    <span>Node #{idx + 1}</span>
                    {run?.duration_seconds && (
                      <span className="text-slate-400">{run.duration_seconds.toFixed(1)}s</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Selected Node Details Drawer */}
      {selectedNode && (
        <div className="p-4 bg-slate-900/90 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center">
              {getStageIcon(selectedNode)}
            </div>
            <div>
              <span className="font-bold text-slate-200">
                {stages.find((s) => s.key === selectedNode)?.name || selectedNode}
              </span>
              <span className="text-slate-400 ml-2 font-normal">
                {stages.find((s) => s.key === selectedNode)?.description}
              </span>
            </div>
          </div>

          <button
            onClick={() => {
              if (onSelectStage) onSelectStage(selectedNode);
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-all shadow-sm"
          >
            <span>Open Studio Tab</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
};
