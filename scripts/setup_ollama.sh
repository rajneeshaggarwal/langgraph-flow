#!/bin/bash

echo "🚀 Setting up Ollama for LangGraph Flow..."
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama is already installed"
fi

# Start Ollama service
echo "🔄 Starting Ollama service..."
ollama serve &

# Wait for service to start
sleep 5

# Pull default models
echo "📥 Pulling recommended models..."
echo "This may take a while depending on your internet connection..."

# Pull models
models=("llama2" "mistral" "nomic-embed-text")

for model in "${models[@]}"; do
    echo "Pulling $model..."
    ollama pull $model
done

echo ""
echo "✅ Ollama setup complete!"
echo ""
echo "Available models:"
ollama list
echo ""
echo "To pull additional models, use: ollama pull <model-name>"
echo "Popular models: codellama, neural-chat, starling-lm"