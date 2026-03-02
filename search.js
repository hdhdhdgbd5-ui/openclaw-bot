fetch('https://html.duckduckgo.com/html/?q=Meta+GDPR+fine+2023+how+to+claim+compensation')
  .then(response => response.text())
  .then(data => console.log(data))
  .catch(err => console.error(err));