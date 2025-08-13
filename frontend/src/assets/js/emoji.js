import data from 'emoji-mart-vue-fast/data/all.json'
import { Picker, EmojiIndex } from 'emoji-mart-vue-fast/src'
import 'emoji-mart-vue-fast/css/emoji-mart.css'

const emojiIndex = new EmojiIndex(data)

export default {
  name: 'Emoji',
  components: { Picker },
  emits: ['select'],
  data() {
    return { emojiIndex }
  },
  methods: {
    onSelect(emoji) {
      this.$emit('select', emoji.native)
    }
  }
}