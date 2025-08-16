import Emoji from '@/components/Emoji.vue'
export default {
  components: {
    Emoji
  },
  props: {
    userID: Number,
  },
  emits: ['update-chat-list'],
  data: () => ({
    title: '新聊天',
    message: '',
    messages: [],
    status: 'Complete',
    streamingMsg: null,
    streamingTokens: [],
    isTypingStream: false,
    sseActive: false,
    typewriterDelayMs: 18,
    isEmojiOpen: false,
    charLimit: 100,
  }),
  created() {
    // Checks whether the chat id is changed.
    // If it changes, get the chat message list from server.
    this.$watch(
      () => this.$route.params.id,
      (newId, oldId) => {
        this.chatID = newId;
        this.message = '';
        this.messages = [];
        fetch('/chat-api/get-chat-message', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({chatID: this.chatID})
        })
        .then(response => response.json())
        .then(result => {
          this.title = result['title']
          this.messages = result['result'].map((row) => ({
            author: row['isUser'] ? 'student' : 'teacher',
            text: row['message'].replace(/(\r\n|\r|\n)/g, '<br/>'),
            createdAt: new Date(row['lastUpdated'])
          }));
        })
        .catch(error => console.error('Error obtaining chat: ', error));
        this.scrollToBottom();
      }
    )
  },
  /* this is the mounted function which is used to get the text from the home page and display it in the chatbot */
  async mounted() {
    this.chatID = this.$route.params.id;
    this.status = 'Pending'
    await fetch('/chat-api/get-chat-message', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({chatID: this.chatID})
    })
    .then(response => response.json())
    .then(result => {
      this.title = result['title'];
      this.messages = result['result'].map((row) => ({
        author: row['isUser'] ? 'student' : 'teacher',
        text: row['message'].replace(/(\r\n|\r|\n)/g, '<br/>'),
        createdAt: new Date(row['lastUpdated'])
      }));
      this.status = result['status'];
      this.scrollToBottom();
    })
    .catch(error => console.error('Error obtaining chat: ', error));
    if (this.$route.query.text) {
      this.message = this.$route.query.text;
      await this.sendMessage();
    }
    
  },
  methods: {
    toggleEmoji() {
      this.isEmojiOpen = !this.isEmojiOpen;
    },

    appendEmoji(emojiChar) {
      this.message = (this.message || '') + emojiChar;
      this.isEmojiOpen = false;
      this.$nextTick(() => {
        const ta = document.querySelector('.message-input');
        if (ta) ta.focus();
      });
    },
    /*
    scrollToBottom function is used to scroll the chat to the bottom
    to show the latest message
    */
    scrollToBottom() {
      this.$nextTick(() => {
        const chatBody = document.querySelector('.content-body');
        if (chatBody) {
          chatBody.scrollTop = chatBody.scrollHeight;
        }
      });
    },
    /*
    sendMessage function is used to send a message to the chatbot
    and the message will be pushed to the messages array
    and the message will be displayed in the chatbot
    */
    async sendMessage() {
      if (this.status === 'Pending' || this.isOverLimit || !this.message || !this.message.trim())
        return;
      this.$emit('update-chat-list');
      this.status = 'Pending';
      const message = this.message;
      this.messages.push({
        author: 'student',
        text: this.message,
        createdAt: new Date()
      });
      this.message = '';
      this.scrollToBottom();
      await fetch('/chat-api/send-message', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          chatID: this.chatID,
          message: message,
        })
      });

      // If the status is pending, we will wait for the server to send the response.
      // This is done in the loadMessage function.
      this.loadMessage();
      // Start streaming the response from the server.
    },

    // If there are pending messages, we wait to get the messages from server.
    loadMessage() {
      const evtSource = new EventSource(`/chat-api/send-message-response?chatID=${this.chatID}`);

      // Create a streaming message to show the user that the message is being processed.
      this.streamingMsg  = {
        author: 'teacher',
        text: '',
        createdAt: new Date()
      }
      this.streamingTokens = [];
      this.isTypingStream = false;
      this.sseActive = true;

      evtSource.onmessage = async (event) => {
        const chunk = JSON.parse(event.data);
        this.status = chunk.status;
        console.log('Received status:', this.status);
        const normalized = (chunk.text || '').replace(/(\r\n|\r|\n)/g, '<br/>');
        this.enqueueStreamText(normalized);
        if (chunk.status && chunk.status !== 'Loading') {
          this.sseActive = false;
          evtSource.close();
          this.maybeFinalizeStream();
          if (chunk.status === 'Pending') {
            // Start next segment after current finishes rendering
            const resumeAfter = () => {
              if (!this.isTypingStream) {
                this.loadMessage();
              } else {
                setTimeout(resumeAfter, 50);
              }
            };
            resumeAfter();
          }
        }
      };
      evtSource.onerror = (error) => {
        console.error('EventSource failed:', error);
        if (this.streamingMsg) {
          this.streamingMsg.text = 'There is an error in the server. Please try again later.';
          this.messages.push(this.streamingMsg);
        }
        this.streamingMsg = null;
        this.streamingTokens = [];
        this.isTypingStream = false;
        this.sseActive = false;
        evtSource.close();
      };
      // Wait for the EventSource to close.
    },
    enqueueStreamText(text) {
      if (!text) return;
      // Preserve <br/> as its own tokens, then tokenize each segment
      const parts = text.split(/(<br\/>)/);
      const tokens = [];
      for (const part of parts) {
        if (!part) continue;
        if (part === '<br/>') {
          tokens.push(part);
          continue;
        }
        if (/\s/.test(part)) {
          // Split by whitespace but keep whitespace tokens
          const wsTokens = part.split(/(\s+)/).filter(t => t.length > 0);
          tokens.push(...wsTokens);
        } else {
          // No whitespace (e.g., Chinese) -> split into characters
          tokens.push(...Array.from(part));
        }
      }
      this.streamingTokens.push(...tokens);
      if (!this.isTypingStream) {
        this.typewriterAppend();
      }
    },

    typewriterAppend() {
      if (!this.streamingMsg) return;
      const nextToken = this.streamingTokens.shift();
      if (nextToken !== undefined) {
        this.streamingMsg.text += nextToken;
        this.isTypingStream = true;
        this.scrollToBottom();
        setTimeout(() => this.typewriterAppend(), this.typewriterDelayMs);
      } else {
        this.isTypingStream = false;
        this.maybeFinalizeStream();
      }
    },

    maybeFinalizeStream() {
      // Finalize only when SSE ended and no tokens remain
      if (!this.sseActive && !this.isTypingStream && this.streamingTokens.length === 0 && this.streamingMsg) {
        this.messages.push(this.streamingMsg);
        this.streamingMsg = null;
        this.scrollToBottom();
      }
    },
  },
  computed: {
      // Messages that is sorted in ascending order by the creation time.
      // This will update upon when messages are sent.
      sortedMessages: {
          get() {
              return [...this.messages].sort((a, b) => a.createdAt - b.createdAt);
          }
      },
      currentLength() {
        return (this.message || '').length;
      },
      remainingChars() {
        return Math.max(0, this.charLimit - this.currentLength);
      },
      isOverLimit() {
        return this.currentLength > this.charLimit;
      },
      canSend() {
        return !this.isOverLimit && this.status !== 'Pending' && this.message && this.message.trim().length > 0;
      }
  }
};