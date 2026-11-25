import logging
import textwrap
from html import escape

import requests
import streamlit as st

from api.endpoints import BASE_URL

logger = logging.getLogger(__name__)

CHAPTERS = {
    "JEE Main": {
        "Physics": {
            "Units and Measurements": [
                "Physical quantities and SI units",
                "Dimensions and dimensional analysis",
                "Significant figures and errors",
                "Accuracy, precision and measurement",
            ],
            "Kinematics": [
                "Position, distance and displacement",
                "Speed and velocity",
                "Acceleration and equations of motion",
                "Motion in a straight line",
                "Projectile motion",
                "Relative velocity",
            ],
            "Laws of Motion": [
                "Newton's First Law of Motion",
                "Newton's Second Law of Motion",
                "Newton's Third Law of Motion",
                "Inertia and its Types",
                "Momentum and Impulse",
                "Free Body Diagrams",
                "Friction",
                "Equilibrium of Forces",
                "Circular Motion and Force",
            ],
            "Work, Energy and Power": [
                "Work done by a constant force",
                "Work done by a variable force",
                "Kinetic and potential energy",
                "Work-energy theorem",
                "Conservation of mechanical energy",
                "Power and efficiency",
                "Collisions",
            ],
            "Rotational Motion": [
                "Centre of mass",
                "Torque and angular momentum",
                "Moment of inertia",
                "Radius of gyration",
                "Rotational kinetic energy",
                "Rolling motion",
                "Conservation of angular momentum",
            ],
            "Gravitation": [
                "Newton's law of gravitation",
                "Acceleration due to gravity",
                "Variation of gravity with height and depth",
                "Gravitational potential and potential energy",
                "Escape velocity",
                "Orbital velocity and satellites",
                "Kepler's laws",
            ],
            "Properties of Solids and Liquids": [
                "Elasticity and stress-strain",
                "Pressure in fluids",
                "Pascal's law",
                "Viscosity and Stokes' law",
                "Surface tension and capillarity",
                "Bernoulli's principle",
                "Thermal expansion and calorimetry",
            ],
            "Thermodynamics": [
                "Thermal equilibrium and zeroth law",
                "Heat, work and internal energy",
                "First law of thermodynamics",
                "Isothermal and adiabatic processes",
                "Specific heat capacities",
                "Second law of thermodynamics",
                "Heat engines and refrigerators",
            ],
            "Kinetic Theory of Gases": [
                "Ideal gas equation",
                "Kinetic interpretation of temperature",
                "Pressure of an ideal gas",
                "Degrees of freedom",
                "Law of equipartition of energy",
                "Mean free path and molecular speeds",
            ],
            "Oscillations and Waves": [
                "Periodic and oscillatory motion",
                "Simple harmonic motion",
                "Energy in SHM",
                "Simple pendulum",
                "Wave motion and wave equation",
                "Superposition of waves",
                "Sound waves and beats",
                "Standing waves and resonance",
            ],
            "Electrostatics": [
                "Electric charge and Coulomb's law",
                "Electric field and field lines",
                "Electric dipole",
                "Electric flux and Gauss's law",
                "Electric potential and potential energy",
                "Capacitance and capacitors",
                "Combination of capacitors",
                "Energy stored in a capacitor",
            ],
            "Current Electricity": [
                "Electric current and drift velocity",
                "Ohm's law and resistance",
                "Resistivity and conductivity",
                "Series and parallel circuits",
                "Kirchhoff's laws",
                "Wheatstone bridge and meter bridge",
                "Potentiometer",
                "Electrical power and heating effect",
            ],
            "Magnetic Effects of Current and Magnetism": [
                "Magnetic field and magnetic force",
                "Biot-Savart law",
                "Ampere's circuital law",
                "Force on a current-carrying conductor",
                "Motion of a charged particle in a magnetic field",
                "Torque on a current loop",
                "Moving coil galvanometer",
                "Bar magnets and magnetic materials",
            ],
            "Electromagnetic Induction and AC": [
                "Magnetic flux",
                "Faraday's laws of induction",
                "Lenz's law",
                "Self and mutual inductance",
                "Alternating current",
                "AC circuits and reactance",
                "LCR circuits and resonance",
                "Transformer",
            ],
            "Optics": [
                "Reflection and spherical mirrors",
                "Refraction and total internal reflection",
                "Lenses and lens formula",
                "Optical instruments",
                "Prism and dispersion",
                "Huygens' principle",
                "Interference and Young's double-slit experiment",
                "Diffraction and polarization",
            ],
            "Modern Physics": [
                "Photoelectric effect",
                "Wave-particle duality",
                "Bohr model of the atom",
                "Atomic spectra",
                "Radioactivity and nuclear decay",
                "Mass defect and binding energy",
                "Nuclear fission and fusion",
            ],
            "Electronic Devices": [
                "Semiconductors and energy bands",
                "Intrinsic and extrinsic semiconductors",
                "p-n junction diode",
                "Diode as a rectifier",
                "Zener diode",
                "Logic gates",
            ],
        },
        "Chemistry": {
            "Some Basic Concepts of Chemistry": [
                "Nature of matter and laws of chemical combination",
                "Atomic and molecular masses",
                "Mole concept and Avogadro constant",
                "Percentage composition",
                "Empirical and molecular formula",
                "Stoichiometry and limiting reagent",
            ],
            "Atomic Structure": [
                "Subatomic particles",
                "Rutherford and Bohr atomic models",
                "Electromagnetic radiation",
                "Quantum numbers",
                "Atomic orbitals and shapes",
                "Aufbau principle, Pauli principle and Hund's rule",
                "Electronic configuration",
            ],
            "Classification of Elements and Periodicity": [
                "Modern periodic law",
                "Periodic table structure",
                "Atomic and ionic radii",
                "Ionisation enthalpy",
                "Electron gain enthalpy",
                "Electronegativity",
                "Periodic trends",
            ],
            "Chemical Bonding and Molecular Structure": [
                "Ionic and covalent bonds",
                "Lewis structures and formal charge",
                "VSEPR theory and molecular shapes",
                "Valence bond theory",
                "Hybridisation",
                "Molecular orbital theory",
                "Bond order and magnetic behaviour",
                "Hydrogen bonding",
            ],
            "Chemical Thermodynamics": [
                "System, surroundings and state functions",
                "First law of thermodynamics",
                "Enthalpy and heat capacity",
                "Hess's law",
                "Entropy",
                "Gibbs energy and spontaneity",
            ],
            "Solutions": [
                "Types of solutions and concentration terms",
                "Solubility",
                "Raoult's law",
                "Ideal and non-ideal solutions",
                "Colligative properties",
                "Abnormal molar mass and van't Hoff factor",
            ],
            "Equilibrium": [
                "Dynamic equilibrium",
                "Law of mass action and equilibrium constant",
                "Le Chatelier's principle",
                "Ionic equilibrium",
                "Acids, bases and pH",
                "Buffer solutions",
                "Solubility product",
                "Common ion effect",
            ],
            "Redox Reactions and Electrochemistry": [
                "Oxidation number",
                "Balancing redox reactions",
                "Electrochemical cells",
                "Electrode potential",
                "Nernst equation",
                "Conductance and conductivity",
                "Electrolysis and Faraday's laws",
                "Batteries and fuel cells",
            ],
            "Chemical Kinetics": [
                "Rate of reaction",
                "Rate law and rate constant",
                "Order and molecularity",
                "Integrated rate equations",
                "Half-life",
                "Temperature dependence and Arrhenius equation",
                "Activation energy",
            ],
            "Periodic and p-Block Elements": [
                "General trends in p-block elements",
                "Group 13 elements",
                "Group 14 elements",
                "Group 15 elements",
                "Group 16 elements",
                "Group 17 elements",
                "Group 18 elements",
                "Important compounds and their properties",
            ],
            "d- and f-Block Elements": [
                "Electronic configuration of transition elements",
                "Oxidation states and colour",
                "Magnetic properties",
                "Catalytic properties",
                "Lanthanoids and lanthanoid contraction",
                "Actinoids",
            ],
            "Coordination Compounds": [
                "Werner's theory",
                "Ligands and coordination number",
                "Nomenclature of coordination compounds",
                "Isomerism",
                "Valence bond theory",
                "Crystal field theory",
                "Applications of coordination compounds",
            ],
            "Organic Chemistry: Basic Principles": [
                "Tetravalency of carbon and shapes of molecules",
                "IUPAC nomenclature",
                "Structural and stereoisomerism",
                "Inductive and resonance effects",
                "Hyperconjugation",
                "Reaction intermediates",
                "Types of organic reactions",
                "Purification and qualitative analysis",
            ],
            "Hydrocarbons": [
                "Alkanes and their reactions",
                "Alkenes and addition reactions",
                "Alkynes and acidity",
                "Aromatic hydrocarbons",
                "Benzene structure and aromaticity",
                "Electrophilic substitution reactions",
            ],
            "Organic Compounds Containing Halogens": [
                "Nomenclature and classification",
                "Preparation of haloalkanes and haloarenes",
                "Nucleophilic substitution reactions",
                "Elimination reactions",
                "Reactivity of haloarenes",
                "Environmental effects of halogen compounds",
            ],
            "Organic Compounds Containing Oxygen": [
                "Alcohols: preparation and properties",
                "Phenols: acidity and reactions",
                "Ethers: preparation and reactions",
                "Aldehydes and ketones",
                "Nucleophilic addition reactions",
                "Carboxylic acids and derivatives",
            ],
            "Organic Compounds Containing Nitrogen": [
                "Amines: classification and nomenclature",
                "Preparation and properties of amines",
                "Basicity of amines",
                "Diazonium salts",
                "Important reactions of nitrogen compounds",
            ],
            "Biomolecules": [
                "Carbohydrates",
                "Glucose and fructose",
                "Amino acids and proteins",
                "Enzymes",
                "Vitamins",
                "Nucleic acids",
            ],
        },
        "Mathematics": {
            "Sets, Relations and Functions": [
                "Representation and types of sets",
                "Set operations and Venn diagrams",
                "Relations and their properties",
                "Types of functions",
                "Composition of functions",
                "Inverse functions",
            ],
            "Complex Numbers and Quadratic Equations": [
                "Algebra of complex numbers",
                "Argand plane and modulus",
                "Polar representation",
                "Properties of quadratic equations",
                "Nature of roots",
                "Roots and coefficients",
            ],
            "Matrices and Determinants": [
                "Types and operations of matrices",
                "Transpose and symmetric matrices",
                "Determinants and their properties",
                "Minors and cofactors",
                "Adjoint and inverse of a matrix",
                "Solving linear equations",
            ],
            "Permutations and Combinations": [
                "Fundamental principle of counting",
                "Factorials",
                "Permutations",
                "Combinations",
                "Arrangements with restrictions",
                "Applications of counting",
            ],
            "Binomial Theorem": [
                "Binomial theorem for positive integer index",
                "General term",
                "Middle term",
                "Binomial coefficients",
                "Applications of binomial expansion",
            ],
            "Sequences and Series": [
                "Sequences and general terms",
                "Arithmetic progression",
                "Geometric progression",
                "Arithmetic and geometric means",
                "Sum of special series",
                "Arithmetico-geometric series",
            ],
            "Limits, Continuity and Differentiability": [
                "Limits and standard limits",
                "Algebra of limits",
                "Continuity of functions",
                "Differentiability",
                "Chain rule",
                "Implicit and logarithmic differentiation",
                "Derivatives of inverse trigonometric functions",
            ],
            "Integral Calculus": [
                "Indefinite integration",
                "Integration by substitution",
                "Integration by parts",
                "Partial fractions",
                "Definite integrals",
                "Properties of definite integrals",
                "Area under curves",
            ],
            "Differential Equations": [
                "Order and degree",
                "Formation of differential equations",
                "Variable separable method",
                "Homogeneous differential equations",
                "Linear differential equations",
                "Applications of differential equations",
            ],
            "Coordinate Geometry: Straight Lines": [
                "Cartesian coordinates and distance formula",
                "Section formula",
                "Slope of a line",
                "Different forms of a straight line",
                "Angle between two lines",
                "Distance of a point from a line",
            ],
            "Circles": [
                "Standard equation of a circle",
                "General equation of a circle",
                "Centre and radius",
                "Equation of tangent",
                "Length of tangent",
                "Common chord and radical axis",
            ],
            "Conic Sections": [
                "Parabola and its standard forms",
                "Focus, directrix and latus rectum",
                "Ellipse and its properties",
                "Hyperbola and its properties",
                "Tangents and normals to conics",
            ],
            "Three-Dimensional Geometry": [
                "Coordinates in three dimensions",
                "Distance and section formula",
                "Direction ratios and direction cosines",
                "Equation of a line in space",
                "Angle between two lines",
                "Shortest distance between skew lines",
            ],
            "Vector Algebra": [
                "Scalars and vectors",
                "Types of vectors",
                "Addition and scalar multiplication",
                "Dot product",
                "Cross product",
                "Applications of vector products",
            ],
            "Statistics and Probability": [
                "Mean, median and mode",
                "Variance and standard deviation",
                "Random experiments and events",
                "Addition and multiplication theorems",
                "Conditional probability",
                "Bayes' theorem",
                "Probability distributions",
            ],
            "Trigonometry": [
                "Trigonometric ratios and identities",
                "Trigonometric equations",
                "Inverse trigonometric functions",
                "Properties of triangles",
                "Sine rule and cosine rule",
                "Heights and distances",
            ],
            "Differential Calculus: Applications": [
                "Rate of change",
                "Increasing and decreasing functions",
                "Tangents and normals",
                "Maxima and minima",
                "Approximation using derivatives",
            ],
        },
    },

    "NEET UG": {
        "Physics": {
            "Physics and Measurement": ["Units, dimensions and dimensional analysis", "Errors in measurement and significant figures", "Experimental skills and measurement instruments"],
            "Kinematics": ["Motion in a straight line", "Position, displacement, speed and velocity", "Uniform and non-uniform acceleration", "Motion graphs and equations of motion", "Projectile motion and relative velocity"],
            "Laws of Motion": ["Newton's laws of motion", "Inertia and momentum", "Impulse and conservation of momentum", "Free body diagrams and equilibrium", "Friction and circular motion"],
            "Work, Energy and Power": ["Work done by constant and variable forces", "Kinetic and potential energy", "Work-energy theorem", "Conservation of mechanical energy", "Power and collisions"],
            "Rotational Motion": ["Centre of mass", "Torque and angular momentum", "Moment of inertia and radius of gyration", "Rotational kinetic energy", "Rolling motion and conservation of angular momentum"],
            "Gravitation": ["Newton's law of gravitation", "Acceleration due to gravity", "Gravitational potential and potential energy", "Escape velocity and orbital velocity", "Satellites and Kepler's laws"],
            "Properties of Solids and Liquids": ["Elasticity and stress-strain", "Pressure, Pascal's law and buoyancy", "Viscosity and fluid flow", "Surface tension and capillarity", "Thermal expansion and calorimetry"],
            "Thermodynamics": ["Thermal equilibrium and zeroth law", "Heat, work and internal energy", "First law of thermodynamics", "Isothermal and adiabatic processes", "Specific heat and second law"],
            "Kinetic Theory of Gases": ["Ideal gas equation", "Kinetic interpretation of temperature", "Pressure and molecular speeds", "Degrees of freedom", "Law of equipartition of energy"],
            "Oscillations and Waves": ["Periodic motion and simple harmonic motion", "Energy in simple harmonic motion", "Simple pendulum", "Wave motion and wave equation", "Superposition, standing waves and sound"],
            "Electrostatics": ["Electric charge and Coulomb's law", "Electric field and electric dipole", "Electric flux and Gauss's law", "Electric potential and potential energy", "Capacitance and capacitors"],
            "Current Electricity": ["Electric current and drift velocity", "Ohm's law, resistance and resistivity", "Series and parallel circuits", "Kirchhoff's laws", "Wheatstone bridge and electrical power"],
            "Magnetic Effects of Current and Magnetism": ["Magnetic field and Lorentz force", "Biot-Savart law and Ampere's law", "Force on current-carrying conductors", "Torque on a current loop", "Moving coil galvanometer and magnetic materials"],
            "Electromagnetic Induction and Alternating Current": ["Magnetic flux and Faraday's laws", "Lenz's law", "Self and mutual inductance", "Alternating current and AC circuits", "LCR circuits, resonance and transformers"],
            "Electromagnetic Waves": ["Displacement current", "Properties of electromagnetic waves", "Electromagnetic spectrum and applications"],
            "Optics": ["Reflection and refraction", "Spherical mirrors and lenses", "Total internal reflection and optical instruments", "Prism and dispersion", "Wave optics, interference and diffraction"],
            "Dual Nature of Matter and Radiation": ["Photoelectric effect", "Einstein's photoelectric equation", "Matter waves and de Broglie wavelength"],
            "Atoms and Nuclei": ["Rutherford and Bohr atomic models", "Hydrogen spectrum", "Nuclear composition and size", "Radioactivity and nuclear decay", "Mass defect, binding energy, fission and fusion"],
            "Electronic Devices": ["Semiconductors and energy bands", "Intrinsic and extrinsic semiconductors", "p-n junction diode", "Diode as a rectifier"],
        },
        "Chemistry": {
            "Some Basic Concepts in Chemistry": ["Nature of matter and laws of chemical combination", "Atomic and molecular masses", "Mole concept and Avogadro constant", "Empirical and molecular formula", "Stoichiometry and limiting reagent"],
            "Atomic Structure": ["Subatomic particles and atomic models", "Electromagnetic radiation", "Bohr model and hydrogen spectrum", "Quantum numbers and atomic orbitals", "Aufbau principle, Pauli principle and Hund's rule", "Electronic configuration"],
            "Chemical Bonding and Molecular Structure": ["Ionic and covalent bonding", "Lewis structures and formal charge", "VSEPR theory and molecular shapes", "Valence bond theory and hybridisation", "Molecular orbital theory and bond order", "Hydrogen bonding"],
            "Chemical Thermodynamics": ["System, surroundings and state functions", "First law and enthalpy", "Heat capacity and Hess's law", "Entropy and spontaneity", "Gibbs energy"],
            "Solutions": ["Types of solutions and concentration terms", "Solubility and vapour pressure", "Raoult's law", "Ideal and non-ideal solutions", "Colligative properties and van't Hoff factor"],
            "Equilibrium": ["Dynamic equilibrium and equilibrium constant", "Le Chatelier's principle", "Ionic equilibrium", "Acids, bases and pH", "Buffer solutions and solubility product"],
            "Redox Reactions and Electrochemistry": ["Oxidation and reduction", "Oxidation number and balancing redox reactions", "Electrochemical cells", "Electrode potential and Nernst equation", "Conductance and electrolysis"],
            "Chemical Kinetics": ["Rate of reaction", "Factors affecting reaction rates", "Rate law and order of reaction", "Integrated rate equations", "Arrhenius equation and activation energy"],
            "Classification of Elements and Periodicity": ["Modern periodic law and periodic table", "Atomic and ionic radii", "Ionisation enthalpy", "Electron gain enthalpy", "Electronegativity and periodic trends"],
            "p-Block Elements": ["General trends in p-block elements", "Group 13 and Group 14 elements", "Group 15 and Group 16 elements", "Group 17 and Group 18 elements", "Important compounds and properties"],
            "d- and f-Block Elements": ["Transition elements and their properties", "Electronic configuration and oxidation states", "Colour and magnetic properties", "Lanthanoids and actinoids", "Important compounds of transition elements"],
            "Coordination Compounds": ["Werner's theory and coordination entities", "Ligands and coordination number", "IUPAC nomenclature", "Isomerism in coordination compounds", "Bonding, colour and magnetic properties"],
            "Organic Chemistry: Basic Principles and Techniques": ["Tetravalency of carbon and structural representation", "Nomenclature and isomerism", "Electronic effects in organic molecules", "Reaction intermediates and mechanisms", "Purification and qualitative analysis"],
            "Hydrocarbons": ["Classification and nomenclature", "Alkanes and their reactions", "Alkenes and addition reactions", "Alkynes and acidic character", "Aromatic hydrocarbons and electrophilic substitution"],
            "Organic Compounds Containing Halogens": ["Nomenclature and nature of C-X bond", "Preparation and properties of haloalkanes", "Nucleophilic substitution reactions", "Haloarenes and their reactions", "Uses and environmental effects"],
            "Organic Compounds Containing Oxygen": ["Alcohols: preparation and properties", "Phenols and their reactions", "Ethers and cleavage", "Aldehydes and ketones", "Carboxylic acids and their reactions"],
            "Organic Compounds Containing Nitrogen": ["Classification and nomenclature of amines", "Preparation and properties of amines", "Basicity of amines", "Diazonium salts and their reactions"],
            "Biomolecules": ["Carbohydrates and their classification", "Proteins and amino acids", "Enzymes and vitamins", "Nucleic acids: DNA and RNA"],
            "Principles Related to Practical Chemistry": ["Detection of functional groups", "Qualitative analysis of inorganic salts", "Basic laboratory techniques", "Preparation of standard solutions and titration concepts"],
        },
        "Biology": {
            "Diversity in the Living World": ["What is living and biodiversity", "Taxonomy and systematics", "Taxonomic categories and aids", "The five-kingdom classification", "Salient features of major plant groups", "Salient features of major animal groups"],
            "Structural Organisation in Plants and Animals": ["Morphology of flowering plants", "Root, stem and leaf modifications", "Inflorescence, flower, fruit and seed", "Anatomy of flowering plants", "Tissues and tissue systems", "Animal tissues and structural organisation"],
            "Cell Structure and Function": ["Cell theory and cell types", "Prokaryotic and eukaryotic cells", "Cell membrane and cell wall", "Cell organelles and their functions", "Biomolecules and enzymes", "Cell cycle and cell division"],
            "Plant Physiology": ["Transport in plants", "Mineral nutrition", "Photosynthesis in higher plants", "Respiration in plants", "Plant growth and development"],
            "Human Physiology": ["Breathing and exchange of gases", "Body fluids and circulation", "Excretory products and their elimination", "Locomotion and movement", "Neural control and coordination", "Chemical coordination and integration"],
            "Reproduction": ["Reproduction in organisms", "Sexual reproduction in flowering plants", "Human reproductive system", "Gametogenesis and menstrual cycle", "Fertilisation and embryonic development", "Reproductive health and contraception"],
            "Genetics and Evolution": ["Mendelian inheritance and genetic principles", "Inheritance patterns and chromosomal theory", "Molecular basis of inheritance", "DNA replication, transcription and translation", "Gene expression and regulation", "Evolution and evidences of evolution"],
            "Biology and Human Welfare": ["Human health and disease", "Pathogens and common infectious diseases", "Immunity and vaccines", "Cancer and HIV/AIDS", "Microbes in human welfare"],
            "Biotechnology and Its Applications": ["Principles and processes of biotechnology", "Recombinant DNA technology", "Applications in medicine and agriculture", "Genetically modified organisms", "Ethical issues in biotechnology"],
            "Ecology and Environment": ["Organisms and populations", "Population interactions and attributes", "Ecosystem structure and function", "Energy flow and ecological pyramids", "Biodiversity and conservation", "Environmental issues"],
        },
    },
}

