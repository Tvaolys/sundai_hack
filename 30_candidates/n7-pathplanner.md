# n7-pathplanner — "Which path planner should I use?" visual classifier on a real Boston grid
Track: Robotics & hardware (Path Planning Classifier) | Scores: I3 F5 N4 | Gates passed: 1,2,3,4,5,6
Problem: Robotics learners and engineers pick A* or RRT by habit, not by fit to map density and compute budget. The official challenge asks exactly this: "How to choose which path planning algorithm for your environmental needs and compute resources or other constraints." The portal ships the benchmark asset to answer it.
Evidence:
- Challenge text verbatim (official portal, extracted 2026-10-24): confidence verified.
- Boston street grid 256 (movingai benchmark zip) + Boston street centerlines (19,440 real segments, geometry) — provided portal datasets: verified (portal registry).
- PythonRobotics (github.com/AtsushiSakai/PythonRobotics) ships A*/Dijkstra/RRT/PRM in pure Python — provided resource: verified.
Demo moment: Pick the Boston grid + start/goal → run A*, Dijkstra, RRT, PRM side by side; show path length, nodes expanded, runtime; classifier recommends one ("RRT — sparse map, tight compute") with the reason.
Audit fix: Boston_0_256 alone is ONE density point, so the classifier would be a lookup, not a rule. Mitigation: (a) run the matrix over MANY movingai maps (several densities) to earn a real decision boundary; (b) wire the actual Boston street-centerline graph (19,440 segments, real geometry) for one concrete MA routing scenario so the provided MA data is load-bearing, not decorative.
Build plan (09:00–20:00):
- 09:00 math grad (spec): define the decision rule over map features (obstacle-density %, free-space ratio, map size, compute budget) + metrics (path length, nodes expanded, wall-time).
- 09:30 CS×2 (agent-executors): load the movingai map set (multiple densities) + Boston street-centerlines graph; wire PythonRobotics planners (A*/Dijkstra/RRT/PRM) behind one interface. CS×1: web UI (grid render, start/goal picker, run). CS×1: metrics panel + path overlays.
- 13:00 tester: run matrix maps×planners, catch crashes/timeouts; cap RRT iterations + fix seeds.
- 15:00 fit the classifier rule from the measured matrix (not a single map); add the "why".
- 16:30 demo-builder: side-by-side race + recommendation + the real Boston-street routing scenario; freeze presets.
- 18:00 FREEZE: cache precomputed runs so the live demo never hangs.
Agent plan: Agent scaffolds planner-runner, grid + street-graph UI, metrics; humans own the classifier rule and the demo narrative. No GPU, no external API — fully offline, laptop-only.
Risks & fallback: (1) RRT non-determinism/timeout → fixed seeds + iteration cap; fallback precomputed runs. (2) Over-claiming "optimal" → frame as guided comparison, not proof. (3) Weak classifier with one map → the multi-map matrix is what makes the rule honest; if it still underwhelms, the side-by-side race + real Boston route alone is a strong demo.
Why it matters: It answers the exact question the organizers posed, on the exact data they shipped, with a reproducible visual anyone can rerun — the most judge-legible robotics entry available to a laptop-only team.
