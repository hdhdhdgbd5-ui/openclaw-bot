$body = @{
    model = "cognitivecomputations/dolphin3.0-r1-mistral-24b:free"
    messages = @(
        @{
            role = "user"
            content = "Hello, how are you?"
        }
    )
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "https://openrouter.ai/api/v1/chat/completions" -Method Post -Body $body -ContentType "application/json" -Headers @{"Authorization" = "Bearer sk-or-v1-0000000000000000000000000000000000000000000000000000000000000000"}

$result | ConvertTo-Json -Depth 5
