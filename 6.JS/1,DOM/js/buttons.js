const button1 = document.getElementById("incButton");
const button2 = document.getElementById("decButton");

// 이벤트 핸들러
button1.addEventListener("click", () => {
  const view = document.getElementById("view");
  view.textContent = Number(view.textContent) + 1;
});

button2.addEventListener("click", () => {
  const view = document.getElementById("view");
  view.textContent = Number(view.textContent) - 1;
});
