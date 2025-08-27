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
          const absUrl = location.origin + js.url;
          const filename = js.url.split('/').pop();
          enableShareButtons(absUrl, filename);
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

// 처리 성공 시 호출되는 곳의 마지막에 결과 URL을 absUrl로 만들었다고 가정
// 예: const absUrl = location.origin + data.url;

const shareBandBtn = document.getElementById('shareBandBtn');
const shareKakaoBtn = document.getElementById('shareKakaoBtn');
const shareNativeBtn = document.getElementById('shareNativeBtn');
const copyLinkBtn   = document.getElementById('copyLinkBtn');
const makeYoutubeBtn= document.getElementById('makeYoutubeBtn');
const openStudioA   = document.getElementById('openStudio');

function enableShareButtons(absUrl, filename) {
  // 1) BAND 플러그인(본문에 링크가 들어간 공유창)
  shareBandBtn.disabled = false;
  shareBandBtn.onclick = () => {
    const text = `보이스투밴드 결과 🎵\n${absUrl}`;
    const route = location.hostname; // 허용 도메인
    const url = `https://band.us/plugin/share?body=${encodeURIComponent(text)}&route=${route}`;
    window.open(url, "share_band", "width=410,height=540");
  };

  // 2) 카카오톡 공유 (Kakao Link JS SDK)
  shareKakaoBtn.disabled = false;
  shareKakaoBtn.onclick = () => {
    Kakao.Share.sendDefault({
      objectType: 'feed',
      content: {
        title: 'Voice2Band 결과',
        description: '클릭하면 오디오 재생',
        imageUrl: location.origin + '/thumbnail.png', // 있으면 사용, 없으면 생략 가능
        link: { mobileWebUrl: absUrl, webUrl: absUrl }
      },
      buttons: [{ title: '듣기', link: { mobileWebUrl: absUrl, webUrl: absUrl } }]
    });
  };

  // 3) OS 공유시트(Web Share)
  shareNativeBtn.disabled = false;
  shareNativeBtn.onclick = async () => {
    if (navigator.share) {
      await navigator.share({ title: 'Voice2Band', text: '결과 듣기', url: absUrl });
    } else {
      alert('이 브라우저는 OS 공유시트를 지원하지 않습니다.');
    }
  };

  // 4) 링크 복사
  copyLinkBtn.disabled = false;
  copyLinkBtn.onclick = async () => {
    await navigator.clipboard.writeText(absUrl);
    alert('링크를 복사했어요!');
  };

  // 5) YouTube용 MP4 만들기 → Studio 열기
  if (filename) {
    makeYoutubeBtn.disabled = false;
    makeYoutubeBtn.onclick = async () => {
      const q = new URLSearchParams({ filename, title: 'Voice2Band Result' });
      const res = await fetch('/api/video/make?' + q.toString(), { method: 'POST' });
      const js = await res.json();
      if (js.ok) {
        // js.video_url: /api/static/xxx.mp4
        const vAbs = location.origin + js.video_url;
        // 다운로드/열기 안내 + Studio 버튼 표시
        openStudioA.style.display = '';
        openStudioA.focus();
        // 즉시 다운로드도 가능
        const a = document.createElement('a');
        a.href = vAbs; a.download = '';
        document.body.appendChild(a); a.click(); a.remove();
        alert('YouTube Studio에서 방금 내려받은 MP4를 업로드하세요!');
      } else {
        alert(js.error || 'MP4 생성 실패');
      }
    };
  }
}