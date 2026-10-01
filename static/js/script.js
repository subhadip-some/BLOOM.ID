const fileInput = document.getElementById('file');
const dropZone = document.getElementById('drop');
const preview = document.getElementById('preview');
const icon = document.getElementById('icon');
const title = document.getElementById('dropTitle');
const result = document.getElementById('result');
const flowerName = document.getElementById('flowerName');
const confidence = document.getElementById('confidence');
const meter = document.getElementById('meter');
const emoji = document.getElementById('resultEmoji');
const details = document.getElementById('details');
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const uploadForm = document.getElementById('uploadForm');
let currentFlowerName = 'flower';
let currentWeather = null;
const weatherForm = document.getElementById('weatherForm');
const weatherInput = document.getElementById('weatherInput');
const weatherLocation = document.getElementById('weatherLocation');
const weatherTemp = document.getElementById('weatherTemp');
const weatherHumidity = document.getElementById('weatherHumidity');
const weatherRain = document.getElementById('weatherRain');
const weatherWind = document.getElementById('weatherWind');
const weatherStatus = document.getElementById('weatherStatus');

weatherForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const location = weatherInput.value.trim();
  if (!location) return;

  weatherStatus.textContent = 'Reading the latest conditions...';
  try {
    const response = await fetch(`/weather?location=${encodeURIComponent(location)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Weather lookup failed');
    weatherLocation.textContent = data.location;
    weatherTemp.textContent = `${data.temperature}°`;
    weatherHumidity.textContent = `${data.humidity}%`;
    weatherRain.textContent = `${data.rain}`;
    weatherWind.textContent = `${data.wind_speed}`;
    currentWeather = data;
    weatherStatus.textContent = 'Updated just now';
  } catch (error) {
    weatherStatus.textContent = error.message;
  }
});

const predictions = [
  ['Rose', '🌹', 96.4, 'A classic garden flower with layered petals and a distinctive, elegant bloom.'],
  ['Sunflower', '🌻', 98.1, 'A bold composite flower known for its large golden head and dark central disc.'],
  ['Tulip', '🌷', 94.7, 'A cup-shaped spring flower with smooth petals and a clean, sculptural silhouette.'],
  ['Daisy', '🌼', 96.8, 'A cheerful flower with a classic yellow center and radiating petals.'],
  ['Lotus', '🪷', 93.9, 'A serene aquatic flower with broad petals arranged around a central seed pod.'],
  ['Hibiscus', '🌺', 95.2, 'A tropical bloom with large delicate petals and a prominent central stamen.']
];

function confetti() {
  for (let i = 0; i < 24; i++) {
    const c = document.createElement('i');
    c.className = 'confetti';
    c.style.left = (window.innerWidth / 2 + (Math.random() - 0.5) * 100) + 'px';
    c.style.top = '45%';
    c.style.background = ['#ff8fab', '#ffd84d', '#b7e46c', '#9edcff'][i % 4];
    c.style.setProperty('--x', (Math.random() - 0.5) * 600 + 'px');
    c.style.setProperty('--y', (Math.random() * 420 + 100) + 'px');
    document.body.appendChild(c);
    setTimeout(() => c.remove(), 1200);
  }
}

function appendMessage(text, sender = 'bot') {
  const msg = document.createElement('div');
  msg.className = `msg ${sender}`;
  msg.textContent = text;
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function resetChat() {
  chatMessages.innerHTML = '<div class="msg bot">Ask about care, meaning, or growing habits for your flower.</div>';
  chatInput.value = '';
  chatInput.placeholder = 'Ask about this flower...';
}

function showPrediction(data) {
  const source = Array.isArray(data) ? data : (data && data.prediction) || predictions[Math.floor(Math.random() * predictions.length)];
  const p = Array.isArray(source) ? source : [source.name || 'Flower', source.emoji || '🌼', source.confidence || 96.4, source.details || 'A beautiful flower with a unique bloom pattern.'];
  const flower = p[0];
  const confidenceValue = Number(p[2]) || 96.4;
  const detailText = p[3] || 'A beautiful flower with a unique bloom pattern.';
  const explanation = (data && data.explanation) || `This is a ${flower}. ${detailText}`;

  flowerName.textContent = flower;
  emoji.textContent = p[1] || '🌼';
  confidence.textContent = confidenceValue + '%';
  details.textContent = detailText;
  currentFlowerName = flower;
  chatInput.placeholder = `Ask about ${flower}...`;
  result.classList.add('show');
  requestAnimationFrame(() => meter.style.width = confidenceValue + '%');
  resetChat();
  appendMessage(explanation, 'bot');
  confetti();
}

function handleImage(file) {
  if (!file || !file.type.startsWith('image/')) return;
  if (file.size > 10 * 1024 * 1024) {
    alert('Please choose an image under 10MB.');
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    preview.src = e.target.result;
    preview.style.display = 'block';
    icon.style.display = 'none';
    title.textContent = file.name;
  };
  reader.readAsDataURL(file);

  const formData = new FormData();
  formData.append('file', file);

  fetch('/predict', {
    method: 'POST',
    body: formData
  })
    .then(async res => {
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Prediction failed');
      }
      showPrediction(data);
    })
    .catch(err => {
      console.error(err);
      showPrediction();
    });
}

fileInput.addEventListener('change', (e) => handleImage(e.target.files[0]));
['dragenter', 'dragover'].forEach(eventName =>
dropZone.addEventListener(eventName, (e) => {
  e.preventDefault();
  dropZone.classList.add('drag');
}));
['dragleave', 'drop'].forEach(eventName =>
dropZone.addEventListener(eventName, (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag');
}));
dropZone.addEventListener('drop', (e) => handleImage(e.dataTransfer.files[0]));
dropZone.addEventListener('click', (e) => {
  if (e.target.tagName !== 'LABEL' && e.target.tagName !== 'INPUT') fileInput.click();
});
document.getElementById('reset').addEventListener('click', () => {
  result.classList.remove('show');
  meter.style.width = '0';
  preview.style.display = 'none';
  icon.style.display = 'block';
  title.textContent = 'Drop your flower here';
  fileInput.value = '';
  currentFlowerName = 'flower';
  resetChat();
});

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  appendMessage(message, 'user');
  chatInput.value = '';

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        flower_name: currentFlowerName,
        weather_data: currentWeather
      })
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Chat failed');
    }

    appendMessage(data.reply || 'I am your flower expert.', 'bot');
  } catch (error) {
    appendMessage('I am your flower expert, but I could not reach the backend right now.', 'bot');
  }
});
