PYTHON ?= python3
CASE ?=
AGENT ?=
MODEL ?=
TRIALS ?= 3

.PHONY: help doctor materialize-skills new validate validate-all oracle rollouts export release-check

help:
	@printf '%s\n' 'tb-hard Studio targets:' \
	  '  make doctor' \
	  '  make materialize-skills' \
	  '  make new CASE=<case_id>' \
	  '  make validate CASE=<case_id>' \
	  '  make oracle CASE=<case_id> [HARBOR_ARGS="..."]' \
	  '  make rollouts CASE=<case_id> AGENT=<agent> MODEL=<model> [TRIALS=3] [HARBOR_ARGS="..."]' \
	  '  make export CASE=<case_id>' \
	  '  make release-check CASE=<case_id>'

doctor:
	@bash scripts/doctor.sh

materialize-skills:
	@$(PYTHON) scripts/sync_skills.py

new:
	@test -n "$(CASE)" || (echo 'CASE is required' >&2; exit 2)
	@$(PYTHON) scripts/new_case.py "$(CASE)"

validate:
	@test -n "$(CASE)" || (echo 'CASE is required' >&2; exit 2)
	@$(PYTHON) scripts/validate_case.py --case "$(CASE)" --deep

validate-all:
	@$(PYTHON) scripts/validate_case.py --all --deep

oracle:
	@test -n "$(CASE)" || (echo 'CASE is required' >&2; exit 2)
	@bash scripts/run_oracle.sh "$(CASE)" $(HARBOR_ARGS)

rollouts:
	@test -n "$(CASE)" || (echo 'CASE is required' >&2; exit 2)
	@test -n "$(AGENT)" || (echo 'AGENT is required' >&2; exit 2)
	@test -n "$(MODEL)" || (echo 'MODEL is required' >&2; exit 2)
	@bash scripts/run_rollouts.sh "$(CASE)" "$(AGENT)" "$(MODEL)" "$(TRIALS)" $(HARBOR_ARGS)

export:
	@test -n "$(CASE)" || (echo 'CASE is required' >&2; exit 2)
	@$(PYTHON) scripts/export_purchaser.py --case "$(CASE)"

release-check:
	@test -n "$(CASE)" || (echo 'CASE is required' >&2; exit 2)
	@bash scripts/package_release.sh "$(CASE)"
