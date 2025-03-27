from fastapi import FastAPI, Depends, HTTPException, status, File, Form, UploadFile
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, joinedload
from datetime import datetime, timedelta, timezone
import jwt  # 使用 PyJWT 進行 JWT 編碼解碼
import os, uuid, html
import argparse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
from openai import OpenAI
from fastapi.requests import Request

client = OpenAI(
    # This is the default and can be omitted
    api_key="",
)

# ★ 1) 改為使用 SQLite 的連線字串，指定資料庫檔名 (例如: my_database.db)
#    sqlite:/// 開頭代表使用 SQLite；後面則是檔案路徑。
#    相對路徑用 ./my_database.db，或絕對路徑用 /path/to/my_database.db。
DATABASE_URL = "sqlite:///./database.db"

# ★ 2) 若要在多執行緒環境存取同一個 SQLite 檔案，需加上 connect_args={"check_same_thread": False}
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 是否打印 SQL 語句
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# 定義資料表模型：User
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    nickname = Column(String(50), nullable=False, default="無名氏")  # 暱稱
    avatar_filename = Column(String(200), nullable=True)  # 儲存頭貼檔名

    # 關聯到 Message 表，用於取得使用者的所有留言
    messages = relationship("Message", back_populates="user")

# 定義資料表模型：Message
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # 關聯到 User 表，用於取得留言者資訊
    user = relationship("User", back_populates="messages")

# 建立資料表（如果尚未存在）
Base.metadata.create_all(bind=engine)

# 取得資料庫 Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from passlib.context import CryptContext
from typing import Optional, List
from pydantic import BaseModel

