import chatList from "../display/chatList";
export default {
    props: {
        head: String,
        userID: Number
    },
    data() {
        return {
            historyExpanded: false,
            userMenuExpanded: false,
            newChatName: '',
            chatList: chatList,
        }
    },
    mounted() {
        fetch('/chat-api/get-chat-list', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({userID: this.userID})
        })
        .then(response => response.json())
        .then(result => {
            this.chatList = result.map(
                (row) => ({
                    id: row['id'],
                    name: row['name'],
                    link: '/chat/' + row['id'],
                    lastUpdated: new Date(row['lastUpdated'])
                })
            );
        })
        .catch(error => console.error('Error submitting data:', error));
    },
    methods: {
        toggleHistoryExpanded() {
            this.historyExpanded = !this.historyExpanded;
        },
        toggleUserMenuExpanded() {
            this.userMenuExpanded = !this.userMenuExpanded;
        },
        // Create a chat without any context given
        async createChatBlank() {
            if (!this.newChatName) return;
            let chatID;
            await fetch('/chat-api/create-chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ 
                    method: 'blank',
                    userID: this.userID,
                    name: this.newChatName,
                })
            })
            .then(response => response.json())
            .then(result => {
                if (result['chatID']) {
                    chatID = result['chatID'];
                } else return;
            })
            .catch(error => console.error('Error submitting data:', error));
            this.chatList.push({
                id: chatID,
                name: this.newChatName,
                link: '/chat/' + chatID,
                lastUpdated: new Date(),
            });
            this.newChatName = '';
        },
    },
    computed: {
        // Sorted in desending order of last update time
        sortedChatList: {
            get() {
                return this.chatList.sort((a, b) => b.lastUpdated - a.lastUpdated);
            }
        }
    }
};