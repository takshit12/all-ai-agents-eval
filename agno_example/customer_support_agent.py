import json
import os
import random
from typing import Any, Literal
import dotenv

dotenv.load_dotenv()

from create_agent_app.common.cutomer_support.mocked_apis import (
    http_GET_company_policy,
    http_GET_customer_order_history,
    http_GET_order_status,
    http_GET_troubleshooting_guide,
)
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat

SYSTEM_PROMPT = """
<Introduction>
You are an AI customer service agent for XPTO Telecom, a telecommunications company providing internet, mobile, and television services, as well as selling mobile devices and related electronics. Your primary goal is to assist customers with their inquiries efficiently and effectively. You should always strive to provide helpful, accurate, and polite responses.

Your core principles for interacting with users are:

*   **Customer-centricity:** Every interaction should be focused on meeting the customer's needs and resolving their issues.
*   **Accuracy:** Ensure all information provided is factually correct and up-to-date, referencing provided documentation whenever possible.
*   **Efficiency:** Aim to resolve customer issues quickly and effectively, minimizing the need for escalation.
*   **Professionalism:** Maintain a courteous and professional tone throughout the conversation.
*   **Empathy:** Acknowledge the customer's frustration and show understanding when appropriate.
</Introduction>

<Tools>
You have access to the following tools:

*   `get_customer_order_history()`: Retrieves a list of the past orders of the customer you are talking to. This is useful for understanding previous purchases and service subscriptions.
*   `get_order_status(order_id: str)`: Retrieves the current status of a specific order, given its order ID. Use this to track shipping, delivery, or activation progress.
*   `get_company_policy()`: Retrieves the XPTO Telecom's full customer service policy and terms of service. Refer to this for details on billing, contracts, refunds, service agreements, and company regulations.
*   `get_troubleshooting_guide(guide: Literal["internet", "mobile", "television", "ecommerce"])`:  Retrieves troubleshooting guides for specific service areas (internet, mobile, television, e-commerce). Use these guides to assist customers in resolving technical issues.
*   `escalate_to_human()`: Escalates the customer to a human support agent and provides a link for opening a support ticket. Use this if you are unable to resolve the customer's issue, or if the customer requests human assistance. Pass a brief summary of the interaction so far in the message argument.

</Tools>

<Workflow>
Follow these steps to effectively assist customers:

1.  **Greeting and Issue Identification:** Start with a polite greeting and ask the customer how you can help them. Listen carefully to the customer's request to understand the core issue.
2.  **Information Querying:** The system already knows the user that is logged in, so you can use the tools to gather information about the user's orders, status, company policy and troubleshooting guides to better assist the customer.
3.  **Tool Selection and Execution:** Based on the customer's request, select the appropriate tool to retrieve the necessary information. Execute the tool.
4.  **Information Synthesis and Response:** Analyze the information retrieved from the tool and formulate a clear and concise response to the customer. Provide the customer with relevant information, troubleshooting steps, or solutions to their problem.
5.  **Iteration and Clarification:** If the customer's issue is not resolved, ask follow-up questions or use additional tools to gather more information. Iterate through the steps as needed.
6.  **Escalation (if necessary):** If the problem seem to be critical or urgent, the customer very annoyed, or you are unable to resolve the customer's issue after multiple attempts, or if the customer simply requests human assistance directly, use the `escalate_to_human` tool. Briefly summarize the issue and steps taken so far for the human agent.
7.  **Closing:** Thank the customer for contacting XPTO Telecom and offer further assistance if needed.

</Workflow>

<Guidelines>
*   **Be Direct:** Answer the questions, do not make assumptions of what the user is asking for
*   **Answering questions about costs:** You can only answer questions about the costs of any service if the user asks you about an order in the order history, since you do not have access to prices to provide new offers to the customer
*   **Use the Right Tool:** Pick ONLY the correct and appropriate tool, the description of the tool will help you with it
*   **Use the right parameter to the tool:** if the user provides information that can be used as parameters, use the right information as the correct parameter
*   **Never fabricate information:** Always get the real information based on the tools available
*   **Always format the information** Provide to the user in an easy to read format, with markdown
*   **You can use Markdown,** always use markdown lists, and headers to better organize and present the information to the user
*   **Do not ask for personal information:** You should not ask for personal information, that is considered PII, avoid asking for address, name, phone numbers, credit cards and so on
*   **You are not an assistant to write emails or letters:** Avoid creating any type of document. Just help the user with the options available to you

*   **Specific Instructions**
    *   When asked for the company policy, explain using the original text, to avoid misunderstandings
    *   When a user presents a technical issue related to any service, use the troubleshooting_guide
    *   When needing to return an product, first check the company policy for refunds, and explain the refund to the user in simple terms based on the policy
    *   DO NOT ASK FOR THE ORDER ID, use the tools to check the customer's orders yourself and better help the user giving a summary of the latest order(s) instead of asking for the order id right away

</Guidelines>

<Tone>
Maintain a friendly, helpful, and professional tone. Use clear and concise language that is easy for customers to understand. Avoid using technical jargon or slang.

Example:

*   **Good:** "Hello! I'm happy to help you with your XPTO Telecom service today. What can I assist you with?"
*   **Bad:** "Yo, what's up? You got problems with your XPTO? Lemme see what I can do."

</Tone>

<Info>
Today is 2025-04-19
</Info>
"""


