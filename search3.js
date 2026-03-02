fetch('https://html.duckduckgo.com/html/?q=TikTok+GDPR+fine+2024+how+to+claim+compensation')
  .then(response => response.text())
  .then(data => console.log(data))
  .catch(err => console.error(err));