# 密碼哈希設定：使用 bcrypt 演算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT 設定
SECRET_KEY = "7123890@"  # 請使用安全隨機字串（可從環境變數讀取）
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7  # Token 有效期 7 天

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """建立 JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

# OAuth2 密碼模式，用於從 Authorization header 自動提取 JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 定義 Pydantic 資料模型，用於請求與回應格式
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    avatar_url: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
    recaptchaToken: str

class UserPublic(BaseModel):
    id: int
    username: str
    nickname: str
    avatar_url: Optional[str] = None
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    user: UserPublic
    class Config:
        from_attributes = True

# 依賴函式：取得目前登入的使用者
def get_current_user(token: str = Depends(oauth2_scheme), db: SessionLocal = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="驗證失敗，無法取得使用者憑證。",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError as e:
        logging.error(f"PyJWTError: {e}")
        # 包含 Token 過期或解碼失敗等情況
        raise credentials_exception
    # 查詢使用者
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 準備頭貼上傳目錄並透過 FastAPI 提供靜態檔案服務
AVATAR_DIR = "avatars"
if not os.path.isdir(AVATAR_DIR):
    os.makedirs(AVATAR_DIR)
# 將資料夾作為靜態檔案掛載 (可提供用戶頭貼圖片的訪問)
app.mount("/avatars", StaticFiles(directory=AVATAR_DIR), name="avatars")

def verifyRecaptcha(recaptcha_token: str):
    # 2) Verify with Google
    secret_key = "6Ldj9fgqAAAAAMVUnJQNelKvjTkZyGP5p8Zo4lSR"
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        'secret': secret_key,
        'response': recaptcha_token
    }
    verification_response = requests.post(verify_url, data=payload).json()
    # 3) Check success
    if not verification_response.get("success", False):
        return False
        #raise HTTPException(status_code=400, detail="reCAPTCHA verification failed")

    # 4) Optionally check 'score' or 'action'
    score = verification_response.get("score", 0)
    if score < 0.5:
        # Score is too low -> likely a bot
        return False
        #raise HTTPException(status_code=400, detail="reCAPTCHA score too low")
    return True

@app.post("/register", summary="使用者註冊", response_model=UserPublic)
async def register(
    username: str = Form(...),
    password: str = Form(...),
    recaptchaToken: str = Form(...),
    nickname: str = Form(...),
    avatar: UploadFile = File(None),
    db: SessionLocal = Depends(get_db)
):
    if not verifyRecaptcha(recaptchaToken):
        raise HTTPException(status_code=400, detail="偵測到異常行為，請稍後再試。")
    # 檢查使用者名稱是否已存在
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="該用戶名已被使用。")
    # 哈希使用者密碼
    hashed_pw = get_password_hash(password)
    avatar_filename = None
    # 若有上傳頭貼，處理圖片檔案
    if avatar:
        # 僅允許 JPEG 或 PNG 格式
        if avatar.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(status_code=400, detail="頭貼圖片僅限 JPG 或 PNG 格式。")
        # 確認副檔名
        ext = os.path.splitext(avatar.filename)[1].lower()  # 取得如 ".jpg" 或 ".png"
        if ext not in (".jpg", ".jpeg", ".png"):
            raise HTTPException(status_code=400, detail="頭貼圖片格式不被允許。")
        # 生成不重複的檔名
        avatar_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(AVATAR_DIR, avatar_filename)
        # 保存上傳的圖片檔案
        try:
            contents = await avatar.read()  # 讀取上傳內容
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"儲存頭貼檔案失敗: {e}")
    # 建立新 User 物件並寫入資料庫
    new_user = User(username=username, hashed_password=hashed_pw, avatar_filename=avatar_filename, nickname=nickname)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # 取回自動產生的 id 等欄位
    # 準備回傳的用戶公開資料（avatar_url 為靜態服務的路徑）
    avatar_url = f"/avatars/{new_user.avatar_filename}" if new_user.avatar_filename else None
    result = {"id": new_user.id, "username": new_user.username, "avatar_url": avatar_url, 'nickname': new_user.nickname}
    return result

@app.post("/login", summary="使用者登入", response_model=TokenResponse)
def login(login_data: LoginRequest, db: SessionLocal = Depends(get_db)):
    # 1) Extract reCAPTCHA token from request
    recaptcha_token = login_data.recaptchaToken

    if not verifyRecaptcha(recaptcha_token):
        raise HTTPException(status_code=400, detail="reCAPTCHA verification failed")
    """
    驗證使用者名稱與密碼，成功則回傳 JWT Token。
    """
    # 查詢使用者
    user = db.query(User).filter(User.username == login_data.username).first()
    if user is None or not verify_password(login_data.password, user.hashed_password):
        # 認證失敗（為安全不細述是用戶還是密碼錯誤）
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用戶名或密碼不正確。")
    # 生成 JWT access token
    access_token = create_access_token({"user_id": user.id}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    avatar_url = f"/avatars/{user.avatar_filename}" if user.avatar_filename else None
    return {"access_token": access_token, "token_type": "bearer", "avatar_url": avatar_url}

from pydantic import BaseModel

class MessageCreate(BaseModel):
    content: str

@app.get("/messages", summary="取得所有留言", response_model=List[MessageResponse])
def list_messages(db: SessionLocal = Depends(get_db)):
    # 取出所有留言，連帶載入關聯的使用者資料
    messages = db.query(Message).options(joinedload(Message.user)).order_by(Message.created_at.desc()).all()

    #List all users and format the avatra_url in user object
    for msg in messages:
        msg.user.avatar_url = f"/avatars/{msg.user.avatar_filename}" if msg.user.avatar_filename else None

    return messages  # FastAPI 會根據 response_model 將 ORM 對象轉換為 JSON

@app.post("/messages", summary="發表新留言", response_model=MessageResponse)
def create_message(
    msg: MessageCreate,
    db: SessionLocal = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 過濾輸入內容，防止 XSS 攻擊：轉義特殊字符
    clean_content = html.escape(msg.content, quote=True)
    # 建立留言物件並儲存
    new_msg = Message(user_id=current_user.id, content=clean_content)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    # 將當前使用者物件附加到新留言，準備輸出
    new_msg.user = current_user
    return new_msg

@app.delete("/messages/{message_id}", summary="刪除留言")
def delete_message(
    message_id: int,
    db: SessionLocal = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="找不到該留言。")
    if msg.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="您沒有權限刪除此留言。")
    db.delete(msg)
    db.commit()
    return {"detail": "留言已刪除。"}

# ★ 新增 get_all_users 路由
@app.get("/users", summary="取得所有使用者", response_model=List[UserPublic])
def get_all_users(db: SessionLocal = Depends(get_db)):
    """
    取得所有使用者，回傳 username、nickname、avatar_url 等公開資訊
    """
    users = db.query(User).all()
    # 動態設定 avatar_url 屬性
    for u in users:
        u.avatar_url = f"/avatars/{u.avatar_filename}" if u.avatar_filename else None
    return users

@app.post("/chat", summary="對話生成")
async def chat(request: Request):
    messages=[
            {"role": "system", "content": "你是網站助理小黃，協助使用者生成程式碼相關的問題，預設的程式語言是Python。"},
        ]
    #array of client messages
    clientMessages = await request.json()

    #append client messages to messages array
    for msg in clientMessages:
        messages.append(msg)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    return completion

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port',
                        type=int,
                        default=8080)
    args = parser.parse_args()
    # 启动服务器
    uvicorn.run(app, host='0.0.0.0', port=args.port)



if __name__ == '__main__':
    main()
