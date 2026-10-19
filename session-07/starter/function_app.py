import json
import logging

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="hello", methods=["GET"])
def hello(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name", "world")
    return func.HttpResponse(f"Hello, {name}\n")


@app.route(route="orders", methods=["POST"])
@app.queue_output(arg_name="msg", queue_name="orders", connection="AzureWebJobsStorage")
def place_order(req: func.HttpRequest, msg: func.Out[str]) -> func.HttpResponse:
    try:
        order = req.get_json()
    except ValueError:
        return func.HttpResponse("Body must be JSON\n", status_code=400)
    msg.set(json.dumps(order))
    return func.HttpResponse("Accepted\n", status_code=202)


@app.queue_trigger(arg_name="msg", queue_name="orders", connection="AzureWebJobsStorage")
@app.blob_output(arg_name="receipt", path="receipts/{rand-guid}.json",
                 connection="AzureWebJobsStorage")
def process_order(msg: func.QueueMessage, receipt: func.Out[str]) -> None:
    order = json.loads(msg.get_body())
    total = order["qty"] * order["price"]
    logging.info("Order for %s: %.2f", order["item"], total)
    receipt.set(json.dumps({"order": order, "total": total,
                            "dequeue_count": msg.dequeue_count}))
