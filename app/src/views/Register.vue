<template>
    <ion-page>
      <!-- 頁首標題：註冊 -->
      <ion-header>
        <ion-toolbar color="primary">
          <ion-title>註冊</ion-title>
          <ion-button slot="start"  @click="goHome">
            <ion-icon :icon="home"></ion-icon>
          </ion-button>
        </ion-toolbar>
      </ion-header>
  
      <ion-content class="ion-padding">
        <!-- 註冊表單 -->
        <ion-list>
          <!-- 使用者名稱 -->
          <ion-item>
            <ion-label position="stacked">使用者名稱</ion-label>
            <ion-input v-model="username" placeholder="請輸入使用者名稱"></ion-input>
          </ion-item>

          <!-- 使用者暱稱 -->
          <ion-item>
            <ion-label position="stacked">使用者暱稱</ion-label>
            <ion-input v-model="nickname" placeholder="請輸入使用者暱稱"></ion-input>
          </ion-item>
  
          <!-- 密碼 -->
          <ion-item>
            <ion-label position="stacked">密碼</ion-label>
            <ion-input v-model="password" type="password" placeholder="請輸入密碼"></ion-input>
          </ion-item>
  
          <!-- 確認密碼 -->
          <ion-item>
            <ion-label position="stacked">確認密碼</ion-label>
            <ion-input v-model="confirmPassword" type="password" placeholder="請再次輸入密碼"></ion-input>
          </ion-item>
  
          <!-- 頭貼上傳 -->
          <ion-item>
            <ion-label>頭貼上傳</ion-label>
            <input type="file" accept="image/png, image/jpeg" @change="onFileChange" />
          </ion-item>
  
          <!-- 頭貼預覽 -->
          <ion-item v-if="previewUrl">
            <ion-label position="stacked">頭貼預覽</ion-label>
            <img
              :src="previewUrl"
              alt="Preview"
              style="width: 100px; height: 100px; margin-top: 8px;"
            />
          </ion-item>
        </ion-list>
  
        <!-- 顯示錯誤訊息 -->
        <ion-text color="danger" v-if="errorMessage">{{ errorMessage }}</ion-text>
        <!-- 顯示成功訊息 -->
        <ion-text color="success" v-if="successMessage">{{ successMessage }}</ion-text>
  
        <!-- 註冊按鈕 -->
        <ion-button expand="block" @click="handleRegister">註冊</ion-button>
  
        <!-- 登入連結 -->
        <div style="text-align: center; margin-top: 1em;">
          <a href="#" @click.prevent="$router.push('/login')">已有帳號？點此登入</a>
        </div>
      </ion-content>
    </ion-page>
  </template>
  
  <script>
  import { defineComponent } from 'vue';
  import {
    IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
    IonList, IonItem, IonLabel, IonInput, IonButton, IonText
  } from '@ionic/vue';
  import { home } from 'ionicons/icons';
  
  import api from '@/services/api.js';
  
  export default defineComponent({
    name: 'RegisterPage',
    components: {
      IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
      IonList, IonItem, IonLabel, IonInput, IonButton, IonText
    },
    data() {
      return {
        nickname: '',
        username: '',
        password: '',
        confirmPassword: '',
        avatarFile: null,  // 儲存使用者選擇的頭貼檔案
        previewUrl: '',    // 用於顯示上傳圖片的預覽
        errorMessage: '',
        successMessage: ''
      };
    },
    methods: {
      onFileChange(event) {
        const file = event.target.files[0];
        this.avatarFile = file || null;
        if (file) {
          this.previewUrl = URL.createObjectURL(file);
        } else {
          this.previewUrl = '';
        }
      },
      goHome() {
            router.push('/');
        },
  
      async handleRegister() {
        this.errorMessage = '';
        this.successMessage = '';
  
        // 檢查使用者基本輸入
        if (!this.username || !this.password || !this.confirmPassword) {
          this.errorMessage = '請填寫帳號、密碼與確認密碼';
          return;
        }

        // 檢查使用者暱稱
        if (!this.nickname) {
          this.errorMessage = '請填寫使用者暱稱';
          return;
        }

        // 檢查密碼是否一致
        if (this.password !== this.confirmPassword) {
          this.errorMessage = '密碼與確認密碼不相符';
          return;
        }
  
        try {
          // 1) 取得 reCAPTCHA token
          const recaptchaToken = await api.executeRecaptcha('register');
  
          // 2) 調用註冊 API，傳送帳號、密碼、頭貼 與 recaptchaToken
          await api.register(this.username, this.password, this.avatarFile, this.nickname,recaptchaToken);
  
          // 註冊成功，提示並導向登入頁面
          alert('註冊成功！請登入');
          this.$router.push('/login');
        } catch (error) {
            console.error(error);
            this.errorMessage = error.response.data.detail;
        }
      }
    }
  });
  </script>