import chatList from "../display/chatList";
export default {
    props: ['head'],
    data() {
        return {
            historyExpanded: false,
            userMenuExpanded: false,
            id: 0, // Temp
            newChatName: '',
            chatList: chatList,
        }
    },
    methods: {
        toggleHistoryExpanded() {
            this.historyExpanded = !this.historyExpanded;
        },
        toggleUserMenuExpanded() {
            this.userMenuExpanded = !this.userMenuExpanded;
        },
        handleEnterPress() {
            if (!this.newChatName) {
                return;
            };
            this.chatList.push({
                id: 0,
                name: this.newChatName,
                link: './placeholder',
                lastUpdated: new Date(),
            });
            this.newChatName = '';
            this.id++;
        },
    },
    computed: {
        sortedChatList: {
            get() {
                return this.chatList.sort((a, b) => b.lastUpdated - a.lastUpdated);
            }
        }
    }
};