LANGUAGES = [
    "English", "Hindi", "Bengali", "Assamese", "Gujarati",
    "Kannada", "Malayalam", "Marathi", "Nepali", "Odia",
    "Punjabi", "Sanskrit", "Tamil", "Telugu", "Urdu",
    "Santali", "Manipuri", "Bodo", "Kashmiri", "Sindhi",
]


# Curated video catalogue. Add entries only after checking the video title,
# channel, relevance and embeddability. YouTube IDs are used for direct embeds.
CURATED_VIDEOS = {
    ("JEE Main", "Physics", "Laws of Motion"): [
        {
            "title": "Newton's Laws of Motion - SATHEE IIT Kanpur",
            "channel": "SATHEE · IIT Kanpur",
            "video_id": "dJgLRfq9YEI",
            "description": "Topic-focused lecture covering Newton's laws of motion.",
        },
        {
            "title": "Laws of Motion - Complete chapter and JEE practice",
            "channel": "JEE Wallah",
            "video_id": "mE8w2uxm6XY",
            "description": "Full chapter revision with concepts and JEE-level practice.",
        },
    ],
}


def render_html(markup):
    """Render HTML without accidental Markdown code-block formatting."""
    st.markdown(textwrap.dedent(markup).strip(), unsafe_allow_html=True)


