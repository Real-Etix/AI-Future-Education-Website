// import Sidebar from '@/components/Sidebar.vue'
export default {
// components: {
//     Sidebar
//   },
  props: {
    userID: Number,
  },
  emits: ['update-chat-list'],
  data: () => ({
    title: '新聊天',
    message: '',
    messages: [],
    status: 'Complete'
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
      if (!this.message || !this.message.trim())
        return;
      this.$emit('update-chat-list');
      this.status = 'Pending'
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
      })
      .then(response => response.json())
      .then(result => {
        this.messages.push({
          author: 'teacher',
          text: result['message'].replace(/(\r\n|\r|\n)/g, '<br/>'),
          createdAt: new Date(result['createdAt'])
        });
        this.status = result['status'];
        this.scrollToBottom();
      })
      .catch(error => console.error('Error sending message: ', error));
      await this.loadingRemainingMessage()

    },

    // If there are pending messages, we wait to get the messages from server.
    async loadingRemainingMessage() {
      while (this.status == 'Pending') {
        await fetch('/chat-api/get-remaining-message', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({chatID: this.chatID})
        })
        .then(response => response.json())
        .then(result => {
          this.messages.push({
            author: 'teacher',
            text: result['message'].replace(/(\r\n|\r|\n)/g, '<br/>'),
            createdAt: new Date(result['createdAt'])
          });
            this.status = result['status'];
            this.scrollToBottom();
        })
        
      }
    }
  },
  computed: {
      // Messages that is sorted in ascending order by the creation time.
      // This will update upon when messages are sent.
      sortedMessages: {
          get() {
              return this.messages.sort((a, b) => a.createdAt - b.createdAt);
          }
      }
  }
};