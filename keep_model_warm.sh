#!/bin/bash
# Keep the model loaded in memory by sending periodic queries

echo "Starting model keep-alive script..."

while true; do
    echo "$(date): Sending keep-alive query..."
    curl -X POST http://localhost:8000/query \
        -H "Content-Type: application/json" \
        -d '{"query": "test", "top_k": 1}' \
        --max-time 10 \
        --silent --output /dev/null
    
    if [ $? -eq 0 ]; then
        echo "$(date): Keep-alive successful"
    else
        echo "$(date): Keep-alive failed"
    fi
    
    # Wait 5 minutes before next keep-alive
    sleep 300
done
