# Check MiniMax redirect manually
$r = [System.Net.WebRequest]::Create("https://api.minimax.chat")
$r.AllowAutoRedirect = $false
try {
    $resp = $r.GetResponse()
    Write-Host "Status: $($resp.StatusCode)"
    Write-Host "Location: $($resp.GetResponseHeader('Location'))"
    $resp.Close()
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
