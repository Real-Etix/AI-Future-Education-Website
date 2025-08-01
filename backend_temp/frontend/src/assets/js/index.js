import valueList from '@/assets/display/valueList';
import consultList from '@/assets/display/consultList';
export default {
    props: {
        userID: Number,
    },
    data() {
        return {
            isShowing: 0,
            storyList: [],
            valueList: valueList,
            consultList: consultList,
            newChatTopic: ''
        }
    },
    mounted() {
        // Obtain a list of stories to be shown on the main page for users to click on.
        fetch('/story-api/get-story-item-list', {
            method: 'GET',
        })
        .then(response => response.json())
        .then(result => {
            this.storyList = result.map(
                (row) => ({
                    id: row['id'],
                    title: row['title'],
                    img: row['img_link']
                })
            )
        }) 
        .catch(error => console.error('Error obtaining story list: ', error));
    },
    methods: {
        // Modify what items are shown
        changeShowing(idx) {
            this.isShowing = idx;
        },
        // Create chat based on what is inputted in text area.
        async createChatByTopic() {
            if (!this.newChatTopic) return;
            let chatID;
            await fetch('/chat-api/create-chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    method: 'main',
                    userID: this.userID,
                    name: this.newChatTopic,
                    message: this.newChatTopic,
                })
            })
            .then(response => response.json())
            .then(result => {
                if (result['chatID']) {
                    chatID = result['chatID'];
                } else return;
            })
            .catch(error => console.error('Error submitting data:', error));
            window.location.href = '/chat/' + chatID;
        },
        // Create a chat based on what story item is chosen on the main page.
        async createChatWithStory(storyID, title) {
            let chatID;
            await fetch('/chat-api/create-chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    method: 'story',
                    userID: this.userID,
                    name: title,
                    storyID: storyID
                })
            })
            .then(response => response.json())
            .then(result => {
                if (result['chatID']) {
                    chatID = result['chatID'];
                } else return;
            })
            .catch(error => console.error('Error submitting data:', error));
            window.location.href = '/chat/' + chatID;
        },
    }
};