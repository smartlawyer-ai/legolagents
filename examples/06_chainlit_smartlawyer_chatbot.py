"""
Example 6 — A French legal research chatbot in ~15 lines
══════════════════════════════════════════════════════════

This is the point of legolagents: bolt a rigorous legal reasoning
strategy (temporal validity checks, citation graph traversal, certainty
levels) onto any chat UI, in a handful of lines — here, Chainlit.

No custom prompt engineering, no manual tool wiring: SmartLawyer MCP
supplies the 13 Legal Graph tools, LegalResearchAgent supplies the
reasoning strategy, Chainlit supplies the chat UI.

Prerequisites:
    pip install legolagents 'smolagents[mcp]' chainlit

    export SMARTLAWYER_API_KEY=sk-sl-your-key   # https://smartlawyer.ai
    export ANTHROPIC_API_KEY=your-key

Run:
    chainlit run 06_chainlit_smartlawyer_chatbot.py
"""

import os

import chainlit as cl
from legolagents import LegalResearchAgent
from legolagents.mcp import SmartLawyerCorpus
from smolagents import LiteLLMModel

model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")


@cl.on_chat_start
async def start_chat():
    corpus = SmartLawyerCorpus(api_key=os.environ["SMARTLAWYER_API_KEY"])
    corpus.__enter__()  # kept open for the session, closed in on_chat_end
    cl.user_session.set("corpus", corpus)
    cl.user_session.set("agent", LegalResearchAgent(corpus=corpus, model=model))
    await cl.Message(content="Ask me anything about French case law.").send()


@cl.on_message
async def handle_message(message: cl.Message):
    agent = cl.user_session.get("agent")
    result = await cl.make_async(agent.run)(message.content)
    await cl.Message(content=str(result)).send()


@cl.on_chat_end
def end_chat():
    corpus = cl.user_session.get("corpus")
    if corpus:
        corpus.__exit__(None, None, None)


# That's it. Ask it something like:
#   "Is decision 17-19.860 still valid?"
#   "What are the landmark decisions on wrongful termination?"
# and it answers with ✅/⚡/⚠️/❌ certainty levels, checking validity and
# walking the citation graph automatically — not just keyword-matching.
