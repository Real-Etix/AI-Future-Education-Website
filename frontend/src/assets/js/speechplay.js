import { isSpeechSynthesisSupported, loadCantoneseVoice, speakCantonese, stopSpeaking } from '@/assets/js/speech'
export default {
  name: 'SpeechPlay',
  props: {
    html: { type: String, required: true },
    autoPrepare: { type: Boolean, default: true },
  },
  data() {
    return {
      isSupported: false,
      voice: null,
      voiceReady: false,
      isSpeaking: false,
    }
  },
  computed: {
    displayText() {
      return this.sanitizeTextForSpeech(this.html);
    }
  },
  async mounted() {
    this.isSupported = isSpeechSynthesisSupported();
    if (!this.isSupported) return;
    if (this.autoPrepare) {
      this.voice = await loadCantoneseVoice();
      this.voiceReady = !!this.voice;
    }
    document.addEventListener('visibilitychange', this.onVisibilityChange);
  },
  beforeUnmount() {
    try { stopSpeaking(); } catch (e) {}
    document.removeEventListener('visibilitychange', this.onVisibilityChange);
  },
  methods: {
    sanitizeTextForSpeech(input) {
      if (!input) return '';
      let text = String(input);
      text = text.replace(/<br\s*\/?>(\n|\r)?/gi, '\n');
      text = text.replace(/<[^>]*>/g, '');
      text = text.replace(/[\t ]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
      return text;
    },
    onVisibilityChange() {
      if (document.hidden && this.isSpeaking) {
        this.isSpeaking = false;
        stopSpeaking();
      }
    },
    async ensureVoice() {
      if (!this.voice) {
        this.voice = await loadCantoneseVoice();
        this.voiceReady = !!this.voice;
      }
    },
    async togglePlay() {
      if (!this.isSupported || !this.displayText) return;
      if (this.isSpeaking) {
        this.isSpeaking = false;
        stopSpeaking();
        return;
      }
      await this.ensureVoice();
      if (!this.voiceReady) return;
      const ok = speakCantonese({
        text: this.displayText,
        voice: this.voice,
        onStart: () => { this.isSpeaking = true; },
        onEnd: () => { this.isSpeaking = false; },
        onError: () => { this.isSpeaking = false; },
      });
      if (!ok) this.isSpeaking = false;
    }
  }
}