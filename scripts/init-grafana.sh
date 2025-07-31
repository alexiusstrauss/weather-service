#!/bin/bash

# Script para inicializar o Grafana com dados e garantir que as queries sejam executadas

echo "🚀 Initializing Grafana with sample data..."

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Make some sample requests to generate data
echo "📊 Generating sample data..."

# Sample weather requests to different cities
cities=("São Paulo" "Rio de Janeiro" "Belo Horizonte" "Salvador" "Fortaleza")

for city in "${cities[@]}"; do
    echo "🌤️  Making request for $city..."
    curl -s "http://localhost:8000/api/v1/weather/?city=$city" > /dev/null || true
    sleep 1
done

# Make some cached requests
echo "🔄 Making cached requests..."
for city in "${cities[@]}"; do
    echo "💾 Making cached request for $city..."
    curl -s "http://localhost:8000/api/v1/weather/?city=$city" > /dev/null || true
    sleep 0.5
done

# Make requests to trigger rate limiting
echo "⚡ Testing rate limiting..."
for i in {1..10}; do
    curl -s "http://localhost:8000/api/v1/weather/?city=São Paulo" > /dev/null || true
    sleep 0.1
done

echo "✅ Sample data generated successfully!"
echo "🎯 Grafana should now have data to display in dashboards"
echo "🌐 Access Grafana at: http://localhost:3000"
echo "👤 Login: admin / admin"