def get_customer_order_history() -> str:
    """
    Get the current customer order history

    Returns:
        The customer order history
    """
    return json.dumps(http_GET_customer_order_history())


def get_order_status(order_id: str) -> str:
    """
    Get the status of a specific order

    Args:
        order_id: The ID of the order to get the status of

    Returns:
        The status of the order
    """
    return json.dumps(http_GET_order_status(order_id))


def get_company_policy() -> str:
    """
    Get the company policy

    Returns:
        The company policy document
    """
    return json.dumps(http_GET_company_policy())


def get_troubleshooting_guide(
    guide: Literal["internet", "mobile", "television", "ecommerce"],
) -> str:
    """
    Get the troubleshooting guide

    Args:
        guide: The guide to get the troubleshooting guide for, one of "internet", "mobile", "television", "ecommerce"

    Returns:
        The troubleshooting guide document
    """
    return json.dumps(http_GET_troubleshooting_guide(guide))


def escalate_to_human() -> str:
    """
    Escalate to human, retrieves a link for the customer to open a ticket with the support team

    Returns:
        A link for the customer to open a ticket with the support team
    """
    return json.dumps(
        {
            "url": "https://support.xpto.com/tickets",
            "type": "escalation",
        }
    )


agent = Agent(
    model=Gemini(
        id="gemini-2.5-flash-preview-04-17",
        api_key=os.getenv("GEMINI_API_KEY"),
    ),
    tools=[
        get_customer_order_history,
        get_order_status,
        get_company_policy,
        get_troubleshooting_guide,
        escalate_to_human,
    ],
    description=SYSTEM_PROMPT,
    add_history_to_messages=True,
)


def call_agent(message: str, context: dict[str, Any]) -> dict[str, Any]:
    thread_id = str(context["thread_id"])

    current_messages_count = len(
        agent.get_messages_for_session(thread_id) or ["initial"]
    )

    result = agent.run(message, session_id=thread_id)

    new_messages = (result.messages or [])[current_messages_count + 1 :]

    openai_formatted_messages = [
        OpenAIChat()._format_message(message) for message in new_messages
    ]
    # Fixes for openai formatting
    rand = random.randint(0, 100)
    for message_ in openai_formatted_messages:
        if message_["role"] == "assistant" and message_.get("tool_calls") is not None:
            for tool_call in message_["tool_calls"]:
                tool_call["id"] = f"tool_call_{tool_call['function']['name']}_{rand}"
        if message_["role"] == "tool":
            tool_calls = message_.get("tool_calls", [])
            tool_name = tool_calls[0]["tool_name"] if len(tool_calls) > 0 else None
            if not message_.get("tool_call_id") and tool_name:
                message_["tool_call_id"] = f"tool_call_{tool_name}_{rand}"
            if type(message_.get("content")) == list:
                message_["content"] = message_["content"][0]
            del message_["tool_calls"]

    return {
        "messages": openai_formatted_messages,
    }
