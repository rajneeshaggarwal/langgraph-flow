# Ollama Integration for LangGraph Flow

This guide explains how to use Ollama as an LLM provider in LangGraph Flow.

## Overview

LangGraph Flow now supports multiple LLM providers:
- **Ollama**: For local, private LLM execution
- **OpenAI**: For cloud-based GPT models
- **Auto**: Automatically selects available provider (Ollama first, then OpenAI)

## Setup

### 1. Install Ollama

```bash
# Using the setup script
chmod +x scripts/setup_ollama.sh
./scripts/setup_ollama.sh

# Or manually
curl -fsSL https://ollama.ai/install.sh | sh