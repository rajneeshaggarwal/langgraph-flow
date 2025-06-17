#!/bin/bash

# Quick start script
echo "🚀 Starting LangGraph Flow..."

# Run setup if needed
if [ ! -f ".env" ]; then
    ./setup.sh init
fi

# Start services
./setup.sh start
