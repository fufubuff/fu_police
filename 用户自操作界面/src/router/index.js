// router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import UploadAndAI from '../components/uploadandai.vue';
import DataDisplay from '../components/datadisplay.vue';

const routes = [
  {
    path: '/',
    name: 'UploadAndAI',
    component: UploadAndAI
  },
  {
    path: '/data',
    name: 'DataDisplay',
    component: DataDisplay
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;