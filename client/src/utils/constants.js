export const RESEARCH_DOMAINS = [
  { id: 'biomedical', label: 'Biomedical & Life Sciences' },
  { id: 'cs-ai', label: 'Computer Science & AI' },
  { id: 'neuroscience', label: 'Neuroscience & Cognitive Science' },
  { id: 'physics-materials', label: 'Physics & Materials Science' },
  { id: 'environmental', label: 'Environmental & Climate Science' },
  { id: 'pharmacology', label: 'Pharmacology & Drug Discovery' },
  { id: 'cross-disciplinary', label: 'Interdisciplinary / Emerging Fields' },
];

export const RESEARCH_SCOPES = [
  { id: 'comprehensive', label: 'Comprehensive Synthesis', desc: 'Full literature exploration and hypothesis formulation' },
  { id: 'gap-detection', label: 'Research Gap Detection', desc: 'Identify overlooked questions and methodological contradictions' },
  { id: 'hypothesis-only', label: 'Hypothesis Formulation', desc: 'Rapid generation of falsifiable, testable claims' },
];

export const WORKSPACE_TABS = [
  { id: 'overview', label: 'Overview', icon: 'LayoutDashboard' },
  { id: 'sources', label: 'Sources & Evidence', icon: 'BookOpen' },
  { id: 'comparisons', label: 'Comparative Analysis', icon: 'Scale' },
  { id: 'discoveries', label: 'Research Discoveries', icon: 'Sparkles' },
  { id: 'hypotheses', label: 'Hypotheses', icon: 'FlaskConical' },
  { id: 'experiments', label: 'Experiments', icon: 'Workflow' },
];

export const DEFAULT_RECENT_PROJECTS = [
  {
    id: "proj_amyloid_microglia_2026",
    title: "Role of TREM2-mediated microglial clearance in early-stage Alzheimer's tau seeding",
    domain: "Neuroscience & Cognitive Science",
    scope: "Comprehensive Synthesis",
    status: "completed",
    createdAt: "2026-11-03T14:32:00Z",
    sourceCount: 14,
    gapCount: 3,
    hypothesisCount: 2,
  },
  {
    id: "proj_perovskite_degradation_2026",
    title: "Mechanisms of ion migration under operational bias in 2D/3D hybrid perovskite solar cells",
    domain: "Physics & Materials Science",
    scope: "Research Gap Detection",
    status: "completed",
    createdAt: "2026-11-04T09:15:00Z",
    sourceCount: 18,
    gapCount: 4,
    hypothesisCount: 3,
  },
  {
    id: "proj_crispr_offtarget_rna_2026",
    title: "Mitigating prime editor RNA-templated off-target indels in therapeutic hematology",
    domain: "Biomedical & Life Sciences",
    scope: "Hypothesis Formulation",
    status: "processing",
    createdAt: "2026-11-05T18:40:00Z",
    sourceCount: 8,
    gapCount: 2,
    hypothesisCount: 1,
  }
];

