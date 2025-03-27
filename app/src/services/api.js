import axios from 'axios';

const BaseUrl = 'http://localhost:8080';
const ReCapptchaSiteKey = '6Ldj9fgqAAAAAE-Lmp1iCjuKMQYFEcwVnZtFArIY';
// 設定後端 API 基本路徑 (根據實際後端位址調整)
const API = axios.create({
    baseURL: BaseUrl  // FastAPI 伺服器位址
});

// 如果 localStorage 中有保存的 JWT 權杖，預設附加在 Headers
const token = localStorage.getItem('token');
if (token) {
    API.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

export default {
    // 使用者註冊，傳送使用者名稱、密碼和頭貼圖片 (FormData)
    register(username, password, avatarFile, nickname,recaptchaToken) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('nickname', nickname);
        formData.append('recaptchaToken', recaptchaToken);
        if (avatarFile) {
            formData.append('avatar', avatarFile);
        }
        // 假設後端有 /register 路由處理使用者註冊
        return API.post('/register', formData);
    },

    isAuthorized() {
        return API.defaults.headers.common['Authorization'] ? true : false;
    },

    // 使用者登入，傳送帳密以取得 JWT，並將權杖保存
    async login(username, password, recaptchaToken) {
        // 假設後端有 /login 路由回傳 { access_token, token_type, user }
        const response = await API.post('/login', { username, password, recaptchaToken });
        const data = response.data;
        if (data.access_token) {
            // 保存 JWT 權杖和當前使用者資訊
            API.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('username', username);
            // 如果後端回傳使用者頭貼網址，可一併保存
            if (data.avatar_url) {
                localStorage.setItem('avatar_url', BaseUrl + data.avatar_url);
            }
        }
        return data;
    },

    // 取得所有留言
    getMessages() {
        // 假設後端有 /messages 路由提供留言列表
        const promise = API.get('/messages');

        // 假設後端回傳的留言格式為 [{ id, content, created_at, user: { id, username, avatar_url } }]
        //List all user objects from messages and format avatar_url by adding the base URL

        return new Promise((resolve, reject) => {
            promise.then((response) => {
                response.data.forEach((message) => {
                    if (message.user && message.user.avatar_url) {
                        message.user.avatar_url = BaseUrl + message.user.avatar_url;
                    }
                });
                resolve(response);
            }).catch((error) => {
                reject(error);
            });
        }
        );

        //return new promise after formatting the avatar_url


    },

    // 發表新留言 (需附帶 JWT 權杖)
    postMessage(content) {
        // 假設後端有受保護的 POST /messages 路由
        return API.post('/messages', { content });
    },

    // 刪除留言 (需附帶 JWT 權杖)
    deleteMessage(messageId) {
        // 假設後端有受保護的 DELETE /messages/{id} 路由
        return API.delete(`/messages/${messageId}`);
    },

    logout() {
        // 假設後端有 /logout 路由清除 JWT 權杖
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        localStorage.removeItem('avatar_url');
        delete API.defaults.headers.common['Authorization'];
    },

    /**
   * Execute reCAPTCHA v3
   * action is a label you assign to track usage (e.g. 'login')
   */
    async executeRecaptcha(action) {
        return new Promise((resolve, reject) => {
            if (!window.grecaptcha) {
                return reject('reCAPTCHA not loaded');
            }

            // Replace YOUR_RECAPTCHA_SITE_KEY with your site key
            window.grecaptcha.ready(() => {
                window.grecaptcha
                    .execute(ReCapptchaSiteKey, { action })
                    .then(token => {
                        resolve(token);
                    })
                    .catch(err => {
                        reject(err);
                    });
            });
        });
    },

    // 新增：取得所有使用者
    getAllUsers() {
        const promise = API.get('/users');
        return new Promise((resolve, reject) => {
            promise.then((response) => {
                // 對每個 user 設定完整的 avatar_url
                response.data.forEach((user) => {
                    if (user.avatar_url) {
                        user.avatar_url = BaseUrl + user.avatar_url;
                    }
                });
                resolve(response);
            }).catch((error) => {
                reject(error);
            });
        });
    },
    /**
     * 與後端 GPT 聊天的函式
     * @param {Array} messages - e.g. [{role: 'user', content: 'Hello'}, {role: 'assistant', content: 'Hi!'}]
     * @returns {Promise} 回傳後端呼叫 GPT 的結果
     */
    chatAI(messages) {
        // 假設後端有 /chat 路由，可以將 messages array 傳送給後端
        return API.post('/chat', messages);
    },

};