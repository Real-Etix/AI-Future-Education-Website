import storyList from '@/assets/display/storyList';
import valueList from '@/assets/display/valueList';
import consultList from '@/assets/display/consultList';
export default {
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
        goToChat() {
            if (this.inputText && this.inputText.trim()) {
                this.$router.push({ name: 'chatbotcontainer', query: { text: this.inputText.trim() } });
            }
        }
    }
};
