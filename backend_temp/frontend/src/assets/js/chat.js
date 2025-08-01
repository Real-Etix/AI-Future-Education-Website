export default {
    props: {
        userID: Number,
    },
    emits: ['temp-update-chat'],
    data() {
        return {
            chatTitle: '新聊天',
            chatID: 0,
            chatMessages: [],
            newMessage: '',
            status: 'Complete'
        }
    },
    created() {
        // Checks whether the chat id is changed.
        // If it changes, get the chat message list from server.
        this.$watch(
            () => this.$route.params.id,
            (newId, oldId) => {
                this.chatID = newId;
                this.chatMessages = [];
                this.newMessage = '';
                fetch('/chat-api/get-chat-message', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({chatID: this.chatID})
                })
                .then(response => response.json())
                .then(result => {
                    this.chatTitle = result['title']
                    this.chatMessages = result['result'].map(
                        (row) => ({
                            role: row['isUser'] ? 'User' : 'Assistant',
                            message: row['message'].replace(/(\r\n|\r|\n)/g, '<br/>'),
                            createdAt: new Date(row['lastUpdated'])
                        })
                    );
                })
                .catch(error => console.error('Error obtaining chat: ', error));
            }
        )
    },
    async mounted() {
        // Get the message list when the HTML element is mounted.
        this.chatID = this.$route.params.id;
        this.status = 'Pending'
        await fetch('/chat-api/get-chat-message', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({chatID: this.chatID})
        })
        .then(response => response.json())
        .then(result => {
            this.chatTitle = result['title'];
            this.chatMessages = result['result'].map(
                (row) => ({
                    role: row['isUser'] ? 'User' : 'Assistant',
                    message: row['message'].replace(/(\r\n|\r|\n)/g, '<br/>'),
                    createdAt: new Date(row['lastUpdated'])
                })
            );
            this.status = result['status'];
        })
        .catch(error => console.error('Error obtaining chat: ', error));
        await this.loadingRemainingMessage()
    },
    methods: {
        // Send messages to be handled to the server.
        async sendMessage() {
            if (!this.newMessage) return;
            this.$emit('temp-update-chat');
            this.status = 'Pending'
            const message = this.newMessage;
            this.newMessage = '';
            // Visualize the message first.
            this.chatMessages.push({
                role: 'User',
                message: message,
                createdAt: new Date()
            })
            // Push the message to the server, then obtain response from the server.
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
                this.chatMessages.push({
                    role: 'Assistant',
                    message: result['message'].replace(/(\r\n|\r|\n)/g, '<br/>'),
                    createdAt: new Date(result['createdAt'])
                });
                this.status = result['status'];
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
                    this.chatMessages.push({
                        role: 'Assistant',
                        message: result['message'].replace(/(\r\n|\r|\n)/g, '<br/>'),
                        createdAt: new Date(result['createdAt'])
                    });
                    this.status = result['status'];
                })
            }
        }
    },
    computed: {
        // Messages that is sorted in ascending order by the creation time.
        // This will update upon when messages are sent.
        sortedMessages: {
            get() {
                return this.chatMessages.sort((a, b) => a.createdAt - b.createdAt);
            }
        }
    }
};