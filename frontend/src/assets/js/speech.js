export function isSpeechRecognitionSupported() {
  if (typeof window === 'undefined') return false;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  return typeof SpeechRecognition === 'function';
}

export function createCantoneseRecognizer({ onResult, onError, onStart, onEnd } = {}) {
  if (typeof window === 'undefined') return null;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return null;

  const recognition = new SpeechRecognition();
  
  recognition.lang = 'yue-HK';
  recognition.interimResults = false;
  recognition.continuous = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => { if (onStart) onStart(); };
  recognition.onerror = (event) => { if (onError) onError(event); };
  recognition.onend = () => { if (onEnd) onEnd(); };
  recognition.onresult = (event) => {
    let finalTranscript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const res = event.results[i];
      if (res.isFinal && res[0]) {
        finalTranscript += res[0].transcript;
      }
    }
    if (finalTranscript && onResult) onResult(finalTranscript);
  };

  return recognition;
}

// --- Web Speech Synthesis helpers ---
export function isSpeechSynthesisSupported() {
  if (typeof window === 'undefined') return false;
  return typeof window.speechSynthesis !== 'undefined' && typeof window.SpeechSynthesisUtterance !== 'undefined';
}

export function loadCantoneseVoice(timeoutMs = 2000) {
  if (typeof window === 'undefined' || !isSpeechSynthesisSupported()) return Promise.resolve(null);
  const synth = window.speechSynthesis;

  function pickVoice(voices) {
    if (!voices || voices.length === 0) return null;
    const byScore = (v) => {
      const lang = (v.lang || '').toLowerCase();
      if (lang.includes('yue') && lang.includes('hk')) return 5; // yue-HK
      if (lang === 'yue-hk') return 5;
      if (lang === 'zh-hk') return 4;
      if (lang.includes('zh') && lang.includes('hk')) return 3;
      if (lang.includes('yue')) return 2;
      if (lang.startsWith('zh')) return 1;
      return 0;
    };
    const sorted = [...voices].sort((a, b) => byScore(b) - byScore(a));
    return sorted[0] || null;
  }

  const immediate = pickVoice(synth.getVoices());
  if (immediate) return Promise.resolve(immediate);

  return new Promise((resolve) => {
    const onVoices = () => {
      const v = pickVoice(synth.getVoices());
      if (v) {
        synth.removeEventListener('voiceschanged', onVoices);
        resolve(v);
      }
    };
    synth.addEventListener('voiceschanged', onVoices);
    setTimeout(() => {
      synth.removeEventListener('voiceschanged', onVoices);
      resolve(pickVoice(synth.getVoices()));
    }, timeoutMs);
    synth.getVoices();
  });
}

export function speakCantonese({ text, voice, rate = 1, pitch = 1, onStart, onEnd, onError } = {}) {
  if (!isSpeechSynthesisSupported()) return false;
  const synth = window.speechSynthesis;
  try { synth.cancel(); } catch (e) {}
  const utterance = new window.SpeechSynthesisUtterance(text || '');
  if (voice) utterance.voice = voice;
  utterance.lang = (voice && voice.lang) ? voice.lang : 'yue-HK';
  utterance.rate = rate;
  utterance.pitch = pitch;
  if (onStart) utterance.onstart = onStart;
  if (onEnd) utterance.onend = onEnd;
  if (onError) utterance.onerror = onError;
  synth.speak(utterance);
  return true;
}

export function stopSpeaking() {
  if (!isSpeechSynthesisSupported()) return;
  try { window.speechSynthesis.cancel(); } catch (e) {}
} 