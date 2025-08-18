import { isSpeechRecognitionSupported, createCantoneseRecognizer } from '@/assets/js/speech'
export default {
  name: 'SpeechMic',
  emits: ['result'],
  data() {
    return {
      isSpeechSupported: false,
      isListening: false,
      recognition: null,
    }
  },
  mounted() {
    this.isSpeechSupported = isSpeechRecognitionSupported();
    if (this.isSpeechSupported) {
      this.recognition = createCantoneseRecognizer({
        onStart: () => { this.isListening = true; },
        onEnd: () => { this.isListening = false; },
        onError: () => { this.isListening = false; },
        onResult: (transcript) => { this.$emit('result', transcript); },
      });
    }
  },
  beforeUnmount() {
    try { if (this.recognition && this.recognition.abort) this.recognition.abort(); } catch (e) {}
  },
  methods: {
    toggleMic() {
      if (!this.isSpeechSupported || !this.recognition) return;
      try {
        if (this.isListening) {
          this.recognition.stop();
        } else {
          this.recognition.start();
        }
      } catch (e) {}
    }
  }
}