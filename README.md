# agentic-ai-agentcore

A ReAct agent deployed as an AWS Bedrock AgentCore runtime (Python, HTTP). The agent plans a task into tool steps, executes them, and replans when the result says to — then returns a single final answer.

## The agent

Plan-and-execute pipeline: validate the question, make a plan, execute the plan's steps, and replan up to twice when a step's result calls for it. Each invoke starts with fresh history, and AgentCore Memory is off by default.

## Tools

| Tool | Description |
|---|---|
| `word_count(text)` | Counts the words in the given text. |
| `calculator(expression)` | Evaluates an arithmetic expression. |
| `get_current_time()` | Returns the current local date and time. |

Each tool declares its parameters in its docstring, so the model passes the declared argument names. Tool dispatch is defensive: a bad call becomes an Observation the agent can recover from, instead of crashing the run.

## Layout

- `app/venkatagent/` — the runtime: `main.py` (entrypoint, serves the AgentCore contract), `agent.py` (the agent), `pyproject.toml`
- `agentcore/` — AgentCore CLI configuration, the CDK stack (`agentcore/cdk/`), and the deployed-state binding (`agentcore/.cli/deployed-state.json`)

The runtime contract is port 8080, `POST /invocations`, `GET /ping`.

## Run locally

```bash
agentcore dev
```

This loads `.env.local` and runs the runtime on your machine. Requires Node 20.12+ and the AgentCore CLI (`npm install -g @aws/agentcore`).

## Deploy

```bash
agentcore build
agentcore deploy --target default
```

Region is `us-east-2`. The deploy creates the `AgentCore-venkatagent-default` stack. Dependencies are `bedrock-agentcore`, `aws-opentelemetry-distro`, and `openai`.

## Invoke

```bash
agentcore invoke --runtime venkatagent --payload '{"prompt": "Count the words in the quick brown fox jumps over the lazy dog, then multiply by 3"}'
```

The runtime returns `{"message": "27"}` for that question. An empty question returns `{"message": "Invalid input: Question cannot be empty."}`. You can also call `InvokeAgentRuntime` directly with boto3; in production, put API Gateway in front of the runtime.

## Configuration

The OpenAI key reaches the runtime through `envVars` in `agentcore/agentcore.json`. That file is gitignored and never committed — set it locally with `agentcore configure` or by editing your local copy.

## Notes

- The agent's history is per-invoke: nothing carries over between calls unless you add Memory.
- Telemetry is automatic on the runtime — traces and metrics land in CloudWatch with no code changes.
