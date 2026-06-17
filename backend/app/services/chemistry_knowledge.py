CHEMISTRY_DATASET_CATEGORIES = [
    {
        "id": "computational",
        "name": "Computational chemistry and materials",
        "use_when": "DFT, molecular dynamics, quantum chemistry, materials screening, catalysis, MOFs, polymers, solvation, reaction energetics.",
        "datasets": [
            {"name": "Materials Project", "domain": "inorganic crystals", "fit": "structure-property prediction, stability screening, phase diagrams"},
            {"name": "QM9", "domain": "small organic molecules", "fit": "molecular property prediction baselines"},
            {"name": "Open Catalyst 2020", "domain": "catalysis surfaces", "fit": "adsorption energy and catalyst discovery"},
            {"name": "OMol25", "domain": "molecular chemistry", "fit": "large-scale molecular foundation model training"},
            {"name": "QMOF / CoRE MOF", "domain": "metal-organic frameworks", "fit": "gas adsorption, porous-material screening"},
            {"name": "DFT Solvation Energy Dataset", "domain": "solvation", "fit": "solubility, solvent effects, electrolyte design"},
        ],
    },
    {
        "id": "experimental",
        "name": "Experimental chemistry",
        "use_when": "Lab-measured bioactivity, solubility, toxicity, binding, crystal structures, polymers, thin-film libraries.",
        "datasets": [
            {"name": "ChEMBL", "domain": "bioactive molecules", "fit": "QSAR, target activity, drug-like prediction"},
            {"name": "MoleculeNet", "domain": "molecular properties", "fit": "standard molecular ML benchmarks"},
            {"name": "BigSolDB", "domain": "organic molecule solubility", "fit": "aqueous and solvent solubility prediction"},
            {"name": "BindingDB / PDBbind", "domain": "protein-ligand binding", "fit": "affinity prediction and virtual screening"},
            {"name": "Tox21 / ToxCast", "domain": "toxicity", "fit": "toxicology classification"},
            {"name": "Polymer Genome", "domain": "polymers", "fit": "polymer property prediction"},
        ],
    },
    {
        "id": "literature",
        "name": "Literature-mined and text",
        "use_when": "Thesis depends on papers, patents, reactions, text-mined synthesis conditions, or chemical entity extraction.",
        "datasets": [
            {"name": "PubChem", "domain": "molecules and annotations", "fit": "compound enrichment and metadata joins"},
            {"name": "Open Reaction Database", "domain": "synthetic reactions", "fit": "reaction condition prediction and yield modelling"},
            {"name": "MatScholar", "domain": "materials NLP", "fit": "literature mining and entity-relation extraction"},
            {"name": "USPTO-Lowe", "domain": "patent reactions", "fit": "reaction prediction and retrosynthesis baselines"},
            {"name": "L2M3", "domain": "MOF literature mining", "fit": "MOF extraction from publications"},
        ],
    },
    {
        "id": "llm_training",
        "name": "Chemistry LLM and instruction data",
        "use_when": "The thesis can become an assistant, tutoring workflow, scientific QA system, extraction agent, or chemistry reasoning benchmark.",
        "datasets": [
            {"name": "ChemPile", "domain": "chemistry text", "fit": "domain language model grounding"},
            {"name": "ChemQA / ChemBench", "domain": "chemistry QA", "fit": "scientific QA evaluation"},
            {"name": "SmolInstruct", "domain": "small molecules", "fit": "molecule instruction-following"},
            {"name": "SciCode", "domain": "research coding", "fit": "thesis-to-code task generation"},
            {"name": "MatSci-Instruct", "domain": "materials science", "fit": "materials assistant instruction tuning"},
        ],
    },
]


ALGORITHM_FAMILIES = [
    {
        "name": "QSAR and molecular property prediction",
        "methods": ["random forest", "gradient boosting", "graph neural networks", "molecular fingerprints", "transformers"],
        "inputs": ["SMILES", "molecular descriptors", "assay labels", "solubility/toxicity/activity values"],
    },
    {
        "name": "Materials property prediction",
        "methods": ["crystal graph neural networks", "kernel ridge regression", "XGBoost", "message passing neural networks"],
        "inputs": ["CIF structures", "composition vectors", "DFT labels", "experimental properties"],
    },
    {
        "name": "Reaction optimization and retrosynthesis",
        "methods": ["sequence-to-sequence models", "template mining", "Bayesian optimization", "yield prediction"],
        "inputs": ["reactants", "products", "conditions", "yields", "solvents", "catalysts"],
    },
    {
        "name": "Spectroscopy and analytical chemistry ML",
        "methods": ["PLS regression", "CNNs", "autoencoders", "classification models", "calibration transfer"],
        "inputs": ["UV/Vis", "IR", "NMR", "MS", "Raman", "chromatography traces"],
    },
    {
        "name": "Literature RAG and scientific extraction",
        "methods": ["RAG", "entity-relation extraction", "schema extraction", "citation-grounded summarization"],
        "inputs": ["thesis text", "papers", "patents", "tables", "figures", "protocols"],
    },
]


def chemistry_context_text() -> str:
    sections = []
    for category in CHEMISTRY_DATASET_CATEGORIES:
        datasets = "; ".join(
            f"{item['name']} ({item['domain']}: {item['fit']})" for item in category["datasets"]
        )
        sections.append(f"{category['name']}: {category['use_when']} Datasets: {datasets}.")
    algorithms = "; ".join(
        f"{family['name']} using {', '.join(family['methods'])} from {', '.join(family['inputs'])}"
        for family in ALGORITHM_FAMILIES
    )
    return "\n".join(sections) + "\nAlgorithm families: " + algorithms
