[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/FdNQOxlf)
# 565 Agent Starter Project - Template (Forkable)

This is a minimal, teachable agent skeleton for a computational social systems course.

## Quickstart
1) Create a virtual environment
2) Install dependencies:
   pip install -r requirements.txt
3) Copy env:
   cp .env.example .env
4) Run:
   python -m src.app

By default the agent uses a **mock LLM** so it runs without any API keys.
To connect a real model, edit `src/llm_provider.py`.

## What to edit for your project
- Role + purpose: `prompts/system.md`
- Style constraints: `prompts/style.md`
- Refusal behavior: `prompts/refusal.md`
- Policy rules: `config/policies.yaml`
- LLM integration: `src/llm_provider.py`

## Outputs
- Conversation + policy decisions are logged to `logs/agent.log`.

The base structure for your AI Agent.

## Project Structure
- **config/**: Configuration files (`agent.yaml`, `policies.yaml`).
- **prompts/**: System and style instructions for the LLM.
- **src/**: Core Python logic including memory and provider settings.
- **tests/**: Scripts for adversarial testing (Red Teaming).

## Assignment Tasks
Please refer to the course syllabus for specific implementation requirements for `memory.py` and `agent.py`.
