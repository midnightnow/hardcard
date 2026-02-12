# HardCard Time Machine Validation Makefile
# Automates the 5-phase TM validation pipeline

# Configuration
PYTHON ?= python3
DATA_DIR ?= $(PWD)/data/tm_validation
HC_TM_DB ?= $(DATA_DIR)/hc_tm.db
DISCOVERY_FILE ?= $(shell ls $(DATA_DIR)/tm_discovery_*.json 2>/dev/null | head -1)

# Default snapshot limits for each phase
PHASE0_LIMIT ?= 3
PHASE1_LIMIT ?= 3

.PHONY: all tm-phase0 tm-phase1 tm-phase2 tm-phase3 tm-phase4 tm-phase5 tm-clean tm-status

# Complete validation pipeline
all: tm-phase0 tm-phase1 tm-phase2 tm-phase3 tm-phase4
	@echo "🎉 HardCard Time Machine validation complete!"
	@$(MAKE) tm-status

# Phase 0: Dry-run discovery
tm-phase0:
	@echo "🚀 Phase 0: Dry-run discovery"
	@./hc-tm-discovery --size-limit $(PHASE0_LIMIT)

# Phase 1: Metadata crawl and indexing
tm-phase1: tm-phase0
	@echo "🚀 Phase 1: Metadata crawl"
	@if [ -z "$(DISCOVERY_FILE)" ]; then \
		echo "❌ No discovery file found. Run 'make tm-phase0' first."; \
		exit 1; \
	fi
	@$(PYTHON) tools/tm_indexer/tm_index.py \
		--db $(HC_TM_DB) \
		--discovery $(DISCOVERY_FILE) \
		--snapshots $(PHASE1_LIMIT)
	@echo "✅ Phase 1 complete: $(HC_TM_DB)"

# Phase 2: Calculate dedup ratio (analysis only)
tm-phase2: tm-phase1
	@echo "🚀 Phase 2: Dedup ratio analysis"
	@sqlite3 $(HC_TM_DB) "SELECT \
		ROUND(CAST(COUNT(DISTINCT quick_sig) AS REAL) / COUNT(*), 3) as dedup_ratio, \
		COUNT(*) as total_files, \
		COUNT(DISTINCT quick_sig) as unique_signatures \
		FROM files;"
	@echo "✅ Phase 2 complete: Dedup analysis ready"

# Phase 3: Hyperspace ingest (mock for now)
tm-phase3: tm-phase2
	@echo "🚀 Phase 3: Hyperspace ingest (mock)"
	@echo "Mock: hc ingest-sql $(HC_TM_DB)"
	@echo "Mock: Ingesting $(shell sqlite3 $(HC_TM_DB) 'SELECT COUNT(*) FROM files') files..."
	@sleep 2
	@echo "✅ Phase 3 complete: Mock ingest successful"

# Phase 4: Query realism testing (mock)
tm-phase4: tm-phase3
	@echo "🚀 Phase 4: Query realism"
	@echo "Mock: hc query 'invoice_2024.pdf' --time-range all"
	@echo "Mock: Query latency < 200ms ✅"
	@echo "✅ Phase 4 complete: Query testing successful"

# Phase 5: Stress testing (full corpus)
tm-phase5:
	@echo "🚀 Phase 5: Stress testing (full corpus)"
	@echo "⚠️  Warning: This will process ALL snapshots"
	@read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ]
	@$(PYTHON) tools/tm_indexer/tm_index.py \
		--db $(HC_TM_DB) \
		--snapshots 0 \
		--discovery $(DISCOVERY_FILE)
	@echo "✅ Phase 5 complete: Full corpus indexed"

