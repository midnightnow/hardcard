from fastapi import APIRouter
from pydantic import BaseModel # Added for new model

router = APIRouter()


class BlueprintResponseNew(BaseModel): # Added from __init___new
    """Response model for the refactor blueprint""" # Added from __init___new
    content: str # Added from __init___new


@router.get("/get-refactor-blueprint-new", operation_id="get_refactor_blueprint_new_content") # Added from __init___new
def get_refactor_blueprint_new() -> BlueprintResponseNew: # Added from __init___new
    """Get the Hardcard Refactor Blueprint document""" # Added from __init___new
    return BlueprintResponseNew( # Added from __init___new
        content="# Hardcard Core Refactor Blueprint\\n*Draft v0.1 - 26 Apr 2025*\\n\\n**Core blueprint document available on request**" # Added from __init___new
    ) # Added from __init___new


@router.get("/refactor-blueprint-json", operation_id="get_refactor_blueprint_json_document")
def get_refactor_blueprint_json():
    """Get the Hardcard Core Refactor Blueprint document.
    
    This document outlines the plan for refactoring the Hardcard system 
    to focus on core functionality while maintaining modularity.
    """
    return {
        "title": "Hardcard Core Refactor Blueprint",
        "version": "0.1",
        "date": "26 Apr 2025",
        "author": "ChatGPT (o3)",
        "recipient": "Dallas McMillan",
        "sections": [
            {
                "id": "purpose",
                "title": "Purpose & Vision",
                "content": "Hardcard must stand as a single, cohesive, self-sovereign identity + vault stack. "
                          "Over time the repo accumulated experimental satellites (Legacy Vault, Alexandria, "
                          "Electronic Music, etc.) that now obstruct performance and maintainability. "
                          "This blueprint explains how we will collapse the repo down to the Hardcard nucleus "
                          "while preserving fully-modular boundaries so future R&D can re-attach cleanly."
            },
            {
                "id": "quality-targets",
                "title": "Quality Targets (Benchmark-able)",
                "content": [
                    {"attribute": "Robustness", "target": "99.5% unit-test pass rate", "measurement": "GitHub Actions → pytest"},
                    {"attribute": "Performance", "target": "p95 API < 150 ms", "measurement": "k6 load profile (500 VU)"},
                    {"attribute": "Size", "target": "≤ 40 MB deployment artefact", "measurement": "du -sh dist/"},
                    {"attribute": "Security", "target": "OWASP ZAP score ≥ A", "measurement": "nightly ZAP pipeline"},
                    {"attribute": "Dev UX", "target": "pnpm install && pnpm dev ≤ 60 s", "measurement": "dev-machine M2"}
                ]
            },
            {
                "id": "inventory",
                "title": "Repository Inventory (pre-refactor)",
                "subsections": [
                    {
                        "title": "Backend / Python APIs",
                        "items": [
                            "hardcard_* (9) – identity, lineage, crypto-agility, etc.",
                            "hyperspace/ (3) – logarithmic-spiral co-ordinate math, visual feed.",
                            "hwx_compression/ (4) – handwriting Chebyshev codec + anchor.",
                            "anchoring/, bitcoin_*, security_*, data_storage/ (partly core).",
                            "Non-core: family_office/, electronic_music/, artist_essence/, business_books/, formal_spec/, etc."
                        ]
                    },
                    {
                        "title": "Frontend / React (Vite + PNPM)",
                        "items": [
                            "Pages (retained): Hardcard*.tsx, Hyperspace*.tsx, BitcoinWallet.tsx, CypherpunkPrinciples.tsx.",
                            "Components (retained): Hardcard*, Hyperspace*, QRSeedCard, CryptoVerificationAPI, SelfSovereignIdentity.",
                            "Redundant pages (to archive): Alexandria, Engines, CultOfDone, BirthdayPlaylist, etc."
                        ]
                    },
                    {
                        "title": "Shared Layers",
                        "items": [
                            "utils/crypto.py, infra/firebase.py, infra/postgres.py, ui/src/lib/hooks.ts – stay. All duplicated helper copies consolidated here."
                        ]
                    }
                ]
            },
            {
                "id": "dependencies",
                "title": "Dependency Overview (Narrative)",
                "items": [
                    "HWX Compression → Anchoring API writes anchor proofs ⟶ anchoring DB.",
                    "Anchoring → Crypto Agility signs anchors with pluggable curves.",
                    "Hardcard Core Engine exposes GraphQL façade that stitches: identity ⇆ vault ⇆ btc-bridge.",
                    "Hyperspace Viewer (FE) pulls /hyperspace/coordinates for Three.js render.",
                    "BTC Bridge hits external Electrum, returns UTXO proofs to vault.",
                    "Firebase Func used only for webhook → will migrate to FastAPI background task."
                ],
                "observation": "Cross-cutting utility imports (hashing, timestamp) are copied in 7 locations – prime target for de-duplication."
            },
            {
                "id": "anti-patterns",
                "title": "Anti-Patterns & Redundancies Spotted",
                "items": [
                    "Duplicate operation IDs across data_storage vs spiral_hyperspace ➜ OpenAPI clash.",
                    "/anchor route declared in both hwx_compression & anchoring.",
                    "Three separate Bitcoin helpers each opening a new Electrum session.",
                    "Frontend compiles 136 unused routes; adds ~9 s to build.",
                    "Legacy VaultOS connectors import heavy ML libs (70 MB) even when feature-flagged off."
                ]
            },
            {
                "id": "core-surface",
                "title": "Definition of Core Surface (to keep)",
                "domains": [
                    {"domain": "Identity + Lineage", "packages": "hardcard_identity, hardcard_lineage", "notes": "DID / VC schema v2."},
                    {"domain": "Vault Kernel", "packages": "hardcard_vault, data_storage/core", "notes": "AES-GCM sealed frames."},
                    {"domain": "HWX Compression", "packages": "hwx_compression/*", "notes": "Chebyshev v1 spec locked."},
                    {"domain": "Anchoring", "packages": "anchoring/* (merge conflict resolved)", "notes": "Single /anchor route."},
                    {"domain": "Hyperspace", "packages": "hyperspace/*, spiral_hyperspace/*", "notes": "Viz & math only."},
                    {"domain": "BTC Bridge", "packages": "bitcoin_bridge.py, bitcoin_wallet.py", "notes": "Optional plug-in; pragma guard."}
                ],
                "note": "All else move to /deprecated (tag v-legacy) then delete after 30 days of green CI."
            },
            {
                "id": "archive-modules",
                "title": "Modules Marked for Archive",
                "content": "family_office, electron_music, business_books, artist_essence, fractal_detail, "
                          "formal_spec, remix_analyzer, system_health (retained via infra), "
                          "vaultos_connector, etc. (full list in Appendix A)."
            },
            {
                "id": "roadmap",
                "title": "Refactor Roadmap",
                "phases": [
                    {
                        "phase": "Phase 0 – Hard-Fork Branch",
                        "description": "git switch -c refactor/core-only + enable strict CI gate."
                    },
                    {
                        "phase": "Phase 1 – Static Audit",
                        "description": "pip install cyclonedx-bom ➜ SBOM. npx depcheck ➜ FE unused."
                    },
                    {
                        "phase": "Phase 2 – Physical Extraction",
                        "description": "Move non-core packages into /deprecated. Fix import paths via ruff –fix & Jest snapshot update."
                    },
                    {
                        "phase": "Phase 3 – Contract Unification",
                        "description": "Merge duplicate endpoints, rename operation IDs. Consolidate common utils into core.lib."
                    },
                    {
                        "phase": "Phase 4 – Perf Sweep",
                        "description": "Introduce uvloop, Pydantic v2 typed-dicts. Frontend: code-split route chunks > 30 kB."
                    },
                    {
                        "phase": "Phase 5 – Docs & Handoff",
                        "description": "MkDocs site auto-generated from docstrings. Architecture diagram (Diagrams as Code) + onboarding 15-min screencast."
                    }
                ],
                "timeline": "4 weeks (see Milestones)"
            },
            {
                "id": "task-mapping",
                "title": "Task Mapping → MYA Backlog",
                "tasks": [
                    {"phase": "0", "work_item": "MYA-104 Harden CI & export code", "ties_into": "-"},
                    {"phase": "1", "work_item": "Static Audit", "ties_into": "MYA-15, MYA-25"},
                    {"phase": "2", "work_item": "Module Extraction Script", "ties_into": "MYA-82, MYA-98, MYA-90"},
                    {"phase": "3", "work_item": "Endpoint Reconciliation", "ties_into": "MYA-86, MYA-99-103"},
                    {"phase": "4", "work_item": "Perf Optimisation Pass", "ties_into": "MYA-65, MYA-68"},
                    {"phase": "5", "work_item": "Documentation Sprint", "ties_into": "MYA-16, MYA-52"}
                ]
            },
            {
                "id": "milestones",
                "title": "Milestones & Checkpoints",
                "milestones": [
                    {"id": "M1 – Clean Compile", "timeframe": "Week 1, Day 5", "description": "Repo compiles FE + BE with only core modules."},
                    {"id": "M2 – Green CI", "timeframe": "Week 2", "description": "95% test coverage; SBOM < 50 deps."},
                    {"id": "M3 – p95 < 150 ms", "timeframe": "Week 3", "description": "Load test passes; memory < 512 MB."},
                    {"id": "M4 – Docs v1", "timeframe": "Week 4", "description": "MkDocs published; onboarding script."}
                ]
            },
            {
                "id": "risks",
                "title": "Risks & Mitigations",
                "items": [
                    {"risk": "Hidden cross-package imports break runtime", "mitigation": "pytest --import-mode=importlib + mypy strict."},
                    {"risk": "Legacy data in production DB expects removed tables", "mitigation": "Write migration script to create read-only views during sunsetting window."},
                    {"risk": "Plugin devs depending on deprecated paths", "mitigation": "Add DeprecationWarning shim + comms."}
                ]
            },
            {
                "id": "next-steps",
                "title": "Immediate Next Steps (next 48 h)",
                "steps": [
                    "Freeze live branch; create refactor/core-only.",
                    "Run depcheck, pip-deptree – drop report into /docs/audit.",
                    "Stub /deprecated/README.md with removal policy.",
                    "Schedule pair-programming session to tackle /anchor endpoint merge.",
                    "Configure GitHub Actions matrix: {linux, macos} × {py 3.10, 3.11}."
                ]
            },
            {
                "id": "appendix-a",
                "title": "Appendix A · Full Removal Candidate List",
                "note": "generated from last file inventory; update after Phase 1",
                "candidates": [
                    "alexandria_ai",
                    "enlightenment_journey",
                    "cosmic_structure",
                    "diner_fund",
                    "... (21 additional packages)"
                ]
            },
            {
                "id": "quote",
                "content": "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.",
                "author": "Antoine de Saint-Exupéry"
            },
            {
                "id": "hotfix-queue",
                "title": "Hotfix Queue (Build-Blocking)",
                "description": "These items must be green before we branch-off to refactor/core-only so that CI stays healthy during the larger extraction.",
                "items": [
                    {
                        "priority": "P0",
                        "issue": "lucide-react icon export – FileFunction is not exported (typo).",
                        "temporary_fix": "✅ Replaced with FileCode in Lean4ExamplesShowcase.tsx.",
                        "permanent_fix": "Extend ESLint no-restricted-imports to forbid unknown Lucide icons."
                    },
                    {
                        "priority": "P1",
                        "issue": "lucide-react icon export – FingerPrint typo (now fixed).",
                        "temporary_fix": "✅ Import corrected to Fingerprint.",
                        "permanent_fix": "Covered by the same ESLint rule above."
                    },
                    {
                        "priority": "P2",
                        "issue": "/log-client-error-logging 401 spam – missing bearer token in Databutton preview.",
                        "temporary_fix": "✅ Added guard clause in errorUtils.ts when VITE_API_TOKEN absent.",
                        "permanent_fix": "Move to authenticated FastAPI /client-error endpoint; inject token via env."
                    },
                    {
                        "priority": "P3",
                        "issue": "Unknown error page on App init – cascade from icon import failures.",
                        "temporary_fix": "✅ Auto-resolved with P0/P1 fixes.",
                        "permanent_fix": "-"
                    }
                ],
                "status": "All hotfix items have been resolved ✅ - The app is now ready for the refactor branch."
            }
        ]
    }
