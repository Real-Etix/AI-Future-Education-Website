import Sidebar from '@/components/Sidebar.vue';
import { useRoute } from 'vue-router';
export default {
    data() {
        return {
            userID: 1,
            renderSidebar: false,
            route: useRoute()
        }
    },
    components: {
        Sidebar
    },
    methods: {

        // Rerender the sidebar to update the sidebar list
        forceRerender() {
            this.renderSidebar = false;
            this.$nextTick(() => {
                this.renderSidebar = true;
            });
        }
    },
    computed: {
        isOnSpecificPage: {
            get() {
                return this.route.name === 'index';
            }
        }
    }
}