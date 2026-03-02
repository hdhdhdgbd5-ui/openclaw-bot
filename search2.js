fetch('https://html.duckduckgo.com/html/?q=how+to+file+GDPR+claim+against+Meta+Facebook+compensation')
  .then(response => response.text())
  .then(data => console.log(data))
  .catch(err => console.error(err));