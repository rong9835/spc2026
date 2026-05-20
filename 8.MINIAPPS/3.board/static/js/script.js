document.getElementById('submitBtn').addEventListener('click', function () {
  console.log('버튼눌림');
  let title = document.getElementById('input-title').value;
  let message = document.getElementById('input-text').value;

  fetch('/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title: title, message: message }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log('서버 응답:', data);
      loadList();
    });
});

function loadList() {
  fetch('/list')
    .then((response) => response.json())

    .then((data) => {
      console.log(data);
      let cardList = document.getElementById('card-list');
      cardList.innerHTML = '';

      data.result.forEach(function (item) {
        let id = item[0];
        let title = item[1];
        let message = item[2];
        let card = document.createElement('div');
        card.innerHTML = `
        <div>
          <h2>${id}<h2>
          <h3>${title}</h3>
          <p>${message}</p>
        </div>
      `;
        cardList.appendChild(card);
      });
    });
}

loadList();
