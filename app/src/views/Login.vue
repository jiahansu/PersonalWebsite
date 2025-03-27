<template>
    <ion-page>
      <!-- 頁首標題：登入 -->
      <ion-header>
        <ion-toolbar color="primary">
          <ion-title>登入</ion-title>
        </ion-toolbar>
      </ion-header>
  
      <ion-content class="ion-padding">
        <!-- 登入表單 -->
        <ion-list>
          <ion-item>
            <ion-label position="stacked">使用者名稱</ion-label>
            <ion-input v-model="username" placeholder="請輸入使用者名稱" clear-input="true"></ion-input>
          </ion-item>
          <ion-item>
            <ion-label position="stacked">密碼</ion-label>
            <ion-input v-model="password" type="password" placeholder="請輸入密碼"></ion-input>
          </ion-item>
        </ion-list>
  
        <!-- 顯示錯誤訊息 -->
        <ion-text color="danger" v-if="errorMessage">{{ errorMessage }}</ion-text>
  
        <!-- 登入按鈕 -->
        <ion-button expand="block" @click="handleLogin">登入</ion-button>
  
        <!-- 註冊連結 -->
        <div style="text-align: center; margin-top: 1em;">
          <a href="#" @click.prevent="$router.push('/register')">沒有帳號？點此註冊</a>
        </div>
      </ion-content>
    </ion-page>
  </template>
  
  <script>
  import { defineComponent } from 'vue';
  import { 
    IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonList, 
    IonItem, IonLabel, IonInput, IonButton, IonText 
  } from '@ionic/vue';
  import api from '@/services/api.js';
  
  export default defineComponent({
    name: 'LoginPage',
    components: {
      IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
      IonList, IonItem, IonLabel, IonInput, IonButton, IonText
    },
    data() {
      return {
        username: '',
        password: '',
        errorMessage: ''
      };
    },
    methods: {
      async handleLogin() {
        this.errorMessage = '';
        if (!this.username || !this.password) {
          this.errorMessage = '請輸入帳號和密碼';
          return;
        }
  
        try {
          // 1) Call reCAPTCHA v3 to get a token
          const recaptchaToken = await api.executeRecaptcha('login'); 
          // 2) Send token with username/password to your API
          await api.login(this.username, this.password, recaptchaToken);
  
          // 登入成功後導向留言板頁面
          this.$router.push('/messages');
        } catch (error) {
          // 登入失敗處理
          switch(error.status){
            case 400:
              this.errorMessage = '偵測到異常行為，請稍後再試。';
              break;
            case 401:
              this.errorMessage = '登入失敗，請檢查帳號或密碼。';
              break;
            default:
                this.errorMessage = '伺服器異常，請稍後再試。';
          }
          console.error(error);
        }
      }
    }
  });
  </script>