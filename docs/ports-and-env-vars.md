# Service Ports, LLM Configurations and Environment Variable Overrides

This table lists the default LLM configurations, along with the environment variables that can be used to override them.

| Service Name              | Default value     | Environment Variables Override | Notes
|---------------------------|-------------------|--------------------------------|-----------------------------------------------------------------------------------|
| RITS service API key      | None              | RITS_API_KEY                   | To use IBM RITS service as LLM Provider (https://github.ibm.com/rits/rits/)       |
| Watsonx API key           | None              | WATSONX_API_KEY                | To use IBM WatsonX service as LLM Provider (https://www.ibm.com/products/watsonx) |
| Watsonx Project ID        | None              | WATSONX_PROJECT_ID             | To use IBM WatsonX service as LLM Provider (https://www.ibm.com/products/watsonx) |
| Watsonx URL               | None              | WATSONX_URL                    | To use IBM WatsonX service as LLM Provider (https://www.ibm.com/products/watsonx) |

> These values are mandatory to be set by setting the corresponding environment variables in your deployment configuration.

This table lists the default MCP related configurations, along with the environment variables that can be used to override them.

| Service Name              | Default value     | Environment Variables Override | Notes
|---------------------------|-------------------|--------------------------------|-----------------------------------------------------------------------------------|
| MCP mode                  | False (disabled)  | BTA_MCP                        | Whether MCP (mode-context-protocol) is being used when serving agentic workloads  |
