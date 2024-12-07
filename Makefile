export PROJECTNAME=$(shell basename "$(PWD)")
export CONTEXT_DIR=build
PY=./venv/bin/python3

.SILENT: ;               # no need for @

deps: ## Install dependencies
	$(PY) -m pip install --upgrade -r requirements/requirements-dev.txt
	$(PY) -m pip install --upgrade pip

pre-commit: ## Manually run all precommit hooks
	./venv/bin/pre-commit install
	./venv/bin/pre-commit run --all-files

pre-commit-tool: ## Manually run a single pre-commit hook
	./venv/bin/pre-commit run $(TOOL) --all-files

clean: ## Clean package
	find . -type d -name '__pycache__' -not -path "./venv/*" | xargs rm -rf
	find . -type d -name "*.egg-info" | xargs rm -rf
	rm -rf build dist

package: clean pre-commit ## Run installer
	$(PY) -m build

context: clean ## Build context file from application sources
	echo "Generating context in $(CONTEXT_DIR) directory"
	mkdir -p $(CONTEXT_DIR)/
	cd src/ && llm-context-builder.py --extensions .py --ignored_dirs build dist generated venv .venv .idea .aider.tags.cache.v3 --print_contents > ../$(CONTEXT_DIR)/$(PROJECTNAME)-src.py
	echo `pwd`/$(CONTEXT_DIR) | pbcopy

.PHONY: help
.DEFAULT_GOAL := help

help: Makefile
	echo
	echo " Choose a command run in "$(PROJECTNAME)":"
	echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	echo
