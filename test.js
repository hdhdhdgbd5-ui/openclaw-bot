fetch('https://api.ipify.org?format=json')
  .then(response => response.json())
  .then(data => console.log(JSON.stringify(data)))
  .catch(err => console.error(err));