# Status and metrics
tm-status:
	@echo "📊 HardCard Time Machine Validation Status"
	@echo "=========================================="
	@if [ -f "$(HC_TM_DB)" ]; then \
		echo "Database: $(HC_TM_DB)"; \
		echo "Database size: $$(du -h $(HC_TM_DB) | cut -f1)"; \
		sqlite3 $(HC_TM_DB) "\
			SELECT 'Snapshots: ' || COUNT(*) FROM snapshots; \
			SELECT 'Files: ' || printf('%,d', COUNT(*)) FROM files; \
			SELECT 'Unique sigs: ' || printf('%,d', COUNT(DISTINCT quick_sig)) FROM files; \
			SELECT 'Dedup ratio: ' || ROUND(CAST(COUNT(DISTINCT quick_sig) AS REAL) / COUNT(*), 3) FROM files; \
			SELECT 'Total size: ' || ROUND(SUM(size_bytes) / 1024.0 / 1024.0 / 1024.0, 1) || ' GB' FROM files;"; \
	else \
		echo "❌ Database not found. Run 'make tm-phase1' first."; \
	fi
	@if [ -n "$(DISCOVERY_FILE)" ]; then \
		echo "Discovery file: $(DISCOVERY_FILE)"; \
	else \
		echo "❌ No discovery file found. Run 'make tm-phase0' first."; \
	fi

# Development and debugging
tm-query:
	@echo "🔍 Sample queries on indexed data:"
	@sqlite3 $(HC_TM_DB) "\
		.headers on \
		.mode column \
		SELECT filename, COUNT(*) as copies, SUM(size_bytes) as total_bytes \
		FROM files \
		GROUP BY quick_sig \
		HAVING copies > 1 \
		ORDER BY total_bytes DESC \
		LIMIT 10;"

tm-extensions:
	@echo "📎 File extension analysis:"
	@sqlite3 $(HC_TM_DB) "\
		.headers on \
		.mode column \
		SELECT extension, COUNT(*) as files, \
		       ROUND(SUM(size_bytes) / 1024.0 / 1024.0, 1) as mb \
		FROM files \
		WHERE extension != '' \
		GROUP BY extension \
		ORDER BY files DESC \
		LIMIT 15;"

tm-snapshots:
	@echo "📸 Snapshot analysis:"
	@sqlite3 $(HC_TM_DB) "\
		.headers on \
		.mode column \
		SELECT name, file_count, \
		       ROUND(size_bytes / 1024.0 / 1024.0 / 1024.0, 2) as gb \
		FROM snapshots \
		ORDER BY name;"

# Cleanup
tm-clean:
	@echo "🧹 Cleaning up Time Machine validation data..."
	@rm -rf $(DATA_DIR)
	@echo "✅ Cleanup complete"

# Help
tm-help:
	@echo "HardCard Time Machine Validation Pipeline"
	@echo "========================================"
	@echo ""
	@echo "Main targets:"
	@echo "  make tm-phase0       - Discovery ($(PHASE0_LIMIT) snapshots)"
	@echo "  make tm-phase1       - Metadata indexing ($(PHASE1_LIMIT) snapshots)"
	@echo "  make tm-phase2       - Dedup analysis"
	@echo "  make tm-phase3       - Hyperspace ingest (mock)"
	@echo "  make tm-phase4       - Query testing (mock)"
	@echo "  make tm-phase5       - Full corpus stress test"
	@echo "  make all             - Run phases 0-4"
	@echo ""
	@echo "Analysis targets:"
	@echo "  make tm-status       - Show current status"
	@echo "  make tm-query        - Sample dedup queries"
	@echo "  make tm-extensions   - File extension analysis"
	@echo "  make tm-snapshots    - Snapshot analysis"
	@echo ""
	@echo "Configuration:"
	@echo "  PHASE0_LIMIT=$(PHASE0_LIMIT)     - Snapshots for discovery"
	@echo "  PHASE1_LIMIT=$(PHASE1_LIMIT)     - Snapshots for indexing"
	@echo "  DATA_DIR=$(DATA_DIR)"
	@echo "  HC_TM_DB=$(HC_TM_DB)"