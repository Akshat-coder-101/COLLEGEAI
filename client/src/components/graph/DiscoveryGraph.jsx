import React, { useMemo } from 'react';
import { ReactFlow, Background, Controls, Handle, Position } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// Custom node rendering for scientific entities
const ScientificNode = ({ data }) => {
  const typeColors = {
    primary: "border-scientific-500 bg-scientific-50 text-scientific-950",
    pathology: "border-rose-400 bg-rose-50 text-rose-950",
    mechanism: "border-amber-400 bg-amber-50 text-amber-950",
    crossDomain: "border-purple-400 bg-purple-50 text-purple-950",
    intervention: "border-emerald-400 bg-emerald-50 text-emerald-950",
  };

  const styleClass = typeColors[data.type] || "border-slate-300 bg-white text-slate-800";

  return (
    <div className={`px-2.5 py-1.5 sm:px-3 sm:py-2 rounded-xl border shadow-sm text-[11px] sm:text-xs font-semibold max-w-[150px] sm:max-w-[180px] text-center ${styleClass}`}>
      <Handle type="target" position={Position.Top} className="w-1.5 h-1.5 bg-slate-400" />
      <div className="leading-tight truncate sm:whitespace-normal">{data.label}</div>
      <div className="text-[8px] sm:text-[9px] font-mono font-normal opacity-70 uppercase tracking-wider mt-0.5">
        {data.type}
      </div>
      <Handle type="source" position={Position.Bottom} className="w-1.5 h-1.5 bg-slate-400" />
    </div>
  );
};

export const DiscoveryGraph = ({ graphData }) => {
  if (!graphData || !graphData.nodes || graphData.nodes.length === 0) return null;

  const nodeTypes = useMemo(() => ({ scientific: ScientificNode }), []);

  const nodes = useMemo(() => {
    const positions = [
      { x: 240, y: 30 },
      { x: 60, y: 150 },
      { x: 420, y: 150 },
      { x: 140, y: 280 },
      { x: 420, y: 280 },
      { x: 240, y: 390 },
    ];

    return graphData.nodes.map((node, i) => ({
      id: node.id,
      type: 'scientific',
      data: { label: node.label, type: node.type },
      position: positions[i % positions.length] || { x: 80 + i * 70, y: 80 + i * 40 },
    }));
  }, [graphData.nodes]);

  const edges = useMemo(() => {
    return graphData.edges.map((edge, i) => ({
      id: `e-${edge.source}-${edge.target}-${i}`,
      source: edge.source,
      target: edge.target,
      label: edge.relation,
      labelStyle: { fontSize: 9, fill: '#64748b', fontWeight: 500 },
      animated: edge.status === 'gap_hypothesis',
      style: {
        stroke: edge.status === 'gap_hypothesis' ? '#8b5cf6' : edge.status === 'discovered' ? '#f59e0b' : '#0ea5e9',
        strokeWidth: 1.5,
      },
    }));
  }, [graphData.edges]);

  return (
    <div className="w-full h-80 sm:h-96 bg-slate-50/50 rounded-xl border border-slate-200 overflow-hidden relative min-w-0">
      <div className="absolute top-2 left-2 z-10 flex flex-wrap gap-1.5 text-[9px] sm:text-[10px] bg-white/95 backdrop-blur-xs p-1.5 rounded-lg border border-slate-200 shadow-xs max-w-[calc(100%-16px)]">
        <span className="flex items-center gap-1 text-scientific-700 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-scientific-500" /> Primary
        </span>
        <span className="flex items-center gap-1 text-rose-700 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-500" /> Pathology
        </span>
        <span className="flex items-center gap-1 text-amber-700 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-500" /> Mechanism
        </span>
        <span className="flex items-center gap-1 text-purple-700 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-purple-500" /> Cross-Domain
        </span>
        <span className="flex items-center gap-1 text-emerald-700 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Intervention
        </span>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-right"
      >
        <Background gap={16} color="#cbd5e1" size={1} />
        <Controls showInteractive={false} className="bg-white border border-slate-200 shadow-xs rounded-lg !bottom-2 !left-2 !top-auto" />
      </ReactFlow>
    </div>
  );
};
