#!/bin/bash

# Fix Docker Space Issues Script
# Run these commands to clean up Docker and free up space

echo "🧹 Cleaning up Docker to free space..."
echo ""

# 1. Stop all services first
echo "Stopping services..."
docker-compose -f docker/docker-compose.yml down

# 2. Clean up Docker system
echo ""
echo "🗑️  Removing unused Docker objects..."
docker system prune -af --volumes

# 3. Remove all stopped containers
echo ""
echo "🗑️  Removing stopped containers..."
docker container prune -f

# 4. Remove unused images
echo ""
echo "🗑️  Removing unused images..."
docker image prune -af

# 5. Remove unused volumes
echo ""
echo "🗑️  Removing unused volumes..."
docker volume prune -f

# 6. Remove build cache
echo ""
echo "🗑️  Removing build cache..."
docker builder prune -af

# 7. Check available space
echo ""
echo "📊 Current Docker disk usage:"
docker system df

echo ""
echo "💾 System disk space:"
df -h /

# 8. If on macOS, you might need to increase Docker Desktop's disk allocation
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "📱 On macOS? You may need to:"
    echo "   1. Open Docker Desktop"
    echo "   2. Go to Settings → Resources → Advanced"
    echo "   3. Increase 'Disk image size' (recommend 60GB+)"
    echo "   4. Click 'Apply & Restart'"
fi

echo ""
echo "✅ Cleanup complete! Try building again."