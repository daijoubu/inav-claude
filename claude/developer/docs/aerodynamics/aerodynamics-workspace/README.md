# Aerodynamics Expert Agent Workspace

This workspace is used by the **aerodynamics-expert** agent to build up knowledge and save reference materials over time.

## Directory Structure

```
aerodynamics-workspace/
├── notes/          - Session notes and analysis from specific questions
├── knowledge-base/ - Accumulated knowledge organized by topic
├── calculations/   - Aerodynamic calculations and derivations
└── references/     - Extracted sections and quick reference materials
```

## Usage

The aerodynamics-expert agent automatically:
1. Checks this workspace for existing notes on topics before searching the textbook
2. Saves complex analyses for future reference
3. Builds up a knowledge base organized by topic (e.g., drag, lift, stall)
4. Creates quick reference materials extracted from the textbook

## Invoke the Agent

```
Task tool with subagent_type="aerodynamics-expert"
Prompt: "Your aerodynamics question here"
```

## Example Topics

The agent can help with:
- Lift and drag coefficients
- Pitot tube calibration and airspeed measurement
- Stall behavior and recovery
- Reynolds number effects
- Induced vs. parasitic drag
- Wing geometry and aspect ratio
- Boundary layer theory
- Pressure distribution
- Flight dynamics fundamentals

All answers include citations to specific pages in Houghton & Carpenter.
