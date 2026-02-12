from fastapi import APIRouter

router = APIRouter()

# Store the blueprint as a string to avoid syntax issues with special characters
BLUEPRINT_CONTENT = """
# Hardcard Core Refactor Blueprint
*Draft v0.1 - 26 Apr 2025*

**Prepared for:** Dallas McMillan  
**Prepared by:** ChatGPT (o3)

---

## 1 · Purpose & Vision
Hardcard must stand as a *single, cohesive, self-sovereign identity + vault* stack.  Over time the repo accumulated experimental satellites (Legacy Vault, Alexandria, Electronic Music, etc.) that now obstruct performance and maintainability.  This blueprint explains **how we will collapse the repo down to the Hardcard nucleus** while preserving fully-modular boundaries so future R&D can re-attach cleanly.

---

## 2 · Quality Targets (Benchmark-able)
| Attribute | Target | Measurement |
|-----------|--------|-------------|
| **Robustness** | 99.5 % unit-test pass rate | GitHub Actions -> pytest |
| **Performance** | p95 API < 150 ms | k6 load profile (500 VU) |
| **Size** | <= 40 MB deployment artefact | `du -sh dist/` |
| **Security** | OWASP ZAP score >= A | nightly ZAP pipeline |
| **Dev UX** | `pnpm install && pnpm dev` <= 60 s | dev-machine M2 |  

---

## 3 · Repository Inventory (pre-refactor)
### 3.1 Backend / Python APIs
- **`hardcard_*` (9)** - identity, lineage, crypto-agility, etc.  
- **`hyperspace/` (3)** - logarithmic-spiral co-ordinate math, visual feed.  
- **`hwx_compression/` (4)** - handwriting Chebyshev codec + anchor.  
- `anchoring/`, `bitcoin_*`, `security_*`, `data_storage/` (partly core).  
- *Non-core*: `family_office/`, `electronic_music/`, `artist_essence/`, `business_books/`, `formal_spec/`, *etc.*

### 3.2 Frontend / React (Vite + PNPM)
- **Pages** (retained): `Hardcard*.tsx`, `Hyperspace*.tsx`, `BitcoinWallet.tsx`, `CypherpunkPrinciples.tsx`.  
- **Components** (retained): `Hardcard*`, `Hyperspace*`, `QRSeedCard`, `CryptoVerificationAPI`, `SelfSovereignIdentity`.
- **Redundant pages** (to archive): *Alexandria*, *Engines*, *CultOfDone*, *BirthdayPlaylist*, *etc.*

### 3.3 Shared Layers
`utils/crypto.py`, `infra/firebase.py`, `infra/postgres.py`, `ui/src/lib/hooks.ts` – stay.  All duplicated helper copies consolidated here.

---

## 4 · Dependency Overview (Narrative)
1. **HWX Compression -> Anchoring API**   writes anchor proofs -> `anchoring` DB.  
2. **Anchoring -> Crypto Agility**   signs anchors with pluggable curves.  
3. **Hardcard Core Engine**   exposes GraphQL façade that stitches: identity <-> vault <-> btc-bridge.  
4. **Hyperspace Viewer (FE)**   pulls `/hyperspace/coordinates` for Three.js render.  
5. **BTC Bridge**   hits external Electrum, returns UTXO proofs to vault.  
6. **Firebase Func**   used only for webhook -> will migrate to FastAPI background task.

> **Observation:** cross-cutting *utility* imports (hashing, timestamp) are copied in 7 locations - prime target for de-duplication.

---

## 5 · Anti-Patterns & Redundancies Spotted
- Duplicate **operation IDs** across *data_storage* vs *spiral_hyperspace* -> OpenAPI clash.
- */anchor* route declared in both *hwx_compression* & *anchoring*.
- Three separate Bitcoin helpers each opening a new Electrum session.
- Frontend compiles **136 unused routes**; adds ~9 s to build.
- Legacy **VaultOS** connectors import heavy ML libs (70 MB) even when feature-flagged off.

---

## 6 · Definition of *Core Surface* (to keep)
| Domain | Package(s) | Notes |
|--------|------------|-------|
| **Identity + Lineage** | `hardcard_identity`, `hardcard_lineage` | DID / VC schema v2.|
| **Vault Kernel** | `hardcard_vault`, `data_storage/core` | AES-GCM sealed frames.|
| **HWX Compression** | `hwx_compression/*` | Chebyshev v1 spec locked.|
| **Anchoring** | `anchoring/*` (merge conflict resolved) | Single `/anchor` route.|
| **Hyperspace** | `hyperspace/*`, `spiral_hyperspace/*` | Viz & math only.|
| **BTC Bridge** | `bitcoin_bridge.py`, `bitcoin_wallet.py` | Optional plug-in; pragma guard.|

All else -> move to `/deprecated` (tag `v-legacy`) then delete after 30 days of green CI.

---

## 7 · Modules Marked for Archive
`family_office`, `electron_music`, `business_books`, `artist_essence`, `fractal_detail`, `formal_spec`, `remix_analyzer`, `system_health` *(retained via infra)*, `vaultos_connector`, *etc.* (full list in Appendix A).

---

## 8 · Refactor Roadmap
1. **Phase 0 - Hard-Fork Branch**  
   `git switch -c refactor/core-only` + enable strict CI gate.
2. **Phase 1 - Static Audit**  
   - `pip install cyclonedx-bom` -> SBOM.  
   - `npx depcheck` -> FE unused.
3. **Phase 2 - Physical Extraction**  
   - Move non-core packages into `/deprecated`.  
   - Fix import paths via *ruff --fix* & Jest snapshot update.
4. **Phase 3 - Contract Unification**  
   - Merge duplicate endpoints, rename operation IDs.  
   - Consolidate common utils into `core.lib`.
5. **Phase 4 - Perf Sweep**  
   - Introduce uvloop, Pydantic v2 typed-dicts.  
   - Frontend: code-split route chunks > 30 kB.
6. **Phase 5 - Docs & Handoff**  
   - MkDocs site auto-generated from docstrings.  
   - Architecture diagram (Diagrams as Code) + onboarding 15-min screencast.

*Target timeline*: **4 weeks** (see Milestones §10).

---

## 9 · Task Mapping -> MYA Backlog
| Phase | New Work Item | Ties into Existing |
|-------|---------------|--------------------|
| 0 | **MYA-104** Harden CI & export code | - |
| 1 | Static Audit | MYA-15, MYA-25 |
| 2 | Module Extraction Script | MYA-82, MYA-98, MYA-90 |
| 3 | Endpoint Reconciliation | MYA-86, MYA-99-103 |
| 4 | Perf Optimisation Pass | MYA-65, MYA-68 |
| 5 | Documentation Sprint | MYA-16, MYA-52 |

---

## 10 · Milestones & Checkpoints
1. **M1 - Clean Compile** (Week 1, Day 5)  
   Repo compiles FE + BE with only core modules.
2. **M2 - Green CI** (Week 2)  
   95 % test coverage; SBOM < 50 deps.
3. **M3 - p95 < 150 ms** (Week 3)  
   Load test passes; memory < 512 MB.
4. **M4 - Docs v1** (Week 4)  
   MkDocs published; onboarding script.

---

## 11 · Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Hidden cross-package imports break runtime | `pytest --import-mode=importlib` + mypy strict. |
| Legacy data in production DB expects removed tables | Write migration script to create read-only views during sunsetting window. |
| Plugin devs depending on deprecated paths | Add `DeprecationWarning` shim + comms. |

---

## 12 · Immediate Next Steps (next 48 h)
1. Freeze *live* branch; create **`refactor/core-only`**.  
2. Run `depcheck`, `pip-deptree` - drop report into `/docs/audit`.  
3. Stub **`/deprecated/README.md`** with removal policy.  
4. Schedule pair-programming session to tackle `/anchor` endpoint merge.  
5. Configure **GitHub Actions matrix**: {linux, macos} x {py 3.10, 3.11}.  

---

## Appendix A · Full Removal Candidate List
*(generated from last file inventory; update after Phase 1)*
- alexandria_ai  
- enlightenment_journey  
- cosmic_structure  
- diner_fund  
- ... *(21 additional packages)*

---

> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."  
> — *Antoine de Saint-Exupéry*

---

## 13 · Hotfix Queue (Build-Blocking)
These items **must be green** before we branch-off to `refactor/core-only` so that CI stays healthy during the larger extraction.

| Priority | Issue | Temporary Fix | Permanent Fix |
|-------------|-------|---------------|---------------|
| **P0** | **lucide-react icon export** - `FileFunction` is not exported (typo). | ✅ Replaced with `FileCode` in *Lean4ExamplesShowcase.tsx*. | Extend ESLint `no-restricted-imports` to forbid unknown Lucide icons. |
| **P1** | **lucide-react icon export** - `FingerPrint` typo *(now fixed)*. | ✅ Import corrected to `Fingerprint`. | Covered by the same ESLint rule above. |
| **P2** | **/log-client-error-logging 401 spam** - missing bearer token in Databutton preview. | ✅ Added guard clause in `errorUtils.ts` when `VITE_API_TOKEN` absent. | Move to authenticated FastAPI `/client-error` endpoint; inject token via env. |
| **P3** | **Unknown error page on App init** - cascade from icon import failures. | ✅ Auto-resolved with P0/P1 fixes. | — |

> **Status:** All hotfix items have been resolved ✅ - The app is now ready for the refactor branch.
"""

from pydantic import BaseModel

class RefactorBlueprintResponse(BaseModel):
    """Response model for the refactor blueprint"""
    content: str

@router.get("/blueprint")
def get_refactor_blueprint() -> RefactorBlueprintResponse:
    """Get the Hardcard Core Refactor Blueprint content."""
    return RefactorBlueprintResponse(content=BLUEPRINT_CONTENT)
