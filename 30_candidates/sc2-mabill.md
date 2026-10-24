# sc2-mabill — Explain what your MA electric bill actually charged you for
Track: Energy | Scores: I4 F4 N3 | Gates passed: 1, 2
Problem: MA residents overpaid $87.4M above basic service in FY2025 ($738.7M/10yr, AGO 2026-03-31) largely because supply-rate mechanics are opaque (municipal aggregation vs utility basic service vs third-party suppliers, look-alike utility-logoed letters). Named user: the Brookline resident whose verbatim 2023 DPU complaint describes CleanChoice letters with the Eversource logo.
Evidence:
- https://www.energychoicematters.com/stories/20260331a.html (2026-03-31) — verified: $87.4M/$738.7M figures, low-income loss $286/yr.
- https://blog.greenenergyconsumers.org/blog/predatory-electricity-suppliers-are-causing-real-pain-to-consumers — verified: quoted DPU complaint; AGO report link (mass.gov 2025 report).
- https://blog.greenenergyconsumers.org/blog/these-energy-suppliers-say-they-can-save-you-money.-regulators-say-its-a-scam (2024-04-01, repost of Globe/WBUR 2024-03-28) — verified: named-person complaint narratives (Natick, Chelsea, Falmouth).
Demo moment: Resident enters/pastes their Eversource bill lines → plain-language breakdown: which rate segment is supply, is it basic/aggregation/third-party, and how it compares to the published basic rate this month.
Build plan: see 40_shortlist.md
Agent plan: agent builds bill parser + rate-lookup tables (published DPU basic rates, MA aggregation rates on mass.gov); humans verify rate data sources and write plain-language copy.
Risks & fallback: Bill layouts vary — fallback: manual field entry for demo. MUST be educational comparison, not financial advice (Gate 5).
Why it matters: Quantified consumer harm with state reports; confusion is the documented mechanism. MA-native problem, Energy track, clean demo.