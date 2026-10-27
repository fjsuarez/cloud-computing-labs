import logging
import time

import azure.durable_functions as df
import azure.functions as func

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)

# Each chunk stands in for a slow call to another service: an API, a model, a database.
SECONDS_PER_CHUNK = 2


@app.route(route="ping", methods=["GET"])
def ping(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("pong\n")


@app.route(route="start/{orchestrator}", methods=["POST"])
@app.durable_client_input(client_name="client")
async def start(req: func.HttpRequest, client) -> func.HttpResponse:
    name = req.route_params["orchestrator"]
    chunks = int(req.params.get("chunks", "8"))
    instance_id = await client.start_new(name, client_input=chunks)
    logging.info("Started %s with %d chunks: %s", name, chunks, instance_id)
    return client.create_check_status_response(req, instance_id)


@app.orchestration_trigger(context_name="context")
def chain(context: df.DurableOrchestrationContext):
    chunks = context.get_input()
    logging.info("chain orchestrator running, replaying=%s", context.is_replaying)
    results = []
    for i in range(chunks):
        result = yield context.call_activity("work", i)
        results.append(result)
    return summarise(results)


@app.orchestration_trigger(context_name="context")
def fan_out(context: df.DurableOrchestrationContext):
    chunks = context.get_input()
    logging.info("fan_out orchestrator running, replaying=%s", context.is_replaying)
    tasks = [context.call_activity("work", i) for i in range(chunks)]
    results = yield context.task_all(tasks)
    return summarise(results)


@app.activity_trigger(input_name="chunk")
def work(chunk: int) -> dict:
    logging.info("work: chunk %d started", chunk)
    time.sleep(SECONDS_PER_CHUNK)
    logging.info("work: chunk %d finished", chunk)
    return {"chunk": chunk, "value": chunk * chunk}


def summarise(results: list[dict]) -> dict:
    return {"chunks": len(results), "total": sum(r["value"] for r in results)}
