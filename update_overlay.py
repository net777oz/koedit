import os
content = r'''import { useEffect, useRef, useState } from 'preact/hooks';

const PALETTE = [
  [0x00, 0x00, 0x00],
  [0x00, 0xA2, 0x61],
  [0xD3, 0x41, 0x00],
  [0xF3, 0xA2, 0x61],
  [0x00, 0x41, 0xD3],
  [0x00, 0xA2, 0xF3],
  [0xD3, 0x61, 0xA2],
  [0xF3, 0xE3, 0xD3]
];

function quantize(data: Uint8ClampedArray) {
  const qData = new Uint8ClampedArray(data.length);
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i], g = data[i+1], b = data[i+2];
    let bestDist = 999999, bestIdx = 0;
    for (let p = 0; p < PALETTE.length; p++) {
      const pr = PALETTE[p][0], pg = PALETTE[p][1], pb = PALETTE[p][2];
      const dist = (r-pr)*(r-pr) + (g-pg)*(g-pg) + (b-pb)*(b-pb);
      if (dist < bestDist) { bestDist = dist; bestIdx = p; }
    }
    qData[i] = PALETTE[bestIdx][0];
    qData[i+1] = PALETTE[bestIdx][1];
    qData[i+2] = PALETTE[bestIdx][2];
    qData[i+3] = 255;
  }
  return qData;
}

function HoverImage({ id, ov, canvasInternalWidth, canvasInternalHeight, hasHover }: any) {
  const [hover, setHover] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [mountedOpacity, setMountedOpacity] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setMountedOpacity(1), 10);
    return () => clearTimeout(timer);
  }, []);

  const isLarge = id > 128;
  const actualId = isLarge ? id - 128 : id;
  const pngSrc = isLarge 
    ? /export/_hover.webp?v= 
    : /export/.png?v=;
  const gifSrc = isLarge ? null : (hasHover ? /export/_hover.webp?v= : null);

  const baseStyle = {
    position: 'absolute' as any,
    left: fullscreen ? '0%' : ${(ov.x / canvasInternalWidth) * 100}%,
    top: fullscreen ? '0%' : ${(ov.y / canvasInternalHeight) * 100}%,
    width: fullscreen ? '100%' : ${(ov.w / canvasInternalWidth) * 100}%,
    height: fullscreen ? '100%' : ${(ov.h / canvasInternalHeight) * 100}%,
    pointerEvents: 'auto' as any,
    transition: 'all 0.4s cubic-bezier(0.25, 1, 0.5, 1)',
    cursor: fullscreen ? 'zoom-out' : 'zoom-in',
    backgroundColor: fullscreen ? 'rgba(0,0,0,0.8)' : 'transparent',
    opacity: mountedOpacity,
    zIndex: fullscreen ? 9999 : 1,
    overflow: 'hidden'
  };

  return (
    <div 
      style={baseStyle}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onClick={() => setFullscreen(!fullscreen)}
    >
      <img src={pngSrc} style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'contain'}} />
      {gifSrc && (
        <img 
          src={gifSrc} 
          style={{
            position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'contain',
            opacity: hover ? 1 : 0,
            transition: 'opacity 0.3s ease-in-out'
          }} 
        />
      )}
    </div>
  );
}

export function PortraitOverlay({ canvasRef }: { canvasRef: preact.RefObject<HTMLCanvasElement> }) {
  const [overlays, setOverlays] = useState<{ id: number, x: number, y: number, w: number, h: number }[]>([]);
  const lastFoundRef = useRef<Map<number, {id: number, x: number, y: number, w: number, h: number, lastSeen: number}>>(new Map());
  const templatesRef = useRef<Map<number, { pixels: Uint8ClampedArray, sigs: {sx: number, sy: number, r: number, g: number, b: number}[] }>>(new Map());
  const [rect, setRect] = useState({ left: 0, top: 0, width: 0, height: 0 });
  const [idsWithHover, setIdsWithHover] = useState<Set<number>>(new Set());
  
  useEffect(() => {
    const fetchImageInfo = async () => {
      try {
        const res = await fetch(/api/images?v=);
        const data = await res.json();
        const hoverSet = new Set<number>();
        data.images.forEach((img: any) => {
          if (img.hover_url) hoverSet.add(img.id);
        });
        setIdsWithHover(hoverSet);
      } catch (e) {
        console.error('Failed to fetch image info', e);
      }
    };
    fetchImageInfo();

    const loadTemplates = async () => {
      for (let i = 1; i <= 128; i++) {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.src = /export/.png?v=;
        img.onload = () => {
          const cvs = document.createElement('canvas');
          cvs.width = 64; cvs.height = 80;
          const ctx = cvs.getContext('2d')!;
          ctx.drawImage(img, 0, 0, 64, 80);
          const rawPixels = ctx.getImageData(0, 0, 64, 80).data;
          const qPixels = quantize(rawPixels);
          const sigs = [];
          for (let py = 5; py < 75; py += 7) {
            for (let px = 5; px < 59; px += 7) {
              const idx = (py * 64 + px) * 4;
              const r = qPixels[idx], g = qPixels[idx+1], b = qPixels[idx+2];
              if (r + g + b > 50) {
                sigs.push({sx: px, sy: py, r, g, b});
                if (sigs.length >= 10) break;
              }
            }
            if (sigs.length >= 10) break;
          }
          templatesRef.current.set(i, { pixels: qPixels, sigs });
        };
      }
      for (let i = 129; i <= 256; i++) {
        const smallId = i - 128;
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.src = /export/_hover.webp?v=;
        img.onload = () => {
          const cvs = document.createElement('canvas');
          cvs.width = 128; cvs.height = 160;
          const ctx = cvs.getContext('2d')!;
          ctx.drawImage(img, 0, 0, 128, 160);
          const mCvs = document.createElement('canvas');
          mCvs.width = 64; mCvs.height = 80;
          mCvs.getContext('2d')!.drawImage(cvs, 0, 0, 64, 80);
          const raw = mCvs.getContext('2d')!.getImageData(0, 0, 64, 80).data;
          const qp = quantize(raw);
          const sigs = [];
          for (let py = 5; py < 75; py += 7) {
            for (let px = 5; px < 59; px += 7) {
              const idx = (py * 64 + px) * 4;
              const r = qp[idx], g = qp[idx+1], b = qp[idx+2];
              if (r + g + b > 50) {
                sigs.push({sx: px, sy: py, r, g, b});
                if (sigs.length >= 10) break;
              }
            }
            if (sigs.length >= 10) break;
          }
          templatesRef.current.set(i, { pixels: qp, sigs });
        };
      }
    };
    loadTemplates();

    const scanInterval = setInterval(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) return;
      const width = canvas.width, height = canvas.height;
      if (width === 0 || height === 0) return;
      
      setRect({ left: canvas.offsetLeft, top: canvas.offsetTop, width: canvas.clientWidth, height: canvas.clientHeight });
      const imgData = ctx.getImageData(0, 0, width, height);
      const data = imgData.data;
      const found = [];
      const templates = templatesRef.current;
      
      const STRIDE = 8;
      for (let y = 0; y < height - 80; y += STRIDE) {
        for (let x = 0; x < width - 64; x += STRIDE) {
          for (const [id, tData] of templates.entries()) {
            if (id > 128) continue;
            let diffs = 0;
            for (const sig of tData.sigs) {
              const sIdx = ((y + sig.sy) * width + (x + sig.sx)) * 4;
              if (Math.abs(data[sIdx] - sig.r) > 30 || Math.abs(data[sIdx+1] - sig.g) > 30 || Math.abs(data[sIdx+2] - sig.b) > 30) diffs++;
            }
            if (diffs <= 3) { 
              let sad = 0;
              for(let py = 0; py < 80; py += 4) {
                for(let px = 0; px < 64; px += 4) {
                  const sIdx = ((y + py) * width + (x + px)) * 4;
                  const tIdx = (py * 64 + px) * 4;
                  sad += Math.abs(data[sIdx] - tData.pixels[tIdx]) + Math.abs(data[sIdx+1] - tData.pixels[tIdx+1]) + Math.abs(data[sIdx+2] - tData.pixels[tIdx+2]);
                }
              }
              if (sad < 35000) found.push({ id, x, y, w: 64, h: 80 });
            }
          }
        }
      }

      for (let y = 10; y < height - 160; y += 10) {
        for (let x = 80; x < width - 128; x += 10) {
          for (const [id, tData] of templates.entries()) {
            if (id <= 128) continue;
            let diffs = 0;
            for (const sig of tData.sigs) {
              const sIdx = ((y + sig.sy * 2) * width + (x + sig.sx * 2)) * 4;
              if (Math.abs(data[sIdx] - sig.r) > 35 || Math.abs(data[sIdx+1] - sig.g) > 35 || Math.abs(data[sIdx+2] - sig.b) > 35) diffs++;
            }
            if (diffs <= 4) found.push({ id, x, y, w: 128, h: 160 });
          }
        }
      }
      
      const now = Date.now();
      const nextMap = new Map(lastFoundRef.current);
      found.forEach(f => nextMap.set(f.id, { ...f, lastSeen: now }));
      for (const [id, d] of nextMap.entries()) if (now - d.lastSeen > 1000) nextMap.delete(id);
      lastFoundRef.current = nextMap;
      setOverlays(Array.from(nextMap.values()));
    }, 200);
    return () => clearInterval(scanInterval);
  }, [canvasRef]);

  if (!canvasRef.current) return null;

  return (
    <div style={{ position: 'absolute', top: ${rect.top}px, left: ${rect.left}px, width: ${rect.width}px, height: ${rect.height}px, pointerEvents: 'none', zIndex: 100 }}>
      {overlays.map(ov => (
        <HoverImage key={ov.id} id={ov.id} ov={ov} canvasInternalWidth={canvasRef.current!.width || 640} canvasInternalHeight={canvasRef.current!.height || 480} hasHover={idsWithHover.has(ov.id)} />
      ))}
    </div>
  );
}
'''
with open('/home/net77/koedit/web_client/src/components/PortraitOverlay.tsx', 'w') as f:
    f.write(content)
