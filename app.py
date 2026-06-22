# app.py
import streamlit as st
import json
import random
from supabase import create_client, Client
from hero import Hero

# --- НАСТРОЙКА БАЗЫ ДАННЫХ SUPABASE ---
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "ВСТАВЬ_СЮДА_СКОПИРОВАННЫЙ_КЛЮЧ"

# Инициализируем подключение к базе данных
@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# --- Конфигурация мобильного интерфейса сайта ---
st.set_page_config(page_title="Моя Реальная Жизнь RPG", page_icon="🎮", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #191923; color: #F0F0FA; }
    div[data-testid="stMetricValue"] { color: #F1C40F !important; font-size: 24px !important; }
    div[data-testid="stMetricDelta"] { color: #F0F0FA !important; font-size: 14px !important; }
    .quest-box { background-color: #232332; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #27AE60; }
    .quest-box-done { background-color: #1E1E28; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #64646E; opacity: 0.6; }
    .shop-box { background-color: #232332; padding: 15px; border-radius: 8px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# Перемешиваем генератор случайных чисел для уникальности квестов
random.seed()

# --- СИСТЕМА ЛОГИНА / АВТОРИЗАЦИИ ---
if "user_name" not in st.session_state:
    st.markdown("<h2 style='text-align: center; color: #F1C40F;'>🎮 ВХОД В LIFE RPG</h2>", unsafe_allow_html=True)
    username = st.text_input("Введите ваше имя (никнейм) для сохранения прогресса:", "").strip()
    
    if st.button("ВОЙТИ В ИГРУ", type="primary", use_container_width=True):
        if username:
            st.session_state.user_name = username
            
            # Проверяем, есть ли игрок в облачной базе данных
            response = supabase.table("players").select("*").eq("username", username).execute()
            player = Hero()
            player.name = username
            
            if isinstance(response.data, list) and len(response.data) > 0:
                # Если игрок найден, загружаем его данные из базы
                db_data = response.data[0]
                player.level = db_data.get("level", 1)
                player.xp = db_data.get("xp", 0)
                player.xp_to_next_level = db_data.get("xp_to_next_level", 100)
                player.gold = db_data.get("gold", 50)
                player.hp = db_data.get("hp", 100)
                player.skills = db_data.get("skills", {"strength": 0, "wisdom": 0, "order": 0})
                player.age_group = db_data.get("age_group", "adult")
                player.body_color_idx = db_data.get("body_idx", 0)
                player.hair_style_idx = db_data.get("hair_idx", 0)
                player.shirt_idx = db_data.get("shirt_idx", 0)
                player.daily_quests = db_data.get("daily_quests", [])
                player.completed_today = db_data.get("completed_today", [])
                player.boss_hp = db_data.get("boss_hp", 300)
                player.inventory = db_data.get("inventory", {"Куртка": 0, "Роба мага": 0, "Броня": 0})
                
                st.session_state.game_state = "gamehub"
            else:
                # Если новый игрок, отправляем на экран создания
                st.session_state.game_state = "creation"
                
            st.session_state.player = player
            st.rerun()
        else:
            st.error("Имя не может быть пустым!")
    st.stop()

player = st.session_state.player

def save_to_database():
    """Автоматически отправляет все данные текущего игрока в облачную базу данных"""
    data_to_save = {
        "username": player.name,
        "level": player.level,
        "xp": player.xp,
        "xp_to_next_level": player.xp_to_next_level,
        "gold": player.gold,
        "hp": player.hp,
        "skills": player.skills,
        "age_group": player.age_group,
        "body_idx": player.body_color_idx,
        "hair_idx": player.hair_style_idx,
        "shirt_idx": player.shirt_idx,
        "daily_quests": player.daily_quests,
        "completed_today": player.completed_today,
        "boss_hp": player.boss_hp,
        "inventory": player.inventory
    }
    # Команда upsert обновляет строку, если имя совпадает, или создает новую, если игрока еще нет
    supabase.table("players").upsert(data_to_save, on_conflict="username").execute()

# ==========================================
# ЭКРАН 1: СОЗДАНИЕ ПЕРСОНАЖА
# ==========================================
if st.session_state.game_state == "creation":
    st.markdown(f"<h2 style='text-align: center; color: #27AE60;'>ПРИВЕТ, {player.name.upper()}!</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #F0F0FA;'>СОЗДАНИЕ ПЕРСОНАЖА</h3>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='text-align: center; font-size: 18px; background: #232332; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        🎭 Кожа: <span style='color: #F1C40F;'>{player.body_colors[player.body_color_idx]}</span><br>
        🦱 Волосы: <span style='color: #F1C40F;'>{player.hair_styles[player.hair_style_idx]}</span><br>
        👕 Одежда: <span style='color: #F1C40F;'>{player.shirts[player.shirt_idx]}</span>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🎭 КОЖА", use_container_width=True):
            player.next_body()
            st.rerun()
    with c2:
        if st.button("🦱 ВОЛОСЫ", use_container_width=True):
            player.next_hair()
            st.rerun()
    with c3:
        if st.button("👕 ОДЕЖДА", use_container_width=True):
            player.next_shirt()
            st.rerun()
            
    if st.button("👦 ВЫБРАТЬ: ПОДРОСТКИ", use_container_width=True):
        player.age_group = "teen"
        st.toast("Выбрана группа: Подростки")
        
    if st.button("🟢 НАЧАТЬ ИГРУ", type="primary", use_container_width=True):
        player.generate_5_quests()
        save_to_database()
        st.session_state.game_state = "gamehub"
        st.rerun()

# ==========================================
# ЭКРАН 2: ИГРОВОЙ ХАБ
# ==========================================
elif st.session_state.game_state == "gamehub":
    st.markdown(f"<h5 style='color: #888;'>Игрок: {player.name}</h5>", unsafe_allow_html=True)
    c_stat1, c_stat2 = st.columns(2)
    with c_stat1:
        st.metric(label="🏆 УРОВЕНЬ", value=player.level, delta=f"ОПЫТ: {player.xp} / {player.xp_to_next_level}")
    with c_stat2:
        st.metric(label="🪙 ЗОЛОТО", value=f"{player.gold} G", delta=f"❤️ ЗДОРОВЬЕ: {player.hp}", delta_color="inverse")
        
    c_nav1, c_nav2 = st.columns(2)
    with c_nav1:
        if st.button("🛍️ МАГАЗИН", type="primary", use_container_width=True):
            st.session_state.game_state = "shop"
            st.rerun()
    with c_nav2:
        if st.button("🚪 ВЫЙТИ", use_container_width=True):
            del st.session_state.user_name
            st.rerun()
            
    st.markdown("<hr style='margin: 15px 0; border-color: #333;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #27AE60; margin-bottom: 5px;'>[ ХАРАКТЕРИСТИКИ ]</h4>", unsafe_allow_html=True)
    st.markdown(f"💪 **СИЛА:** {player.skills.get('strength', 0)} | 🧠 **РАЗУМ:** {player.skills.get('wisdom', 0)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    boss_percent = max(0, min(100, int((player.boss_hp / 300) * 100)))
    st.progress(boss_percent / 100, text=f"👹 БОСС: {player.boss_name} ({player.boss_hp}/300 HP)")
    
    st.markdown("<hr style='margin: 15px 0; border-color: #333;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #F1C40F;'>[ КВЕСТЫ НА СЕГОДНЯ ]</h3>", unsafe_allow_html=True)
    
    for q in player.daily_quests:
        done = q["id"] in player.completed_today
        box_class = "quest-box-done" if done else "quest-box"
        
        st.markdown(f"""
        <div class="{box_class}">
            <span style="font-size: 17px; font-weight: bold; color: #F1C40F;">{q['title']}</span><br>
            <span style="font-size: 14px; color: #F0F0FA;">{q['text']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if not done:
            if st.button("ГОТОВО", key=f"q_{q['id']}", use_container_width=True):
                player.complete_quest(q["id"])
                save_to_database()
                st.rerun()
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# ==========================================
# ЭКРАН 3: МАГАЗИН ОДЕЖДЫ
# ==========================================
elif st.session_state.game_state == "shop":
    st.markdown("<h2 style='text-align: center; color: #F1C40F;'>🛍️ МАГАЗИН</h2>", unsafe_allow_html=True)
    st.metric(label="ВАШЕ ЗОЛОТО", value=f"{player.gold} 🪙")
    
    if st.button("⬅️ НАЗАД В ИГРУ", use_container_width=True):
        st.session_state.game_state = "gamehub"
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    items = [("Куртка", 1, "Дает +20% опыта"), ("Роба мага", 2, "Дает +50% опыта"), ("Броня", 3, "Удваивает опыт!")]
    
    for name, idx, desc in items:
        is_equipped = player.shirt_idx == idx
        has_item = player.inventory.get(name, 0) == 1
        
        st.markdown(f"""
        <div class="shop-box">
            <span style="font-size: 16px; font-weight: bold; color: #F1C40F;">{name.upper()}</span><br>
            <span style="font-size: 14px; color: #F0F0FA;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if is_equipped:
            st.button("🟢 НАДЕТО", key=f"sh_{idx}", disabled=True, use_container_width=True)
        else:
            btn_txt = "НАДЕТЬ" if has_item else f"КУПИТЬ {player.shop_prices[name]}G"
            if st.button(btn_txt, key=f"sh_{idx}", type="primary", use_container_width=True):
                player.buy_item(name, idx)
                save_to_database()
                st.rerun()
                st.markdown("", unsafe_allow_html=True)
