##@ Development

test-e2e: ## Test end-to-end the agent service
	@$(MAKE) install_requirements
	pytest -s tests/e2e

lint: ## Lint the agent service
	@$(MAKE) install_requirements
	black --check --diff --color agents config fast_api llm utils || \
		(echo "Lint Failed. Please run 'black agents config fast_api llm utils' to fix the issues" && exit 1)