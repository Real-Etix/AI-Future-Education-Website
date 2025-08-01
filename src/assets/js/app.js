import Sidebar from '@/components/Sidebar.vue';
export default {
    data() {
        return {
            userID: 1,
            renderSidebar: false
        }
    },
    components: {
        Sidebar
    },
    methods: {
        // Load sidebar
        showSidebar() {
            this.renderSidebar = !this.renderSidebar;
        },

        // Rerender the sidebar to update the sidebar list
        forceRerender() {
            this.renderSidebar = false;
            this.$nextTick(() => {
                this.renderSidebar = true;
            });
        }
    }
}