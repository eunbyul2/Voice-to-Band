// app.js
const recBtn = document.getElementById('rec');
const stopBtn = document.getElementById('stop');
const player = document.getElementById('player');

let mediaRecorder;
let chunks = [];

recBtn.onclick = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    chunks = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) chunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      try {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const form = new FormData();
        form.append('file', blob, 'audio.webm');

        const pitch = document.getElementById('pitch').value;
        const stretch = document.getElementById('stretch').value;
        const query = `?pitch_semitones=${pitch}&time_stretch=${stretch}`;

        const res = await fetch('/api/process' + query, { method: 'POST', body: form });
        const js = await res.json();
        if (js.ok) {
          player.src = js.url;
          player.play().catch(() => {}); // 자동재생 차단 대응
        } else {
          alert(js.error || 'processing error');
        }
      } catch (err) {
        console.error(err);
        alert('업로드/처리 중 오류');
      }
    };

    mediaRecorder.start(250); // 250ms chunk
    recBtn.disabled = true;
    stopBtn.disabled = false;
  } catch (err) {
    console.error(err);
    alert('마이크 권한 또는 녹음 초기화 실패');
  }
};

stopBtn.onclick = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
  recBtn.disabled = false;
  stopBtn.disabled = true;
};