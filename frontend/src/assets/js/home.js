import storyList from '@/assets/display/storyList';
import valueList from '@/assets/display/valueList';
import consultList from '@/assets/display/consultList';
import Emoji from '@/components/Emoji.vue';
import Handwriting from '@/components/Handwriting.vue';
export default {
    components: { Emoji, Handwriting },
    props: {
        userID: Number,
    },
    data() {
        return {
            isShowing: 0,
            inputText: '',
            storyList: storyList,
            valueList: valueList,
            consultList: consultList,
            charLimit: 100,
            isSubmitting: false,
            isEmojiOpen: false,
            isHandwritingOpen: false,
        }
    },
    methods: {
        changeShowing(idx) {
            this.isShowing = idx;
        },
        onEmojiSelect(emojiChar) {
            this.inputText = (this.inputText || '') + emojiChar;
            this.isEmojiOpen = false;
        },
        onHandwritingSelect(text) {
            const next = (this.inputText || '') + text;
            this.inputText = next.length > this.charLimit ? next.slice(0, this.charLimit) : next;
        },
        async createChatByTopic() {
            if (this.isSubmitting || this.isOverLimit || !this.inputText || !this.inputText.trim()) {
                return;
            }
            this.isSubmitting = true;
            let chatID;
            try {
                await fetch('/chat-api/create-chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ 
                        method: 'main',
                        userID: this.userID,
                        name: this.inputText,
                    })
                })
                .then(response => response.json())
                .then(result => {
                    if (result['chatID']) {
                        chatID = result['chatID'];
                    } else return;
                })
                .catch(error => console.error('Error submitting data:', error));
                if (!chatID) return;
                this.$router.push({ name: 'chatbot', params: {id: chatID}, query: { text: this.inputText.trim() } });
            } finally {
                this.isSubmitting = false;
            }
        }
    },
    computed: {
        currentLength() {
            return (this.inputText || '').length;
        },
        remainingChars() {
            return Math.max(0, this.charLimit - this.currentLength);
        },
        isOverLimit() {
            return this.currentLength > this.charLimit;
        },
        canCreate() {
            return !this.isOverLimit && !this.isSubmitting && this.inputText && this.inputText.trim().length > 0;
        }
    }
};
