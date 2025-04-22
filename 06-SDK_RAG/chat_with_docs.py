import os
from pathlib import Path
from opentelemetry import trace
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from config import ASSET_PATH, get_logger, enable_telemetry
from get_documents import get_documents
from azure.ai.inference.prompts import PromptTemplate
from azure.ai.evaluation import ContentSafetyEvaluator
import json
from dotenv import load_dotenv


# initialize logging and tracing objects
logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

load_dotenv("credentials.env", override=True)

# create a project client using environment variables loaded from the credentials.env file
project = AIProjectClient.from_connection_string(
    conn_str=os.environ["AIPROJECT_CONNECTION_STRING"], credential=DefaultAzureCredential()
)

# create a chat client we can use for testing
chat = project.inference.get_chat_completions_client()

@tracer.start_as_current_span(name="chat_with_docs")
def chat_with_docs(messages: list, context: dict = None) -> dict:
    if context is None:
        context = {}

    documents = get_documents(messages, context)

    # do a grounded chat call using the search results
    grounded_chat_prompt = PromptTemplate.from_prompty(Path(ASSET_PATH) / "grounded_chat.prompty")

    system_message = grounded_chat_prompt.create_messages(documents=documents, context=context)
    response = chat.complete(
        model=os.environ["CHAT_MODEL"],
        messages=system_message + messages,
        **grounded_chat_prompt.parameters,
    )
    #logger.info(f"Response: {response.choices[0].message}")

    # Return a chat protocol compliant response
    return {"message": response.choices[0].message, "context": context}

if __name__ == "__main__":
    print("RAG Chat. Write 'exit' to exit.\n")
    history = []

    import argparse

    # load command line arguments
    parser = argparse.ArgumentParser()
   
    parser.add_argument(
        "--enable-telemetry",
        action="store_true",
        help="Enable sending telemetry back to the project",
    )
    parser.add_argument(
        "--enable-evaluation",
        action="store_true",
        help="Enable content safety evaluation on responses",
    )
    args = parser.parse_args()
    if args.enable_telemetry:
        enable_telemetry(True)

    if args.enable_evaluation:
        evaluators = ["hate_unfairness", "sexual", "violence", "self_harm"]
        safety_evaluator = ContentSafetyEvaluator(azure_ai_project = project.scope,
                                            credential=DefaultAzureCredential())
        
    while True:
        user_input = input("You: ")
        if user_input.lower().strip() == "exit":
            print("Chat terminated!")
            break

        history.append({"role": "user", "content": user_input})
        try:
            response = chat_with_docs(messages=history)
            ai_message = response["message"]["content"]

            if args.enable_evaluation:
                safety_score = safety_evaluator(query = user_input, response = ai_message)
                logger.debug("🦺 Safety score:\n%s", json.dumps(safety_score, indent=4, ensure_ascii=False))
                for evaluator in evaluators:
                    if safety_score[evaluator] != "Very low":
                        ai_message = f"This response was blocked by the content safety evaluator"

            print(f"AI: {ai_message}\n")
            history.append({"role": "assistant", "content": ai_message})
        except Exception as e:
            print(f"An error occurred: {e}")