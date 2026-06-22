# app.py
import streamlit as st
import json
from hero import Hero

# Конфигурация мобильного интерфейса сайта
st.set_page_config(page_title="Моя Реальная Жизнь RPG", page_icon="🎮", layout="centered")

# Кастомный CSS для тёмной темы, красивых карточек и кнопок как в оригинале
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

# Инициализация персонажа в сессии конкретного пользователя браузера
if "player" not in st.session_state:
    player = Hero()
    
    # Пытаемся достать старые личные сохранения из локальной памяти браузера
    if "saved_rpg_data" in st.query_params:
        try:
            js_data = json.loads(st.query_params["saved_rpg_data"])
            with open("save_data.json", "w", encoding="utf-8") as f:
                json.dump(js_data, f, ensure_ascii=False)
            player.load_from_file()
        except:
            player.load_from_file()
    else:
        player.load_from_file()
        
    st.session_state.player = player

player = st.session_state.player

# Управляем экранами игры
if "game_state" not in st.session_state:
    st.session_state.game_state = "gamehub" if player.daily_quests else "creation"

def save_and_sync():
    """Сохраняет прогресс и выводит ссылку для сохранения в закладки телефона"""
    player.save_to_file()
    try:
        with open("save_data.json", "r", encoding="utf-8") as f:
            current_save = json.load(f)
        # Кодируем сохранение прямо в URL-адрес страницы
        st.query_params["saved_rpg_data"] = json.dumps(current_save, ensure_ascii=False)
    except:
        pass

# ==========================================
# 🧙‍♂️ ЭКРАН 1: СОЗДАНИЕ ПЕРСОНАЖА
# ==========================================
if st.session_state.game_state == "creation":
    st.markdown("<h2 style='text-align: center; color: #27AE60;'>СОЗДАНИЕ ПЕРСОНАЖА</h2>", unsafe_allow_html=True)
    
    # Визуальный аватар в вебе (текстовый аналог пиксель-арта)
    st.markdown(f"""
    <div style='text-align: center; font-size: 18px; background: #232332; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        👤 <b>Текущий облик героя:</b><br><br>
        🎭 Кожа: <span style='color: #F1C40F;'>{player.body_colors[player.body_color_idx]}</span><br>
        🦱 Волосы: <span style='color: #F1C40F;'>{player.hair_styles[player.hair_style_idx]}</span><br>
        👕 Одежда: <span style='color: #F1C40F;'>{player.shirts[player.shirt_idx]}</span>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🎭 ИЗМ. КОЖУ", use_container_width=True):
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
            
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("👦 ВЫБРАТЬ: ПОДРОСТКИ", use_container_width=True):
        player.age_group = "teen"
        st.toast("Возрастная группа изменена на: Подростки!")
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🟢 НАЧАТЬ ИГРУ", type="primary", use_container_width=True):
        player.generate_5_quests()
        save_and_sync()
        st.session_state.game_state = "gamehub"
        st.rerun()

# ==========================================
# 🎮 ЭКРАН 2: ИГРОВОЙ ХАБ
# ==========================================
elif st.session_state.game_state == "gamehub":
    # Верхняя статус-панель
    c_stat1, c_stat2 = st.columns(2)
    with c_stat1:
        st.metric(label="🏆 УРОВЕНЬ", value=player.level, delta=f"ОПЫТ: {player.xp} / {player.xp_to_next_level}")
    with c_stat2:
        st.metric(label="🪙 ЗОЛОТО", value=f"{player.gold} G", delta=f"❤️ ЗДОРОВЬЕ: {player.hp}", delta_color="inverse")
        
    # Навигационные мобильные кнопки
    c_nav1, c_nav2 = st.columns(2)
    with c_nav1:
        if st.button("🛍️ МАГАЗИН", type="primary", use_container_width=True):
            st.session_state.game_state = "shop"
            st.rerun()
    with c_nav2:
        if st.button("🔴 СБРОС", use_container_width=True):
            st.session_state.player = Hero()
            st.session_state.player.save_to_file()
            st.query_params.clear()
            st.session_state.game_state = "creation"
            st.rerun()
            
    st.markdown("<hr style='margin: 15px 0; border-color: #333;'>", unsafe_allow_html=True)
    
    # Характеристики персонажа и Босс
    st.markdown("<h4 style='color: #27AE60; margin-bottom: 5px;'>[ ХАРАКТЕРИСТИКИ ]</h4>", unsafe_allow_html=True)
    st.markdown(f"💪 **СИЛА:** {player.skills.get('strength', 0)} | 🧠 **РАЗУМ:** {player.skills.get('wisdom', 0)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    boss_percent = max(0, min(100, int((player.boss_hp / 300) * 100)))
    st.progress(boss_percent / 100, text=f"👹 БОСС: {player.boss_name} ({player.boss_hp}/300 HP)")
    
    st.markdown("<hr style='margin: 15px 0; border-color: #333;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #F1C40F;'>[ КВЕСТЫ НА СЕГОДНЯ ]</h3>", unsafe_allow_html=True)
    
    # Вывод карточек квестов
    if not player.daily_quests:
        st.write("Квесты отсутствуют. Нажмите кнопку Сброс для создания.")
        
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
                save_and_sync()
                st.rerun()
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# ==========================================
# 🛍️ ЭКРАН 3: МАГАЗИН ОДЕЖДЫ
# ==========================================
elif st.session_state.game_state == "shop":
    st.markdown("<h2 style='text-align: center; color: #F1C40F;'>🛍️ МАГАЗИН ОДЕЖДЫ</h2>", unsafe_allow_html=True)
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
                save_and_sync()
                st.rerun()
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
