import chatList from "../display/chatList";
export default {
    data() {
        return {
            chatList: chatList
        }
    },
    computed: {
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