<template>
    <ion-page>
      <!-- 頁首標題：關於本站/個人自介 -->
      <ion-header>
        <ion-toolbar color="primary">
          <ion-title>個人自介</ion-title>
        </ion-toolbar>
      </ion-header>
  
      <ion-content class="ion-padding">
        <!-- 個人簡介卡片 -->
        <ion-card>
          <ion-card-header>
            <ion-card-title>網站主人</ion-card-title>
          </ion-card-header>
          <ion-card-content>
            <!-- 主人頭貼 -->
            <ion-avatar style="width: 100px; height: 100px; margin-bottom: 16px;">
              <!-- 範例圖片，可替換為實際圖片路徑 -->
              <img src="https://via.placeholder.com/100" alt="Profile Picture">
            </ion-avatar>
            <!-- 簡介文字 -->
            <p>您好，我是本站的站長！這是一個使用 Ionic + Vue 打造的簡易網站，提供使用者註冊登入、留言板功能，以及將 AI 文字轉換為程式碼的服務。歡迎體驗！</p>
          </ion-card-content>
        </ion-card>
      </ion-content>
    </ion-page>
  </template>
  
  <script>
  import { defineComponent } from 'vue';
  import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonCard, IonCardHeader, IonCardTitle, IonCardContent, IonAvatar } from '@ionic/vue';
  
  export default defineComponent({
    name: 'ProfilePage',
    components: {
      IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
      IonCard, IonCardHeader, IonCardTitle, IonCardContent, IonAvatar
    }
  });
  </script>