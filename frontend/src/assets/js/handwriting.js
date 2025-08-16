import '../../handwriting/handwriting.canvas.js'
export default {
  name: 'Handwriting',
  props: {
    language: { type: String, default: 'zh_TW' },
    numOfReturn: { type: Number, default: 5 },
    width: { type: Number, default: 300 },
    height: { type: Number, default: 300 }
  },
  emits: ['select', 'close'],
  data() {
    return {
      hw: null,
      candidates: [],
      dragging: false,
      dragStartX: 0,
      dragStartY: 0,
      panelStartLeft: 0,
      panelStartTop: 0,
      panelLeft: 0,
      panelTop: 0,
    }
  },
  mounted() {
    const cvs = this.$refs.canvas
    if (!cvs || !window.handwriting) return
    this.hw = new window.handwriting.Canvas(cvs)
    this.hw.setOptions({ language: this.language, numOfReturn: this.numOfReturn, width: this.width, height: this.height })
    this.hw.set_Undo_Redo(true, true)
    this.hw.setCallBack((res, err) => {
      if (err) return
      this.candidates = res || []
    })
    // center the panel
    this.$nextTick(() => {
      const panel = this.$refs.panel
      if (panel) {
        const rect = panel.getBoundingClientRect()
        const vw = window.innerWidth, vh = window.innerHeight
        this.panelLeft = Math.max(8, Math.round((vw - rect.width) / 2))
        this.panelTop = Math.max(8, Math.round((vh - rect.height) / 2))
      }
    })
  },
  beforeUnmount() {
    this.detachDrag()
  },
  methods: {
    recognize() { if (this.hw) this.hw.recognize() },
    erase() { if (this.hw) { this.hw.erase(); this.candidates = [] } },
    undo() { if (this.hw) this.hw.undo() },
    redo() { if (this.hw) this.hw.redo() },
    apply(text) {
      this.$emit('select', text)
      this.erase()
    },
    startDrag(e) {
      const point = e.touches ? e.touches[0] : e
      this.dragging = true
      this.dragStartX = point.clientX
      this.dragStartY = point.clientY
      this.panelStartLeft = this.panelLeft
      this.panelStartTop = this.panelTop
      window.addEventListener('mousemove', this.onDrag)
      window.addEventListener('mouseup', this.stopDrag)
      window.addEventListener('touchmove', this.onDrag, { passive: false })
      window.addEventListener('touchend', this.stopDrag)
    },
    onDrag(e) {
      if (!this.dragging) return
      const point = e.touches ? e.touches[0] : e
      if (e.cancelable) e.preventDefault()
      const dx = point.clientX - this.dragStartX
      const dy = point.clientY - this.dragStartY
      const panel = this.$refs.panel
      if (!panel) return
      const rect = panel.getBoundingClientRect()
      const vw = window.innerWidth, vh = window.innerHeight
      const newLeft = Math.min(vw - rect.width - 8, Math.max(8, this.panelStartLeft + dx))
      const newTop = Math.min(vh - rect.height - 8, Math.max(8, this.panelStartTop + dy))
      this.panelLeft = newLeft
      this.panelTop = newTop
    },
    stopDrag() {
      this.dragging = false
      this.detachDrag()
    },
    detachDrag() {
      window.removeEventListener('mousemove', this.onDrag)
      window.removeEventListener('mouseup', this.stopDrag)
      window.removeEventListener('touchmove', this.onDrag)
      window.removeEventListener('touchend', this.stopDrag)
    }
  }
}