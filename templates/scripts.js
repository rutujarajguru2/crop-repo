const chatButton = document.getElementById('toggleChat');
const chatFrame = document.querySelector('.chatFrame');

let isChatOpen = false;

chatButton.addEventListener('click', () => {
  if (!isChatOpen) {
    chatFrame.style.display = 'block';
    isChatOpen = true;
  } else {
    chatFrame.style.display = 'none';
    isChatOpen = false;
  }
});
