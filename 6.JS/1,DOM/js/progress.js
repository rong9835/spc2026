let interval;
let timerId;
const timeInput = document.getElementById('timeInput');
const progress = document.getElementById('progress');
const progressText = document.getElementById('progressText');
const startButton = document.getElementById('startButton');
const clearButton = document.getElementById('clearButton');

startButton.addEventListener('click', startProgress);
clearButton.addEventListener('click', clearProgress);

//모듈화 고려해볼것..
function startProgress() {
  const duration = parseInt(timeInput.value);
  console.log('입력초 :', duration);
  startButton.disabled = true;

  let elapsed = 0; //초과시간
  interval = setInterval(() => {
    // console.log('반복호출');
    elapsed++;
    const ratio = Math.floor((elapsed / duration) * 100); //진행율 계산
    progress.style.width = `${ratio}%`; //ratio + %
    progressText.textContent = `${ratio}%`;
    console.log(progress);

    if (ratio >= 100) {
      //타이머 중지
      clearInterval(interval);
      startButton.disabled = false;
    }
  }, 1000);
}

function clearProgress() {
  clearInterval(interval);
  progress.style.width = '2px';
  timeInput.value = '';
  progressText.textContent = '0%';
}
