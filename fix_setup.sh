#!/bin/bash

# Complete fix for Docker build issues
set -e

echo "🔧 Fixing Docker build issues for LangGraph Flow..."
echo ""

# 1. Clean Docker first
echo "1️⃣ Cleaning Docker space..."
docker system prune -af --volumes
echo ""

# 2. Create optimized Dockerfile
echo "2️⃣ Creating optimized Dockerfile..."
cat > docker/Dockerfile.airflow << 'EOF'
# Optimized Dockerfile for Airflow with LangGraph
FROM apache/airflow:2.8.0-python3.11

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Set pip configuration
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install packages in batches to avoid space issues
# First, core packages that are already in constraints
RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.9 \
    redis==5.0.0 \
    python-dotenv==1.0.0 \
    pillow==10.0.0

# Install a minimal langchain setup
RUN pip install --no-cache-dir \
    langchain==0.1.0 \
    langsmith==0.0.83

# Copy requirements for runtime installation
COPY --chown=airflow:airflow requirements-runtime.txt /opt/airflow/

# Copy DAGs and plugins
COPY --chown=airflow:airflow ./airflow/dags /opt/airflow/dags/
COPY --chown=airflow:airflow ./airflow/plugins /opt/airflow/plugins/

# Set environment variables
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
ENV AIRFLOW__API__AUTH_BACKENDS='airflow.api.auth.backend.basic_auth'

# Create startup script
RUN echo '#!/bin/bash\n\
if [ ! -f /opt/airflow/.langgraph_installed ]; then\n\
    echo "Installing additional packages..."\n\
    pip install --no-cache-dir langgraph langfuse langchain-openai langchain-community\n\
    touch /opt/airflow/.langgraph_installed\n\
fi\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
EOF

# 3. Create runtime requirements
echo "3️⃣ Creating runtime requirements..."
cat > requirements-runtime.txt << 'EOF'
# Additional packages to install at runtime
langgraph
langfuse
langchain-openai
langchain-community
EOF

# 4. Create a simplified docker-compose with more resources
echo "4️⃣ Updating docker-compose configuration..."
# Add this to your docker-compose.yml under airflow services:
cat > docker/docker-compose.override.yml << 'EOF'
# Override file to increase resources
version: '3.8'

services:
  airflow-init:
    environment:
      DOCKER_BUILDKIT: 1
    deploy:
      resources:
        limits:
          memory: 4G
          
  airflow-webserver:
    deploy:
      resources:
        limits:
          memory: 2G
          
  airflow-scheduler:
    deploy:
      resources:
        limits:
          memory: 2G
          
  airflow-worker:
    deploy:
      resources:
        limits:
          memory: 2G
EOF

# 5. Alternative: Use pre-built image approach
echo "5️⃣ Creating alternative solution with pre-built image..."
cat > build_custom_image.sh << 'EOF'
#!/bin/bash
# Build custom Airflow image separately

# Create a temporary build directory
mkdir -p /tmp/airflow-build
cd /tmp/airflow-build

# Create Dockerfile
cat > Dockerfile << 'DOCKERFILE'
FROM apache/airflow:2.8.0-python3.11

USER root
RUN apt-get update && apt-get install -y gcc g++ python3-dev git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow

# Install only essential packages
RUN pip install --no-cache-dir \
    langchain \
    psycopg2-binary \
    redis \
    python-dotenv

# Environment
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
DOCKERFILE

# Build the image
docker build -t langgraph-airflow:latest .

# Clean up
cd -
rm -rf /tmp/airflow-build

echo "Custom image built successfully!"
EOF

chmod +x build_custom_image.sh

# 6. Update .env file to use less memory during build
echo "6️⃣ Optimizing Docker build settings..."
if ! grep -q "DOCKER_BUILDKIT" .env; then
    echo "" >> .env
    echo "# Docker build optimization" >> .env
    echo "DOCKER_BUILDKIT=1" >> .env
    echo "COMPOSE_DOCKER_CLI_BUILD=1" >> .env
fi

echo ""
echo "✅ Fixes applied! Now try one of these approaches:"
echo ""
echo "Option 1 - Use the optimized Dockerfile:"
echo "  ./setup.sh start"
echo ""
echo "Option 2 - Build custom image first:"
echo "  ./build_custom_image.sh"
echo "  # Then update docker-compose.yml to use 'langgraph-airflow:latest' instead of building"
echo ""
echo "Option 3 - If still having issues, install packages at runtime:"
echo "  # Start services with minimal packages"
echo "  docker-compose -f docker/docker-compose.yml up -d"
echo "  # Then install additional packages in running containers"
echo ""
echo "💡 Tips:"
echo "- Make sure Docker Desktop has at least 8GB RAM and 60GB disk allocated"
echo "- Run 'docker system df' to check space usage"
echo "- Consider using external volume mounts for large data"