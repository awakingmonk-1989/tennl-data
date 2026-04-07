.PHONY: help build run

help:
	@echo "Targets:"
	@echo "  build           Build wheel"
	@echo "  run             Run sample workflow via uv"

build:
	@uv build --project .

run:
	@uv run python -m tennl.batch.workflows.sample_workflow

