# Smart API Router - Unlimited Free Keys
param(
    [string]$Prompt,
    [int]$MaxRetries = 5
)

$APIs = @(
    @{ Name = "Groq-1"; Key = "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"; URL = "https://api.groq.com/openai/v1/chat/completions"; Model = "llama-3.3-70b-versatile" },
    @{ Name = "Ollama-Kimi"; Key = "1234"; URL = "http://127.0.0.1:11434/v1/chat/completions"; Model = "kimi-k2.5:cloud" },
    @{ Name = "Ollama-Qwen"; Key = "1234"; URL = "http://127.0.0.1:11434/v1/chat/completions"; Model = "qwen3:4b" },
    @{ Name = "MiniMax"; Key = "oauth"; URL = "https://api.minimax.io/anthropic"; Model = "MiniMax-M2.5" }
)

$Attempt = 0
$Success = $false

while ($Attempt -lt $MaxRetries -and -not $Success) {
    foreach ($API in $APIs | Get-Random -Count $APIs.Count) {
        try {
            Write-Host "Trying $($API.Name)..." -ForegroundColor Yellow
            
            $Body = @{
                model = $API.Model
                messages = @(@{ role = "user"; content = $Prompt })
                max_tokens = 4096
            } | ConvertTo-Json -Depth 10
            
            $Headers = @{ "Authorization" = "Bearer $($API.Key)"; "Content-Type" = "application/json" }
            
            $Response = Invoke-RestMethod -Uri $API.URL -Method Post -Body $Body -Headers $Headers -TimeoutSec 30
            
            Write-Host "✅ SUCCESS with $($API.Name)!" -ForegroundColor Green
            return $Response.choices[0].message.content
            
        } catch {
            Write-Host "❌ $($API.Name) failed: $($_.Exception.Message)" -ForegroundColor Red
            Start-Sleep -Milliseconds 100
        }
    }
    
    $Attempt++
    if (-not $Success) {
        Write-Host "Waiting before retry $Attempt..." -ForegroundColor Cyan
        Start-Sleep -Seconds 2
    }
}

throw "All APIs exhausted after $MaxRetries attempts"
