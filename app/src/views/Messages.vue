<template>
    <ion-menu side="end" content-id="main-content">
        <ion-header>
            <ion-toolbar>
            <ion-title>選單</ion-title>
            </ion-toolbar>
        </ion-header>

        <ion-content class="ion-padding">
            <!-- A list for the menu items -->
            <ion-list>
            <!-- Users Button -->
                <ion-button  expand="block"  @click="goUsers">
                <ion-icon :icon="peopleOutline" slot="start" @click="goUsers"></ion-icon>
                <ion-label>使用者列表</ion-label>
                </ion-button>
            <!-- Logout Button -->
                <ion-button v-if="isLogin()" expand="block" @click="handleLogout">
                <ion-icon :icon="logOutOutline" slot="start"></ion-icon>
                <ion-label>登出</ion-label>
                </ion-button>
                <ion-button v-else  expand="block" color="secondary" @click="goLogin">
                <ion-icon :icon="logInOutline" slot="start"></ion-icon>
                <ion-label>登入</ion-label>
                </ion-button>
            </ion-list>
        </ion-content>
    </ion-menu>
    <ion-page id="main-content" v-bind="$attrs">
        <!-- 頁首標題：留言板 -->
        <ion-header>
            <ion-toolbar color="primary">
                <ion-title>黃杬霆的個人網站</ion-title>
                <ion-buttons slot="end">
                    <ion-menu-button></ion-menu-button>
                </ion-buttons>
            </ion-toolbar>
        </ion-header>
        <ion-content class="ion-padding">

            <!-- 主人頭貼 -->
            <ion-avatar style="width: 100px; height: 100px; margin-bottom: 16px;">
                <!-- 範例圖片，可替換為實際圖片路徑 -->
                <img src="/412351.jpg" alt="Profile Picture">
            </ion-avatar>
            <!-- 簡介文字 -->
            <p>我是黃杬霆，過去曾為黑色金屬樂團吉他手、瑜伽老師、dancer等，現為公務人員及博士生，請多指教！</p>

            <!-- 新增留言區塊（僅登入使用者可見） -->
            <ion-card>
                <ion-card-header>
                    <ion-card-title id="bullet-title">留言板</ion-card-title>
                </ion-card-header>


                <ion-card-content>
                    <div v-if="isLogin()">
                        <div class="message-card">
                            <!-- If logged in, show user avatar that opens a popover -->
                            <ion-avatar id="avatarIcon" class="avatar-top-right" style="cursor: pointer;">
                                <!-- If user has an avatar, display it; otherwise, fallback to an icon -->
                                <ion-img v-if="userAvatar" :src="userAvatar" />
                            </ion-avatar>
                            <!-- <ion-button @click="handleLogout" fill="clear" color="secondary">
                                    <ion-icon :icon="logOutIcon" slot="start"></ion-icon>
                                </ion-button> -->

                            <ion-item id="new-post">
                                <ion-label position="stacked">新增留言</ion-label>
                                <ion-textarea v-model="newMessage" placeholder="輸入留言內容..." rows="3"></ion-textarea>
                                <ion-button position="stacked" expand="block" style="margin-top: 8px;width:100%"
                                    @click="submitMessage">發表</ion-button>
                            </ion-item>
                        </div>
                    </div>
                    <div v-else class="message-card">
                        <!-- If not logged in, show a Login button -->
                        <p style="align-self: center;">請先登入以發表留言。</p>
                        <ion-button @click="goLogin">
                            <ion-icon :icon="logInOutline" slot="start"></ion-icon>
                            登入/註冊
                        </ion-button>
                    </div>

                    <!-- 留言列表 -->
                    <div v-for="(msg, index) in messages" :key="msg.id" class="message-card">
                        <div class="avatar-box">
                            <img :src="msg.user.avatar_url" class="avatar-img" alt="avatar" />
                        </div>
                        <div class="content-box">
                            <div class="post-header">
                                <ion-badge color="primary">{{ (index + 1) + ' 樓 ' }}</ion-badge>
                                <strong class="nickname">
                                    {{ msg.user.nickname || msg.user.username }}
                                </strong>
                                <span class="timestamp">{{ formatTime(msg.created_at) }}</span>
                            </div>
                            <div class="post-content">{{ msg.content }}</div>
                            <div v-if="isLogin() && msg.user.username === currentUser" class="delete-button">
                                <ion-button fill="clear" color="secondary" @click="confirmDeleteMessage(msg.id)">
                                    <ion-icon :icon="trash" slot="icon-only"></ion-icon>
                                </ion-button>
                            </div>
                        </div>
                    </div>
                </ion-card-content>
            </ion-card>
            <!-- Ion Popover (user avatar menu) -->
             <!--
            <ion-popover v-if="isLogin" trigger="avatarIcon" trigger-action="click" :dismiss-on-select="true">
                <ion-content>
                    <ion-item :button="true" :detail="false" @click="handleLogout" lines="none">
                        <ion-icon aria-hidden="true" :icon="logOutIcon" slot="start"></ion-icon>
                        <ion-label>登出</ion-label>
                    </ion-item>
                </ion-content>
            </ion-popover>
        -->
            <!-- 錯誤警示 (warning dialog) -->
            <ion-alert :is-open="alertOpen" header="Warning" :message="alertMessage" :buttons="[
                    {
                        text: 'OK',
                        role: 'ok'
                    }
                ]"
                @didDismiss="() => (alertOpen = false)"></ion-alert>

            <!-- 確認刪除 IonAlert -->
            <ion-alert :is-open="deleteAlertOpen" header="確認刪除" message="確定要刪除此留言？"
                @didDismiss="() => (deleteAlertOpen = false)" :buttons="[
                    {
                        text: '取消',
                        role: 'cancel',
                        handler: () => {
                            deleteAlertOpen = false;
                            messageIdToDelete = null;
                        }
                    },
                    {
                        text: '刪除',
                        role: 'destructive',
                        handler: () => {
                            // User confirmed deletion
                            deleteMessage(messageIdToDelete);
                        }
                    }
                ]" />
            <!-- Floating Chat Button in bottom-right corner -->
            <ion-fab v-if="isLogin()" vertical="bottom" horizontal="start" slot="fixed">
                <ion-fab-button @click="showChatModal = true">
                    <ion-icon :icon="chatbubblesOutline"></ion-icon>
                </ion-fab-button>
            </ion-fab>

            <!-- Modal for the ChatBox -->
            <ion-modal :is-open="showChatModal" swipe-to-close="true" presenting-element="ion-router-outlet"
                @will-dismiss="onModalWillDismiss">
                <ChatBox @closed="onModalWillDismiss" :userAvatar="userAvatar" />
            </ion-modal>
        </ion-content>
    </ion-page>