def inject_chapter_learning_styles():
    """Apply a spacious, consistent visual system only inside Chapter Learning."""
    st.markdown(
        """
<style>
:root{color-scheme:light}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"],[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{background:#f4faf6!important}
[data-testid="stAppViewContainer"]{background-image:radial-gradient(ellipse at 8% 0%,rgba(187,232,202,.24),transparent 34%),radial-gradient(ellipse at 96% 8%,rgba(211,239,220,.22),transparent 30%)!important}
[data-testid="stMainBlockContainer"]{max-width:1240px;padding:2rem 2.2rem 4rem!important}
.st-key-chapter_learning_root{max-width:1120px;margin:0 auto}
.st-key-chapter_learning_root .hero{position:relative;overflow:hidden;padding:38px 42px;margin:0 0 34px;border:1px solid #cce5d3;border-radius:24px;background:radial-gradient(circle at 88% 18%,rgba(115,207,146,.17),transparent 30%),linear-gradient(135deg,#e9f7ee 0%,#fff 82%);box-shadow:0 12px 34px rgba(25,75,45,.055);animation:clRise .65s ease-out both}
.st-key-chapter_learning_root .hero:after{content:"";position:absolute;width:190px;height:190px;right:-65px;top:-80px;border-radius:50%;background:rgba(112,208,143,.10);filter:blur(8px);pointer-events:none}
.st-key-chapter_learning_root .hero h1{color:#173b28!important;font-size:clamp(30px,3.4vw,43px);font-weight:800;line-height:1.2;margin:18px 0}
.st-key-chapter_learning_root .hero p{color:#52665a!important;font-size:15px;line-height:1.8;max-width:780px;margin-bottom:18px}
.st-key-chapter_learning_root .eyebrow{color:#267548!important;font-size:11px;font-weight:850;letter-spacing:2px}
.st-key-chapter_learning_root .hero-tag{display:inline-block;padding:8px 13px;margin:7px 7px 0 0;border:1px solid #d5e8da;border-radius:30px;color:#267548!important;background:rgba(255,255,255,.9);font-size:12px;font-weight:700}
.st-key-chapter_learning_root .section-heading{color:#173b28!important;font-size:23px;font-weight:800;margin:30px 0 6px}
.st-key-chapter_learning_root .section-caption{color:#607568!important;font-size:13px;margin-bottom:20px;line-height:1.65}
.st-key-chapter_learning_root .info-card{padding:20px;min-height:116px;border:1px solid #d5e8da;border-radius:17px;background:linear-gradient(135deg,#eaf7ee,#fff 90%);box-shadow:0 5px 18px rgba(28,82,47,.04);transition:transform .2s ease,box-shadow .2s ease}
.st-key-chapter_learning_root .info-card:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(28,82,47,.07)}
.st-key-chapter_learning_root .info-icon{font-size:25px}
.st-key-chapter_learning_root .info-label{color:#567361!important;font-size:10px;font-weight:800;margin-top:10px;letter-spacing:.07em}
.st-key-chapter_learning_root .info-value{color:#173b28!important;font-size:16px;font-weight:800;margin-top:6px;line-height:1.4}
.st-key-chapter_learning_root div[data-testid="stWidgetLabel"],.st-key-chapter_learning_root div[data-testid="stWidgetLabel"] p,.st-key-chapter_learning_root div[data-testid="stSelectbox"] label,.st-key-chapter_learning_root div[data-testid="stSelectbox"] label p{color:#284b36!important;opacity:1!important;font-weight:700!important}
.st-key-chapter_learning_root div[data-baseweb="select"]>div{background:#fff!important;border:1px solid #d8e5dc!important;border-radius:11px!important;min-height:44px}
.st-key-chapter_learning_root div[data-baseweb="select"] *{color:#284b36!important}
.st-key-chapter_learning_root div[data-baseweb="select"]:hover>div{border-color:#68b987!important}
.st-key-chapter_learning_root div[data-testid="stButton"] button,.st-key-chapter_learning_root div[data-testid="stLinkButton"] a{border-radius:11px!important;min-height:46px;font-weight:750!important;transition:all .2s ease}
.st-key-chapter_learning_root div[data-testid="stButton"] button{background:linear-gradient(110deg,#166534,#23834c)!important;color:#fff!important;border:1px solid #23834c!important}
.st-key-chapter_learning_root div[data-testid="stButton"] button *{color:#fff!important}
.st-key-chapter_learning_root div[data-testid="stButton"] button:hover,.st-key-chapter_learning_root div[data-testid="stLinkButton"] a:hover{transform:translateY(-2px);box-shadow:0 7px 20px rgba(22,101,52,.14)}
.st-key-chapter_learning_root .video-panel,.st-key-chapter_learning_root .lesson-panel{background:linear-gradient(135deg,#eaf7ee,#fff 88%);border:1px solid #d2e7d8;border-radius:18px;padding:24px;margin:16px 0 22px}
.st-key-chapter_learning_root .video-panel h3{color:#173b28!important;font-size:23px;margin:0 0 10px}
.st-key-chapter_learning_root .lesson-kicker{color:#267548!important;font-size:11px;font-weight:800;letter-spacing:2px}
.st-key-chapter_learning_root .lesson-panel h2{color:#173b28!important}
.st-key-chapter_learning_root [data-testid="stMarkdownContainer"]{color:#263f30}
.st-key-chapter_learning_root [data-testid="stMarkdownContainer"] h1,.st-key-chapter_learning_root [data-testid="stMarkdownContainer"] h2,.st-key-chapter_learning_root [data-testid="stMarkdownContainer"] h3{color:#173b28!important}
.st-key-chapter_learning_root [data-testid="stMarkdownContainer"] p,.st-key-chapter_learning_root [data-testid="stMarkdownContainer"] li{color:#405b49;line-height:1.75}
.st-key-chapter_learning_root div[data-testid="stAlert"]{
    border-radius:14px!important;margin:16px 0!important;
    background:linear-gradient(110deg,#e9f8ee,#f7fcf8)!important;
    border:1px solid #cfe8d7!important;color:#315b40!important;
    box-shadow:0 5px 18px rgba(25,90,48,.045)!important;
}
.st-key-chapter_learning_root div[data-testid="stAlert"] *,
.st-key-chapter_learning_root div[data-testid="stAlert"] p{
    color:#315b40!important;opacity:1!important;
}
.st-key-chapter_learning_root div[data-testid="stAlert"] svg{fill:#26834b!important;color:#26834b!important}
.st-key-chapter_learning_root [data-testid="stTabs"] [role="tablist"]{
    gap:9px!important;border-bottom:1px solid #d9e9de!important;
    padding:8px 4px 12px!important;flex-wrap:wrap!important;
}
.st-key-chapter_learning_root [data-testid="stTabs"] button[role="tab"]{
    border:1px solid #d8e9dd!important;border-radius:12px!important;
    background:#fff!important;padding:11px 16px!important;
    transition:all .22s ease!important;margin:0 2px!important;
}
.st-key-chapter_learning_root [data-testid="stTabs"] button[role="tab"]:hover{
    background:#effaf2!important;transform:translateY(-2px)!important;
    border-color:#83c99a!important;
}
.st-key-chapter_learning_root [data-testid="stTabs"] button[aria-selected="true"]{
    background:linear-gradient(110deg,#e3f8e9,#f7fff9)!important;
    color:#176438!important;border:1px solid #83c99a!important;
    box-shadow:0 5px 16px rgba(26,120,60,.09)!important;
}
.st-key-chapter_learning_root [data-testid="stTabs"] [data-testid="stTabContent"]{
    padding-top:24px!important;
    animation:clRise .42s ease both;
}
.st-key-chapter_learning_root .hero,
.st-key-chapter_learning_root .video-panel,
.st-key-chapter_learning_root .info-card{
    will-change:transform;
}
.st-key-chapter_learning_root .video-panel{
    position:relative;overflow:hidden;
    background:
      radial-gradient(circle at 94% 4%,rgba(108,210,142,.16),transparent 27%),
      linear-gradient(125deg,#e8f7ed,#fff 80%)!important;
    box-shadow:0 10px 28px rgba(25,75,45,.055);
    animation:clRise .55s ease both;
}
.st-key-chapter_learning_root .video-panel:after{
    content:"";position:absolute;top:-50%;left:-40%;width:26%;height:200%;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,.5),transparent);
    transform:rotate(18deg);animation:clShimmer 8s ease-in-out infinite;
    pointer-events:none;
}
.st-key-chapter_learning_root .info-card{
    animation:clRise .55s ease both;
}
.st-key-chapter_learning_root div[data-testid="stLinkButton"] a{
    background:#fff!important;color:#23583a!important;
    border:1px solid #d3e8d9!important;
}
.st-key-chapter_learning_root div[data-testid="stLinkButton"] a *{
    color:#23583a!important;
}
.st-key-chapter_learning_root div[data-testid="stLinkButton"] a:hover{
    background:#effaf2!important;border-color:#75bd8d!important;
}
.st-key-chapter_learning_root [data-testid="stTabs"]{margin-top:30px}
.st-key-chapter_learning_root [data-testid="stTabs"] button{font-weight:750!important;color:#42624d!important;padding:12px 15px!important}
.st-key-chapter_learning_root [data-testid="stTabs"] button[aria-selected="true"]{color:#176438!important;border-bottom-color:#23834c!important}
.st-key-chapter_learning_root [data-testid="stExpander"]{border:1px solid #d7e8dc!important;border-radius:12px!important;background:#fff!important;margin:12px 0}
.st-key-chapter_learning_root hr{margin:28px 0;border-color:#dcebe0}
@keyframes clRise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes clShimmer{0%,65%{left:-45%;opacity:0}72%{opacity:.65}100%{left:135%;opacity:0}}
@media(max-width:768px){[data-testid="stMainBlockContainer"]{padding:1rem .8rem 2rem!important}.st-key-chapter_learning_root .hero{padding:25px 22px;border-radius:18px}.st-key-chapter_learning_root .section-heading{font-size:20px}}

/* Chapter Learning motion accents: floating study icon, soft glow and staggered reveal */
.st-key-chapter_learning_root .hero{padding-right:230px!important}
.st-key-chapter_learning_root .cl-hero-art{
    position:absolute;right:38px;top:50%;width:150px;height:150px;
    transform:translateY(-50%);display:grid;place-items:center;
    border:1px solid rgba(65,166,100,.25);border-radius:34px;
    background:radial-gradient(circle,rgba(184,239,198,.72),rgba(232,248,237,.45) 58%,transparent 72%);
    animation:clFloat 4.8s ease-in-out infinite;
}
.st-key-chapter_learning_root .cl-hero-book{
    font-size:76px;line-height:1;filter:drop-shadow(0 10px 12px rgba(35,112,62,.18));
    animation:clBookGlow 3.2s ease-in-out infinite;
}
.st-key-chapter_learning_root .cl-orbit{
    position:absolute;width:116px;height:116px;border:1px solid rgba(54,166,94,.42);
    border-radius:50%;animation:clOrbit 12s linear infinite;
}
.st-key-chapter_learning_root .cl-orbit:before{
    content:"✦";position:absolute;top:8px;right:12px;color:#31a65d;
    font-size:16px;text-shadow:0 0 12px rgba(49,166,93,.7)
}
.st-key-chapter_learning_root .hero:before{
    content:"";position:absolute;inset:0;pointer-events:none;
    background:linear-gradient(110deg,transparent 30%,rgba(255,255,255,.48) 48%,transparent 62%);
    transform:translateX(-120%);animation:clHeroShine 9s ease-in-out infinite;
}
.st-key-chapter_learning_root .section-heading{animation:clRise .55s ease both}
.st-key-chapter_learning_root .info-card{transition:transform .24s ease,box-shadow .24s ease}
.st-key-chapter_learning_root .info-card:hover{transform:translateY(-4px);box-shadow:0 12px 26px rgba(25,90,48,.10)}
@keyframes clFloat{0%,100%{margin-top:0}50%{margin-top:-12px}}
@keyframes clBookGlow{0%,100%{filter:drop-shadow(0 7px 10px rgba(35,112,62,.12));transform:rotate(-3deg) scale(1)}50%{filter:drop-shadow(0 12px 18px rgba(38,166,85,.32));transform:rotate(3deg) scale(1.06)}}
@keyframes clOrbit{to{transform:rotate(360deg)}}
@keyframes clHeroShine{0%,72%{transform:translateX(-120%);opacity:0}78%{opacity:.8}100%{transform:translateX(120%);opacity:0}}
@media(max-width:768px){
 .st-key-chapter_learning_root .hero{padding-right:22px!important}
 .st-key-chapter_learning_root .cl-hero-art{position:relative;right:auto;top:auto;transform:none;width:100px;height:100px;margin:20px auto 0}
 .st-key-chapter_learning_root .cl-hero-book{font-size:52px}
 .st-key-chapter_learning_root .cl-orbit{width:82px;height:82px}
}


/* Premium motion layer: ambient particles, glowing borders and interactive study surfaces */
.st-key-chapter_learning_root{
    position:relative;
    isolation:isolate;
}
.st-key-chapter_learning_root:before,
.st-key-chapter_learning_root:after{
    content:"";position:absolute;z-index:-1;pointer-events:none;border-radius:50%;
    filter:blur(2px);opacity:.5;
}
.st-key-chapter_learning_root:before{
    width:260px;height:260px;top:160px;left:-150px;
    background:radial-gradient(circle,rgba(106,205,139,.18),transparent 70%);
    animation:clAmbientA 13s ease-in-out infinite alternate;
}
.st-key-chapter_learning_root:after{
    width:300px;height:300px;top:720px;right:-180px;
    background:radial-gradient(circle,rgba(132,218,157,.16),transparent 70%);
    animation:clAmbientB 16s ease-in-out infinite alternate;
}
.st-key-chapter_learning_root .hero{
    border-color:rgba(94,178,119,.48)!important;
    background:
      radial-gradient(circle at 78% 30%,rgba(103,213,139,.22),transparent 28%),
      radial-gradient(circle at 8% 100%,rgba(181,232,194,.35),transparent 38%),
      linear-gradient(125deg,#e5f7eb 0%,#fafffb 58%,#effaf2 100%)!important;
    box-shadow:0 18px 48px rgba(24,91,49,.09),inset 0 1px 0 rgba(255,255,255,.9)!important;
}
.st-key-chapter_learning_root .hero:after{
    width:230px!important;height:230px!important;right:115px!important;top:-110px!important;
    background:radial-gradient(circle,rgba(84,201,123,.18),transparent 70%)!important;
    animation:clPulseAura 5s ease-in-out infinite!important;
}
.st-key-chapter_learning_root .hero-tag{
    position:relative;overflow:hidden;
    box-shadow:0 3px 10px rgba(28,91,50,.045);
    transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease!important;
}
.st-key-chapter_learning_root .hero-tag:hover{
    transform:translateY(-4px)!important;
    border-color:#79c792!important;
    box-shadow:0 8px 18px rgba(28,125,62,.12)!important;
}
.st-key-chapter_learning_root .cl-hero-art{
    border:1px solid rgba(67,175,103,.35)!important;
    box-shadow:0 0 0 10px rgba(97,196,126,.045),0 16px 35px rgba(38,120,65,.10);
    background:
      radial-gradient(circle at 50% 45%,rgba(255,255,255,.96),rgba(203,244,214,.72) 48%,rgba(226,249,233,.12) 76%)!important;
}
.st-key-chapter_learning_root .cl-hero-art:before,
.st-key-chapter_learning_root .cl-hero-art:after{
    content:"✦";position:absolute;color:#42b96d;font-size:16px;
    text-shadow:0 0 12px rgba(66,185,109,.8);
}
.st-key-chapter_learning_root .cl-hero-art:before{
    left:3px;top:20px;animation:clSparkle 2.8s ease-in-out infinite;
}
.st-key-chapter_learning_root .cl-hero-art:after{
    right:5px;bottom:18px;font-size:12px;animation:clSparkle 3.4s .6s ease-in-out infinite;
}
.st-key-chapter_learning_root .section-heading{
    position:relative;padding-left:14px!important;
}
.st-key-chapter_learning_root .section-heading:before{
    content:"";position:absolute;left:0;top:3px;bottom:3px;width:4px;
    border-radius:5px;background:linear-gradient(180deg,#38b96a,#a6dfb5);
    box-shadow:0 0 12px rgba(56,185,106,.22);
}
.st-key-chapter_learning_root .info-card{
    position:relative;overflow:hidden;
    background:linear-gradient(145deg,rgba(232,248,237,.96),rgba(255,255,255,.98) 72%)!important;
    border-color:#cfe6d5!important;
    box-shadow:0 8px 24px rgba(26,83,47,.055)!important;
}
.st-key-chapter_learning_root .info-card:after{
    content:"";position:absolute;right:-35px;bottom:-55px;width:120px;height:120px;
    border-radius:50%;background:radial-gradient(circle,rgba(113,208,143,.15),transparent 70%);
    transition:transform .35s ease;
}
.st-key-chapter_learning_root .info-card:hover:after{transform:scale(1.8)}
.st-key-chapter_learning_root div[data-testid="stButton"] button,
.st-key-chapter_learning_root div[data-testid="stLinkButton"] a{
    position:relative;overflow:hidden;
}
.st-key-chapter_learning_root div[data-testid="stButton"] button:after,
.st-key-chapter_learning_root div[data-testid="stLinkButton"] a:after{
    content:"";position:absolute;inset:0;pointer-events:none;
    background:linear-gradient(110deg,transparent 25%,rgba(255,255,255,.32) 48%,transparent 70%);
    transform:translateX(-120%);transition:transform .65s ease;
}
.st-key-chapter_learning_root div[data-testid="stButton"] button:hover:after,
.st-key-chapter_learning_root div[data-testid="stLinkButton"] a:hover:after{
    transform:translateX(120%);
}
.st-key-chapter_learning_root .video-panel{
    border-color:#bfe0c9!important;
    box-shadow:0 14px 34px rgba(28,91,50,.075)!important;
}
.st-key-chapter_learning_root [data-testid="stTabs"] button[role="tab"]{
    box-shadow:0 3px 10px rgba(26,83,47,.035);
}
.st-key-chapter_learning_root [data-testid="stTabs"] button[aria-selected="true"]{
    box-shadow:0 7px 20px rgba(26,120,60,.12)!important;
}
@keyframes clAmbientA{0%{transform:translate(0,0) scale(.9)}100%{transform:translate(90px,80px) scale(1.25)}}
@keyframes clAmbientB{0%{transform:translate(0,0) scale(1)}100%{transform:translate(-100px,-70px) scale(1.2)}}
@keyframes clPulseAura{0%,100%{transform:scale(.9);opacity:.55}50%{transform:scale(1.18);opacity:1}}
@keyframes clSparkle{0%,100%{transform:scale(.65) rotate(0deg);opacity:.35}50%{transform:scale(1.35) rotate(35deg);opacity:1}}

@media(prefers-reduced-motion:reduce){.st-key-chapter_learning_root *{animation:none!important;transition:none!important}}
</style>
        """,
        unsafe_allow_html=True,
    )

