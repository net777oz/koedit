const puppeteer = require('puppeteer');
const { WebSocketServer } = require('ws');

const GAME_URL     = 'http://localhost:5005/emulator/?stream=true';
const WS_PORT      = 5174;
const TARGET_FPS   = 30;
const JPEG_QUALITY = 90;
const VIEWPORT     = { width: 1280, height: 960 };

let page = null;
let captureInterval = null;
const clients = new Set();

const wss = new WebSocketServer({ port: WS_PORT });
console.log('[Stream] WebSocket server started -> ws://0.0.0.0:' + WS_PORT);

wss.on('connection', (ws, req) => {
  const ip = req.socket.remoteAddress;
  console.log('[Stream] Client connected: ' + ip + ' (total: ' + wss.clients.size + ')');
  clients.add(ws);

  ws.on('message', async (raw) => {
    try {
      const msg = JSON.parse(raw.toString());
      if (msg.type === 'keydown') await page.keyboard.down(msg.key).catch(() => {});
      else if (msg.type === 'keyup') await page.keyboard.up(msg.key).catch(() => {});
      else if (msg.type === 'click') await page.mouse.click(msg.x, msg.y).catch(() => {});
    } catch (e) {}
  });

  ws.on('close', () => {
    clients.delete(ws);
    console.log('[Stream] Client disconnected. Remaining: ' + clients.size);
  });
  ws.on('error', () => clients.delete(ws));
});

// 오디오 브로드캐스트 함수
function broadcastAudio(audioData) {
  const buf = Buffer.from(audioData);
  // 바이너리 데이터 앞에 0x01 태그를 붙여 오디오임을 표시 (0x00은 비디오/JPEG)
  const taggedBuf = Buffer.concat([Buffer.from([0x01]), buf]);
  for (const ws of clients) {
    if (ws.readyState === 1) {
      ws.send(taggedBuf, { binary: true });
    }
  }
}

function startCapture() {
  if (captureInterval) clearTimeout(captureInterval);
  captureInterval = null;

  const minInterval = Math.floor(1000 / TARGET_FPS);
  let loopId = 0;
  startCapture._loopId = (startCapture._loopId || 0) + 1;
  const myId = startCapture._loopId;

  // 게임 캔버스 영역 캐시 (첫 캡처 시 한 번만 조회)
  let clipRect = null;

  async function captureLoop() {
    if (!page || startCapture._loopId !== myId) return;
    const t0 = Date.now();
    try {
      if (clients.size > 0) {
        const frame = await page.screenshot({
          type: 'jpeg',
          quality: JPEG_QUALITY,
          encoding: 'binary',
        });
        const buf = Buffer.isBuffer(frame) ? frame : Buffer.from(frame);
        const taggedBuf = Buffer.concat([Buffer.from([0x00]), buf]);
        for (const ws of clients) {
          if (ws.readyState === 1) {
            ws.send(taggedBuf, { binary: true }, (err) => {
              if (err) clients.delete(ws);
            });
          }
        }
      }
    } catch (e) {}
    if (startCapture._loopId !== myId) return;
    const elapsed = Date.now() - t0;
    const wait = clients.size > 0
      ? Math.max(0, minInterval - elapsed)
      : 500; // 클라이언트 없으면 500ms 대기
    captureInterval = setTimeout(captureLoop, wait);
  }

  captureLoop();
}

async function startBrowser() {
  console.log('[Stream] Starting headless Chromium with Audio Capture...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--autoplay-policy=no-user-gesture-required',
      '--window-size=' + VIEWPORT.width + ',' + VIEWPORT.height,
      '--audio-output-channels=2',
    ],
    defaultViewport: VIEWPORT,
  });

  page = await browser.newPage();

  page.on('error', err => console.log('[Browser Error] ' + err));
  page.on('pageerror', err => console.log('[Browser Page Error] ' + err));

  // 브라우저 내부 오디오 데이터를 Node.js로 전달하는 통로
  await page.exposeFunction('sendAudioToNode', (base64Data) => {
    try {
      const audioBuf = Buffer.from(base64Data, 'base64');
      broadcastAudio(audioBuf);
    } catch (e) {}
  });

  // 오디오 캡처 스크립트 주입 (심플 버전으로 롤백)
  await page.evaluateOnNewDocument(() => {
    const originalAudioContext = window.AudioContext || window.webkitAudioContext;
    if (!originalAudioContext) return;

    window.AudioContext = window.webkitAudioContext = function() {
      const ctx = new originalAudioContext();
      const processor = ctx.createScriptProcessor(4096, 2, 2);
      processor.onaudioprocess = (e) => {
        const left = e.inputBuffer.getChannelData(0);
        const right = e.inputBuffer.getChannelData(1);
        const int16 = new Int16Array(left.length * 2);
        for (let i = 0; i < left.length; i++) {
          int16[i * 2] = Math.max(-1, Math.min(1, left[i])) * 0x7FFF;
          int16[i * 2 + 1] = Math.max(-1, Math.min(1, right[i])) * 0x7FFF;
        }
        const base64 = btoa(String.fromCharCode(...new Uint8Array(int16.buffer)));
        window.sendAudioToNode(base64);
      };

      const oldConnect = AudioNode.prototype.connect;
      AudioNode.prototype.connect = function(dest) {
        if (dest === ctx.destination) {
          oldConnect.call(this, processor);
        }
        return oldConnect.apply(this, arguments);
      };
      
      processor.connect(ctx.destination);
      return ctx;
    };
  });

  page.on('console', (msg) => {
    if (msg.type() === 'error') console.log('[Browser Console] ' + msg.text());
  });

  page.on('crash', () => {
    console.error('[Stream] Page crashed! Restarting in 3s...');
    setTimeout(() => startBrowser(), 3000);
  });

  console.log('[Stream] Loading game page: ' + GAME_URL);
  await page.goto(GAME_URL, { waitUntil: 'networkidle2', timeout: 60000 });
  console.log('[Stream] Game loaded! Capture started.');
  startCapture();

  browser.on('disconnected', () => {
    console.error('[Stream] Browser disconnected. Restarting in 3s...');
    clearTimeout(captureInterval);
    page = null;
    setTimeout(() => startBrowser(), 3000);
  });
}

startBrowser().catch((err) => {
  console.error('[Stream] Failed to start browser:', err.message);
  process.exit(1);
});

process.on('SIGINT', () => {
  console.log('\n[Stream] Shutting down...');
  clearTimeout(captureInterval);
  wss.close();
  process.exit(0);
});
