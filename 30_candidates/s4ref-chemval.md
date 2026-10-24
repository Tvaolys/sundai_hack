# s4ref-chemval — Validate chemistry file conversions before they silently corrupt your data
Track: Biotech | Scores: I3 F3 N5 | Gates passed: 1, 2
Problem: Computational chemists running RDKit/OpenBabel pipelines hit silent-wrong-output format conversions (valence errors, sanitization surprises). Named user: filing authors of the open OpenBabel issues (e.g., MatthewMasters, heme xyz→mol2).
Evidence:
- https://github.com/openbabel/openbabel/issues/2427 — verified live, open: heme valence incorrect xyz→mol2; suggested fix is MANUAL connection-table editing.
- https://github.com/openbabel/openbabel/issues/1049 — verified open: "wrong mol2 -> SMILES conversion" (silent).
- https://github.com/rdkit/rdkit/discussions/8529 + /discussions/4084 — verified: confusing sanitize/implicit-H behavior; opaque KekulizeException ingesting journal mol blocks.
Demo moment: Convert heme xyz→mol2 with stock OpenBabel → silent wrong valence; run the same file through our validator → red flag "valence mismatch vs XYZ topology" before it enters the pipeline.
Build plan: see 40_shortlist.md
Agent plan: agent builds the web validator (RDKit/OpenBabel wrappers, cross-format consistency checks: atom counts, valence sanity, charge, H-count); humans (chem major) curate the check list and test set.
Risks & fallback: Defining "correct" is hard — fallback: consistency checks (formula preserved, valence bounds, kekulization success) still catch the demo cases. RDKit/OpenBabel install via pip/conda — test tonight.
Why it matters: Every silent conversion error propagates into docking/MD/papers. No "pre-flight validator" sits between these free tools. Esoteric, real, exactly the team's chem-major sweet spot.