import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Landingpage from '../views/Landingpage.vue'
// import HomeContainer from '../views/HomeContainer.vue'
import Chatbot from '../views/Chatbot.vue'
// import ChatbotContainer from '../views/ChatbotContainer.vue'
import History from '../views/History.vue'

const router = createRouter({
  mode: 'history',
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'index',
      component: Landingpage,
    },
    // {
    //   path: '/homecontainer',
    //   name:'homecontainer',
    //   component: HomeContainer,
    // },
    {
      path: '/home',
      name: 'home',
      component: Home,
    },
    // {
    //   path: '/chatbotcontainer',
    //   name: 'chatbotcontainer',
    //   component: ChatbotContainer,
    // },
    {
      path:'/chatbot/:id/',
      name: 'chatbot',
      component: Chatbot,
    },
    {
      path: '/placeholder',
      name: 'placeholder',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/Placeholder.vue'),
    },
    {
      path: '/history',
      name: 'history',
      component: History,
    },
    // {
    //   path: '/chat/:id/',
    //   name: 'chat',
    //   component: ChatbotContainer,
    // }
  ],
})

export default router
