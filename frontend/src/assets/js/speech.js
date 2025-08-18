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