</template>

<script setup>
/* -----------------------------
   Imports
--------------------------------*/
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import {
    IonPage,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonItem,
    IonLabel,
    IonTextarea,
    IonButton,
    IonAvatar,
    IonIcon,
    IonAlert,
    IonBadge,
    IonModal,
    IonImg,
    IonPopover,
    IonFab,
    IonFabButton,
    IonCard,
    IonCardContent,
    IonCardHeader,
    IonCardTitle,
    IonMenu,
    IonButtons,
    IonMenuButton,
    IonList
} from '@ionic/vue';

import { trash, logOutOutline, logInOutline, chatbubblesOutline, peopleOutline} from 'ionicons/icons';
import api from '@/services/api.js';
import ChatBox from '@/components/ChatBox.vue'; // The second view described below
import { useAttrs } from 'vue';

const attrs = useAttrs();

// Local state for controlling modal
const showChatModal = ref(false);

// Callback for IonModal "willDismiss" event
function onModalWillDismiss() {
    showChatModal.value = false;
}

/* -----------------------------
   Define reactive variables
--------------------------------*/
const messages = ref([]);
const newMessage = ref('');
const currentUser = ref('');

const alertOpen = ref(false);
const alertMessage = ref('');

const userAvatar = ref('');
// Deletion confirmation
const deleteAlertOpen = ref(false);
let messageIdToDelete = null; // Not a ref if we only update in handlers

/* -----------------------------
   Setup Router
--------------------------------*/
const router = useRouter();

/* -----------------------------
   Functions
--------------------------------*/
function formatTime(timestamp) {
    return new Date(timestamp).toLocaleString();
}

function showWarningDialog(message) {
    alertMessage.value = message;
    alertOpen.value = true;
}

function isLogin() {
    return api.isAuthorized();
}

async function fetchMessages() {
    try {
        const response = await api.getMessages();
        messages.value = response.data;
    } catch (error) {
        showWarningDialog('Failed to fetch messages: ' + error);
    }
}

async function submitMessage() {
    if (!newMessage.value.trim()) return;
    try {
        await api.postMessage(newMessage.value);
        newMessage.value = '';
        fetchMessages();
    } catch (error) {
        showWarningDialog('發表新貼文失敗: ' + error);
        if (error.response && error.response.status === 401) {
            api.logout();
            router.push('/login');
        }
    }
}

function confirmDeleteMessage(id) {
    messageIdToDelete = id;
    deleteAlertOpen.value = true;
}

async function deleteMessage(id) {
    if (!id) return;
    try {
        await api.deleteMessage(id);
        fetchMessages();
    } catch (error) {
        showWarningDialog('Failed to delete message: ' + error);
    } finally {
        deleteAlertOpen.value = false;
        messageIdToDelete = null;
    }
}

function goLogin() {
    router.push('/login');
}

function goUsers() {
    router.push('/users');
}

function handleLogout() {
    api.logout();
    //In.value = false;
    userAvatar.value = '';
    currentUser.value = '';
    router.push('/login');
}

/* -----------------------------
   onMounted Lifecycle
--------------------------------*/
onMounted(() => {
    const username = localStorage.getItem('username');
    const avatarUrl = localStorage.getItem('avatar_url');

    //loggedIn.value = api.isAuthorized();
    currentUser.value = username || '';
    userAvatar.value = avatarUrl || '';

    fetchMessages();
});
</script>

<style scoped>
.message-card {
    display: flex;
    margin-bottom: 16px;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px;
    background-color: #f9f9f9;
}

.avatar-box {
    margin-right: 12px;
}

.avatar-img {
    width: 80px;
    height: 80px;
    object-fit: cover;
    border-radius: 4px;
}

.content-box {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.post-header {
    display: flex;
    align-items: center;
    margin-bottom: 4px;
}

.nickname {
    margin-right: 8px;
    margin-left: 8px;
    font-size: 1.1em;
    color: #333;
}

.timestamp {
    font-size: 0.8em;
    color: #999;
}

.post-content {
    margin-top: 4px;
    font-size: 1em;
    white-space: pre-wrap;
}

.delete-button {
    margin-top: 8px;
    align-self: flex-end;
}

#bullet-title {
    align-self: center;
}

#new-post {
    width: 100%
}
</style>