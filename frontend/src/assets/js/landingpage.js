export default {
    name: 'Homepage',
    methods: {
      goToChatbot() {
        this.$emit('show-sidebar');
        this.$router.push('/home');
      }
    }
  }

  