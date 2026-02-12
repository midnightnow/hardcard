#!/bin/bash

echo "🏥 VetSorcery Status Check"
echo "========================"
echo

# Check services
echo "📊 Service Status:"
if curl -s http://localhost:8000/docs >/dev/null; then
    echo "✅ Backend API: Running"
else
    echo "❌ Backend API: Not responding"
fi

if curl -s http://localhost:5173 >/dev/null; then
    echo "✅ Frontend: Running"
else
    echo "❌ Frontend: Not responding"
fi

echo
echo "📋 Available API Modules:"
curl -s http://localhost:8000/openapi.json | jq -r '.paths | keys[]' | grep -o '/routes/api/[^/]*' | sort -u | sed 's|/routes/api/||' | while read module; do
    echo "  • $module"
done

echo
echo "🔐 Authentication Status:"
echo "  • Telehealth: Requires auth (401 responses)"
echo "  • Web Portal: Requires auth (401 responses)"
echo "  • Health: Should be public (if loaded)"

echo
echo "🌐 Access URLs:"
echo "  • Frontend: http://localhost:5173"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Telehealth: http://localhost:5173/telehealth"
echo "  • Client Portal: http://localhost:5173/web-portal"

echo
echo "📊 Demo Accounts:"
echo "  • Regular: john.doe@example.com"
echo "  • Demo: demo@vetsorcery.com"