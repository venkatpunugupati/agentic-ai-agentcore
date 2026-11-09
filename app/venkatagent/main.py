from bedrock_agentcore.runtime import BedrockAgentCoreApp

from agent import validate_question, build_system_message, make_plan, execute_plan

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload, context):
    question = payload.get("prompt", "")
    valid, reason = validate_question(question)
    if not valid:
        return {"message": f"Invalid input: {reason}"}

    messages = [build_system_message()]
    messages.append({"role": "user", "content": question})
    plan = make_plan(question)
    _results, final_answer = execute_plan(question, plan, messages)
    return {"message": final_answer}


if __name__ == "__main__":
    app.run()
