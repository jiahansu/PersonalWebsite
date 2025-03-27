<template>
    <ion-page>
      <!-- 頁首標題：AI 文字轉程式碼 -->
      <ion-header>
        <ion-toolbar color="primary">
          <ion-title>AI 程式碼產生</ion-title>
        </ion-toolbar>
      </ion-header>
  
      <ion-content class="ion-padding">
        <!-- 輸入程式需求描述 -->
        <ion-item>
          <ion-label position="stacked">程式需求描述</ion-label>
          <ion-textarea v-model="description" placeholder="描述您想要實現的功能..." rows="4"></ion-textarea>
        </ion-item>
        <!-- 選擇程式語言 -->
        <ion-item>
          <ion-label>選擇語言</ion-label>
          <ion-select v-model="language" placeholder="選擇語言">
            <ion-select-option value="Python">Python</ion-select-option>
            <ion-select-option value="JavaScript">JavaScript</ion-select-option>
            <ion-select-option value="C++">C++</ion-select-option>
          </ion-select>
        </ion-item>
        <!-- 產生程式碼按鈕 -->
        <ion-button expand="block" style="margin-top: 12px;" @click="generateCode">產生程式碼</ion-button>
        <!-- 顯示產生的程式碼或錯誤訊息 -->
        <div style="margin-top: 16px;">
          <ion-text color="danger" v-if="errorMessage">{{ errorMessage }}</ion-text>
          <ion-card v-if="codeOutput">
            <ion-card-header>
              <ion-card-title>產生的程式碼</ion-card-title>
            </ion-card-header>
            <ion-card-content>
              <!-- 使用 <pre> 保留程式碼格式 -->
              <pre>{{ codeOutput }}</pre>
            </ion-card-content>
          </ion-card>
        </div>
      </ion-content>
    </ion-page>
  </template>
  
  <script>
  import { defineComponent } from 'vue';
  import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
           IonItem, IonLabel, IonTextarea, IonSelect, IonSelectOption, IonButton,
           IonText, IonCard, IonCardHeader, IonCardTitle, IonCardContent } from '@ionic/vue';
  import api from '@/services/api.js';
  
  export default defineComponent({
    name: 'AIPage',
    components: {
      IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
      IonItem, IonLabel, IonTextarea, IonSelect, IonSelectOption, IonButton,
      IonText, IonCard, IonCardHeader, IonCardTitle, IonCardContent
    },
    data() {
      return {
        description: '',    // 使用者輸入的需求描述
        language: '',       // 選擇的程式語言
        codeOutput: '',     // 從 OpenAI API 獲得的程式碼
        errorMessage: ''    // 錯誤訊息
      };
    },
    methods: {
      async generateCode() {
        this.errorMessage = '';
        this.codeOutput = '';
        if (!this.description.trim() || !this.language) {
          this.errorMessage = '請輸入需求描述並選擇語言';
          return;
        }
        try {
          // 調用後端 API 產生程式碼
          const response = await api.generateCode(this.description, this.language);
          // 假設後端回傳 JSON：{ code: '...程式碼...' }
          const data = response.data;
          this.codeOutput = data.code || data;  // 部分情況直接是程式碼字串
        } catch (error) {
          // 顯示錯誤訊息
          this.errorMessage = '產生程式碼失敗，請稍後再試。';
          console.error('AI generate code error:', error);
        }
      }
    }
  });
  </script>