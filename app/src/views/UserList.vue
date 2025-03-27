<template>
    <ion-page>
      <ion-header>
        <ion-toolbar color="primary">
          <ion-title>所有使用者</ion-title>
          <ion-button slot="start"  @click="goHome">
            <ion-icon :icon="home"></ion-icon>
          </ion-button>
        </ion-toolbar>
      </ion-header>
  
      <ion-content class="ion-padding">
        <!-- Display users in an IonList -->
        <ion-list>
          <ion-item v-for="user in users" :key="user.id">
            <!-- Avatar slot -->
            <ion-avatar slot="start">
              <!-- Example: user.photo or user.avatarFilename -->
              <img :src="user.avatar_url || placeholderImg" alt="User Avatar" />
            </ion-avatar>
  
            <!-- Username & Nickname -->
            <ion-label>
              <h2>{{ user.username }}</h2>
              <p>{{ user.nickname || 'No Nickname' }}</p>
            </ion-label>
          </ion-item>
        </ion-list>
  
        <!-- If there’s a chance of errors, show an alert or message -->
        <ion-alert
          :is-open="alertOpen"
          header="Error"
          :message="alertMessage"
          buttons="OK"
          @didDismiss="alertOpen = false"
        ></ion-alert>
      </ion-content>
    </ion-page>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import {
    IonPage,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonList,
    IonItem,
    IonAvatar,
    IonLabel,
    IonAlert,
    IonButton,
    IonIcon,
  } from '@ionic/vue';
  
  // Import your API service
  import api from '@/services/api.js';
  import { home } from 'ionicons/icons';
  import { useRouter } from 'vue-router';

const router = useRouter();
  
  // Reactive state
  const users = ref([]);
  const alertOpen = ref(false);
  const alertMessage = ref('');
  
  // Optional: placeholder image if user has no avatar
  const placeholderImg = 'https://via.placeholder.com/80';
  
  // Fetch users on mount
  onMounted(() => {
    loadUsers();
  });

  function goHome() {
    router.push('/');
  }
  
  // Load all users from API
  async function loadUsers() {
    try {
      const response = await api.getAllUsers(); // Adjust to match your endpoint
      users.value = response.data;             // e.g. an array of user objects
    } catch (error) {
      // Show error in IonAlert
      alertMessage.value = 'Failed to load users: ' + error;
      alertOpen.value = true;
    }
  }
  </script>
  
  <style scoped>
  /* Basic styling, adjust to taste. */
  </style>