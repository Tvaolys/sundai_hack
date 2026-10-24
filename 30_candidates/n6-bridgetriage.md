# n6-bridgetriage — Bridge-condition maintenance triage from NBI data (+ optional defect vision)
Track: Robotics & hardware (Safer Inspection of Critical Infrastructure) | Scores: I3 F4 N4 | Gates passed: 1,2,3,4,5,6
Problem: The official challenge is explicit: MassDOT Aeronautics "already flies drones to inspect bridges… the bottleneck has moved from [capture] to interpretation." Turning raw condition ratings (and images) into a prioritized maintenance list is the real, current gap — not more data capture.
Evidence:
- Challenge text (official portal, extracted 2026-10-24): verified.
- National Bridge Inventory MA file (fhwa.dot.gov/bridge/nbi/2022/delimited/MA22.txt) LIVE — real delimited file with condition columns (deck/superstructure/substructure coded fields): curl-verified 2026-10-24.
- FHWA InfoBridge/SNBI (schema) + dacl10k (HF) / CODEBRIM bridge-defect image sets: provided portal resources (verified in registry; redistribution caveat on images noted).
Demo moment: Load MA NBI → ranked maintenance list where each rank is explained by the driving deck/superstructure/substructure rating; click a bridge → a sample inspection photo with a crack/corrosion flag overlaid (defect-dataset model). Capture→interpretation, shown end to end.
Build plan (09:00–20:00):
- 09:00 spec: decode the NBI condition columns (item 58/59/60) into a defensible priority score; confirm field meanings against SNBI docs.
- 10:00 CS×2: NBI parser + scoring + ranked table UI; CS×1: bridge detail view; CS×1 (stretch): a small pretrained defect classifier on a handful of dacl10k/CODEBRIM sample images (CPU-only, inference on 5-10 images, not training).
- 13:00 tester: verify ranks against raw ratings; confirm no bridge is mis-decoded.
- 15:00 wire the image flag into the detail view (stretch) or fall back to tabular-only.
- 16:30 demo-builder: a MA county story; 18:00 FREEZE.
Agent plan: Agent builds parser + scoring + UI; humans own the NBI column decoding (rule-critical) and whether the vision stretch ships. Tabular core is laptop-only; vision uses CPU inference on a few cached images.
Risks & fallback: (1) NBI column misread → human-verified decoding table frozen in repo. (2) Defect vision too slow/unreliable on CPU → drop to tabular triage (still a complete demo matching the challenge). (3) image redistribution → use only sample images per dataset-card terms.
Why it matters: Addresses the challenge's own stated shift — from capturing inspection data to interpreting it — using the MA bridge file they provided, producing a list an asset manager could actually act on.
