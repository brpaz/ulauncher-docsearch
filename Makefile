
EXT_NAME:=com.github.brpaz.ulauncher-docsearch
EXT_DIR:=$(shell pwd)

.PHONY: help lint format link unlink deps dev setup icons
.DEFAULT_GOAL := help

setup: ## Setups the project
	pre-commit install

lint: ## Run Pylint
	@flake8

format: ## Format code using yapf
	@yapf --in-place --recursive .

link: ## Symlink the project source directory with Ulauncher extensions dir.
	@ln -s ${EXT_DIR} ~/.local/share/ulauncher/extensions/${EXT_NAME}

unlink: ## Unlink extension from Ulauncher
	@rm -r ~/.local/share/ulauncher/extensions/${EXT_NAME}

deps: ## Install Python Dependencies
	@pip3 install -r requirements.txt

dev: ## Runs ulauncher on development mode
	ulauncher -v --dev --no-extensions  |& grep "docsearch"

icons: ## Optimize and resize documentation icons
	RESIZE_PARAM='128x128>'
	cd images/docs/
	find . -name "*.png" -exec convert -resize $(RESIZE_PARAM) -verbose {} {} \;

gen-docsets-keywords: ## Generates individual docsets keywords
	python scripts/gen-keywords.py

help: ## Show help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
