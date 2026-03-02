Get-ChildItem 'C:\Users\armoo\.openclaw\media\browser\' -Filter *.png | Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-60) } | Remove-Item -Force