def generate_chapter_lesson(exam, subject, chapter, topic, language, difficulty):
    """Call the existing FastAPI Chapter Learning endpoint."""
    url = f"{BASE_URL.rstrip('/')}/api/v1/chapter-study/generate-lesson"
    payload = {
        "exam": exam,
        "subject": subject,
        "chapter": chapter,
        "topic": topic,
        "language": language,
        "difficulty": difficulty,
    }
    try:
        response = requests.post(url, json=payload, timeout=(15, 300))
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            return {"success": False, "error": "Unexpected response from the backend."}
        if not data.get("success"):
            return {"success": False, "error": data.get("message", "The backend could not generate the lesson.")}
        if not data.get("lesson"):
            return {"success": False, "error": "The AI provider returned an empty lesson."}
        return data
    except requests.exceptions.Timeout:
        logger.exception("Chapter lesson request timed out.")
        return {"success": False, "error": "Lesson generation timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        logger.exception("Chapter Learning backend connection failed.")
        return {"success": False, "error": "Cannot connect to FastAPI. Check whether the backend is running."}
    except requests.exceptions.HTTPError as exc:
        logger.exception("Chapter Learning API returned an HTTP error.")
        try:
            detail = response.json().get("detail", str(exc))
        except Exception:
            detail = str(exc)
        return {"success": False, "error": str(detail)}
    except Exception as exc:
        logger.exception("Unexpected Chapter Learning error.")
        return {"success": False, "error": f"{type(exc).__name__}: {exc}"}


def render_info_card(icon, label, value):
    render_html(f"""
    <div class="info-card">
        <div class="info-icon">{escape(str(icon))}</div>
        <div class="info-label">{escape(str(label))}</div>
        <div class="info-value">{escape(str(value))}</div>
    </div>
    """)




def on_exam_change():
    """Reset dependent selections when the examination changes."""
    exam = st.session_state["cl_exam"]
    subject = next(iter(CHAPTERS[exam]))
    chapter = next(iter(CHAPTERS[exam][subject]))
    st.session_state["cl_subject"] = subject
    st.session_state["cl_chapter"] = chapter
    st.session_state["cl_topic"] = CHAPTERS[exam][subject][chapter][0]


def on_subject_change():
    """Reset chapter and topic when the subject changes."""
    exam = st.session_state["cl_exam"]
    subject = st.session_state["cl_subject"]
    chapter = next(iter(CHAPTERS[exam][subject]))
    st.session_state["cl_chapter"] = chapter
    st.session_state["cl_topic"] = CHAPTERS[exam][subject][chapter][0]


def on_chapter_change():
    """Reset topic when the chapter changes."""
    exam = st.session_state["cl_exam"]
    subject = st.session_state["cl_subject"]
    chapter = st.session_state["cl_chapter"]
    st.session_state["cl_topic"] = CHAPTERS[exam][subject][chapter][0]



def call_chapter_study_api(task, payload):
    """Call the isolated Chapter Study Tools API."""
    url = f"{BASE_URL.rstrip('/')}/api/v1/chapter-study/{task}"
    try:
        response = requests.post(url, json=payload, timeout=(15, 240))
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or not data.get("success"):
            return {"success": False, "error": (data or {}).get("detail", "Unexpected backend response.")}
        return data
    except requests.exceptions.Timeout:
        return {"success": False, "error": "The AI request timed out. Try fewer questions or retry shortly."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to FastAPI. Check that the backend is running."}
    except requests.exceptions.HTTPError:
        try:
            message = response.json().get("detail", response.text[:300])
        except Exception:
            message = response.text[:300]
        return {"success": False, "error": str(message)}
    except Exception as exc:
        logger.exception("Chapter Study Tools request failed.")
        return {"success": False, "error": f"{type(exc).__name__}: {exc}"}


def _study_context(exam, subject, chapter, topic, language, difficulty):
    return {
        "exam": exam, "subject": subject, "chapter": chapter,
        "topic": topic, "language": language, "difficulty": difficulty,
    }


def render_study_tools(exam, subject, chapter, topic, language, difficulty):
    """Render quiz, doubt-solving, flashcards and a session-based mistake notebook."""
    render_html("""
    <div class="section-heading">05 · Practice, ask and revise</div>
    <div class="section-caption">Three AI learning tools for your selected exam, subject, chapter and topic.</div>
    """)
    quiz_tab, doubt_tab, flashcard_tab, mistakes_tab = st.tabs([
        "🧪 AI Quiz", "💡 Ask AI Doubts", "🗂️ Smart Flashcards", "📒 Mistake Notebook"
    ])
    context = _study_context(exam, subject, chapter, topic, language, difficulty)

    with quiz_tab:
        st.markdown("#### Test your understanding")
        q1, q2 = st.columns(2)
        with q1:
            question_count = st.selectbox("Number of questions", [5, 10, 15, 20], index=1, key="cl_quiz_count")
        with q2:
            quiz_level = st.selectbox("Quiz difficulty", ["Easy", "Medium", "Hard", "Mixed"], index=3, key="cl_quiz_level")
        if st.button("✨ Generate AI quiz", key="cl_make_quiz", use_container_width=True):
            payload = {**context, "question_count": question_count, "quiz_difficulty": quiz_level}
            with st.spinner("Tribal AI is preparing your chapter quiz..."):
                result = call_chapter_study_api("quiz", payload)
            if result.get("success"):
                st.session_state["cl_active_quiz"] = result
                st.session_state["cl_quiz_answers"] = {}
                st.session_state["cl_quiz_submitted"] = False
                st.rerun()
            else:
                st.error(result.get("error", "Could not generate the quiz."))

        quiz = st.session_state.get("cl_active_quiz")
        if quiz and quiz.get("context") == context:
            questions = quiz.get("questions", [])
            st.caption(f"{len(questions)} questions · {exam} · {subject} · {chapter}")
            if not questions:
                st.warning("The AI did not return any usable questions. Please generate the quiz again.")
            else:
                answers = st.session_state.setdefault("cl_quiz_answers", {})
                submitted = st.session_state.get("cl_quiz_submitted", False)
                for index, question in enumerate(questions):
                    qid = str(question.get("id", index + 1))
                    st.markdown(f"**Q{index + 1}. {question.get('question', 'Question text unavailable')}**")
                    options = question.get("options", {})
                    if isinstance(options, list):
                        options = {chr(65 + i): value for i, value in enumerate(options)}
                    option_labels = [f"{key}. {value}" for key, value in options.items()]
                    if not option_labels:
                        st.warning("Options were missing for this question.")
                        continue
                    selected_label = st.radio(
                        "Choose your answer",
                        option_labels,
                        index=(next((i for i, label in enumerate(option_labels) if label.startswith(str(answers.get(qid, "")) + ".")), None)),
                        key=f"cl_quiz_answer_{qid}",
                        disabled=submitted,
                        label_visibility="collapsed",
                    )
                    # Streamlit returns None until the student selects an option.
                    # Do not call .split() on an unanswered radio button.
                    if selected_label is not None:
                        answers[qid] = selected_label.split(".", 1)[0].strip()

                    if submitted:
                        user_answer = str(answers.get(qid, "")).strip().upper()
                        correct = str(question.get("answer", "")).strip().upper()
                        is_correct = bool(user_answer) and user_answer == correct

                        if not user_answer:
                            st.markdown(f"⚪ **Not answered · Correct answer: {correct}**")
                        else:
                            st.markdown(
                                "✅ **Correct**"
                                if is_correct
                                else f"❌ **Incorrect · Correct answer: {correct}**"
                            )

                        if question.get("explanation"):
                            st.markdown(f"**Explanation:** {question['explanation']}")

                        # Record only an actual incorrect answer, not a skipped question.
                        if user_answer and not is_correct:
                            mistake = {
                                "exam": exam, "subject": subject, "chapter": chapter, "topic": topic,
                                "question": question.get("question", ""),
                                "your_answer": user_answer, "correct_answer": correct,
                                "explanation": question.get("explanation", ""),
                            }
                            notebook = st.session_state.setdefault("cl_mistakes", [])
                            if not any(
                                m.get("question") == mistake["question"] and m.get("chapter") == chapter
                                for m in notebook
                            ):
                                notebook.append(mistake)
                    st.divider()
                if not submitted and st.button("Submit quiz", key="cl_submit_quiz", use_container_width=True):
                    st.session_state["cl_quiz_submitted"] = True
                    st.rerun()
                if submitted:
                    score = sum(
                        str(st.session_state["cl_quiz_answers"].get(str(q.get("id", i + 1)), "")).upper()
                        == str(q.get("answer", "")).upper()
                        for i, q in enumerate(questions)
                    )
                    st.success(f"Your score: {score}/{len(questions)} · Accuracy: {score / len(questions) * 100:.1f}%")
                    if st.button("Try another quiz", key="cl_new_quiz", use_container_width=True):
                        st.session_state.pop("cl_active_quiz", None)
                        st.session_state.pop("cl_quiz_answers", None)
                        st.session_state.pop("cl_quiz_submitted", None)
                        st.rerun()
        elif quiz:
            st.info("Your previous quiz belongs to a different topic. Generate a new quiz for the current selection.")

    with doubt_tab:
        st.markdown("#### Get a step-by-step explanation")
        doubt = st.text_area(
            "Enter your question or paste a problem",
            placeholder="Example: A 5 kg block is pulled by a 20 N force on a frictionless surface. Find its acceleration and explain each step.",
            height=130,
            key="cl_doubt_input",
        )
        if st.button("💡 Explain my doubt", key="cl_solve_doubt", use_container_width=True):
            if not doubt.strip():
                st.warning("Please enter a question first.")
            else:
                with st.spinner("Tribal AI is solving your doubt..."):
                    result = call_chapter_study_api("doubt", {**context, "question": doubt.strip()})
                if result.get("success"):
                    st.session_state["cl_doubt_result"] = result
                    st.session_state["cl_doubt_context"] = context
                else:
                    st.error(result.get("error", "Could not solve this doubt."))
        doubt_result = st.session_state.get("cl_doubt_result")
        if doubt_result and st.session_state.get("cl_doubt_context") == context:
            st.markdown("---")
            st.markdown(doubt_result.get("answer", "No explanation was returned."))
            st.download_button(
                "⬇️ Download explanation",
                data=doubt_result.get("answer", ""),
                file_name="tribal_ai_doubt_solution.md",
                mime="text/markdown",
                key="cl_download_doubt",
            )

    with flashcard_tab:
        st.markdown("#### Revise important concepts quickly")
        f1, f2 = st.columns(2)
        with f1:
            flashcard_count = st.selectbox("Number of flashcards", [5, 10, 15, 20], index=1, key="cl_flashcard_count")
        with f2:
            flashcard_focus = st.selectbox("Flashcard focus", ["Definitions", "Formulas and facts", "Concepts", "Mixed revision"], index=3, key="cl_flashcard_focus")
        if st.button("🗂️ Generate flashcards", key="cl_make_flashcards", use_container_width=True):
            with st.spinner("Tribal AI is creating revision flashcards..."):
                result = call_chapter_study_api("flashcards", {
                    **context, "card_count": flashcard_count, "focus": flashcard_focus
                })
            if result.get("success"):
                st.session_state["cl_flashcards"] = result
                st.session_state["cl_flashcard_context"] = context
                st.session_state["cl_flashcard_index"] = 0
                st.session_state["cl_flashcard_revealed"] = False
                st.rerun()
            else:
                st.error(result.get("error", "Could not generate flashcards."))
        flashcards_result = st.session_state.get("cl_flashcards")
        if flashcards_result and st.session_state.get("cl_flashcard_context") == context:
            cards = flashcards_result.get("cards", [])
            if cards:
                index = min(st.session_state.get("cl_flashcard_index", 0), len(cards) - 1)
                card = cards[index]
                st.caption(f"Card {index + 1} of {len(cards)}")
                st.markdown(
                    f"""<div class="video-panel"><div class="lesson-kicker">QUESTION</div>
                    <h3>{escape(str(card.get('front', '')))}</h3></div>""",
                    unsafe_allow_html=True,
                )
                if st.button("Show answer" if not st.session_state.get("cl_flashcard_revealed") else "Hide answer", key="cl_reveal_card"):
                    st.session_state["cl_flashcard_revealed"] = not st.session_state.get("cl_flashcard_revealed", False)
                    st.rerun()
                if st.session_state.get("cl_flashcard_revealed"):
                    st.info(card.get("back", "No answer was returned."))
                prev_col, next_col = st.columns(2)
                with prev_col:
                    if st.button("← Previous", key="cl_prev_card", disabled=index == 0, use_container_width=True):
                        st.session_state["cl_flashcard_index"] = index - 1
                        st.session_state["cl_flashcard_revealed"] = False
                        st.rerun()
                with next_col:
                    if st.button("Next →", key="cl_next_card", disabled=index >= len(cards) - 1, use_container_width=True):
                        st.session_state["cl_flashcard_index"] = index + 1
                        st.session_state["cl_flashcard_revealed"] = False
                        st.rerun()
                st.download_button(
                    "⬇️ Download all flashcards",
                    data="\\n\\n".join(f"Q: {c.get('front','')}\\nA: {c.get('back','')}" for c in cards),
                    file_name="tribal_ai_flashcards.txt",
                    mime="text/plain",
                    key="cl_download_flashcards",
                )
            else:
                st.warning("No flashcards were returned. Please generate them again.")

    with mistakes_tab:
        st.markdown("#### Questions you answered incorrectly")
        notebook = st.session_state.get("cl_mistakes", [])
        if not notebook:
            st.info("Your mistake notebook is empty. Submit a quiz and incorrect answers will be saved here.")
        else:
            st.caption(f"{len(notebook)} saved mistake(s) in this Streamlit session.")
            for index, mistake in enumerate(notebook, start=1):
                with st.expander(f"{index}. {mistake.get('chapter')} · {mistake.get('question', '')[:90]}"):
                    st.markdown(f"**Your answer:** {mistake.get('your_answer')}")
                    st.markdown(f"**Correct answer:** {mistake.get('correct_answer')}")
                    st.markdown(f"**Explanation:** {mistake.get('explanation') or 'No explanation supplied.'}")
            notebook_text = "\\n\\n".join(
                f"Chapter: {m.get('chapter')}\\nQuestion: {m.get('question')}\\nYour answer: {m.get('your_answer')}\\nCorrect answer: {m.get('correct_answer')}\\nExplanation: {m.get('explanation')}"
                for m in notebook
            )
            st.download_button("⬇️ Export mistake notebook", notebook_text, "tribal_ai_mistakes.txt", "text/plain", key="cl_export_mistakes")
            if st.button("Clear mistake notebook", key="cl_clear_mistakes"):
                st.session_state["cl_mistakes"] = []
                st.rerun()


def show_chapter_learning_page():
    """Render Chapter Learning with clear sections and less visual crowding."""
    inject_chapter_learning_styles()
    with st.container(key="chapter_learning_root"):
        render_html("""
        <div class="hero">
            <div class="cl-hero-art" aria-hidden="true">
                <div class="cl-orbit"></div>
                <div class="cl-hero-book">📚</div>
            </div>
            <div class="eyebrow">✦ &nbsp; TRIBAL AI · INTELLIGENT LEARNING &nbsp; ✦</div>
            <h1>Learn beyond the classroom. <span style="color:#28a85a;text-shadow:0 0 18px rgba(40,168,90,.22)">✨</span></h1>
            <p>Your personal AI-powered learning space. Understand difficult concepts, watch focused lectures, practise examination questions and build confidence one chapter at a time.</p>
            <span class="hero-tag">✦ Tribal AI Learning Assistant</span>
            <span class="hero-tag">📚 Chapter-wise Learning</span>
            <span class="hero-tag">🎥 Video Learning</span>
            <span class="hero-tag">🌍 Multilingual Learning</span>
        </div>
        """)

        render_html("""
        <div class="section-heading">01 · Set up your learning path</div>
        <div class="section-caption">Start by choosing your examination, subject and chapter. Then select the language and difficulty that suit you.</div>
        """)

        left, right = st.columns(2, gap="large")
        with left:
            exam = st.selectbox("Examination", list(CHAPTERS.keys()), key="cl_exam", on_change=on_exam_change)
            subjects = list(CHAPTERS[exam].keys())
            if st.session_state.get("cl_subject") not in subjects:
                st.session_state["cl_subject"] = subjects[0]
            subject = st.selectbox("Subject", subjects, key="cl_subject", on_change=on_subject_change)
            chapters = list(CHAPTERS[exam][subject].keys())
            if st.session_state.get("cl_chapter") not in chapters:
                st.session_state["cl_chapter"] = chapters[0]
            chapter = st.selectbox("Chapter", chapters, key="cl_chapter", on_change=on_chapter_change)
        with right:
            language = st.selectbox("Lesson language", LANGUAGES, key="cl_language")
            difficulty = st.selectbox("Learning level", ["Beginner", "Intermediate", "Advanced"], key="cl_difficulty")
            st.markdown("")
            render_info_card("🧠", "YOUR LEARNING COMPANION", "Powered by Tribal AI")

        if exam == "NEET UG":
            st.link_button(
                "📑 View official NEET UG 2026 syllabus",
                "https://neet.nta.nic.in/document/syllabus-for-neet-ug-2026-examination/",
                use_container_width=True,
            )

        topics = CHAPTERS[exam][subject][chapter]
        if st.session_state.get("cl_topic") not in topics:
            st.session_state["cl_topic"] = topics[0]

        render_html("""
        <div class="section-heading">02 · Choose what to learn</div>
        <div class="section-caption">Pick one topic from the selected chapter. All learning resources below will follow this selection.</div>
        """)
        topic = st.selectbox("Chapter topic", topics, key="cl_topic")

        subject_icons = {"Physics": "⚛️", "Chemistry": "🧪", "Mathematics": "📐", "Biology": "🧬"}
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            render_info_card("🎯", "EXAMINATION", exam)
        with c2:
            render_info_card(subject_icons.get(subject, "📚"), "SUBJECT", subject)
        with c3:
            render_info_card("📖", "CHAPTER", chapter)

        render_html(f"""
        <div class="info-card" style="margin-top:16px;border-color:#73c991">
            <div class="info-label">YOUR SELECTED LEARNING PATH</div>
            <div class="info-value">{escape(exam)} &nbsp;›&nbsp; {escape(subject)} &nbsp;›&nbsp; {escape(chapter)}</div>
            <div class="info-label">TOPIC: {escape(topic)}</div>
        </div>
        """)

        st.markdown("")
        render_html("""
        <div class="section-heading">03 · Your learning studio</div>
        <div class="section-caption">Choose one learning activity below. Your selected exam, chapter and topic stay connected across every tab.</div>
        """)
        video_tab, pyq_tab, tools_tab, lesson_tab = st.tabs([
            "🎥 Video lessons",
            "📝 Previous year questions",
            "🧠 Study tools",
            "📘 Generate lesson",
        ])

        with video_tab:
            render_html("""
            <div class="video-panel">
                <h3>🎥 Learn this chapter from video lectures</h3>
                <p>Explore topic-focused lectures and trusted learning channels. Your search is based on the examination, subject, chapter, topic and lesson language selected above.</p>
            </div>
            """)
            curated_videos = CURATED_VIDEOS.get((exam, subject, chapter), [])
            if curated_videos:
                video_labels = [f"{item['title']} · {item['channel']}" for item in curated_videos]
                selected_video_label = st.selectbox("Recommended lectures", video_labels, key="cl_curated_video")
                selected_video = curated_videos[video_labels.index(selected_video_label)]
                st.markdown(f"**{selected_video['title']}**")
                st.caption(f"{selected_video['channel']} · {selected_video['description']}")
                st.video(f"https://www.youtube.com/watch?v={selected_video['video_id']}")
                st.caption("Videos are curated for this chapter. Availability and embedding are controlled by the video publisher.")
            else:
                render_html("""
                <div class="info-card" style="min-height:0;margin:14px 0 18px;padding:16px 18px">
                    <div class="info-value" style="font-size:14px">🌱 Explore lectures for this topic</div>
                    <div style="color:#587363;font-size:13px;line-height:1.65;margin-top:5px">
                        No verified embedded lecture is listed for this chapter yet. Use the topic-specific search below to discover available lessons.
                    </div>
                </div>
                """)

            search_query = f"{exam} {subject} {chapter} {topic} {language} lecture"
            youtube_url = "https://www.youtube.com/results?search_query=" + requests.utils.quote(search_query)
            st.link_button(
                f"▶ Find video lectures for: {topic}",
                youtube_url,
                use_container_width=True,
            )
            st.markdown("#### Explore lectures by learning channel")
            channel_queries = [
                ("Physics Wallah", f"{exam} {subject} {chapter} {topic} Physics Wallah"),
                ("Unacademy", f"{exam} {subject} {chapter} {topic} Unacademy"),
                ("Vedantu", f"{exam} {subject} {chapter} {topic} Vedantu"),
                ("SATHEE · IIT Kanpur", f"{exam} {subject} {chapter} {topic} SATHEE IIT Kanpur"),
                ("Khan Academy", f"{subject} {chapter} {topic} Khan Academy"),
            ]
            channel_cols = st.columns(2, gap="medium")
            for index, (channel, query) in enumerate(channel_queries):
                with channel_cols[index % 2]:
                    st.link_button(
                        f"📺 {channel}",
                        "https://www.youtube.com/results?search_query=" + requests.utils.quote(query),
                        use_container_width=True,
                    )
            st.caption("Video search and playback are provided by YouTube. Watching videos does not use Tribal AI's Gemini API token quota.")

        with pyq_tab:
            render_html("""
            <div class="video-panel">
                <h3>📝 Practise real examination questions</h3>
                <p>Open established question banks and official examination documents. Use the selected year, subject and chapter as filters on the source website.</p>
            </div>
            """)
            pyq_years = list(range(2026, 2008, -1)) if exam == "JEE Main" else list(range(2026, 2012, -1))
            pyq_year = st.selectbox("PYQ year", pyq_years, key="cl_pyq_year")
            if exam == "JEE Main":
                st.markdown("**Recommended question bank:** SATHEE – JEE previous-year questions, including year-wise, subject-wise and chapter-wise collections.")
                pyq_col1, pyq_col2 = st.columns(2, gap="medium")
                with pyq_col1:
                    st.link_button("📚 Open JEE chapter-wise PYQs (SATHEE)", "https://sathee.iitk.ac.in/jee-pyq/", use_container_width=True)
                with pyq_col2:
                    st.link_button("🏛️ Open official JEE Main documents (NTA)", "https://jeemain.nta.nic.in/documents/", use_container_width=True)
            else:
                st.markdown("**Recommended question bank:** SATHEE – NEET previous-year questions, with year-wise medical entrance practice.")
                pyq_col1, pyq_col2 = st.columns(2, gap="medium")
                with pyq_col1:
                    st.link_button("📚 Open NEET PYQs (SATHEE / IIT Kanpur)", "https://sathee.iitk.ac.in/sathee-neet/neet-pyq/", use_container_width=True)
                with pyq_col2:
                    st.link_button("🏛️ Open official NEET documents (NTA)", "https://neet.nta.nic.in/documents/", use_container_width=True)
            st.caption(f"Selected filters: {pyq_year} · {subject} · {chapter}. Apply the same filters in the question bank where available.")
            with st.expander("How answers are verified"):
                st.markdown(
                    "- Use the answer or solution shown with the SATHEE question where available. "
                    "- For the official final answer, cross-check the matching year, paper/shift and question ID against the NTA final answer key. "
                    "- Match the correct paper code or question ID before checking."
                )
            render_html("""
            <div class="info-card" style="min-height:0;margin:18px 0;padding:16px 18px">
                <div class="info-value" style="font-size:14px">✓ About these question sources</div>
                <div style="color:#587363;font-size:13px;line-height:1.65;margin-top:5px">
                    These links open established question banks and NTA documents. Questions are not yet imported into Tribal AI, and AI-generated practice will never be labelled as an actual previous-year question.
                </div>
            </div>
            """)
            st.caption("Source note: SATHEE is an initiative of the Ministry of Education in association with IIT Kanpur. NTA is the official examination authority.")

        with tools_tab:
            st.markdown("### 🧠 Practise and strengthen your understanding")
            st.caption("Use these tools with your selected chapter and topic.")
            render_study_tools(exam, subject, chapter, topic, language, difficulty)

        with lesson_tab:
            render_html("""
            <div class="video-panel">
                <h3>📘 Generate your personalised lesson</h3>
                <p>Tribal AI will prepare a structured explanation for your selected topic, in your chosen language and learning level.</p>
            </div>
            """)
            st.write(f"**Topic:** {topic}")
            st.write(f"**Language:** {language}  ·  **Level:** {difficulty}")
            if st.button("✨ Generate my personalised lesson", use_container_width=True, key="cl_generate"):
                with st.spinner("Tribal AI is preparing your personalised lesson..."):
                    result = generate_chapter_lesson(exam, subject, chapter, topic, language, difficulty)
                if result.get("success"):
                    st.session_state["chapter_lesson_result"] = result
                    st.session_state["chapter_lesson_selection"] = (exam, subject, chapter, topic, language, difficulty)
                    st.rerun()
                else:
                    st.error(result.get("error", "Unable to generate the lesson."))

            current_selection = (exam, subject, chapter, topic, language, difficulty)
            previous_selection = st.session_state.get("chapter_lesson_selection")
            result = st.session_state.get("chapter_lesson_result")
            if result and previous_selection == current_selection:
                st.success("Your lesson is ready!")
                lesson_tab_inner, revision_tab = st.tabs(["📖 Complete lesson", "📝 Quick revision"])
                lesson_text = result.get("lesson", "")
                with lesson_tab_inner:
                    st.markdown(lesson_text)
                with revision_tab:
                    render_html("""
                    <div class="info-card" style="min-height:0;padding:16px">
                        <div class="info-value" style="font-size:14px">Quick revision</div>
                        <div style="color:#587363;font-size:13px;line-height:1.65">Use the complete lesson for explanations, worked examples and practice questions.</div>
                    </div>
                    """)
                st.download_button("⬇️ Download lesson", data=lesson_text, file_name="chapter_lesson.md", mime="text/markdown", use_container_width=True)
                st.caption("AI-generated educational content. Verify examination-specific facts against official materials.")
            elif result and previous_selection != current_selection:
                render_html("""
                <div class="info-card" style="min-height:0;padding:16px">
                    <div class="info-value" style="font-size:14px">A previous lesson is saved in this session.</div>
                    <div style="color:#587363;font-size:13px">Generate a new lesson to match your current examination, chapter and topic.</div>
                </div>
                """)
