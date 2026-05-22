document.getElementById('submitBtn').addEventListener('click', function () {
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
      document.getElementById('input-title').value = '';
      document.getElementById('input-text').value = '';
      loadList();
    });
});

function loadList() {
  fetch('/list')
    .then((response) => response.json())
    .then((data) => {
      let cardList = document.getElementById('card-list');
      cardList.innerHTML = '';

      data.result.forEach(function (item) {
        let id = item[0];
        let title = item[1];
        let message = item[2];
        let card = document.createElement('div');
        card.id = `card-${id}`;
        card.innerHTML = `
        <div>
          <h2>${id}</h2>
          <h3>${title}</h3>
          <p>${message}</p>
          <button onclick="editBtn(${id}, '${title}', '${message}')">수정</button>
          <button onclick="deleteBtn(${id})">삭제</button>
        </div>
      `;
        cardList.appendChild(card);
      });
    });
}

loadList();

function deleteBtn(id) {
  fetch('/delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: id }),
  })
    .then((response) => response.json())
    .then((data) => {
      loadList();
    });
}

function editBtn(id, title, message) {
  let card = document.getElementById(`card-${id}`);
  card.innerHTML = `
    <div>
      <input id="modify-title-${id}" value="${title}" />
      <input id="modify-message-${id}" value="${message}" />
      <button onclick="modifyBtn(${id})">저장</button>
      <button onclick="loadList()">취소</button>
    </div>
  `;
}

function modifyBtn(id) {
  let newTitle = document.getElementById(`modify-title-${id}`).value;
  let newMessage = document.getElementById(`modify-message-${id}`).value;
  fetch('/modify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: id, title: newTitle, message: newMessage }),
  })
    .then((response) => response.json())
    .then((data) => {
      loadList();
    });
}
