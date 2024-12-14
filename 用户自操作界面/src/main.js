import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // 确保路径正确

createApp(App)
  .use(router) // 使用路由
  .mount('#app');