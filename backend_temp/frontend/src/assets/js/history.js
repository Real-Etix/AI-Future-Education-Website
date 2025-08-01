export default {
    props: {
        userID: Number,
    },
    data() {
        return {
            chatList: []
        }
    },
    mounted() {
        // Obtain the chat list from server.
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
    computed: {
        // Obtain a dictionary of chat lists grouped in time.
        sortedChatList: {
            get() {
                const today = new Date();
                const todayDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
                const yesterdayDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 1);
                const sorted = [...this.chatList].sort((a, b) => b.lastUpdated - a.lastUpdated);
                return sorted.reduce((acc, item) => {
                    let comparingDate = new Date(
                        item.lastUpdated.getFullYear(), 
                        item.lastUpdated.getMonth(), 
                        item.lastUpdated.getDate()
                    );
                    let dateVisual;
                    // Change the visuals of the date based on last update date
                    // today -> 今日
                    // yesterday -> 昨日
                    // this year -> remove the year part
                    if (comparingDate.getTime() === todayDate.getTime()) {
                        dateVisual = '今日';
                    } else if (comparingDate.getTime() === yesterdayDate.getTime()) {
                        dateVisual = '昨日';
                    } else {
                        dateVisual = (item.lastUpdated.getFullYear() == new Date().getFullYear()) ? '' : item.lastUpdated.getFullYear() + '年';
                        dateVisual += item.lastUpdated.getMonth() + 1 + '月' + item.lastUpdated.getDate() + '日';
                    }
                    if (!acc[dateVisual]) {
                        acc[dateVisual] = [];
                    }
                    acc[dateVisual].push(item);
                    return acc;
                }, {});
            }
        }
    }
};