import streamlit as st
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(
    page_title="무한의 계단 - 3D 입체 계단",
    page_icon="🪜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태로 로그인 정보 관리
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = "게스트"
    st.session_state.user_uid = "guest_user"

# 상단에 파이썬 네이티브 로그인 영역 배치 (iframe 차단 우회)
with st.container():
    col1, col2, col3 = st.columns([2, 6, 2])
    with col2:
        st.markdown("<h3 style='text-align: center; color: white;'>🪜 무한의 계단 & 실시간 랭킹</h3>", unsafe_allow_html=True)
        
        if not st.session_state.logged_in:
            with st.form("login_form"):
                nickname = st.text_input("플레이어 닉네임을 입력하세요", placeholder="홍길동")
                submitted = st.form_submit_button("게임 시작 및 랭킹 등록 활성화")
                if submitted and nickname.strip():
                    st.session_state.logged_in = True
                    st.session_state.user_name = nickname.strip()
                    st.session_state.user_uid = "user_" + str(hash(nickname))
                    st.rerun()
        else:
            st.success(f"환영합니다, **{st.session_state.user_name}**님! (기록이 자동으로 랭킹에 반영됩니다)")
            if st.button("로그아웃 / 닉네임 변경"):
                st.session_state.logged_in = False
                st.rerun()

# 모바일 UI 스타일링: Streamlit 여백 제거 및 풀스크린 설정
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding: 0rem !important;
            max-width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# 파이썬 변수를 안전하게 JS 변수로 치환하기 위한 값 준비
is_logged_in_val = "true" if st.session_state.logged_in else "false"
user_uid_val = st.session_state.user_uid
user_name_val = st.session_state.user_name

# HTML 및 게임 로직 코드
game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>무한의 계단 - 랭킹</title>
    
    <!-- Firebase SDK 로드 -->
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
        import { getDatabase, ref, set, get, child, query, orderByChild, limitToLast } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-database.js";

        const firebaseConfig = {
            apiKey: "AIzaSyBojibEddXnq5MvQPz0TRNiaF-8ZO2r0yA",
            authDomain: "kidscience-e4a24.firebaseapp.com",
            databaseURL: "https://kidscience-e4a24-default-rtdb.firebaseio.com",
            projectId: "kidscience-e4a24",
            storageBucket: "kidscience-e4a24.firebasestorage.app",
            messagingSenderId: "982051065836",
            appId: "1:982051065836:web:563829aece0746ac11fac9",
            measurementId: "G-G5B44WYEMG"
        };

        const app = initializeApp(firebaseConfig);
        const db = getDatabase(app);

        window.firebaseDB = db;
        window.currentUser = {
            isLoggedIn: __IS_LOGGED_IN__,
            uid: "__USER_UID__",
            displayName: "__USER_NAME__"
        };

        window.ref = ref;
        window.set = set;
        window.get = get;
        window.child = child;
        window.query = query;
        window.orderByChild = orderByChild;
        window.limitToLast = limitToLast;
        
        fetchRankings();
    </script>

    <style>
        * {
            box-sizing: border-box;
            user-select: none;
            -webkit-user-select: none;
            -webkit-touch-callout: none;
            touch-action: manipulation;
        }
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #111e38;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            flex-direction: column;
        }
        #game-container {
            position: relative;
            width: 100%;
            height: 100dvh;
            display: flex;
            flex-direction: column;
        }
        canvas {
            width: 100%;
            flex: 1;
            display: block;
        }
        .ui-panel {
            height: 110px;
            background: #191928;
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding: 10px 15px;
            padding-bottom: max(10px, env(safe-area-inset-bottom));
            box-shadow: 0 -4px 15px rgba(0,0,0,0.5);
            z-index: 10;
        }
        .control-btn {
            flex: 1;
            height: 100%;
            margin: 0 8px;
            font-size: 21px;
            font-weight: 800;
            color: white;
            border: none;
            border-radius: 16px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 4px;
            transition: transform 0.05s, opacity 0.1s;
            outline: none;
        }
        .control-btn:active {
            transform: scale(0.95);
            opacity: 0.85;
        }
        .turn-btn {
            background: linear-gradient(135deg, #feca57, #ff9f43);
            color: #1e1e2f;
            flex: 0.8;
        }
        .jump-btn {
            background: linear-gradient(135deg, #ff6b6b, #ee5253);
            flex: 1.2;
        }
    </style>
</head>
<body>
    <div id="game-container">
        <canvas id="gameCanvas"></canvas>
        <div class="ui-panel">
            <button class="control-btn turn-btn" id="turnBtn">
                <span>🔄</span>
                <span style="font-size: 15px;">방향전환</span>
            </button>
            <button class="control-btn jump-btn" id="jumpBtn">
                <span>⬆</span>
                <span style="font-size: 16px;">점프!</span>
            </button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        let W = window.innerWidth;
        let H = canvas.clientHeight;

        function resizeCanvas() {
            W = window.innerWidth;
            H = canvas.clientHeight;
            canvas.width = W;
            canvas.height = H;
        }
        window.addEventListener('resize', resizeCanvas);

        let score = 0;
        let highScore = 0;
        let gameState = 'START'; 
        let currentTheme = 'jungle'; 
        let rankingList = [];

        let energy = 100;
        let maxEnergy = 100;
        let energyDecayRate = 0.35;

        let character = { x: 0, y: 0, dir: 1, legOffset: 0, armOffset: 0 };
        let stairs = [];
        let currentIndex = 0;
        let cameraY = 0;
        let targetCameraY = 0;

        const STAIR_WIDTH = 76;
        const STAIR_TREAD_HEIGHT = 12;
        const STAIR_RISER_HEIGHT = 10;
        const STAIR_STEP_X = 60;
        const STAIR_STEP_Y = 50;

        async function saveScoreToDB(newScore) {
            if (!window.currentUser.isLoggedIn) return;
            if (newScore > highScore) highScore = newScore;

            try {
                await window.set(window.ref(window.firebaseDB, 'scores/' + window.currentUser.uid), {
                    name: window.currentUser.displayName,
                    score: highScore
                });
                fetchRankings();
            } catch (e) { console.error(e); }
        }

        async function fetchRankings() {
            try {
                const dbRef = window.ref(window.firebaseDB, 'scores');
                const topQuery = window.query(dbRef, window.orderByChild('score'), window.limitToLast(5));
                const snapshot = await window.get(topQuery);
                if (snapshot.exists()) {
                    let list = [];
                    snapshot.forEach((childSnapshot) => {
                        list.push(childSnapshot.val());
                    });
                    rankingList = list.sort((a, b) => b.score - a.score);
                }
            } catch (e) { console.error(e); }
        }

        function initStairs() {
            stairs = [];
            let currentX = W / 2;
            let currentY = H - 180;
            stairs.push({ x: currentX, y: currentY });

            for (let i = 1; i < 200; i++) {
                let direction = Math.random() < 0.5 ? -1 : 1;
                let nextX = currentX + (direction * STAIR_STEP_X);
                if (nextX < 60) nextX = currentX + STAIR_STEP_X;
                if (nextX > W - 60) nextX = currentX - STAIR_STEP_X;
                currentY -= STAIR_STEP_Y;
                stairs.push({ x: nextX, y: currentY });
                currentX = nextX;
            }
        }

        function resetGame() {
            resizeCanvas();
            score = 0;
            energy = maxEnergy;
            currentIndex = 0;
            initStairs();
            
            character.dir = (stairs[1].x > stairs[0].x) ? 1 : -1;
            character.x = stairs[0].x;
            character.y = stairs[0].y - STAIR_TREAD_HEIGHT;
            character.legOffset = 0;
            character.armOffset = 0;

            cameraY = 0;
            targetCameraY = 0;
            gameState = 'PLAYING';
        }

        function turnCharacter() {
            if (gameState !== 'PLAYING') return;
            character.dir *= -1;
        }

        function jump() {
            if (gameState !== 'PLAYING') {
                resetGame();
                return;
            }

            let nextIndex = currentIndex + 1;
            if (nextIndex >= stairs.length) {
                let lastStair = stairs[stairs.length - 1];
                let nextX = Math.random() < 0.5 ? lastStair.x - STAIR_STEP_X : lastStair.x + STAIR_STEP_X;
                if (nextX < 60) nextX = lastStair.x + STAIR_STEP_X;
                if (nextX > W - 60) nextX = lastStair.x - STAIR_STEP_X;
                stairs.push({ x: nextX, y: lastStair.y - STAIR_STEP_Y });
                nextIndex = stairs.length - 1;
            }

            let currentStair = stairs[currentIndex];
            let targetStair = stairs[nextIndex];
            let expectedX = currentStair.x + (character.dir * STAIR_STEP_X);

            if (Math.abs(expectedX - targetStair.x) < 15) {
                currentIndex = nextIndex;
                score++;
                energy = Math.min(maxEnergy, energy + 12);
                
                if (score > highScore) {
                    highScore = score;
                    saveScoreToDB(score);
                }

                character.x = targetStair.x;
                character.y = targetStair.y - STAIR_TREAD_HEIGHT;
                character.legOffset = character.legOffset === 0 ? 10 : 0;
                character.armOffset = character.armOffset === 0 ? 12 : 0;

                targetCameraY = currentIndex * STAIR_STEP_Y - (H * 0.35);
            } else {
                gameState = 'GAMEOVER';
                saveScoreToDB(score);
            }
        }

        document.getElementById('turnBtn').addEventListener('pointerdown', (e) => {
            e.stopPropagation();
            turnCharacter();
        });

        document.getElementById('jumpBtn').addEventListener('pointerdown', (e) => {
            e.stopPropagation();
            jump();
        });

        canvas.addEventListener('pointerdown', (e) => {
            let rect = canvas.getBoundingClientRect();
            let clientX = e.clientX - rect.left;
            let clientY = e.clientY - rect.top;

            if (gameState === 'START') {
                let themes = ['jungle', 'city', 'space', 'cyber', 'sky'];
                let startY = 80;
                let btnW = W * 0.82;
                let btnH = 36;
                
                for (let i = 0; i < themes.length; i++) {
                    let bX = (W - btnW) / 2;
                    let bY = startY + (i * 42);
                    if (clientX > bX && clientX < bX + btnW && clientY > bY && clientY < bY + btnH) {
                        currentTheme = themes[i];
                        resetGame();
                        return;
                    }
                }
            }
            jump();
        });

        window.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'a' || e.key === 'd') {
                turnCharacter();
            } else if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                jump();
            }
        });

        function drawHumanCharacter(x, y, dir) {
            ctx.save();
            ctx.translate(x, y);
            ctx.scale(dir, 1);

            ctx.strokeStyle = '#2e86de';
            ctx.lineWidth = 5;
            ctx.lineCap = 'round';

            ctx.beginPath();
            ctx.moveTo(-2, -18);
            ctx.lineTo(-6 - character.legOffset * 0.5, -4);
            ctx.lineTo(-2 - character.legOffset, 0);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(2, -18);
            ctx.lineTo(6 + character.legOffset * 0.5, -6);
            ctx.lineTo(8 + character.legOffset, 0);
            ctx.stroke();

            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(-2 - character.legOffset, 0, 3, 0, Math.PI * 2);
            ctx.arc(8 + character.legOffset, 0, 3, 0, Math.PI * 2);
            ctx.fill();

            let shirtColor = '#ff9f43';
            if (currentTheme === 'jungle') shirtColor = '#27ae60';
            else if (currentTheme === 'city') shirtColor = '#e74c3c';
            else if (currentTheme === 'space') shirtColor = '#3498db';
            else if (currentTheme === 'cyber') shirtColor = '#00ffcc';
            else if (currentTheme === 'sky') shirtColor = '#f39c12';

            ctx.fillStyle = shirtColor;
            ctx.beginPath();
            ctx.roundRect(-8, -38, 16, 22, 4);
            ctx.fill();

            ctx.fillStyle = '#ffdd99';
            ctx.beginPath();
            ctx.arc(0, -46, 9, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = shirtColor;
            ctx.beginPath();
            ctx.arc(0, -48, 9.5, Math.PI * 0.9, Math.PI * 2.1);
            ctx.fill();
            ctx.fillRect(2, -50, 10, 3);

            ctx.fillStyle = '#222222';
            ctx.beginPath();
            ctx.arc(4, -46, 1.5, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = shirtColor;
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(0, -34);
            ctx.lineTo(8 - character.armOffset, -24);
            ctx.lineTo(12 - character.armOffset, -18);
            ctx.stroke();

            ctx.fillStyle = '#ffdd99';
            ctx.beginPath();
            ctx.arc(12 - character.armOffset, -18, 2.5, 0, Math.PI * 2);
            ctx.fill();

            ctx.restore();
        }

        function drawBackground() {
            let parallaxY = cameraY * 0.35;
            if (currentTheme === 'jungle') {
                let grad = ctx.createLinearGradient(0, 0, 0, H);
                grad.addColorStop(0, '#0d2b1d'); grad.addColorStop(1, '#4e9f3d');
                ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);
            } else if (currentTheme === 'city') {
                let grad = ctx.createLinearGradient(0, 0, 0, H);
                grad.addColorStop(0, '#080514'); grad.addColorStop(1, '#2c2b54');
                ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);
            } else if (currentTheme === 'space') {
                let grad = ctx.createLinearGradient(0, 0, 0, H);
                grad.addColorStop(0, '#02000a'); grad.addColorStop(1, '#10052b');
                ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);
            } else if (currentTheme === 'cyber') {
                let grad = ctx.createLinearGradient(0, 0, 0, H);
                grad.addColorStop(0, '#090014'); grad.addColorStop(1, '#001a1a');
                ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);
            } else {
                let grad = ctx.createLinearGradient(0, 0, 0, H);
                grad.addColorStop(0, '#1a75ff'); grad.addColorStop(1, '#e6f2ff');
                ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);
            }
        }

        function update() {
            if (gameState === 'PLAYING') {
                cameraY += (targetCameraY - cameraY) * 0.15;
                energy -= energyDecayRate + (score * 0.003);
                if (energy <= 0) {
                    energy = 0;
                    gameState = 'GAMEOVER';
                    saveScoreToDB(score);
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);
            drawBackground();

            ctx.save();
            ctx.translate(0, cameraY);

            stairs.forEach((stair, index) => {
                let isCurrent = index === currentIndex;
                let sx = stair.x - STAIR_WIDTH / 2;
                let sy = stair.y;

                ctx.fillStyle = isCurrent ? '#900c3f' : '#28283d';
                ctx.fillRect(sx, sy + STAIR_TREAD_HEIGHT, STAIR_WIDTH, STAIR_RISER_HEIGHT);

                ctx.fillStyle = isCurrent ? '#ff6b6b' : '#4d4d73';
                ctx.fillRect(sx, sy, STAIR_WIDTH, STAIR_TREAD_HEIGHT);

                ctx.strokeStyle = isCurrent ? '#ff9ff3' : '#7070a3';
                ctx.lineWidth = 1.5;
                ctx.strokeRect(sx, sy, STAIR_WIDTH, STAIR_TREAD_HEIGHT);
                ctx.strokeRect(sx, sy + STAIR_TREAD_HEIGHT, STAIR_WIDTH, STAIR_RISER_HEIGHT);
            });

            drawHumanCharacter(character.x, character.y, character.dir);
            ctx.restore();

            if (gameState === 'PLAYING' || gameState === 'GAMEOVER') {
                let barW = W * 0.7;
                let barH = 14;
                let barX = (W - barW) / 2;
                let barY = 20;

                ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
                ctx.beginPath();
                ctx.roundRect(barX, barY, barW, barH, 7);
                ctx.fill();

                let currentBarW = (energy / maxEnergy) * barW;
                ctx.fillStyle = energy > 30 ? '#10ac84' : '#ee5253';
                ctx.beginPath();
                ctx.roundRect(barX, barY, currentBarW, barH, 7);
                ctx.fill();

                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 28px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(score, W / 2, 65);
                ctx.font = '13px sans-serif';
                ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
                ctx.fillText('내 점수: ' + score, W / 2, 85);
            }

            if (gameState === 'START') {
                ctx.fillStyle = 'rgba(15, 23, 42, 0.96)';
                ctx.fillRect(0, 0, W, H);

                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 22px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('테마를 선택하세요', W / 2, 50);

                let themes = [
                    { id: 'jungle', name: '🌴 밀림 숲속' },
                    { id: 'city', name: '🏙 도심 빌딩' },
                    { id: 'space', name: '🌌 밤하늘 우주' },
                    { id: 'cyber', name: '⚡ 사이버펑크' },
                    { id: 'sky', name: '☁ 구름 하늘' }
                ];
                let startY = 80;
                let btnW = W * 0.82;
                let btnH = 36;

                for (let i = 0; i < themes.length; i++) {
                    let bX = (W - btnW) / 2;
                    let bY = startY + (i * 42);
                    let isSelected = currentTheme === themes[i].id;
                    
                    ctx.fillStyle = isSelected ? '#ff6b6b' : 'rgba(255, 255, 255, 0.1)';
                    ctx.beginPath();
                    ctx.roundRect(bX, bY, btnW, btnH, 6);
                    ctx.fill();

                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 14px sans-serif';
                    ctx.fillText(themes[i].name, W / 2, bY + 23);
                }

                let rankStartY = startY + (themes.length * 42) + 20;
                ctx.fillStyle = '#ff9f43';
                ctx.font = 'bold 16px sans-serif';
                ctx.fillText('🏆 실시간 TOP 랭킹', W / 2, rankStartY);

                ctx.font = '13px sans-serif';
                ctx.fillStyle = '#ffffff';
                let rankY = rankStartY + 25;
                if (rankingList.length === 0) {
                    ctx.fillText('등록된 랭킹 데이터가 없습니다.', W / 2, rankY);
                } else {
                    rankingList.forEach((r, idx) => {
                        ctx.fillText((idx + 1) + '위: ' + r.name + ' - ' + r.score + '점', W / 2, rankY + (idx * 22));
                    });
                }

            } else if (gameState === 'GAMEOVER') {
                ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
                ctx.fillRect(0, 0, W, H);

                ctx.fillStyle = '#ff6b6b';
                ctx.font = 'bold 34px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('GAME OVER', W / 2, H / 2 - 40);

                ctx.fillStyle = '#ffffff';
                ctx.font = '20px sans-serif';
                ctx.fillText('최종 점수: ' + score + '점', W / 2, H / 2 + 5);

                ctx.font = '14px sans-serif';
                ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
                ctx.fillText('랭킹 자동저장 완료!', W / 2, H / 2 + 32);

                ctx.fillStyle = '#10ac84';
                ctx.font = '15px sans-serif';
                ctx.fillText('다시 하려면 화면을 터치하세요', W / 2, H / 2 + 75);
            }
            ctx.textAlign = 'left';
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        resizeCanvas();
        resetGame();
        gameState = 'START';
        loop();
    </script>
</body>
</html>
"""

# .replace()를 사용해 자바스크립트 변수를 안전하게 주입
game_html = game_html.replace("__IS_LOGGED_IN__", is_logged_in_val)
game_html = game_html.replace("__USER_UID__", user_uid_val)
game_html = game_html.replace("__USER_NAME__", user_name_val)

# Streamlit HTML 컴포넌트 출력
components.html(game_html, height=850)