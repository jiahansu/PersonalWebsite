// 使用 Ionic 提供的 Vue Router 套件
import { createRouter, createWebHistory } from '@ionic/vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Messages from '../views/Messages.vue';
import Profile from '../views/Profile.vue';
import AI from '../views/AI.vue';
import api from '@/services/api.js';
import UserList from '../views/UserList.vue';

const routes = [
  { path: '/', redirect: '/messages' },                // 預設導向個人自介頁面
  { path: '/login', component: Login},
  { path: '/register', component: Register },
  { path: '/messages', component: Messages, meta: { requiresAuth: true }  },
  { path: '/profile', component: Profile },
  { path: '/ai', component: AI },
  { path: '/users', component: UserList },
  // 捕捉未定義路徑，導向自介頁面或登入頁面
  { path: '/:pathMatch(.*)*', redirect: '/profile' }
];

const router = createRouter({
  history: createWebHistory(),  // 使用瀏覽器歷史模式
  routes
});

// ★ 全局導航守衛
router.beforeEach((to, from, next) => {
    // 檢查路由是否需要登入
    if (to.meta.requiresAuth) {
      // 檢查使用者是否已登入 (例如 localStorage 中有無 token)
    //   if (!api.isAuthorized()) {
    //     // 未登入 → 強制跳轉 login
    //     next({ path: '/login' });
    //   } else {
    //     // 已登入 → 允許進入
    //     next();
    //   }
      next();
    } else if(to.path === '/login' || to.path === '/register'){
      // 不需登入 → 允許直接進入
      if (api.isAuthorized()) {
        // 已登入 → 強制跳轉 messages
        next({ path: '/messages' });
      } else {
        // 未登入 → 允許進入
        next();
      }
    }else{
        next();
    }
  });

export default router;