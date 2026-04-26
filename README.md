# UNMAPPED — Infrastructure for Recognizing Informal Work in the AI Era

UNMAPPED is a country-agnostic labour intelligence system that converts informal experience into structured, portable skill profiles, estimates AI displacement exposure, and generates realistic economic pathways using live global labour signals.

It is built for a simple yet overlooked reality: Most of the world’s workers are absent from its data systems.

---

## The Problem

In many low- and middle-income economies:

- The majority of work is informal, undocumented, or partially recognized
- Skills exist in practice but not in formal taxonomies
- Labour datasets fail to reflect real economic activity
- AI risk discussions exclude informal workers entirely
- Policy and education systems operate on incomplete labour intelligence

This creates a structural blind spot in how opportunity, risk, and workforce transitions are designed.

---

## The Solution

UNMAPPED introduces a portable skills and labour intelligence layer that:

- Translates informal experience into structured skill representations
- Matches individuals to occupation families using durable skill signals
- Models AI exposure using contextual assumptions
- Anchors analysis in real-time World Bank labour indicators
- Produces ranked, feasible opportunity pathways
- Remains fully reconfigurable across countries without code changes

---

## Core System Design

### 1. Portable Skills Engine
Extracts structured skill axes from unstructured experience:
- Repair & technical work  
- Sales & informal trade  
- Digital capability  
- Care and community work  
- Craft and garment production  
- Logistics and mobility labour  
- Administrative and record-based work  

This enables comparison across roles that are normally invisible to formal systems.

---

### 2. Occupation Matching Model
Maps individuals to occupation families using:
- Skill keyword alignment
- Durable capability signals 
- Informal-to-formal translation logic
- Cross-context portability scoring

The system prioritizes *transferable capability over credential labels*.

---

### 3. AI Exposure & Risk Calibration
A contextual risk model combining:

- Occupation-level automation exposure
- Device access constraints (feature phone → laptop)
- Digital access intensity
- Local economic calibration factors
- Skill-based resilience buffers (repair, care, craft, sales)

The output is a transparent, explainable risk score.

---

### 4. Real Labour Market Signals (World Bank API)
The system integrates live macro indicators:

- Youth NEET rates  
- Employment-to-population ratios  
- Vulnerable employment share  
- Internet penetration  
- GDP per capita  
- Secondary education enrollment  

These signals ground micro-level profiles in macroeconomic reality.

---

### 5. Opportunity Generation Engine
Produces ranked, realistic pathways such as:

- Apprenticeships and skill transitions  
- Micro-enterprise expansion routes  
- Gig and informal labour opportunities  
- Formal employment entry points  
- Digital augmentation pathways  

Each recommendation is scored by feasibility, context fit, and risk sensitivity.

---

### 6. Country-Agnostic Architecture
The system is fully configurable across contexts:

- Ghana (urban informal economy)
- India (rural agricultural transition)

Swapping contexts dynamically adjusts:
- Automation calibration
- Labour signal interpretation
- Opportunity structures
- Constraint environments
- Policy framing assumptions

Simply configure.

---

## Technical Stack

- Python (core logic)
- Gradio (interactive interface)
- Pandas & NumPy (data processing)
- Plotly (visual analytics)
- Requests (World Bank API integration)

---

## System Outputs

The dashboard delivers:

- Skill radar profiles (portable capability mapping)
- AI exposure and displacement risk scoring
- Live labour market signal dashboards
- Ranked opportunity pathways
- Context comparison views
- Optional WCDE projection overlays
- Debug-level transparency for evaluation

---

## End-to-End Flow

1. User inputs informal experience and competencies  
2. System extracts structured skill signals  
3. Occupation family matching is performed  
4. World Bank indicators contextualize the environment  
5. AI risk model computes exposure and resilience  
6. Opportunity engine generates ranked pathways  
7. UI renders explainable, decision-ready insights  

---

## Why This Matters

UNMAPPED is an infrastructure for a missing layer in global labour systems:

- Between informal work and formal recognition  
- Between AI exposure and policy visibility  
- Between lived skill and economic classification  

It reframes informal labour as

> structurally unclassified, economically active capability.

---

## Deployment

UNMAPPED is deployed as a Hugging Face Space.

Once live:
- It runs entirely in the cloud
- Requires no local execution
- Is accessible via a public URL
- Automatically rebuilds on updates

---

## Future Extensions

- Integration with ESCO / O*NET skill graphs  
- Offline-first mobile deployment  
- Government labour policy dashboards  
- Employer-side matching APIs  
- Real-time gig and micro-work marketplaces  
- Longitudinal worker transition tracking  

---

## Author

Built for the World Bank Hackathon — Jessica Anabor

---

## Disclaimer

This system is a decision-support and exploration tool. It provides probabilistic and contextual analysis, not deterministic employment outcomes or guarantees.
