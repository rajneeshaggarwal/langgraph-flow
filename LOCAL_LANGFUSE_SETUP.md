# Local LangFuse Setup Guide

This guide walks you through setting up LangFuse locally for the LangGraph Flow project.

## Quick Start

```bash
# 1. Run the setup script
chmod +x scripts/setup_langfuse.sh
./scripts/setup_langfuse.sh

# 2. Start services (if not already running)
make langfuse-start

# 3. Access LangFuse UI
open http://localhost:3001