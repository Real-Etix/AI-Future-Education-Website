import Sidebar from '@/components/Sidebar.vue'
export default{
components: {
    Sidebar
  },
  
  data:()=>({
        message:'',
        messages:[],
    }),
    /* this is the mounted function which is used to get the text from the home page and display it in the chatbot */
    mounted() {
      const text = this.$route.query.text;
      if (text) {
        this.messages.push({ text, author: 'student' });
      }
    },
    methods: {
          /*
          sendMessage function is used to send a message to the chatbot
          and the message will be pushed to the messages array
          and the message will be displayed in the chatbot
          */
        sendMessage() {
            if (this.message && this.message.trim()) {
                this.messages.push({
                    text: this.message,
                    author: 'student'
                });
                this.message = '';
            }
        }
    }
    } 

 