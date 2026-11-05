export const MOCK_PROJECT_DETAILS = {
  id: "proj_amyloid_microglia_2026",
  title: "Role of TREM2-mediated microglial clearance in early-stage Alzheimer's tau seeding",
  question: "How does microglial TREM2 signaling modulate tau spreading and oligodendrocyte vulnerability in early-stage Alzheimer's disease?",
  domain: "Neuroscience & Cognitive Science",
  scope: "Comprehensive Synthesis",
  status: "completed",
  createdAt: "2026-11-03T14:32:00Z",
  completedAt: "2026-11-03T14:35:12Z",
  workflow: {
    currentStage: "completed",
    stages: [
      { id: "retrieval", name: "Literature Ingestion", status: "completed", timestamp: "14:32:10" },
      { id: "extraction", name: "Evidence & Finding Extraction", status: "completed", timestamp: "14:33:05" },
      { id: "comparison", name: "Comparative & Conflict Synthesis", status: "completed", timestamp: "14:33:55" },
      { id: "discovery", name: "Research Gap Identification", status: "completed", timestamp: "14:34:30" },
      { id: "hypotheses", name: "Testable Hypothesis Formulation", status: "completed", timestamp: "14:35:12" },
    ]
  },
  stats: {
    papersReviewed: 14,
    extractedFindings: 42,
    gapsIdentified: 3,
    crossDomainLinks: 2,
    hypothesesFormulated: 2,
    experimentsAvailable: false,
  },
  overview: {
    summary: "Investigation into microglial TREM2 indicates a bifurcated role: protective compaction of early tau oligomers in early stages, but deleterious pro-inflammatory cytokine release during advanced neurodegeneration. Crucially, a significant blind spot exists regarding how TREM2-dependent lipid droplet-accumulating microglia (LDAM) interact with nearby myelinating oligodendrocytes.",
    keyFindings: [
      "TREM2 R47H loss-of-function variants reduce microglial phagocytosis of hyperphosphorylated tau seeds by 68% in vitro.",
      "APOE4 significantly downregulates TREM2 surface shedding via ADAM10 inhibition in human iPSC-derived microglia.",
      "Tau seeding in the entorhinal cortex accelerates microglial transition into a senescent, lipid-laden phenotype."
    ],
    primaryGaps: [
      "Lack of spatial transcriptomic resolution separating homeostatic microglia from plaque-associated microglia during initial tau propagation.",
      "Unknown cross-talk mechanism between TREM2 lipid sensing and oligodendrocyte precursor cell (OPC) survival under chronic amyloid stress."
    ],
    primaryDiscoveries: [
      "Cross-domain connection between microglial lipid metabolism (Atherosclerosis literature) and local myelin sheath degeneration in early Alzheimer's.",
      "Apparent contradiction between murine transgenic models showing protective TREM2 upregulation and human post-mortem single-nucleus RNA-seq showing pathogenic TREM2 hyper-activation."
    ]
  },
  sources: [
    {
      id: "src-01",
      title: "TREM2 activation promotes microglial clearance of pathologic tau and limits secondary neurodegeneration",
      authors: "Leyns, C. E. G., Ulrich, J. D., Finn, M. B., et al.",
      year: 2021,
      journal: "Science Translational Medicine",
      doi: "10.1126/scitranslmed.aau6221",
      url: "https://doi.org/10.1126/scitranslmed.aau6221",
      relevanceScore: 0.96,
      methodology: "In vivo PS19 tauopathy mouse models with TREM2 agonistic monoclonal antibodies (AL002a).",
      extractedFindings: [
        "Systemic administration of TREM2-agonistic antibody reduced sarkosyl-insoluble phosphorylated tau by 43% in the hippocampus.",
        "Microglia displayed enhanced morphological ramification around dystrophic neurites without inducing systemic inflammation."
      ],
      supportingQuotes: [
        {
          quote: "Sustained TREM2 agonism rescued synaptic density and ameliorated behavioral spatial memory deficits in 9-month-old PS19 mice without elevating TNF-alpha.",
          page: "Page 8, Paragraph 3"
        }
      ]
    },
    {
      id: "src-02",
      title: "Human single-nucleus RNA sequencing reveals distinct microglial states in Alzheimer's disease cortices",
      authors: "Mathys, H., Davila-Velderrain, J., Peng, Z., et al.",
      year: 2023,
      journal: "Nature Neuroscience",
      doi: "10.1038/s41593-023-01315-7",
      url: "https://doi.org/10.1038/s41593-023-01315-7",
      relevanceScore: 0.94,
      methodology: "snRNA-seq on 427 prefrontal cortex samples from the ROSMAP longitudinal aging cohort.",
      extractedFindings: [
        "Identified 12 distinct microglial subclusters; disease-associated microglia (DAM) signature in humans differs substantially from mouse Dam profiles.",
        "High TREM2 expression in advanced stages strongly correlates with glycolytic reprogramming and senescence-associated secretory phenotype (SASP)."
      ],
      supportingQuotes: [
        {
          quote: "Contrary to transgenic mouse paradigms where TREM2 upregulation is universally protective, human cortical microglia exhibit an uncoupling between phagocytic markers and metabolic viability at Braak stage IV-VI.",
          page: "Page 14, Discussion"
        }
      ]
    },
    {
      id: "src-03",
      title: "Lipid droplet-accumulating microglia represent a dysfunctional state in the aging and diseased brain",
      authors: "Marschallinger, J., Iram, T., Zardeneta, M., et al.",
      year: 2020,
      journal: "Nature Cell Biology",
      doi: "10.1038/s41556-019-0456-1",
      url: "https://doi.org/10.1038/s41556-019-0456-1",
      relevanceScore: 0.91,
      methodology: "Lipidomics, FACS sorting, and ex vivo hippocampal slice electrophysiology.",
      extractedFindings: [
        "Lipid droplet-accumulating microglia (LDAM) produce elevated baseline reactive oxygen species (ROS) and fail to clear amyloid fibrils.",
        "Defective autophagy and cholesterol ester accumulation precede tau tangles in adjacent pyramidal neurons."
      ],
      supportingQuotes: [
        {
          quote: "LDAM are defective in phagocytosis, produce high levels of ROS, and secrete neurotoxic factors, suggesting that lipid storage failure directly exacerbates neurodegenerative cascades.",
          page: "Page 224, Results"
        }
      ]
    },
    {
      id: "src-04",
      title: "Oligodendrocyte-microglia crosstalk drives remyelination failure in chronic neuroinflammation",
      authors: "Kirby, L. A., Jin, J., Cardona, A. E., et al.",
      year: 2024,
      journal: "Cell Stem Cell",
      doi: "10.1016/j.stem.2024.01.008",
      url: "https://doi.org/10.1016/j.stem.2024.01.008",
      relevanceScore: 0.88,
      methodology: "Single-cell co-culture systems and spatial transcriptomics in mouse cuprizone demyelination.",
      extractedFindings: [
        "Microglial release of Complement C1q and TNF-alpha triggers necroptosis in mature myelinating oligodendrocytes.",
        "TREM2 lipid clearance is required to prevent extracellular cholesterol crystallization that damages nearby myelin sheaths."
      ],
      supportingQuotes: [
        {
          quote: "When microglia fail to clear myelin-derived debris via TREM2, microcrystalline cholesterol crystals form, causing mechanical membrane rupture in adjacent oligodendrocyte processes.",
          page: "Page 112, Paragraph 2"
        }
      ]
    }
  ],
  comparisons: {
    summary: "Comparative synthesis reveals a clear operational paradox: acute mouse models show uniform benefits from TREM2 upregulation, whereas post-mortem human single-cell studies exhibit late-stage metabolic burnout and lipid overload.",
    agreements: [
      {
        topic: "R47H mutation impairs ligand binding",
        consensus: "Unanimous agreement across all 4 studies that genetic loss of TREM2 lipid-binding capacity eliminates protective barrier formation around toxic aggregates.",
        papers: ["Leyns et al. (2021)", "Mathys et al. (2023)", "Marschallinger et al. (2020)"]
      },
      {
        topic: "Lipid accumulation leads to microglial dysfunction",
        consensus: "All sources confirm that excessive intracellular cholesteryl ester accumulation disables phagocytic machinery.",
        papers: ["Marschallinger et al. (2020)", "Kirby et al. (2024)"]
      }
    ],
    contradictions: [
      {
        topic: "Therapeutic window for TREM2 agonism",
        conflict: "Leyns et al. argue that sustained lifelong TREM2 activation is universally neuroprotective, while Mathys et al. demonstrate that hyper-stimulating TREM2 in human cortices with existing tau tangles exacerbates SASP-driven cell death.",
        contextDifference: "Young transgenic rodent overexpression (pre-symptomatic) vs. Elderly human heterogeneous post-mortem tissue (advanced Braak stage V-VI).",
        resolution: "TREM2 agonism is strictly beneficial in early pre-plaque stages but requires metabolic co-factor rescue (e.g. NAD+ supplementation) in symptomatic disease."
      }
    ],
    methodologicalDifferences: [
      {
        aspect: "Model System",
        detail: "Rodent PS19 tau models express 5x human tau with rapid artificial onset; human cortical snRNA-seq captures sporadic natural aging with polygenic background."
      },
      {
        aspect: "Cellular Resolution",
        detail: "Bulk tissue immunohistochemistry vs. 10x Genomics single-nucleus sequencing with 40,000+ individual nuclei."
      }
    ],
    comparisonTable: [
      { parameter: "Target Pathology", leyns: "PS19 Tau aggregates", mathys: "Sporadic AD Plaques & Tangles", marschallinger: "Aging lipid droplets", kirby: "Myelin debris & C1q" },
      { parameter: "TREM2 State", leyns: "Agonistic mAb stimulation", mathys: "Endogenous transcriptional profiling", marschallinger: "Endogenous lipid overload", kirby: "Knockout vs WT co-culture" },
      { parameter: "Phagocytic Efficiency", leyns: "+43% tau clearance", mathys: "Impaired at late stages", marschallinger: "-68% clearance in LDAM", kirby: "Dependent on lipid efflux" },
      { parameter: "Inflammatory Cytokines", leyns: "Unaltered / Normal", mathys: "Elevated SASP markers", marschallinger: "Elevated ROS & TNF-alpha", kirby: "High C1q & TNF-alpha" },
    ]
  },
  discoveries: {
    gaps: [
      {
        id: "gap-1",
        title: "Stage-Dependent Switch Mechanism in TREM2-Mediated Microglial Energetics",
        description: "While TREM2 activation stimulates initial clearance, the exact metabolic checkpoint where microglia exhaust mitochondrial capacity and transition into toxic lipid-accumulating microglia (LDAM) remains uncharacterized in early human tauopathy.",
        significance: "High — dictates the therapeutic dosing window for ongoing Phase 2 TREM2 antibody clinical trials.",
        confidence: 0.89
      },
      {
        id: "gap-2",
        title: "Bystander Oligodendrocyte Death Driven by Microglial Cholesterol Crystallization",
        description: "Prior literature treats neuronal loss and demyelination as separate parallel cascades. No study has evaluated whether microglial TREM2 insufficiency directly precipitates white matter degeneration via mechanical cholesterol crystal shearing.",
        significance: "Crucial — connects Alzheimer's pathology to early MRI white matter hyperintensities.",
        confidence: 0.84
      }
    ],
    crossDomainConnections: [
      {
        id: "cdc-1",
        sourceField: "Vascular Biology & Atherosclerosis",
        targetField: "Neurodegenerative Disease",
        connection: "Macrophage foam cell cholesterol ester crystallization mechanisms (well studied in arterial plaque rupture) directly parallel microglial lipid droplet breakdown failure in Alzheimer's cortex.",
        implication: "Statins and ACAT1/SOAT1 inhibitors developed for cardiovascular disease could restore microglial clearance efficiency in the brain."
      }
    ],
    knowledgeGraph: {
      nodes: [
        { id: "1", label: "TREM2 Signaling", type: "primary" },
        { id: "2", label: "Tau Oligomer Seeding", type: "pathology" },
        { id: "3", label: "Lipid Droplets (LDAM)", type: "mechanism" },
        { id: "4", label: "Oligodendrocyte Necroptosis", type: "pathology" },
        { id: "5", label: "Cholesterol Crystallization", type: "crossDomain" },
        { id: "6", label: "Therapeutic Agonism (AL002)", type: "intervention" }
      ],
      edges: [
        { source: "1", target: "2", relation: "suppresses in early stage", status: "supported" },
        { source: "2", target: "3", relation: "triggers metabolic switch to", status: "supported" },
        { source: "3", target: "5", relation: "fails to efflux lipids causing", status: "discovered" },
        { source: "5", target: "4", relation: "physically punctures & induces", status: "gap_hypothesis" },
        { source: "6", target: "1", relation: "activates receptor", status: "intervention" }
      ]
    }
  },
  hypotheses: [
    {
      id: "hyp-1",
      statement: "In early-stage tauopathy, microglial TREM2 activation prevents oligodendrocyte necroptosis by accelerating the lysosomal clearance of myelin-derived cholesterol crystals before membrane permeabilization occurs.",
      gapAddressed: "Bystander Oligodendrocyte Death Driven by Microglial Cholesterol Crystallization",
      variables: {
        independent: "TREM2 activation level (WT vs R47H vs Agonist mAb treated)",
        dependent: "Oligodendrocyte viability and phosphorylated MLKL (p-MLKL) necroptotic marker expression",
        control: "Tau seed concentration, baseline myelin lipid load, culture temperature"
      },
      supportingEvidence: [
        "Leyns et al. demonstrated TREM2 agonism rescues synaptic densities and stabilizes adjacent glial structures.",
        "Kirby et al. proved that microcrystalline cholesterol directly initiates oligodendrocyte membrane rupture in inflammatory demyelination models."
      ],
      counterarguments: [
        "Oligodendrocyte loss might be primarily mediated by astrocyte A1 reactive conversion rather than direct microglial contact.",
        "In vitro co-cultures do not account for cerebral spinal fluid interstitial bulk flow which may dilute extracellular crystal concentrations."
      ],
      suggestedExperiment: {
        methodology: "Human iPSC-derived tri-culture (microglia, oligodendrocytes, and cortical neurons) exposed to synthetic human hyperphosphorylated tau-441 seeds under TREM2 agonist treatment vs vehicle control.",
        measurements: "Live-cell confocal imaging of BODIPY lipid droplet trafficking, flow cytometric quantification of Annexin V / p-MLKL in oligodendrocytes at 24h, 48h, and 72h post-exposure.",
        falsificationCriteria: "If TREM2 activation fails to alter p-MLKL levels in oligodendrocytes or if cholesterol crystal formation is absent under electron microscopy, the hypothesis is falsified."
      },
      criticalReview: {
        strengths: "Addresses an unexplained early MRI biomarker (white matter hyperintensities) using a falsifiable biochemical pathway with existing clinical-grade reagents.",
        weaknesses: "Requires delicate spatial resolution to distinguish direct mechanical crystal damage from indirect cytokine-mediated signaling.",
        alternativeExplanations: "Cytokine release (e.g. TNF-alpha) could be the true driver of oligodendrocyte death, with lipid crystallization being an epiphenomenon.",
        suggestedImprovements: "Incorporate selective ACAT1 inhibitors (e.g., K-604) alongside TREM2 agonists to isolate the lipid crystallization variable specifically."
      }
    },
    {
      id: "hyp-2",
      statement: "Co-administration of NAD+ precursors (Nicotinamide Riboside) rescues the late-stage metabolic exhaustion of TREM2-hyperactivated microglia, reverting the senescent LDAM phenotype into a phagocytic state.",
      gapAddressed: "Stage-Dependent Switch Mechanism in TREM2-Mediated Microglial Energetics",
      variables: {
        independent: "Extracellular NAD+ / Nicotinamide Riboside supplementation in high-TREM2 microglial cultures",
        dependent: "Oxygen consumption rate (OCR), extracellular acidification rate (ECAR), and phagocytosis index of fluorescent tau seeds",
        control: "Untreated senescent microglia, baseline glucose and pyruvate levels"
      },
      supportingEvidence: [
        "Mathys et al. noted glycolytic collapse and mitochondrial dysfunction in high-TREM2 late-stage human microglia.",
        "Marschallinger et al. confirmed that defective lipid droplet mobilization can be reversed in aged mice through metabolic rejuvenation."
      ],
      counterarguments: [
        "Late-stage epigenetic remodeling and chromatin condensation in senescent microglia may be irreversible through bioenergetic intervention alone."
      ],
      suggestedExperiment: {
        methodology: "Seahorse XF Flux analysis on human microglia chronically stimulated with TREM2 agonistic antibodies for 14 days, with and without 1mM Nicotinamide Riboside.",
        measurements: "Mitochondrial spare respiratory capacity, intracellular ATP/ADP ratio, and phagocytic uptake of pHrodo-labeled recombinant tau aggregates.",
        falsificationCriteria: "If NAD+ supplementation does not increase tau seed uptake by at least 25% or fails to reduce senescence markers (p16INK4a, senescence-associated beta-galactosidase), the hypothesis is rejected."
      },
      criticalReview: {
        strengths: "Translational readiness; Nicotinamide Riboside is an orally bioavailable, FDA-recognized compound already evaluated in human phase 1 trials.",
        weaknesses: "Blood-brain barrier penetrance in human patients may necessitate high dosing regimens.",
        alternativeExplanations: "Microglial exhaustion could be secondary to chronic glutamate excitotoxicity from adjacent dying neurons.",
        suggestedImprovements: "Validate target engagement using in vivo mouse microdialysis of cortical interstitial fluid NAD+ levels."
      }
    }
  ],
  experiments: null // Backend experiment execution not yet connected
};

