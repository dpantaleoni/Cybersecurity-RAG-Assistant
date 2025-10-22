#!/bin/bash
# Test queries for NCL RAG system

echo "Testing NCL RAG System..."
echo ""

API_URL="http://localhost:8000"

# Function to make query
query() {
    local question="$1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Q: $question"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    response=$(curl -s -X POST "$API_URL/query" \
      -H "Content-Type: application/json" \
      -d "{
        \"query\": \"$question\",
        \"top_k\": 3,
        \"return_sources\": false
      }")
    
    answer=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('answer', 'Error'))")
    time=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('response_time', 0))")
    
    echo "A: $answer"
    echo ""
    echo "Response time: ${time}s"
    echo ""
}

# Test queries
echo "Testing Cryptography Knowledge..."
query "What is a Caesar cipher and how do I decode it?"

echo ""
query "How can I crack RSA encryption in CTF challenges?"

echo ""
echo "Testing Web Exploitation Knowledge..."
query "What payloads should I try for SQL injection?"

echo ""
query "How do I find XSS vulnerabilities?"

echo ""
echo "Testing Network Analysis Knowledge..."
query "How do I extract files from a packet capture?"

echo ""
query "What Wireshark filters should I use to find credentials?"

echo ""
echo "Testing General CTF Knowledge..."
query "What tools should I use for password cracking?"

echo ""
echo "All tests complete!"

