import storyList from '@/assets/display/storyList';
import valueList from '@/assets/display/valueList';
import consultList from '@/assets/display/consultList';
export default {
    props: {
        userID: Number,
    },
    data() {
        return {
            isShowing: 0,
            inputText: '',
            storyList: storyList,
            valueList: valueList,
            consultList: consultList
        }
    },
    methods: {
        changeShowing(idx) {
            this.isShowing = idx;
        },
        async createChatByTopic() {
            if (!this.inputText || !this.inputText.trim()) {
                return;
            }
            let chatID;
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
            // window.location.href = '/chatbot/' + chatID;
            this.$router.push({ name: 'chatbot', params: {id: chatID}, query: { text: this.inputText.trim() } });
        }
    }
};
