$lastEmailCount = 2
$logFile = 'C:\Users\armoo\.openclaw\workspace\mail_server_security_log.txt'

while ($true) {
    $output = @()
    $output += '--- Monitor Check: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' ---'
    
    # Check server process
    $proc = Get-Process -Id 24844 -ErrorAction SilentlyContinue
    if ($proc) {
        $output += '[OK] Mail server process running (PID 24844)'
    } else {
        $output += '[ALERT] Mail server process NOT FOUND!'
    }
    
    # Check connections
    $connections = Get-NetTCPConnection -LocalPort 2525,8888 -ErrorAction SilentlyContinue
    $output += '[INFO] Active connections:'
    foreach ($conn in $connections) {
        $remote = $conn.RemoteAddress
        $localAddr = $conn.LocalAddress
        $localPort = $conn.LocalPort
        $remotePort = $conn.RemotePort
        $state = $conn.State
        $output += "  $localAddr`:$localPort -> $remote`:$remotePort [$state]"
        
        # Check for external connections
        if ($remote -ne '0.0.0.0' -and $remote -ne '::' -and $remote -ne '127.0.0.1' -and $remote -ne '::1') {
            $output += "[ALERT] EXTERNAL CONNECTION DETECTED: $remote"
        }
    }
    
    # Check emails
    $emailsFile = 'C:\Users\armoo\.openclaw\workspace\skills\local-mail-server\emails.json'
    if (Test-Path $emailsFile) {
        $emails = Get-Content $emailsFile -Raw | ConvertFrom-Json
        $count = $emails.Count
        $output += "[INFO] Emails in inbox: $count"
        
        if ($count -gt $lastEmailCount) {
            $newCount = $count - $lastEmailCount
            $output += "[NEW EMAIL] $newCount new email(s) received!"
            $lastEmailCount = $count
            
            # Check latest email
            $latest = $emails[0]
            $output += "  From: $($latest.from)"
            $output += "  Subject: $($latest.subject)"
            $bodyLen = $latest.body.Length
            if ($bodyLen -gt 100) { $bodyLen = 100 }
            $bodyPreview = $latest.body.Substring(0, $bodyLen)
            $output += "  Body: $bodyPreview"
        }
    }
    
    # Log to file
    $output | Out-File -FilePath $logFile -Append
    
    Start-Sleep -Seconds 30
}
