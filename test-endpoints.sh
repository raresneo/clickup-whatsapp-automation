#!/bin/bash

# Test endpoints
echo "🧪 Testing Endpoints..."

# Health check
echo ""
echo "1️⃣  Health Check:"
curl -s http://localhost:5000/health | jq .

# Dashboard
echo ""
echo "2️⃣  Dashboard:"
curl -s http://localhost:5000/dashboard | head -20

# Test webhook
echo ""
echo "3️⃣  Webhook Test:"
curl -X POST http://localhost:5000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "results": [
      {
        "from": "+44123456789",
        "text": {"body": "Test message"}
      }
    ]
  }' | jq .

# Test manual send
echo ""
echo "4️⃣  Manual Send Test:"
curl -X POST http://localhost:5000/send \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+44123456789",
    "message": "Test message from automation"
  }' | jq .

echo ""
echo "✅ Tests complete"
