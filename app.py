import os
import sys
import sqlite3
import datetime
import random
import re
import json
from flask import Flask, render_template, request, jsonify, session, make_response

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = Flask(__name__, 
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))
app.secret_key = 'xiyu_os_kernel_v7_0_7'

# Data files should remain in the same directory as the EXE for persistence
BASE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
DB_FILE = os.path.join(BASE_DIR, 'os_kernel.db')
# We keep UPLOAD_FOLDER relative to the EXE for persistence
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

DEFAULT_WALLPAPER = "https://api.dujin.org/bing/1920.php"
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'avatars'))
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'chat'))
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'space'))

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT, uid INTEGER UNIQUE, avatar TEXT DEFAULT '', qq TEXT, bio TEXT, theme TEXT DEFAULT 'dark', wallpaper TEXT DEFAULT '{}', sys_color TEXT DEFAULT '#0078d4', icon_size TEXT DEFAULT '80', dock_scale REAL DEFAULT 1.0, di_show INTEGER DEFAULT 1, dev_mode INTEGER DEFAULT 0, exp INTEGER DEFAULT 0, is_vip INTEGER DEFAULT 0, last_sign TEXT DEFAULT '', lat REAL, lng REAL, created_at TEXT)".format(DEFAULT_WALLPAPER))
    c.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, content TEXT, owner TEXT, type TEXT DEFAULT 'file', parent_id INTEGER DEFAULT 0, is_desktop INTEGER DEFAULT 0, is_deleted INTEGER DEFAULT 0, pos_x INTEGER DEFAULT 0, pos_y INTEGER DEFAULT 0, is_autostart INTEGER DEFAULT 0, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS apps (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, icon TEXT, description TEXT, code TEXT, author TEXT, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT DEFAULT 'group', content TEXT, type TEXT DEFAULT 'text', created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS sys_config (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS friend_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, status TEXT DEFAULT 'pending', created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS friends (user1 TEXT, user2 TEXT, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS moments (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, content TEXT, media TEXT DEFAULT '[]', likes TEXT DEFAULT '[]', comments TEXT DEFAULT '[]', created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, author TEXT, author_qq TEXT, category TEXT DEFAULT '全部', likes INTEGER DEFAULT 0, stars INTEGER DEFAULT 0, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS emails (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, title TEXT, content TEXT, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS notes (username TEXT PRIMARY KEY, content TEXT, updated_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS timetables (username TEXT PRIMARY KEY, content TEXT, updated_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS follows (follower TEXT, followed TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS post_actions (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, action_type TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS shares (share_code TEXT PRIMARY KEY, file_id INTEGER, owner TEXT, created_at TEXT, views INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS recharge_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, amount INTEGER, status TEXT DEFAULT 'pending', created_at TEXT, reviewed_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS red_envelopes (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, amount INTEGER, count INTEGER, type TEXT, claimed_by TEXT DEFAULT '[]', created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, author TEXT, author_qq TEXT, content TEXT, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS recent_files (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, file_id INTEGER, access_time TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS todos (username TEXT PRIMARY KEY, content TEXT, updated_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS chat_reports (id INTEGER PRIMARY KEY AUTOINCREMENT, reporter TEXT, reported TEXT, reason TEXT, msg_id INTEGER, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS official_accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, icon TEXT, color TEXT, description TEXT, owner TEXT, status TEXT DEFAULT 'pending', created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS oa_articles (id INTEGER PRIMARY KEY AUTOINCREMENT, oa_id INTEGER, title TEXT, content TEXT, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS daily_tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, reward INTEGER, type TEXT, target_count INTEGER DEFAULT 1)")
    c.execute("CREATE TABLE IF NOT EXISTS user_tasks (username TEXT, task_id INTEGER, count INTEGER DEFAULT 0, is_claimed INTEGER DEFAULT 0, date TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS oa_follows (oa_id INTEGER, username TEXT, created_at TEXT, PRIMARY KEY(oa_id, username))")
    c.execute("CREATE TABLE IF NOT EXISTS space_comments (id INTEGER PRIMARY KEY AUTOINCREMENT, moment_id INTEGER, author TEXT, content TEXT, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS chat_favorites (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, message_id INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    
    columns_oa = [col['name'] for col in c.execute("PRAGMA table_info(official_accounts)").fetchall()]
    if 'hulling_code' not in columns_oa: c.execute("ALTER TABLE official_accounts ADD COLUMN hulling_code TEXT")
    if 'page_config' not in columns_oa: c.execute("ALTER TABLE official_accounts ADD COLUMN page_config TEXT DEFAULT '{}'")
    if 'bot_enabled' not in columns_oa: c.execute("ALTER TABLE official_accounts ADD COLUMN bot_enabled INTEGER DEFAULT 0")
    if 'bot_config' not in columns_oa: c.execute("ALTER TABLE official_accounts ADD COLUMN bot_config TEXT DEFAULT '{}'")
    if 'avatar' not in columns_oa: c.execute("ALTER TABLE official_accounts ADD COLUMN avatar TEXT")


    columns_u = [col['name'] for col in c.execute("PRAGMA table_info(users)").fetchall()]
    if 'lat' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN lat REAL")
    if 'lng' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN lng REAL")
    if 'sys_color' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN sys_color TEXT DEFAULT '#0078d4'")
    if 'icon_size' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN icon_size TEXT DEFAULT '80'")
    if 'storage_limit' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN storage_limit INTEGER DEFAULT 52428800")
    if 'vip_expire' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN vip_expire TEXT")
    if 'balance' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN balance INTEGER DEFAULT 0")
    if 'vip_tier' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN vip_tier INTEGER DEFAULT 0")
    if 'loading_style' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN loading_style TEXT DEFAULT 'default'")
    if 'dev_mode' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN dev_mode INTEGER DEFAULT 0")
    if 'dock_scale' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN dock_scale REAL DEFAULT 1.0")
    if 'di_show' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN di_show INTEGER DEFAULT 1")
    if 'win_radius' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN win_radius INTEGER DEFAULT 14")
    if 'win_blur' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN win_blur INTEGER DEFAULT 15")
    if 'win_opacity' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN win_opacity REAL DEFAULT 0.85")
    if 'font_main' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN font_main TEXT DEFAULT 'Outfit'")
    if 'win_title_bg' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN win_title_bg TEXT DEFAULT ''")
    if 'taskbar_align' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN taskbar_align TEXT DEFAULT 'flex-start'")
    if 'icon_filter' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN icon_filter TEXT DEFAULT 'none'")
    if 'dock_style' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN dock_style TEXT DEFAULT 'None'")
    if 'tb_opacity' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN tb_opacity REAL DEFAULT 0.85")
    if 'sm_blur' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN sm_blur INTEGER DEFAULT 40")
    if 'master_volume' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN master_volume INTEGER DEFAULT 80")
    if 'anim_enabled' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN anim_enabled INTEGER DEFAULT 1")
    if 'font_scale' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN font_scale REAL DEFAULT 1.0")
    if 'uid' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN uid INTEGER UNIQUE")
    if 'avatar' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT ''")
    if 'is_banned' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")
    if 'chat_theme' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN chat_theme TEXT DEFAULT 'default'")
    if 'chat_bg' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN chat_bg TEXT")
    if 'chat_bubble_color' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN chat_bubble_color TEXT DEFAULT '#0099ff'")
    if 'level' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1")
    if 'exp' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN exp INTEGER DEFAULT 0")
    if 'chat_vip' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN chat_vip INTEGER DEFAULT 0")
    if 'mc_ip' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN mc_ip TEXT")
    if( 'chat_vip_expire' not in columns_u): c.execute("ALTER TABLE users ADD COLUMN chat_vip_expire TEXT")
    if( 'nameplate' not in columns_u): c.execute("ALTER TABLE users ADD COLUMN nameplate TEXT DEFAULT ''")
    if 'chat_bubble_skin' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN chat_bubble_skin TEXT DEFAULT 'default'")
    if 'mc_uuid' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN mc_uuid TEXT")
    if 'mc_name' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN mc_name TEXT")
    if 'gold_balance' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN gold_balance INTEGER DEFAULT 0")
    if 'pending_notifications' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN pending_notifications TEXT DEFAULT '[]'")
    if 'mc_pos' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN mc_pos TEXT")
    if 'mc_health' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN mc_health INTEGER DEFAULT 20")
    if 'flight_time_left' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN flight_time_left INTEGER DEFAULT 7200")
    if 'last_flight_reset' not in columns_u: c.execute("ALTER TABLE users ADD COLUMN last_flight_reset TEXT")
    
    c.execute("CREATE TABLE IF NOT EXISTS mc_server_status (id INTEGER PRIMARY KEY, tps REAL, ram_used INTEGER, ram_total INTEGER, updated_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS mc_shop_items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, icon TEXT, price INTEGER, description TEXT, command TEXT, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS mc_shop_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, item_id INTEGER, price INTEGER, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS mc_market_listings (id INTEGER PRIMARY KEY AUTOINCREMENT, seller TEXT, item_name TEXT, item_data TEXT, price INTEGER, price_type TEXT, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS mc_binding_codes (mc_name TEXT, mc_uuid TEXT, code TEXT UNIQUE, expires_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS mc_remote_commands (id INTEGER PRIMARY KEY AUTOINCREMENT, mc_uuid TEXT, command TEXT, status TEXT DEFAULT 'pending', created_at TEXT)")
    
    
    columns_m = [col['name'] for col in c.execute("PRAGMA table_info(messages)").fetchall()]
    if 'type' not in columns_m: c.execute("ALTER TABLE messages ADD COLUMN type TEXT DEFAULT 'text'")
    if 'voice_duration' not in columns_m: c.execute("ALTER TABLE messages ADD COLUMN voice_duration INTEGER DEFAULT 0")
    if 'file_id' not in columns_m: c.execute("ALTER TABLE messages ADD COLUMN file_id INTEGER")
    
    columns_p = [col['name'] for col in c.execute("PRAGMA table_info(posts)").fetchall()]
    if 'category' not in columns_p: c.execute("ALTER TABLE posts ADD COLUMN category TEXT DEFAULT '全部'")
    if 'media' not in columns_p: c.execute("ALTER TABLE posts ADD COLUMN media TEXT DEFAULT '[]'")
    
    columns_s = [col['name'] for col in c.execute("PRAGMA table_info(shares)").fetchall()]
    if 'views' not in columns_s: c.execute("ALTER TABLE shares ADD COLUMN views INTEGER DEFAULT 0")
    
    columns_f = [col['name'] for col in c.execute("PRAGMA table_info(files)").fetchall()]
    if 'is_autostart' not in columns_f: c.execute("ALTER TABLE files ADD COLUMN is_autostart INTEGER DEFAULT 0")

    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if c.execute("SELECT count(*) FROM apps WHERE name='Minecraft'").fetchone()[0] == 0:
        mc_code = "XiYuSDK.createWindow('mc_game', 'Minecraft', '<div style=\"width:100%;height:100%;\"><iframe src=\"https://eaglercraft.ir/zh/\" style=\"width:100%;height:100%;border:none;background:#000;\"></iframe></div>', 1050, 700);"
        c.execute("INSERT INTO apps (name, icon, description, code, author, created_at) VALUES ('Minecraft', 'fas fa-cubes', 'Minecraft', ?, 'System', ?)", (mc_code, dt))

    if c.execute("SELECT count(*) FROM apps WHERE name='哔哩哔哩'").fetchone()[0] == 0:
        bili_code = "WM.create('bilibili', '哔哩哔哩', '<iframe src=\"https://m.bilibili.com\" style=\"width:100%;height:100%;border:none;background:#fff\"></iframe>', 450, 750);"
        c.execute("INSERT INTO apps (name, icon, description, code, author, created_at) VALUES ('哔哩哔哩', 'fas fa-tv', 'B站', ?, 'System', ?)", (bili_code, dt))
    conn.commit()

def check_installed():
    if not os.path.exists(DB_FILE): return False
    try: return get_db().execute("SELECT count(*) FROM users WHERE role='admin'").fetchone()[0] > 0
    except: return False

@app.before_request
def security_check():
    if not hasattr(app, 'db_initialized'):
        init_db()
        app.db_initialized = True
    for k, v in request.args.items():
        if re.search(r"(select|union|insert|drop|truncate|--|;)", str(v).lower()):
            return jsonify({'success': False, 'message': '非法请求'})
    
    # Request logging for debugging
    if request.path.startswith('/api/mc'):
        print(f"[MC_DEBUG] {request.method} {request.path} - Args: {request.args} - Body: {request.json if request.is_json else 'None'}")

@app.route('/')
def index(): return render_template('index.html')

@app.route('/manifest.json')
def serve_manifest(): return app.send_static_file('manifest.json')

@app.route('/sw.js')
def serve_sw(): return app.send_static_file('sw.js')

@app.route('/api/sys/status')
def sys_status():
    conn = get_db()
    try: notice = conn.execute("SELECT value FROM sys_config WHERE key='notice'").fetchone()
    except: notice = None
    return jsonify({'installed': check_installed(), 'notice': str(notice['value']) if notice else ''})

@app.route('/api/sys/install', methods=['POST'])
def sys_install():
    if check_installed(): return jsonify({'success': False})
    data = request.json
    conn = get_db()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('sys_name', '汐语OS 7.0.7')")
    # Assign first UID 10001 to admin
    conn.execute("INSERT INTO users (username, password, role, uid, qq, bio, is_vip, lat, lng, created_at) VALUES (?, ?, 'admin', 10001, ?, '系统管理员', 1, ?, ?, ?)", (data['username'], data['password'], data.get('qq',''), random.uniform(-40, 60), random.uniform(-150, 150), dt))
    conn.commit()
    return jsonify({'success': True})

def get_computed_avatar(u):
    if not u: return 'https://cravatar.cn/avatar/?d=mp'
    
    # Priority 1: Custom uploaded avatar or external link
    if u.get('avatar'): 
        av = u['avatar']
        if av.startswith('/static/') or av.startswith('http') or av.startswith('data:') or av.startswith('fa-') or av.startswith('fas ') or av.startswith('fab '):
            return av
            
    # Priority 2: OA Icon
    if u.get('icon'):
        return u['icon']
        
    # Priority 3: QQ Avatar
    if u.get('qq'):
        qq = str(u['qq']).strip()
        if qq and qq != 'None': return f"https://q1.qlogo.cn/g?b=qq&nk={qq}&s=100"

    # Priority 4: Minecraft skin as fallback
    if u.get('mc_uuid'):
        return f"https://crafatar.com/avatars/{u['mc_uuid']}?size=100&overlay"
        
    return "/static/icons/user.png"

def link_mc_account(conn, username, code):
    if not code: return True
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bind_data = conn.execute("SELECT * FROM mc_binding_codes WHERE code=? AND expires_at > ?", (code, now)).fetchone()
    if not bind_data: return False
    
    mc_name = bind_data['mc_name']
    mc_uuid = bind_data['mc_uuid']
    
    # Check if this MC account is already bound
    existing = conn.execute("SELECT id FROM users WHERE mc_uuid=?", (mc_uuid,)).fetchone()
    if existing: return False
    
    conn.execute("UPDATE users SET mc_name=?, mc_uuid=? WHERE username=?", (mc_name, mc_uuid, username))
    conn.execute("DELETE FROM mc_binding_codes WHERE code=?", (code,))
    return True

@app.route('/api/user/auth', methods=['POST'])
def auth():
    data = request.json
    act = data.get('action')
    conn = get_db()
    if act == 'register':
        if conn.execute("SELECT 1 FROM users WHERE username=?", (data['username'],)).fetchone(): return jsonify({'success': False, 'message': '账号已存在'})
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Generate UID - handle case if it is first user but via register
        last_u = conn.execute("SELECT MAX(uid) FROM users").fetchone()
        last_uid = last_u[0] if last_u else None
        new_uid = (last_uid if last_uid else 10000) + 1
        conn.execute("INSERT INTO users (username, password, role, uid, qq, bio, lat, lng, created_at) VALUES (?, ?, 'user', ?, ?, '这个人很懒，什么都没写', ?, ?, ?)", (data['username'], data['password'], new_uid, data.get('qq',''), random.uniform(-50, 50), random.uniform(-160, 160), dt))
        conn.commit()
        return jsonify({'success': True, 'uid': new_uid})
    elif act == 'login':
        u = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (data['username'], data['password'])).fetchone()
        if u:
            if int(u['is_banned'] or 0) == 1: return jsonify({'success': False, 'message': '您的账号已被封禁，无法登录。'})
            # Update last login IP for Minecraft auto-login
            conn.execute("UPDATE users SET mc_ip=? WHERE username=?", (request.remote_addr, data['username']))
            conn.commit()
            session['user'] = u['username']
            session['role'] = u['role']
            u_dict = dict(u)
            u_dict['avatar'] = get_computed_avatar(u_dict)
            return jsonify({'success': True, 'data': u_dict})
        return jsonify({'success': False, 'message': '账号或密码错误'})

@app.route('/api/user/action', methods=['POST'])
def user_action():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    conn = get_db()
    
    def calculate_level(exp):
        lv_map = [
            (8, 2800), (7, 2100), (6, 1500), (5, 1000), 
            (4, 600), (3, 300), (2, 100), (1, 0)
        ]
        for lv, threshold in lv_map:
            if exp >= threshold: return lv
        return 1

    if act == 'info':
        target = data.get('target', session['user'])
        u = conn.execute("SELECT * FROM users WHERE username=?", (target,)).fetchone()
        
        if u:
            u_dict = dict(u)
            u_dict['avatar'] = get_computed_avatar(u_dict)
            
            # Social Stats
            f_ing = conn.execute("SELECT count(*) as c FROM follows WHERE follower=?", (target,)).fetchone()['c']
            f_ers = conn.execute("SELECT count(*) as c FROM follows WHERE followed=?", (target,)).fetchone()['c']
            u_dict['following_count'] = f_ing
            u_dict['followers_count'] = f_ers
            
            # Follow status relative to current user
            if session['user'] != target:
                is_f = conn.execute("SELECT 1 FROM follows WHERE follower=? AND followed=?", (session['user'], target)).fetchone()
                u_dict['is_following'] = True if is_f else False
            
            u_dict['level'] = calculate_level(int(u_dict['exp'] or 0))
            return jsonify({'success': True, 'data': u_dict})
        return jsonify({'success': False})
    elif act == 'settings':
        # Handle password change separately for security if provided
        new_pw = data.get('password')
        if new_pw:
            conn.execute("UPDATE users SET password=? WHERE username=?", (new_pw, session['user']))
        
        conn.execute("UPDATE users SET qq=COALESCE(?,qq), bio=COALESCE(?,bio), theme=COALESCE(?,theme), wallpaper=COALESCE(?,wallpaper), sys_color=COALESCE(?,sys_color), icon_size=COALESCE(?,icon_size), loading_style=COALESCE(?,loading_style), dev_mode=COALESCE(?,dev_mode), dock_scale=COALESCE(?,dock_scale), di_show=COALESCE(?,di_show), win_radius=COALESCE(?,win_radius), win_blur=COALESCE(?,win_blur), win_opacity=COALESCE(?,win_opacity), font_main=COALESCE(?,font_main), win_title_bg=COALESCE(?,win_title_bg), taskbar_align=COALESCE(?,taskbar_align), icon_filter=COALESCE(?,icon_filter), dock_style=COALESCE(?,dock_style), tb_opacity=COALESCE(?,tb_opacity), sm_blur=COALESCE(?,sm_blur), master_volume=COALESCE(?,master_volume), anim_enabled=COALESCE(?,anim_enabled), font_scale=COALESCE(?,font_scale), chat_theme=COALESCE(?,chat_theme), chat_bg=COALESCE(?,chat_bg), chat_bubble_color=COALESCE(?,chat_bubble_color) WHERE username=?", (data.get('qq'), data.get('bio'), data.get('theme'), data.get('wallpaper'), data.get('sys_color'), data.get('icon_size'), data.get('loading_style'), data.get('dev_mode'), data.get('dock_scale'), data.get('di_show'), data.get('win_radius'), data.get('win_blur'), data.get('win_opacity'), data.get('font_main'), data.get('win_title_bg'), data.get('taskbar_align'), data.get('icon_filter'), data.get('dock_style'), data.get('tb_opacity'), data.get('sm_blur'), data.get('master_volume'), data.get('anim_enabled'), data.get('font_scale'), data.get('chat_theme'), data.get('chat_bg'), data.get('chat_bubble_color'), session['user']))
        conn.commit()
        return jsonify({'success': True})
    elif act == 'profile':
        target = data.get('username', session['user'])
        u = conn.execute("SELECT * FROM users WHERE username=?", (target,)).fetchone()
        if u:
            u_dict = dict(u)
            u_dict['avatar'] = get_computed_avatar(u_dict)
            u_dict['following_count'] = conn.execute("SELECT count(*) as c FROM follows WHERE follower=?", (target,)).fetchone()['c']
            u_dict['follower_count'] = conn.execute("SELECT count(*) as c FROM follows WHERE followed=?", (target,)).fetchone()['c']
            return jsonify({'success': True, 'user': u_dict})
        return jsonify({'success': False, 'message': '用户不存在'})
        return jsonify({'success': True})
    elif act == 'sign':
        today = datetime.date.today().isoformat()
        u = conn.execute("SELECT last_sign, mc_uuid FROM users WHERE username=?", (session['user'],)).fetchone()
        if u and u['last_sign'] == today: return jsonify({'success': False, 'message': '今天已经签到过啦'})
        
        gold_msg = ""
        if u['mc_uuid']:
            conn.execute("UPDATE users SET gold_balance = gold_balance + 100 WHERE username=?", (session['user'],))
            gold_msg = "，金币+100"
            
        conn.execute("UPDATE users SET exp = exp + 50, last_sign = ? WHERE username=?", (today, session['user']))
        # Increment daily task
        conn.execute("INSERT OR IGNORE INTO user_tasks (username, task_id, count, date) SELECT ?, id, 0, ? FROM daily_tasks WHERE type='sign'", (session['user'], today))
        conn.execute("UPDATE user_tasks SET count = count + 1 WHERE username=? AND date=? AND task_id IN (SELECT id FROM daily_tasks WHERE type='sign')", (session['user'], today))
        conn.commit()
        # Get updated data
        updated = conn.execute("SELECT exp, last_sign FROM users WHERE username=?", (session['user'],)).fetchone()
        u_exp = int(updated['exp'] or 0)
        return jsonify({
            'success': True, 
            'message': f'签到成功，经验+50{gold_msg}', 
            'exp': u_exp,
            'level': calculate_level(u_exp),
            'last_sign': updated['last_sign']
        })
    # Remove legacy recharge to enforce "recharge only" for Star Coins
    elif act == 'sign':
        u = conn.execute("SELECT * FROM users WHERE username=?", (session['user'],)).fetchone()
        u_dict = dict(u)
        u_dict['avatar'] = get_computed_avatar(u_dict)
        return jsonify({'success': True, 'data': u_dict})
    elif act == 'buy_vip':
        u = conn.execute("SELECT balance, vip_expire, dev_mode FROM users WHERE username=?", (session['user'],)).fetchone()
        tier = data.get('tier', 1)
        prices = {1: 15, 2: 30, 3: 50}
        cost = prices.get(tier, 15)
        
        if u and u['balance'] >= cost:
            today = datetime.date.today()
            cur_expire = u['vip_expire']
            if cur_expire:
                try: base = max(datetime.datetime.strptime(cur_expire, "%Y-%m-%d").date(), today)
                except: base = today
            else: base = today
            new_expire = (base + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            # VIP Storage benefits: Bronze +2GB, Silver +5GB, Gold +10GB
            storage_bonus = {1: 2*1024*1024*1024, 2: 5*1024*1024*1024, 3: 10*1024*1024*1024}.get(tier, 0)
            conn.execute("UPDATE users SET balance = balance - ?, is_vip = 1, vip_tier = ?, vip_expire = ?, dev_mode = 1, storage_limit = storage_limit + ? WHERE username=?", (cost, tier, new_expire, storage_bonus, session['user']))
            conn.commit()
            updated = conn.execute("SELECT * FROM users WHERE username=?", (session['user'],)).fetchone()
            return jsonify({'success': True, 'message': f'开通成功！增加{storage_bonus//(1024**3)}GB云盘空间，会员有效期至 {new_expire}', 'data': dict(updated)})
        return jsonify({'success': False, 'message': f'余额不足{cost}星币，请先充值'})
    elif act == 'social_follow':
        target = data.get('target')
        if not target or target == session['user']: return jsonify({'success': False})
        is_f = conn.execute("SELECT 1 FROM follows WHERE follower=? AND followed=?", (session['user'], target)).fetchone()
        if is_f:
            conn.execute("DELETE FROM follows WHERE follower=? AND followed=?", (session['user'], target))
            msg = "已取消关注"
            f_status = False
        else:
            conn.execute("INSERT INTO follows (follower, followed) VALUES (?, ?)", (session['user'], target))
            msg = "关注成功"
            f_status = True
        conn.commit()
        return jsonify({'success': True, 'message': msg, 'is_following': f_status})
    elif act == 'search':
        query = data.get('query', '')
        if not query: return jsonify({'success': True, 'users': []})
        rows = conn.execute("SELECT username, uid, avatar, mc_uuid, qq, bio FROM users WHERE username LIKE ? OR uid LIKE ? LIMIT 20", (f'%{query}%', f'%{query}%')).fetchall()
        users = []
        for r in rows:
            u_dict = dict(r)
            u_dict['avatar'] = get_computed_avatar(u_dict)
            users.append(u_dict)
        return jsonify({'success': True, 'users': users})
    elif act == 'social_list':
        # Get following or followers
        ltype = data.get('type', 'following')
        target = data.get('target') or data.get('username') or session['user']
        if ltype == 'following':
            rows = conn.execute("SELECT u.* FROM users u JOIN follows f ON u.username = f.followed WHERE f.follower=?", (target,)).fetchall()
        else:
            rows = conn.execute("SELECT u.* FROM users u JOIN follows f ON u.username = f.follower WHERE f.followed=?", (target,)).fetchall()
        
        users = []
        for r in rows:
            u_dict = dict(r)
            u_dict['avatar'] = get_computed_avatar(u_dict)
            users.append(u_dict)
        return jsonify({'success': True, 'users': users})
    elif act == 'follow':
        target = data.get('target')
        if not target or target == session['user']: return jsonify({'success': False, 'message': '目标不合法'})
        try:
            conn.execute("INSERT INTO follows (follower, followed) VALUES (?, ?)", (session['user'], target))
            conn.commit()
            return jsonify({'success': True, 'message': '已关注'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': '已经关注过了'})
    elif act == 'unfollow':
        target = data.get('target')
        conn.execute("DELETE FROM follows WHERE follower=? AND followed=?", (session['user'], target))
        conn.commit()
        return jsonify({'success': True, 'message': '已取消关注'})
    elif act == 'profile':
        target = data.get('username') or data.get('target')
        if not target: return jsonify({'success': False, 'message': '用户未指定'})
        
        # Try finding in users first
        u = conn.execute("SELECT username, uid, avatar, mc_uuid, bio, exp, is_vip, chat_vip, nameplate, qq FROM users WHERE username=?", (target,)).fetchone()
        if u:
            u_dict = dict(u)
            u_dict['avatar'] = get_computed_avatar(u_dict)
            u_dict['following_count'] = conn.execute("SELECT count(*) FROM follows WHERE follower=?", (target,)).fetchone()[0]
            u_dict['follower_count'] = conn.execute("SELECT count(*) FROM follows WHERE followed=?", (target,)).fetchone()[0]
            u_dict['is_following'] = conn.execute("SELECT 1 FROM follows WHERE follower=? AND followed=?", (session['user'], target)).fetchone() is not None
            u_dict['level'] = calculate_level(int(u_dict['exp'] or 0))
            return jsonify({'success': True, 'user': u_dict})
            
        # If not user, try finding in official_accounts
        oa = conn.execute("SELECT id as uid, name as username, avatar, icon, description as bio, 'Official Account' as nameplate FROM official_accounts WHERE name=? OR id=?", (target, target)).fetchone()
        if oa:
            # Deep copy to plain dict to avoid strict type restrictions
            import json
            oa_data = json.loads(json.dumps(dict(oa)))
            if not oa_data.get('avatar'): oa_data['avatar'] = oa_data.get('icon')
            oa_data['avatar'] = get_computed_avatar(oa_data)
            
            oa_id = oa_data['uid']
            oa_data['following_count'] = 0
            oa_data['follower_count'] = conn.execute("SELECT count(*) FROM oa_follows WHERE oa_id=?", (oa_id,)).fetchone()[0]
            oa_data['is_following']# --- Minecraft Integration APIs ---
@app.route('/api/mc/auth', methods=['GET', 'POST'])
def mc_auth():
    conn = get_db()
    if request.method == 'GET':
        uuid = request.args.get('mc_uuid')
        if not uuid: return jsonify({'success': False})
        user = conn.execute("SELECT username, balance, gold_balance, is_vip, vip_tier FROM users WHERE mc_uuid=?", (uuid,)).fetchone()
        if user:
            return jsonify({
                'success': True,
                'username': user['username'],
                'balance': user['balance'],
                'gold_balance': user['gold_balance'],
                'is_vip': bool(user['is_vip']),
                'vip_tier': user['vip_tier'] or 0
            })
        return jsonify({'success': False})

    data = request.json
    uuid = data.get('mc_uuid')
    name = data.get('name')
    current_ip = data.get('ip')
    refresh = data.get('refresh', False)
    
    # Try finding by UUID first, then by name (for nickname-based binding auto-sync)
    user = conn.execute("SELECT username, balance, gold_balance, mc_ip, mc_uuid, is_vip, vip_tier FROM users WHERE mc_uuid=? OR (mc_name=? AND mc_uuid IS NULL)", (uuid, name)).fetchone()
    
    if user:
        # Auto-sync UUID if it was bound by name only
        if not user['mc_uuid'] and uuid:
            conn.execute("UPDATE users SET mc_uuid=? WHERE username=?", (uuid, user['username']))
            conn.commit()
            
        ip_match = (user['mc_ip'] == current_ip)
        return jsonify({
            'success': True, 
            'username': user['username'], 
            'balance': user['balance'],
            'gold_balance': user['gold_balance'],
            'is_vip': user['is_vip'],
            'vip_tier': user['vip_tier'],
            'ip_match': ip_match
        })
    
    # If not bound, return a binding code
    if refresh:
        conn.execute("DELETE FROM mc_binding_codes WHERE mc_name=? OR mc_uuid=?", (name, uuid))
        code = None # Force re-gen
    else:
        code_row = conn.execute("SELECT code FROM mc_binding_codes WHERE mc_name=? OR mc_uuid=?", (name, uuid)).fetchone()
        code = code_row['code'] if code_row else None

    if not code:
        import random, string
        code = ''.join(random.choices(string.digits, k=6))
        # 20 minutes expiration
        expires = (datetime.datetime.now() + datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT INTO mc_binding_codes (mc_name, mc_uuid, code, expires_at) VALUES (?, ?, ?, ?)", (name, uuid, code, expires))
        conn.commit()
    
    return jsonify({'success': False, 'message': 'NOT_BOUND', 'binding_code': code})

@app.route('/api/mc/bind', methods=['POST'])
def mc_bind():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    code = data.get('code')
    conn = get_db()
    
    # Verify code
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bind_data = conn.execute("SELECT * FROM mc_binding_codes WHERE code=? AND expires_at > ?", (code, now)).fetchone()
    if not bind_data:
        return jsonify({'success': False, 'message': '验证码错误或已过期'})
    
    mc_name = bind_data['mc_name']
    mc_uuid = bind_data['mc_uuid']
    
    # Check if this MC account is already bound
    existing = conn.execute("SELECT username FROM users WHERE mc_name=?", (mc_name,)).fetchone()
    if existing and existing['username'] != session['user']:
        return jsonify({'success': False, 'message': f'该 MC 账号已绑定到用户: {existing["username"]}'})
        
    conn.execute("UPDATE users SET mc_name=?, mc_uuid=? WHERE username=?", (mc_name, mc_uuid, session['user']))
    # Clean up code
    conn.execute("DELETE FROM mc_binding_codes WHERE code=?", (code,))
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/mc/verify_password', methods=['POST'])
def mc_verify_password():
    data = request.json
    uuid = data.get('mc_uuid')
    password = data.get('password')
    conn = get_db()
    user = conn.execute("SELECT username FROM users WHERE mc_uuid=? AND password=?", (uuid, password)).fetchone()
    if user: return jsonify({'success': True, 'username': user['username']})
    return jsonify({'success': False})

@app.route('/api/mc/bedrock_form', methods=['POST'])
def mc_bedrock_form():
    # Returns a JSON structure that the mod can use to build a Geyser Form
    return jsonify({
        'title': '汐语 OS 身份检查',
        'content': '检测到 IP 变动或未登录，请输入您的 OS 账户密码：',
        'input_placeholder': '密码'
    })

@app.route('/api/mc/chat', methods=['POST'])
def mc_chat():
    data = request.json
    sender = data.get('sender')
    content = data.get('content')
    mc_uuid = data.get('mc_uuid')
    
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    u = conn.execute("SELECT username FROM users WHERE mc_uuid=?", (mc_uuid,)).fetchone()
    display_name = f"[MC] {sender}"
    if u: display_name = f"[MC] {u['username']}"
    
    conn.execute("INSERT INTO messages (sender, receiver, content, type, created_at) VALUES (?, 'group', ?, 'mc_sync', ?)", (display_name, content, dt))
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/mc/market/list')
def mc_market_list():
    conn = get_db()
    listings = conn.execute("SELECT * FROM mc_market_listings ORDER BY created_at DESC").fetchall()
    return jsonify({'success': True, 'listings': [dict(l) for l in listings]})

@app.route('/api/mc/flight/claim', methods=['POST'])
def mc_flight_claim():
    data = request.json or {}
    mc_uuid = data.get('mc_uuid')
    
    conn = get_db()
    if mc_uuid:
        u = conn.execute("SELECT username, is_vip, vip_tier, last_flight_reset FROM users WHERE mc_uuid=?", (mc_uuid,)).fetchone()
    elif 'user' in session:
        u = conn.execute("SELECT username, is_vip, vip_tier, last_flight_reset FROM users WHERE username=?", (session['user'],)).fetchone()
    else:
        return jsonify({'success': False, 'message': '未登录'})

    if not u or not u['is_vip']: return jsonify({'success': False, 'message': '非VIP用户无法领取'})
    username = u['username']
    today = datetime.date.today().isoformat()
    if u['last_flight_reset'] == today: return jsonify({'success': False, 'message': '今日已领取，请明日再来'})
    
    tier = u['vip_tier']
    # Daily storage bonus: Tier 1: 10MB, Tier 2: 30MB, Tier 3: 100MB
    storage_reward = {1: 10*1024*1024, 2: 30*1024*1024, 3: 100*1024*1024}.get(tier, 10*1024*1024)
    
    conn.execute("UPDATE users SET flight_time_left=7200, storage_limit = storage_limit + ?, last_flight_reset=? WHERE username=?", 
                 (storage_reward, today, username))
    conn.commit()
    return jsonify({'success': True, 'message': f'领取成功！2小时飞行时长已入账，并额外获得 {storage_reward//(1024*1024)}MB 云盘容量奖励'})

@app.route('/api/mc/server/info', methods=['GET'])
def mc_market_post():
    data = request.json
    mc_uuid = data.get('mc_uuid')
    item_name = data.get('item_name')
    price = int(data.get('price', 0))
    # In a real mod, you'd store more complex item data (NBT) as a string
    
    conn = get_db()
    user = conn.execute("SELECT username FROM users WHERE mc_uuid=?", (mc_uuid,)).fetchone()
    if not user: return jsonify({'success': False, 'message': '未绑定账号'})
    
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Store item as lowercase for consistency
    item_key = item_name.lower()
    if not item_key.startswith('minecraft:'): item_key = 'minecraft:' + item_key
    
    conn.execute("INSERT INTO mc_market_listings (seller, item_name, price, price_type, created_at) VALUES (?, ?, ?, 'gold', ?)", (user['username'], item_key, price, dt))
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/mc/market/buy', methods=['POST'])
def mc_market_buy():
    data = request.json
    buyer_uuid = data.get('mc_uuid')
    listing_id = data.get('listing_id')
    
    conn = get_db()
    buyer = conn.execute("SELECT username, gold_balance FROM users WHERE mc_uuid=?", (buyer_uuid,)).fetchone()
    listing = conn.execute("SELECT * FROM mc_market_listings WHERE id=?", (listing_id,)).fetchone()
    
    if not buyer or not listing: return jsonify({'success': False, 'message': '数据错误'})
    if buyer['username'] == listing['seller']: return jsonify({'success': False, 'message': '不能购买自己的商品'})
    
    if buyer['gold_balance'] >= listing['price']:
        # Update balances
        conn.execute("UPDATE users SET gold_balance = gold_balance - ? WHERE username=?", (listing['price'], buyer['username']))
        conn.execute("UPDATE users SET gold_balance = gold_balance + ? WHERE username=?", (listing['price'], listing['seller']))
        # Remove listing
        conn.execute("DELETE FROM mc_market_listings WHERE id=?", (listing_id,))
        conn.commit()
        return jsonify({'success': True, 'item_name': listing['item_name']})
    return jsonify({'success': False, 'message': '金币不足'})

@app.route('/api/mc/status')
def mc_status():
    uuid = request.args.get('mc_uuid')
    conn = get_db()
    u = conn.execute("SELECT username, gold_balance, balance, is_vip, vip_tier, vip_expire, storage_limit, pending_notifications, flight_time_left, last_flight_reset FROM users WHERE mc_uuid=?", (uuid,)).fetchone()
    
    if not u:
        return jsonify({'success': False, 'message': 'Not bound'})

    # --- VIP Expiration Check ---
    is_vip = u['is_vip']
    tier = u['vip_tier']
    limit = u['storage_limit']
    if is_vip and u['vip_expire']:
        try:
            expire_date = datetime.datetime.strptime(u['vip_expire'], "%Y-%m-%d").date()
            if expire_date < datetime.date.today():
                # VIP Expired!
                bonus = {1: 2*1024*1024*1024, 2: 5*1024*1024*1024, 3: 10*1024*1024*1024}.get(tier, 0)
                is_vip = 0
                tier = 0
                limit = max(50*1024*1024, limit - bonus) # Ensure at least 50MB
                conn.execute("UPDATE users SET is_vip=0, vip_tier=0, storage_limit=? WHERE mc_uuid=?", (limit, uuid))
                conn.commit()
                # Reload u for consistency
                u = conn.execute("SELECT gold_balance, balance, is_vip, vip_tier, pending_notifications, flight_time_left, last_flight_reset FROM users WHERE mc_uuid=?", (uuid,)).fetchone()
        except Exception as e:
            print(f"Error checking VIP expire: {e}")
    
    # Process and clear pending notifications
    notifications = json.loads(u['pending_notifications'] or '[]')
    if notifications:
        conn.execute("UPDATE users SET pending_notifications = '[]' WHERE mc_uuid=?", (uuid,))
        conn.commit()

    # VIP Flight daily reset logic (7200s = 2h)
    today = datetime.date.today().isoformat()
    flight_time = u['flight_time_left']
    if u['is_vip'] and u['last_flight_reset'] != today:
        flight_time = 7200
        conn.execute("UPDATE users SET flight_time_left=7200, last_flight_reset=? WHERE mc_uuid=?", (today, uuid))
        conn.commit()
        
    # Process commands
    cmds = conn.execute("SELECT id, command FROM mc_remote_commands WHERE mc_uuid=? AND status='pending'", (uuid,)).fetchall()
    ret_cmds = []
    for c_row in cmds:
        ret_cmds.append({'id': c_row['id'], 'command': c_row['command']})
        conn.execute("UPDATE mc_remote_commands SET status='sent' WHERE id=?", (c_row['id'],))
        
    conn.commit()
    
    return jsonify({
        'success': True,
        'gold': u['gold_balance'],
        'coins': u['balance'],
        'is_vip': bool(u['is_vip']),
        'vip_tier': u['vip_tier'] or 0,
        'notifications': notifications,
        'flight_time': flight_time,
        'commands': ret_cmds
    })

@app.route('/api/mc/flight/sync', methods=['POST'])
def mc_flight_sync():
    data = request.json
    uuid = data.get('mc_uuid')
    time_left = data.get('time_left')
    conn = get_db()
    conn.execute("UPDATE users SET flight_time_left=? WHERE mc_uuid=?", (time_left, uuid))
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/mc/heartbeat', methods=['POST'])
def mc_heartbeat():
    data = request.json
    uuid = data.get('mc_uuid')
    tps = data.get('tps')
    ram_used = data.get('ram_used')
    ram_total = data.get('ram_total')
    
    conn = get_db()
    # Update player pos/health if provided (already exists in some form probably, but let's be safe)
    if 'pos' in data and 'health' in data:
        conn.execute("UPDATE users SET mc_pos=?, mc_health=? WHERE mc_uuid=?", (data['pos'], data['health'], uuid))
    
    # Update global server status if provided
    if tps is not None:
        conn.execute("INSERT OR REPLACE INTO mc_server_status (id, tps, ram_used, ram_total, updated_at) VALUES (1, ?, ?, ?, ?)", (tps, ram_used, ram_total, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/mc/server/info')
def mc_server_info():
    conn = get_db()
    s = conn.execute("SELECT tps, ram_used, ram_total, updated_at FROM mc_server_status WHERE id=1").fetchone()
    if not s: return jsonify({'success': False})
    return jsonify({
        'success': True,
        'tps': s['tps'],
        'ram_used': s['ram_used'],
        'ram_total': s['ram_total'],
        'updated_at': s['updated_at']
    })

@app.route('/api/mc/shop/sell', methods=['POST'])
def mc_shop_sell():
    data = request.json
    uuid = data.get('mc_uuid')
    item_name = data.get('item_name') # Standardized item name, e.g., 'minecraft:diamond'
    amount = int(data.get('amount', 1))
    
    # Simple recycling prices
    prices = {
        'minecraft:diamond': 50,
        'minecraft:gold_ingot': 20,
        'minecraft:iron_ingot': 5,
        'minecraft:emerald': 100,
        'minecraft:netherite_ingot': 500,
    }
    
    if item_name not in prices:
        return jsonify({'success': False, 'message': '该物品无法回收'})
        
    reward = prices[item_name] * amount
    conn = get_db()
    u = conn.execute("SELECT username FROM users WHERE mc_uuid=?", (uuid,)).fetchone()
    if not u: return jsonify({'success': False, 'message': '玩家尚未绑定 OS 账号'})
    
    conn.execute("UPDATE users SET gold_balance = gold_balance + ? WHERE username=?", (reward, u['username']))
    conn.commit()
    return jsonify({'success': True, 'message': f'成功回收 {amount} 个 {item_name}，获得 {reward} 金币'})

@app.route('/api/mc/signin', methods=['POST'])
def mc_signin():
    data = request.json
    uuid = data.get('mc_uuid')
    conn = get_db()
    u = conn.execute("SELECT username, last_mc_sign FROM users WHERE mc_uuid=?", (uuid,)).fetchone()
    if not u: return jsonify({'success': False, 'message': '玩家尚未绑定 OS 账号'})
    
    today = datetime.date.today().isoformat()
    if u['last_mc_sign'] == today:
        return jsonify({'success': False, 'message': '今天已经签到过了'})
    
    conn.execute("UPDATE users SET gold_balance = gold_balance + 100, last_mc_sign=? WHERE username=?", (today, u['username']))
    conn.commit()
    return jsonify({'success': True, 'message': '签到成功！奖励 100 金币'})

@app.route('/api/mc/shop/list')
def mc_shop_list():
    conn = get_db()
    items = conn.execute("SELECT * FROM mc_shop_items").fetchall()
    return jsonify({'success': True, 'items': [dict(i) for i in items]})

@app.route('/api/mc/shop/buy', methods=['POST'])
def mc_shop_buy():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    item_id = data.get('item_id')
    
    conn = get_db()
    item = conn.execute("SELECT * FROM mc_shop_items WHERE id=?", (item_id,)).fetchone()
    u = conn.execute("SELECT balance, is_vip FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if item and u:
        price = item['price']
        if u['is_vip']:
            price = int(price * 0.8) # 20% discount for VIP
            
        if u['balance'] >= price:
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("UPDATE users SET balance = balance - ? WHERE username=?", (price, session['user']))
            conn.execute("INSERT INTO mc_shop_logs (username, item_id, price, created_at) VALUES (?, ?, ?, ?)", (session['user'], item_id, price, dt))
            conn.commit()
            return jsonify({'success': True, 'message': f'购买成功: {item["name"]} (扣除 {price} 星币)'})
    return jsonify({'success': False, 'message': '余额不足或商品不存在'})

@app.route('/api/theme/buy', methods=['POST'])
def theme_buy():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    price = int(data.get('price', 0))
    if price <= 0: return jsonify({'success': False, 'message': '价格错误'})
    conn = get_db()
    u = conn.execute("SELECT balance FROM users WHERE username=?", (session['user'],)).fetchone()
    if u and u['balance'] >= price:
        conn.execute("UPDATE users SET balance = balance - ? WHERE username=?", (price, session['user']))
        conn.commit()
        return jsonify({'success': True, 'message': f'购买成功，扣除{price}星币'})
    return jsonify({'success': False, 'message': '星币不足'})

@app.route('/api/user/recharge', methods=['POST'])
def recharge():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    amount = int(data.get('amount', 0))
    if amount <= 0: return jsonify({'success': False, 'message': '金额不合法'})
    conn = get_db()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO recharge_requests (username, amount, status, created_at) VALUES (?, ?, 'pending', ?)", (session['user'], amount, dt))
    conn.commit()
    return jsonify({'success': True, 'message': f'充值申请已提交（{amount}星币），请等待管理员审核到账。'})

@app.route('/api/user/buy_storage', methods=['POST'])
def buy_storage():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    mb = int(data.get('mb', 0))
    months = int(data.get('months', 1))
    if mb <= 0 or months <= 0: return jsonify({'success': False, 'message': '参数错误'})
    
    # 10 Balance per 100MB per month
    cost = max(1, (mb // 100) * 10 * months)
    
    conn = get_db()
    u = conn.execute("SELECT balance, storage_limit FROM users WHERE username=?", (session['user'],)).fetchone()
    if u['balance'] < cost: return jsonify({'success': False, 'message': f'星币不足，需要{cost}星币'})
    
    new_limit = u['storage_limit'] + (mb * 1024 * 1024)
    conn.execute("UPDATE users SET balance = balance - ?, storage_limit = ? WHERE username=?", (cost, new_limit, session['user']))
    conn.commit()
    return jsonify({'success': True, 'message': f'成功通过星币扩容 {mb}MB！'})

@app.route('/api/earth/data')
def earth_data():
    conn = get_db()
    users = conn.execute("SELECT username, lat, lng, is_vip, role FROM users").fetchall()
    return jsonify({'success': True, 'users':[dict(u) for u in users]})

@app.route('/api/weather')
def get_weather():
    # Simulated weather data based on user or random
    city = request.args.get('city', '北京')
    # Use fixed consistent data or random based on city name hash
    import hashlib
    h_seed = int(hashlib.md5(city.encode()).hexdigest(), 16)
    temp = 15 + (h_seed % 15)
    weathers = ['晴朗', '多云', '阴天', '小雨', '阵雨']
    w_type = weathers[h_seed % len(weathers)]
    wind = 1 + (h_seed % 5)
    humidity = 30 + (h_seed % 40)
    return jsonify({
        'success': True,
        'city': city,
        'temp': int(temp),
        'type': str(w_type),
        'wind': int(wind),
        'humidity': int(humidity),
        'pm25': int(10 + (h_seed % 50)),
        'uv': int(h_seed % 10),
        'forecast': [
            {'day': '明天', 'temp': int(temp + 2), 'type': str(weathers[(h_seed+1)%len(weathers)])},
            {'day': '后天', 'temp': int(temp - 1), 'type': str(weathers[(h_seed+2)%len(weathers)])}
        ]
    })

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    msg = data.get('message', '').lower()
    
    # Simple simulated AI logic
    replies = [
        "你好！我是汐语 AI 助手，很高兴为你服务。",
        "这是一个非常有趣的问题，让我想想...",
        "汐语 OS 正在不断进化中，感谢你的陪伴。",
        "今天的气温很适合出去走走呢。",
        "我也在学习如何更好地帮助你。"
    ]
    
    import random
    reply = random.choice(replies)
    
    if '天气' in msg:
        reply = "你可以打开工具箱里的天气插件，实时查看最新的天气详情哦。"
    elif '功能' in msg:
        reply = "畅聊现在支持了全服大厅、私聊、红包、语音、搜索还有各种有趣的小工具！"
    elif '作者' in msg or '谁做的' in msg:
        reply = "我是由汐语工作室（XiYu Studio）开发的智能助手。"

    return jsonify({'success': True, 'reply': reply})

@app.route('/api/fs/action', methods=['POST'])
def fs_action():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    conn = get_db()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if act == 'list':
        is_del = data.get('is_deleted', 0)
        pid = data.get('parent_id', 0)
        if data.get('is_desktop'): files = conn.execute("SELECT * FROM files WHERE owner=? AND is_deleted=0 AND is_desktop=1", (session['user'],)).fetchall()
        elif data.get('recent'):
            files = conn.execute("SELECT f.* FROM recent_files r JOIN files f ON r.file_id = f.id WHERE r.username=? AND f.owner=? AND f.is_deleted=0 ORDER BY r.access_time DESC LIMIT 15", (session['user'], session['user'])).fetchall()
        else: files = conn.execute("SELECT * FROM files WHERE owner=? AND is_deleted=? AND is_desktop=0 AND parent_id=? ORDER BY type DESC, id DESC", (session['user'], is_del, pid)).fetchall()
        return jsonify({'success': True, 'files': [dict(f) for f in files]})
    elif act == 'save':
        if data.get('content'):
            u = conn.execute("SELECT storage_limit FROM users WHERE username=?", (session['user'],)).fetchone()
            used = conn.execute("SELECT sum(length(content)) as s FROM files WHERE owner=?", (session['user'],)).fetchone()['s'] or 0
            if used + len(data['content']) > u['storage_limit']:
                return jsonify({'success': False, 'message': '存储空间不足，请在设置中扩容'})
        if data.get('id'): conn.execute("UPDATE files SET filename=?, content=? WHERE id=? AND owner=?", (data['filename'], data['content'], data['id'], session['user']))
        else: conn.execute("INSERT INTO files (filename, content, owner, type, parent_id, is_desktop, pos_x, pos_y, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (data['filename'], data.get('content',''), session['user'], data.get('type','file'), data.get('parent_id',0), data.get('is_desktop',0), data.get('x',0), data.get('y',0), dt))
    elif act == 'pos': conn.execute("UPDATE files SET pos_x=?, pos_y=? WHERE id=? AND owner=?", (data['x'], data['y'], data['id'], session['user']))
    elif act == 'trash': conn.execute("UPDATE files SET is_deleted=1 WHERE id=? AND owner=?", (data['id'], session['user']))
    elif act == 'restore': conn.execute("UPDATE files SET is_deleted=0 WHERE id=? AND owner=?", (data['id'], session['user']))
    elif act == 'delete_hard': conn.execute("DELETE FROM files WHERE is_deleted=1 AND owner=?", (session['user'],))
    elif act == 'read':
        file = conn.execute("SELECT * FROM files WHERE id=? AND owner=?", (data['id'], session['user'])).fetchone()
        if file:
            conn.execute("DELETE FROM recent_files WHERE username=? AND file_id=?", (session['user'], data['id']))
            conn.execute("INSERT INTO recent_files (username, file_id, access_time) VALUES (?, ?, ?)", (session['user'], data['id'], dt))
            # Keep only last 20
            conn.execute("DELETE FROM recent_files WHERE id NOT IN (SELECT id FROM recent_files WHERE username=? ORDER BY access_time DESC LIMIT 20)", (session['user'],))
        return jsonify({'success': True, 'file': dict(file)})
    elif act == 'rename': conn.execute("UPDATE files SET filename=? WHERE id=? AND owner=?", (data['filename'], data['id'], session['user']))
    elif act == 'copy':
        src = conn.execute("SELECT * FROM files WHERE id=? AND owner=?", (data['id'], session['user'])).fetchone()
        if src: conn.execute("INSERT INTO files (filename, content, owner, type, parent_id, is_desktop, pos_x, pos_y, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (src['filename']+"_副本", src['content'], session['user'], src['type'], data.get('parent_id',0), data.get('is_desktop',0), data.get('x',0), data.get('y',0), dt))
    elif act == 'toggle_autostart':
        conn.execute("UPDATE files SET is_autostart = CASE WHEN is_autostart=1 THEN 0 ELSE 1 END WHERE id=? AND owner=?", (data['id'], session['user']))
    elif act == 'list_autostart':
        files = conn.execute("SELECT * FROM files WHERE owner=? AND is_deleted=0 AND is_autostart=1", (session['user'],)).fetchall()
        return jsonify({'success': True, 'files': [dict(f) for f in files]})
    elif act == 'share':
        import uuid
        existing = conn.execute("SELECT share_code FROM shares WHERE file_id=? AND owner=?", (data['id'], session['user'])).fetchone()
        if existing:
            code = existing['share_code']
        else:
            code = str(uuid.uuid4())[:8]
            conn.execute("INSERT INTO shares (share_code, file_id, owner, created_at) VALUES (?, ?, ?, ?)", (code, data['id'], session['user'], dt))
            conn.commit()
        return jsonify({'success': True, 'share_code': code})
    elif act == 'unshare':
        conn.execute("DELETE FROM shares WHERE file_id=? AND owner=?", (data['id'], session['user']))
        conn.commit()
        return jsonify({'success': True})
    elif act == 'list_shares':
        shares = conn.execute("SELECT s.share_code, s.file_id, s.created_at, f.filename, f.type FROM shares s LEFT JOIN files f ON s.file_id=f.id WHERE s.owner=? ORDER BY s.created_at DESC", (session['user'],)).fetchall()
        return jsonify({'success': True, 'shares': [dict(s) for s in shares]})
    elif act == 'capacity':
        u = conn.execute("SELECT storage_limit FROM users WHERE username=?", (session['user'],)).fetchone()
        used = conn.execute("SELECT sum(length(content)) as s FROM files WHERE owner=?", (session['user'],)).fetchone()['s'] or 0
        return jsonify({'success': True, 'limit': u['storage_limit'], 'used': used})
    elif act == 'capacity_analysis':
        u = conn.execute("SELECT storage_limit FROM users WHERE username=?", (session['user'],)).fetchone()
        stats = conn.execute("SELECT type, sum(length(content)) as size, count(*) as count FROM files WHERE owner=? GROUP BY type", (session['user'],)).fetchall()
        return jsonify({'success': True, 'limit': u['storage_limit'], 'stats': [dict(s) for s in stats]})
    elif act == 'direct_link':
        # VIP users can generate direct links
        u = conn.execute("SELECT is_vip FROM users WHERE username=?", (session['user'],)).fetchone()
        if not u or not u['is_vip']: return jsonify({'success': False, 'message': '仅限VIP用户使用直链'})
        # Just use file_id as token for now, or could use more secure token
        return jsonify({'success': True, 'token': data['id']})
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/chat/action', methods=['POST'])
def chat_action():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    conn = get_db()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.date.today().isoformat()
    if act == 'list':
        receiver = data.get('receiver', 'group')
        sender_oa = data.get('sender_oa')
        
        # Identity to act as (User by default, OA if sender_oa provided and owned)
        active_identity = session['user']
        if sender_oa:
            oa_check = conn.execute("SELECT 1 FROM official_accounts WHERE id=? AND owner=?", (sender_oa, session['user'])).fetchone()
            if oa_check:
                active_identity = str(sender_oa)

        if receiver == 'group':
            msgs = conn.execute("""
                SELECT m.*, 
                       COALESCE(u.avatar, oa.avatar, oa.icon) as avatar, 
                       u.mc_uuid,
                       u.qq, 
                       COALESCE(u.uid, oa.id) as sender_uid,
                       COALESCE(u.username, oa.name) as display_name
                FROM messages m 
                LEFT JOIN users u ON m.sender = u.username 
                LEFT JOIN official_accounts oa ON m.sender = CAST(oa.id AS TEXT) OR m.sender = oa.id
                WHERE m.receiver='group' 
                ORDER BY m.id DESC LIMIT 100
            """).fetchall()
            new_msgs = []
            for m in msgs:
                m_dict = dict(m)
                # Overwrite sender name if it's an OA
                if not m_dict.get('qq') and m_dict.get('avatar') and (m_dict['avatar'].startswith('fa-') or m_dict['avatar'].startswith('fas ') or m_dict['avatar'].startswith('fab ')):
                    m_dict['sender_name'] = m_dict['display_name']
                
                m_dict['sender_avatar'] = get_computed_avatar(m_dict)
                if m_dict['content'].startswith('[RED_ENVELOPE:') and m_dict['content'].endswith(']'):
                    try:
                        re_id = int(m_dict['content'][14:-1])
                        re_data = conn.execute("SELECT * FROM red_envelopes WHERE id=?", (re_id,)).fetchone()
                        if re_data:
                            m_dict['type'] = 'red_envelope'
                            m_dict['content'] = dict(re_data)
                    except: pass
                new_msgs.append(m_dict)
            return jsonify({'success': True, 'msgs': new_msgs})
        else:
            msgs = conn.execute("""
                SELECT m.*, 
                       COALESCE(u.avatar, oa.avatar, oa.icon) as avatar, 
                       u.mc_uuid,
                       u.qq, 
                       COALESCE(u.uid, oa.id) as sender_uid,
                       COALESCE(u.username, oa.name) as display_name
                FROM messages m 
                LEFT JOIN users u ON m.sender = u.username 
                LEFT JOIN official_accounts oa ON m.sender = CAST(oa.id AS TEXT) OR m.sender = oa.id
                WHERE (m.sender=? AND m.receiver=?) OR (m.sender=? AND m.receiver=?) 
                ORDER BY m.id DESC LIMIT 50
            """, (active_identity, receiver, receiver, active_identity)).fetchall()
            
            res_msgs = []
            for m in msgs:
                m_dict = dict(m)
                if m_dict.get('display_name'):
                    m_dict['sender_name'] = m_dict['display_name']
                m_dict['sender_avatar'] = get_computed_avatar(m_dict)
                res_msgs.append(m_dict)
            return jsonify({'success': True, 'msgs': res_msgs})
    elif act == 'recent':
        # Unified recent chats including friends and group
        # Find OAs owned by the user
        owned_oas = conn.execute("SELECT id FROM official_accounts WHERE owner=?", (session['user'],)).fetchall()
        owned_oa_ids = [str(o['id']) for o in owned_oas]
        
        # Private chats: Includes messages where sender or receiver is the user OR an OA owned by the user
        oa_placeholders = ','.join([':o' + str(i) for i, _ in enumerate(owned_oa_ids)])
        oa_params = { 'o' + str(i): oid for i, oid in enumerate(owned_oa_ids) }
        
        query = f"""
            SELECT m1.* FROM messages m1 
            INNER JOIN (
                SELECT MAX(id) as id 
                FROM messages 
                WHERE (sender=:u OR receiver=:u { ("OR sender IN ("+oa_placeholders+") OR receiver IN ("+oa_placeholders+")") if owned_oa_ids else "" }) AND receiver != 'group' 
                GROUP BY CASE WHEN (sender=:u { ("OR sender IN ("+oa_placeholders+")") if owned_oa_ids else "" }) THEN receiver ELSE sender END
            ) m2 ON m1.id = m2.id
        """
        p_msgs = conn.execute(query, {**{'u': session['user']}, **oa_params}).fetchall()
        
        # Group chat
        g_msg = conn.execute("SELECT * FROM messages WHERE receiver='group' ORDER BY id DESC LIMIT 1").fetchone()
        
        recent = []
        for m in p_msgs:
            m_dict = dict(m)
            # If sender is ME or MY OA, target is receiver. Else target is sender.
            is_me_or_my_oa = m_dict['sender'] == session['user'] or str(m_dict['sender']) in owned_oa_ids
            target = m_dict['receiver'] if is_me_or_my_oa else m_dict['sender']
            
            # Try user first
            t_user = conn.execute("SELECT username, uid, avatar, mc_uuid, qq FROM users WHERE username=?", (target,)).fetchone()
            as_oa = m_dict['sender'] if str(m_dict['sender']) in owned_oa_ids else (m_dict['receiver'] if str(m_dict['receiver']) in owned_oa_ids else None)
            
            # Reminder logic for OA owners
            display_content = m_dict['content']
            if as_oa and str(m_dict['sender']) not in owned_oa_ids:
                display_content = f"收到来自 @{m_dict['sender']} 的互动提醒"

            if t_user:
                u_dict = dict(t_user)
                u_dict['avatar'] = get_computed_avatar(u_dict)
                recent.append({
                    'target': target, 
                    'content': display_content, 
                    'time': m_dict['created_at'], 
                    'type': m_dict.get('type', 'text'),
                    'uid': u_dict.get('uid', 0),
                    'avatar': u_dict['avatar'],
                    'name': u_dict['username'],
                    'as_oa': as_oa
                })
            else:
                # Try OA
                oa = conn.execute("SELECT id as uid, name as username, avatar, icon FROM official_accounts WHERE id=? OR name=?", (target, target)).fetchone()
                if oa:
                    oa_dict = dict(oa)
                    if not oa_dict.get('avatar'): oa_dict['avatar'] = oa_dict.get('icon')
                    recent.append({
                        'target': str(oa_dict['uid']), 
                        'content': m_dict['content'], 
                        'time': m_dict['created_at'], 
                        'type': m_dict.get('type', 'text'),
                        'uid': oa_dict['uid'],
                        'avatar': get_computed_avatar(oa_dict),
                        'name': oa_dict['username']
                    })
                else:
                    recent.append({
                        'target': target, 
                        'content': m_dict['content'], 
                        'time': m_dict['created_at'], 
                        'type': m_dict.get('type', 'text'),
                        'uid': 0,
                        'avatar': '/static/icons/user.png',
                        'name': target
                    })
        
        if g_msg:
            # Check if group is already in recent (e.g. if I sent a message and it's in p_msgs, but it shouldn't be as receiver='group')
            if not any(r['target'] == 'group' for r in recent):
                recent.append({
                    'target': 'group', 
                    'content': f"{g_msg['sender']}: {g_msg['content']}", 
                    'time': g_msg['created_at'], 
                    'type': 'group',
                    'avatar': 'https://q1.qlogo.cn/g?b=qq&nk=10001&s=100' # Default Hall Icon
                })
        else:
            # Even if no messages, show the hall
            recent.append({
                'target': 'group',
                'content': '欢迎来到全服大厅',
                'time': dt,
                'type': 'group',
                'avatar': 'https://q1.qlogo.cn/g?b=qq&nk=10001&s=100'
            })
        
        # Sort by time descending
        recent.sort(key=lambda x: x['time'], reverse=True)
        return jsonify({'success': True, 'chats': recent})
    elif act == 'send':
        msg_type = data.get('msg_type', 'text') # Renamed from type to avoid conflict
        receiver = data.get('receiver', 'group')
        content = data.get('content')
        voice_duration = data.get('voice_duration', 0)
        sender = data.get('sender_oa') # Support replying AS an official account
        
        # Verify ownership if sender_oa is provided
        if sender:
            oa_check = conn.execute("SELECT 1 FROM official_accounts WHERE id=? AND owner=?", (sender, session['user'])).fetchone()
            if not oa_check: return jsonify({'success': False, 'message': '无权以该公众号身份发送消息'})
        else:
            sender = session['user']

        conn.execute("INSERT INTO messages (sender, receiver, content, type, voice_duration, created_at) VALUES (?, ?, ?, ?, ?, ?)", (sender, receiver, content, msg_type, voice_duration, dt))
        # Increment daily task for private chat
        if receiver != 'group':
            conn.execute("INSERT OR IGNORE INTO user_tasks (username, task_id, count, date) SELECT ?, id, 0, ? FROM daily_tasks WHERE type='chat'", (session['user'], today))
            conn.execute("UPDATE user_tasks SET count = count + 1 WHERE username=? AND date=? AND task_id IN (SELECT id FROM daily_tasks WHERE type='chat')", (session['user'], today))
        conn.commit()
        
        # OA Bot logic
        try:
            oa_id = int(receiver)
            oa = conn.execute("SELECT name, bot_enabled, bot_config FROM official_accounts WHERE id=?", (oa_id,)).fetchone()
            if oa and oa['bot_enabled']:
                rules = json.loads(oa['bot_config'] or '{}')
                reply = None
                for kw, ans in rules.items():
                    if kw in content:
                        reply = ans
                        break
                if reply:
                    conn.execute("INSERT INTO messages (sender, receiver, content, type, created_at) VALUES (?, ?, ?, 'text', ?)", (receiver, session['user'], reply, dt))
                    conn.commit()
        except: pass
        
        return jsonify({'success': True})
    elif act == 'red_envelope':
        # Send red envelope
        amount = int(data.get('amount', 0))
        count = int(data.get('count', 1))
        etype = data.get('type', 'random') # random or equal
        if amount <= 0 or count <= 0: return jsonify({'success': False, 'message': '金额或数量不合法'})
        u = conn.execute("SELECT balance FROM users WHERE username=?", (session['user'],)).fetchone()
        if not u or u['balance'] < amount: return jsonify({'success': False, 'message': '余额不足'})
        
        conn.execute("INSERT INTO red_envelopes (sender, amount, count, type, created_at) VALUES (?, ?, ?, ?, ?)", (session['user'], amount, count, etype, dt))
        re_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute("UPDATE users SET balance = balance - ? WHERE username=?", (amount, session['user']))
        conn.execute("INSERT INTO messages (sender, receiver, content, created_at) VALUES (?, 'group', ?, ?)", (session['user'], f"[RED_ENVELOPE:{re_id}]", dt))
        conn.commit()
        return jsonify({'success': True, 'message': '红包已发出'})
    elif act == 'claim_red_envelope':
        re_id = data.get('red_id')
        r = conn.execute("SELECT * FROM red_envelopes WHERE id=?", (re_id,)).fetchone()
        if not r: return jsonify({'success': False, 'message': '红包不存在'})
        try: claimed = json.loads(r['claimed_by'])
        except: claimed = []
        if session['user'] in [c['user'] for c in claimed]: return jsonify({'success': False, 'message': '你已经领过啦'})
        if len(claimed) >= r['count']: return jsonify({'success': False, 'message': '红包已被抢光啦'})
        
        # Calculate amount
        remaining_count = r['count'] - len(claimed)
        if remaining_count == 1:
            claimed_amount = r['amount'] - sum([c['amount'] for c in claimed])
        else:
            if r['type'] == 'equal':
                claimed_amount = r['amount'] // r['count']
            else:
                # Basic random algorithm: 0.01 to 2 * average
                avg = (r['amount'] - sum([c['amount'] for c in claimed])) / remaining_count
                claimed_amount = random.randint(1, int(avg * 200)) / 100
                claimed_amount = int(max(1, int(claimed_amount)))
        
        claimed.append({'user': session['user'], 'amount': claimed_amount, 'time': dt})
        conn.execute("UPDATE red_envelopes SET claimed_by=? WHERE id=?", (json.dumps(claimed), re_id))
        conn.execute("UPDATE users SET gold_balance = gold_balance + ? WHERE username=?", (claimed_amount, session['user']))
        conn.commit()
        return jsonify({'success': True, 'amount': claimed_amount})
    elif act == 'withdraw':
        msg_id = data.get('id')
        msg = conn.execute("SELECT sender FROM messages WHERE id=?", (msg_id,)).fetchone()
        if msg and msg['sender'] == session['user']:
            conn.execute("DELETE FROM messages WHERE id=?", (msg_id,))
            conn.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '无权操作'})
    elif act == 'search_msgs':
        query = data.get('query', '')
        receiver = data.get('receiver', 'group')
        if receiver == 'group':
            rows = conn.execute("""
                SELECT m.*, u.avatar, u.mc_uuid, u.qq 
                FROM messages m 
                LEFT JOIN users u ON m.sender = u.username 
                WHERE m.receiver='group' AND m.content LIKE ? 
                ORDER BY m.id DESC LIMIT 30
            """, (f'%{query}%',)).fetchall()
        else:
            rows = conn.execute("""
                SELECT m.*, u.avatar, u.mc_uuid, u.qq 
                FROM messages m 
                LEFT JOIN users u ON m.sender = u.username 
                WHERE ((m.sender=? AND m.receiver=?) OR (m.sender=? AND m.receiver=?)) AND m.content LIKE ? 
                ORDER BY m.id DESC LIMIT 30
            """, (session['user'], receiver, receiver, session['user'], f'%{query}%')).fetchall()
        
        msgs = []
        for r in rows:
            m = dict(r)
            m['sender_avatar'] = get_computed_avatar(m)
            msgs.append(m)
        return jsonify({'success': True, 'msgs': msgs})
    elif act == 'clear_history':
        receiver = data.get('receiver', 'group')
        if receiver == 'group':
            conn.execute("DELETE FROM messages WHERE receiver='group'")
        else:
            conn.execute("DELETE FROM messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)", (session['user'], receiver, receiver, session['user']))
        conn.commit()
        return jsonify({'success': True})
    elif act == 'buy_membership':
        tier_price = {1: 15, 2: 30, 3: 50} # Balance price for chat VIP (consistent with system VIP)
        tier = data.get('tier', 1)
        price = tier_price.get(tier, 15)
        u = conn.execute("SELECT balance FROM users WHERE username=?", (session['user'],)).fetchone()
        if not u or u['balance'] < price: return jsonify({'success': False, 'message': '星币不足'})
        
        expire_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("UPDATE users SET balance = balance - ?, chat_vip = ?, chat_vip_expire = ? WHERE username=?", (price, tier, expire_date, session['user']))
        conn.commit()
        return jsonify({'success': True, 'message': f'成功开通 {tier} 级畅聊会员'})
    elif act == 'set_nameplate':
        nameplate = data.get('nameplate', '')
        conn.execute("UPDATE users SET nameplate=? WHERE username=?", (nameplate, session['user']))
        conn.commit()
        return jsonify({'success': True})
    elif act == 'favorite':
        msg_id = data.get('id')
        msg = conn.execute("SELECT id FROM messages WHERE id=?", (msg_id,)).fetchone()
        if not msg: return jsonify({'success': False, 'message': '消息不存在'})
        exists = conn.execute("SELECT id FROM chat_favorites WHERE username=? AND message_id=?", (session['user'], msg_id)).fetchone()
        if exists: return jsonify({'success': False, 'message': '已经收藏过了'})
        conn.execute("INSERT INTO chat_favorites (username, message_id) VALUES (?, ?)", (session['user'], msg_id))
        conn.commit()
        return jsonify({'success': True, 'message': '收藏成功'})
    elif act == 'list_favorites':
       faves = conn.execute("""
            SELECT f.id as fav_id, f.created_at as fav_time, m.*, u.avatar, u.mc_uuid, u.qq, u.uid as sender_uid
            FROM chat_favorites f
            JOIN messages m ON f.message_id = m.id
            LEFT JOIN users u ON m.sender = u.username
            WHERE f.username = ?
            ORDER BY f.id DESC
       """, (session['user'],)).fetchall()
       res_faves = []
       for f in faves:
           f_dict = dict(f)
           f_dict['sender_avatar'] = get_computed_avatar(f_dict)
           res_faves.append(f_dict)
       return jsonify({'success': True, 'favorites': res_faves})
    elif act == 'remove_favorite':
        fav_id = data.get('id')
        conn.execute("DELETE FROM chat_favorites WHERE id=? AND username=?", (fav_id, session['user']))
        conn.commit()
        return jsonify({'success': True})
    elif act == 'translate':
        text = data.get('text', '')
        lang = data.get('lang', 'en')
        
        # Simulated high-quality translation engine
        # In a real app, this would call an AI API or translation library
        translations = {
            'en': {
                '你好': 'Hello', '早上好': 'Good morning', '干嘛呢': 'What are you doing?',
                '汐语': 'XiYu', '系统': 'System', '很高兴遇见你': 'Nice to meet you',
                '我爱你': 'I love you', '再见': 'Goodbye', '谢谢': 'Thank you'
            },
            'jp': {
                '你好': 'こんにちは', '早上好': 'おはようございます', '干嘛呢': '何をしていますか？',
                '汐语': 'XiYu', '系统': 'システム', '很高兴遇见你': 'はじめまして',
                '我爱你': '愛してる', '再见': 'さようなら', '谢谢': 'ありがとうございます'
            },
            'kr': {
                '你好': '안녕하세요', '早上好': '좋은 아침이에요', '干嘛呢': '뭐해요?',
                '汐语': 'XiYu', '系统': '시스템', '很高兴遇见你': '만나서 반가워요',
                '我爱你': '사랑해요', '再见': '안녕히 가세요', '谢谢': '감사합니다'
            }
        }
        
        result = translations.get(lang, {}).get(text)
        if not result:
            # Fallback for untranslated text (simulating AI processing)
            prefix = {'en': '[EN]', 'jp': '[JP]', 'kr': '[KR]', 'zh': '[ZH]'}.get(lang, '[TR]')
            result = f"{prefix} {text} (AI-Simulated)"
            
        return jsonify({'success': True, 'translated': result})
    elif act == 'stt':
        # Simulated Speech-to-Text engine
        # In a real app, this would process the audio file or content
        stt_results = [
            "好的，我知道了。",
            "今晚一起去吃火锅吗？",
            "这个项目进展得非常顺利，继续保持。",
            "汐语 OS 的翻译效果确实很惊艳。",
            "语音转文字功能测试中，123456。"
        ]
        import random
        result = random.choice(stt_results)
        return jsonify({'success': True, 'text': result})
    elif act == 'report':
        reported = data.get('reported')
        reason = data.get('reason')
        msg_id = data.get('msg_id')
        conn.execute("INSERT INTO chat_reports (reporter, reported, reason, msg_id, created_at) VALUES (?, ?, ?, ?, ?)", (session['user'], reported, reason, msg_id, dt))
        conn.commit()
        return jsonify({'success': True})

@app.route('/api/cloud/data', methods=['POST'])
def cloud_data():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    conn = get_db()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if act == 'get_note':
        row = conn.execute("SELECT content FROM notes WHERE username=?", (session['user'],)).fetchone()
        return jsonify({'success': True, 'content': row['content'] if row else ''})
    elif act == 'save_note': conn.execute("INSERT OR REPLACE INTO notes (username, content, updated_at) VALUES (?, ?, ?)", (session['user'], data.get('content',''), dt))
    elif act == 'get_table':
        row = conn.execute("SELECT content FROM timetables WHERE username=?", (session['user'],)).fetchone()
        return jsonify({'success': True, 'content': row['content'] if row else ''})
    elif act == 'save_table': conn.execute("INSERT OR REPLACE INTO timetables (username, content, updated_at) VALUES (?, ?, ?)", (session['user'], data.get('content',''), dt))
    elif act == 'get_todo':
        row = conn.execute("SELECT content FROM todos WHERE username=?", (session['user'],)).fetchone()
        return jsonify({'success': True, 'content': row['content'] if row else ''})
    elif act == 'save_todo': conn.execute("INSERT OR REPLACE INTO todos (username, content, updated_at) VALUES (?, ?, ?)", (session['user'], data.get('content',''), dt))
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/app/action', methods=['POST'])
def app_action():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    conn = get_db()
    if act == 'list':
        apps = conn.execute("SELECT * FROM apps ORDER BY id DESC").fetchall()
        return jsonify({'success': True, 'apps': [dict(a) for a in apps]})
    elif act == 'upload':
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT INTO apps (name, icon, description, code, author, created_at) VALUES (?, ?, ?, ?, ?, ?)", (data.get('name','未命名'), data.get('icon','fa-cube'), data.get('description',''), data.get('code',''), session['user'], dt))
        conn.commit()
        return jsonify({'success': True})


@app.route('/api/media/upload', methods=['POST'])
def media_upload():
    if 'user' not in session: return jsonify({'success': False})
    if 'file' not in request.files: return jsonify({'success': False, 'message': '无文件'})
    file = request.files['file']
    ftype = request.form.get('type', 'chat') # avatars, chat, space
    if not file: return jsonify({'success': False})
    ext = file.filename.split('.')[-1].lower()
    fname = f"{session['user']}_{int(datetime.datetime.now().timestamp())}.{ext}"
    path = os.path.join(UPLOAD_FOLDER, ftype, fname)
    file.save(path)
    url = f"/{path.replace('\\', '/')}"
    
    file_type = 'file'
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']: file_type = 'image'
    elif ext in ['mp3', 'wav', 'ogg', 'm4a']: file_type = 'voice'
    elif ext in ['mp4', 'webm', 'mov']: file_type = 'video'
    
    if ftype == 'avatars':
        conn = get_db()
        conn.execute("UPDATE users SET avatar=? WHERE username=?", (url, session['user']))
        conn.commit()
    return jsonify({'success': True, 'url': url, 'file_type': file_type})

@app.route('/api/space/action', methods=['POST'])
def space_action():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    conn = get_db()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if act == 'list':
        # Filter by author if username is provided (for user spaces)
        target_author = data.get('username')
        if target_author:
            rows = conn.execute("SELECT * FROM moments WHERE author=? ORDER BY id DESC LIMIT 50", (target_author,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM moments ORDER BY id DESC LIMIT 50").fetchall()
        
        moments = []
        for r in rows:
            m = dict(r)
            u = conn.execute("SELECT username, avatar, mc_uuid, qq, uid FROM users WHERE username=?", (m['author'],)).fetchone()
            u_dict = dict(u) if u else {'username': m['author']}
            m['avatar'] = get_computed_avatar(u_dict)
            m['uid'] = u_dict.get('uid', 0)
            m['nameplate'] = u_dict.get('nameplate', '')
            m['chat_vip'] = u_dict.get('chat_vip', 0)
            try: m['media'] = json.loads(str(m['media'] or '[]'))
            except: m['media'] = []
            try: m['likes'] = json.loads(str(m['likes'] or '[]'))
            except: m['likes'] = []
            # Fetch comments from dedicated table
            m_comments = conn.execute("SELECT author, content, created_at FROM space_comments WHERE moment_id=? ORDER BY id ASC", (m['id'],)).fetchall()
            m['comments_list'] = [dict(c) for c in m_comments]
            moments.append(m)
        return jsonify({'success': True, 'moments': moments})
    elif act == 'post':
        conn.execute("INSERT INTO moments (author, content, media, created_at, likes, comments) VALUES (?, ?, ?, ?, '[]', '[]')", (session['user'], data.get('content'), str(data.get('media', [])), dt))
        # Increment daily task
        today = datetime.date.today().isoformat()
        conn.execute("INSERT OR IGNORE INTO user_tasks (username, task_id, count, date) SELECT ?, id, 0, ? FROM daily_tasks WHERE type='moment'", (session['user'], today))
        conn.execute("UPDATE user_tasks SET count = count + 1 WHERE username=? AND date=? AND task_id IN (SELECT id FROM daily_tasks WHERE type='moment')", (session['user'], today))
        conn.commit()
        return jsonify({'success': True})
    elif act == 'comment':
        m_id = data.get('post_id') # Match frontend param
        content = data.get('content')
        if not content: return jsonify({'success': False, 'message': '内容不能为空'})
        conn.execute("INSERT INTO space_comments (moment_id, author, content, created_at) VALUES (?, ?, ?, ?)", (m_id, session['user'], content, dt))
        conn.commit()
        return jsonify({'success': True})
    elif act == 'like':
        m_id = data.get('id')
        r = conn.execute("SELECT likes FROM moments WHERE id=?", (m_id,)).fetchone()
        try: likes = json.loads(str(r['likes'] or '[]'))
        except: likes = []
        if session['user'] in likes: likes.remove(session['user'])
        else: likes.append(session['user'])
        conn.execute("UPDATE moments SET likes=? WHERE id=?", (json.dumps(likes), m_id))
        conn.commit()
        return jsonify({'success': True})
    elif act == 'delete':
        m_id = data.get('id')
        res = conn.execute("SELECT author FROM moments WHERE id=?", (m_id,)).fetchone()
        if res and res['author'] == session['user']:
            conn.execute("DELETE FROM moments WHERE id=?", (m_id,))
            conn.execute("DELETE FROM space_comments WHERE moment_id=?", (m_id,))
            conn.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '无权删除'})
    return jsonify({'success': False})

@app.route('/api/friend/action', methods=['POST'])
def friend_action():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    conn = get_db()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    me = session['user']
    if act == 'list':
        fs = conn.execute("""
            SELECT u.username, u.avatar, u.mc_uuid, u.qq, u.uid 
            FROM users u
            INNER JOIN (
                SELECT user2 as f FROM friends WHERE user1=? 
                UNION 
                SELECT user1 as f FROM friends WHERE user2=?
            ) f_table ON u.username = f_table.f
        """, (me, me)).fetchall()
        friends = []
        for f in fs:
            f_dict = dict(f)
            f_dict['avatar'] = get_computed_avatar(f_dict)
            friends.append(f_dict)
        return jsonify({'success': True, 'friends': friends})
    elif act == 'request':
        target = data.get('target')
        if not conn.execute("SELECT 1 FROM users WHERE username=?", (target,)).fetchone(): return jsonify({'success': False, 'message': '对方不存在'})
        conn.execute("INSERT INTO friend_requests (sender, receiver, created_at) VALUES (?, ?, ?)", (me, target, dt))
        conn.commit()
        return jsonify({'success': True, 'message': '请求已发送'})
    elif act == 'requests':
        reqs = conn.execute("SELECT * FROM friend_requests WHERE receiver=? AND status='pending'", (me,)).fetchall()
        return jsonify({'success': True, 'requests': [dict(r) for r in reqs]})
    elif act == 'handle':
        status = data.get('status')
        req = conn.execute("SELECT * FROM friend_requests WHERE id=?", (data.get('id'),)).fetchone()
        if req and status == 'accepted': conn.execute("INSERT INTO friends (user1, user2, created_at) VALUES (?, ?, ?)", (req['sender'], req['receiver'], dt))
        conn.execute("UPDATE friend_requests SET status=? WHERE id=?", (status, data.get('id')))
        conn.commit()
        return jsonify({'success': True})
    return jsonify({'success': True})

@app.route('/api/forum/action', methods=['POST'])
def forum_action():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    conn = get_db()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now_ts = datetime.datetime.now().timestamp()
    
    if act == 'list':
        cat = data.get('category')
        search = data.get('search')
        if search: 
            posts = conn.execute("""
                SELECT p.*, u.avatar, u.mc_uuid, u.qq, u.uid 
                FROM posts p 
                LEFT JOIN users u ON p.author = u.username 
                WHERE p.title LIKE ? OR p.content LIKE ? ORDER BY p.id DESC
            """, (f'%{search}%', f'%{search}%')).fetchall()
        elif cat: 
            posts = conn.execute("""
                SELECT p.*, u.avatar, u.mc_uuid, u.qq, u.uid 
                FROM posts p 
                LEFT JOIN users u ON p.author = u.username 
                WHERE p.category=? ORDER BY p.id DESC
            """, (cat,)).fetchall()
        else: 
            posts = conn.execute("""
                SELECT p.*, u.avatar, u.mc_uuid, u.qq, u.uid 
                FROM posts p 
                LEFT JOIN users u ON p.author = u.username 
                ORDER BY p.id DESC
            """).fetchall()
        result = []
        for p in posts:
            d = dict(p)
            d['avatar'] = get_computed_avatar(d)
            d['comment_count'] = conn.execute("SELECT count() FROM comments WHERE post_id=?", (p['id'],)).fetchone()[0]
            result.append(d)
        return jsonify({'success': True, 'posts': result})
    elif act == 'stats':
        u_count = conn.execute("SELECT count() FROM users").fetchone()[0]
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        p_count = conn.execute("SELECT count() FROM posts WHERE created_at LIKE ?", (today + '%',)).fetchone()[0]
        total = conn.execute("SELECT count() FROM posts").fetchone()[0]
        hot = conn.execute("SELECT id, title, likes FROM posts ORDER BY likes DESC LIMIT 5").fetchall()
        return jsonify({'success': True, 'users': u_count, 'today_posts': p_count, 'total_posts': total, 'hot_posts': [dict(h) for h in hot]})
    elif act == 'post':
        last_post = session.get('last_post_ts', 0)
        if now_ts - last_post < 10: return jsonify({'success': False, 'message': '发布太频繁了，请稍后再试'})
        session['last_post_ts'] = now_ts
        
        qq = conn.execute("SELECT qq FROM users WHERE username=?", (session['user'],)).fetchone()['qq']
        conn.execute("INSERT INTO posts (title, content, author, author_qq, category, media, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (data.get('title'), data.get('content'), session['user'], qq, data.get('category', '全部'), data.get('media', '[]'), dt))
        conn.commit()
        return jsonify({'success': True})
    elif act == 'interact':
        itype = data.get('type')
        if itype == 'like': conn.execute("UPDATE posts SET likes = likes + 1 WHERE id=?", (data.get('id'),))
        elif itype == 'star': conn.execute("UPDATE posts SET stars = stars + 1 WHERE id=?", (data.get('id'),))
        conn.commit()
        return jsonify({'success': True})
    elif act == 'get':
        post = conn.execute("""
            SELECT p.*, u.avatar, u.mc_uuid, u.qq, u.uid 
            FROM posts p 
            LEFT JOIN users u ON p.author = u.username 
            WHERE p.id=?
        """, (data.get('id'),)).fetchone()
        if not post: return jsonify({'success': False, 'message': '帖子不存在'})
        p_dict = dict(post)
        p_dict['avatar'] = get_computed_avatar(p_dict)
        
        comments = conn.execute("""
            SELECT c.*, u.avatar, u.mc_uuid, u.qq, u.uid 
            FROM comments c 
            LEFT JOIN users u ON c.author = u.username 
            WHERE c.post_id=? ORDER BY c.id ASC
        """, (data.get('id'),)).fetchall()
        
        c_list = []
        for c in comments:
            cd = dict(c)
            cd['avatar'] = get_computed_avatar(cd)
            c_list.append(cd)
            
        return jsonify({'success': True, 'post': p_dict, 'comments': c_list})
    elif act == 'comment':
        last_comm = session.get('last_comm_ts', 0)
        if now_ts - last_comm < 5: return jsonify({'success': False, 'message': '评论太频繁了'})
        session['last_comm_ts'] = now_ts
        
        qq = conn.execute("SELECT qq FROM users WHERE username=?", (session['user'],)).fetchone()['qq']
        conn.execute("INSERT INTO comments (post_id, author, author_qq, content, created_at) VALUES (?, ?, ?, ?, ?)", (data.get('post_id'), session['user'], qq, data.get('content'), dt))
        conn.commit()
        return jsonify({'success': True})
    elif act == 'delete':
        post = conn.execute("SELECT author FROM posts WHERE id=?", (data.get('id'),)).fetchone()
        if not post: return jsonify({'success': False, 'message': '帖子不存在'})
        if post['author'] == session['user'] or session.get('role') == 'admin':
            conn.execute("DELETE FROM posts WHERE id=?", (data.get('id'),))
            conn.execute("DELETE FROM comments WHERE post_id=?", (data.get('id'),))
            conn.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '无权操作'})

@app.route('/api/email/action', methods=['POST'])
def email_action():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    conn = get_db()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if act == 'list':
        emails = conn.execute("SELECT * FROM emails WHERE receiver=? ORDER BY id DESC", (session['user'],)).fetchall()
        return jsonify({'success': True, 'emails': [dict(e) for e in emails]})
    elif act == 'send':
        conn.execute("INSERT INTO emails (sender, receiver, title, content, created_at) VALUES (?, ?, ?, ?, ?)", (session['user'], data.get('receiver'), data.get('title'), data.get('content'), dt))
        conn.commit()
        return jsonify({'success': True})

@app.route('/api/admin/action', methods=['POST'])
def admin_action():
    if 'user' not in session or session.get('role') != 'admin': return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    conn = get_db()
    if act == 'data':
        u_c = conn.execute("SELECT count() FROM users").fetchone()[0]
        f_c = conn.execute("SELECT count() FROM files").fetchone()[0]
        users = conn.execute("SELECT username, role, is_vip, mc_uuid, vip_expire, storage_limit, balance, is_banned FROM users ORDER BY created_at DESC").fetchall()
        apps = conn.execute("SELECT id, name, author, created_at FROM apps ORDER BY id DESC").fetchall()
        posts = conn.execute("SELECT id, title, author, created_at FROM posts ORDER BY id DESC").fetchall()
        shares = conn.execute("SELECT s.share_code, s.owner, s.created_at, f.filename FROM shares s LEFT JOIN files f ON s.file_id = f.id ORDER BY s.created_at DESC").fetchall()
        recharges = conn.execute("SELECT * FROM recharge_requests WHERE status='pending' ORDER BY created_at DESC").fetchall()
        reports = conn.execute("SELECT * FROM chat_reports ORDER BY id DESC").fetchall()
        sys_info = {
            'os_name': 'XiYu OS',
            'version': '7.0.7',
            'kernel': 'xiyu-kernel-v707-premium',
            'python_version': '3.x',
            'flask_version': 'latest'
        }
        return jsonify({'success': True, 'stats': {'users_count': u_c, 'files_count': f_c}, 'users': [dict(u) for u in users], 'apps': [dict(a) for a in apps], 'posts': [dict(p) for p in posts], 'shares': [dict(s) for s in shares], 'recharges': [dict(r) for r in recharges], 'reports': [dict(rep) for rep in reports], 'sys_info': sys_info})
    elif act == 'edit_user':
        conn.execute("UPDATE users SET balance=?, is_vip=?, storage_limit=?, role=? WHERE username=?", (data.get('balance'), data.get('is_vip'), data.get('storage_limit'), data.get('role'), data.get('username')))
    elif act == 'reset_password':
        conn.execute("UPDATE users SET password=? WHERE username=?", (data.get('password', '123456'), data.get('username')))
    elif act == 'set_sys_config':
        for k, v in data.get('configs', {}).items():
            conn.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES (?, ?)", (k, v))
    elif act == 'get_sys_config':
        configs = conn.execute("SELECT * FROM sys_config").fetchall()
        return jsonify({'success': True, 'configs': {c['key']: c['value'] for c in configs}})
    elif act == 'approve_recharge':
        req_id = data.get('id')
        r = conn.execute("SELECT * FROM recharge_requests WHERE id=? AND status='pending'", (req_id,)).fetchone()
        if r:
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("UPDATE users SET balance = balance + ? WHERE username=?", (r['amount'], r['username']))
            conn.execute("UPDATE recharge_requests SET status='approved', reviewed_at=? WHERE id=?", (dt, req_id))
    elif act == 'reject_recharge':
        req_id = data.get('id')
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("UPDATE recharge_requests SET status='rejected', reviewed_at=? WHERE id=?", (dt, req_id))
    elif act == 'delete':
        conn.execute("DELETE FROM users WHERE username=?", (data.get('username'),))
        conn.execute("DELETE FROM files WHERE owner=?", (data.get('username'),))
    elif act == 'ban_user':
        conn.execute("UPDATE users SET is_banned=? WHERE username=?", (1 if data.get('is_banned') else 0, data.get('username')))
    elif act == 'delete_report':
        conn.execute("DELETE FROM chat_reports WHERE id=?", (data.get('id'),))
    elif act == 'clear_files': conn.execute("DELETE FROM files WHERE is_deleted=1")
    elif act == 'notice': conn.execute("INSERT OR REPLACE INTO sys_config (key, value) VALUES ('notice', ?)", (data.get('content'),))
    elif act == 'sysmail':
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for u in conn.execute("SELECT username FROM users").fetchall(): 
            conn.execute("INSERT INTO emails (sender, receiver, title, content, created_at) VALUES ('管理员', ?, '系统群发', ?, ?)", (u['username'], data.get('content'), dt))
    elif act == 'delete_app': conn.execute("DELETE FROM apps WHERE id=?", (data.get('id'),))
    elif act == 'delete_post': conn.execute("DELETE FROM posts WHERE id=?", (data.get('id'),))
    elif act == 'delete_share': conn.execute("DELETE FROM shares WHERE share_code=?", (data.get('code'),))
    elif act == 'batch_delete_posts':
        ids = data.get('ids', [])
        for pid in ids: conn.execute("DELETE FROM posts WHERE id=?", (pid,))
    elif act == 'batch_ban':
        usernames = data.get('usernames', [])
        for uname in usernames:
            conn.execute("UPDATE users SET is_banned=1 WHERE username=?", (uname,))
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/share/<code>')
def share_page(code):
    conn = get_db()
    conn.execute("UPDATE shares SET views = views + 1 WHERE share_code=?", (code,))
    conn.commit()
    share = conn.execute("SELECT * FROM shares WHERE share_code=?", (code,)).fetchone()
    if not share:
        return '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>链接失效 - 汐语OS</title>
<style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0a0a0a;color:#fff;font-family:system-ui} .card{text-align:center;padding:50px;background:rgba(255,255,255,0.02);border-radius:30px;border:1px solid rgba(255,255,255,0.05);backdrop-filter:blur(20px)}</style></head>
<body><div class="card"><div style="font-size:80px">📡</div><h2>链接已失效</h2><p style="opacity:0.5">该分享码不存在或已被撤回</p></div></body></html>'''
    
    file = conn.execute("SELECT * FROM files WHERE id=?", (share['file_id'],)).fetchone()
    if not file:
        return '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>文件消失 - 汐语OS</title>
<style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0a0a0a;color:#fff;font-family:system-ui} .card{text-align:center;padding:50px;background:rgba(255,255,255,0.02);border-radius:30px;border:1px solid rgba(255,255,255,0.05);backdrop-filter:blur(20px)}</style></head>
<body><div class="card"><div style="font-size:80px">📦</div><h2>源文件已移除</h2><p style="opacity:0.5">分享的文件已被所有者从系统中移除</p></div></body></html>'''
    
    data_url = file['content'] or ''
    dl_attr = 'download' if 'base64,' in data_url else ''
    href = data_url if 'base64,' in data_url else '#'
    fsize = "{:.2f}".format(len(data_url) / 1024)
    f_icon = {'dir':'fa-folder-open','media':'fa-compact-disc','image':'fa-image','doc':'fa-file-signature'}.get(file['type'], 'fa-file-alt')
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>{file["filename"]} - 极速分享</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --primary: #00d2ff; --secondary: #3a7bd5; }}
        * {{ margin:0; padding:0; box-sizing:border-box; font-family: "Segoe UI", "PingFang SC", sans-serif; }}
        body {{ min-height:100vh; background:#050505; color:#fff; display:flex; align-items:center; justify-content:center; overflow:hidden; }}
        .bg-glow {{ position:fixed; width:400px; height:400px; background:radial-gradient(circle, var(--primary), transparent 70%); filter:blur(100px); opacity:0.1; z-index:-1; animation: float 10s infinite alternate; }}
        @keyframes float {{ from {{ transform: translate(-50%, -50%); }} to {{ transform: translate(50%, 40%); }} }}
        .card {{ background:rgba(255,255,255,0.03); backdrop-filter:blur(40px) saturate(180%); border:1px solid rgba(255,255,255,0.08); border-radius:40px; width:450px; padding:60px 40px; box-shadow:0 50px 100px rgba(0,0,0,0.8); position:relative; overflow:hidden; text-align:center; }}
        .card::before {{ content:''; position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(90deg, var(--primary), var(--secondary)); }}
        .icon-box {{ width:100px; height:100px; background:rgba(255,255,255,0.05); border-radius:30px; margin:0 auto 30px; display:flex; align-items:center; justify-content:center; font-size:45px; color:var(--primary); box-shadow:0 20px 40px rgba(0,0,0,0.2); border:1px solid rgba(255,255,255,0.1); }}
        .title {{ font-size:28px; font-weight:800; margin-bottom:10px; background:linear-gradient(to bottom, #fff, #999); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
        .stats {{ display:flex; justify-content:center; gap:20px; font-size:13px; color:#888; margin-bottom:35px; }}
        .stat-item {{ display:flex; align-items:center; gap:6px; background:rgba(255,255,255,0.05); padding:6px 12px; border-radius:20px; }}
        .dl-btn {{ display:block; width:100%; padding:20px; background:linear-gradient(135deg, var(--primary), var(--secondary)); border-radius:20px; color:#fff; text-decoration:none; font-weight:800; font-size:18px; transition:0.4s; box-shadow:0 15px 30px rgba(0,210,255,0.2); }}
        .dl-btn:hover {{ transform:translateY(-5px); box-shadow:0 25px 45px rgba(0,210,255,0.4); filter:brightness(1.1); }}
        .footer {{ margin-top:40px; font-size:11px; color:rgba(255,255,255,0.2); letter-spacing:2px; text-transform:uppercase; }}
    </style>
</head>
<body>
    <div class="bg-glow"></div>
    <div class="card">
        <div class="icon-box"><i class="fas {f_icon}"></i></div>
        <h1 class="title">{file["filename"]}</h1>
        <div class="stats">
            <div class="stat-item"><i class="fas fa-eye"></i> {share["views"]} 次浏览</div>
            <div class="stat-item"><i class="fas fa-database"></i> {fsize} KB</div>
        </div>
        <div style="background:rgba(255,255,255,0.03); border-radius:20px; padding:20px; margin-bottom:30px; border:1px solid rgba(255,255,255,0.05); font-size:14px;">
            <div style="opacity:0.4; margin-bottom:5px;">分享者</div>
            <div style="font-weight:700; font-size:16px;">{share["owner"]}</div>
            <div style="font-size:11px; opacity:0.3; margin-top:10px;">发布于 {share["created_at"]}</div>
        </div>
        <a class="dl-btn" href="{href}" {dl_attr}="{file['filename']}">
            <i class="fas fa-download"></i> 立即下载
        </a>
        <div class="footer">XiYu OS Cloud Architecture</div>
    </div>
</body>
</html>'''

@app.route('/dl/<int:file_id>')
def direct_link(file_id):
    conn = get_db()
    
    file = conn.execute("SELECT * FROM files WHERE id=?", (file_id,)).fetchone()
    if not file: return "文件不存在"
    
    # 允许分享文件或VIP自己下载
    share = conn.execute("SELECT * FROM shares WHERE file_id=?", (file_id,)).fetchone()
    if not share:
        if 'user' not in session: return "未登录，仅限VIP用户使用私人直链"
        u = conn.execute("SELECT is_vip FROM users WHERE username=?", (session['user'],)).fetchone()
        if not u or not u['is_vip']: return "仅限VIP使用私人文件直链功能"
    
    file = conn.execute("SELECT * FROM files WHERE id=?", (file_id,)).fetchone()
    if not file: return "文件不存在"
    
    content = file['content'] or ''
    import base64
    if 'base64,' in content:
        data = base64.b64decode(content.split('base64,')[1])
        r = make_response(data)
        # Determine strict MIME? Guess from extension or return binary chunk.
        r.headers['Content-Disposition'] = f'attachment; filename={file["filename"]}'
        return r
    else:
        r = make_response(content)
        r.headers['Content-Disposition'] = f'attachment; filename={file["filename"]}'
        return r


@app.route('/api/oa/action', methods=['POST'])
def oa_action():
    if 'user' not in session: return jsonify({'success': False, 'message': '未登录'})
    data = request.json
    act = data.get('action')
    conn = get_db()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if act == 'apply':
        # Check if user already has an OA
        existing = conn.execute("SELECT id FROM official_accounts WHERE owner=?", (session['user'],)).fetchone()
        if existing: return jsonify({'success': False, 'message': '你已经申请或拥有一个公众号了'})
        
        name = data.get('name')
        desc = data.get('desc')
        icon = data.get('icon', 'fa-bullhorn')
        color = data.get('color', '#00c6fb')
        if not name or not desc: return jsonify({'success': False, 'message': '请填写名称和简介'})
        
        conn.execute("INSERT INTO official_accounts (name, icon, color, description, owner, status, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?)",
                     (name, icon, color, desc, session['user'], dt))
        conn.commit()
        return jsonify({'success': True, 'message': '申请已提交，请等待审核'})

    elif act == 'list':
        # List approved accounts
        rows = conn.execute("SELECT * FROM official_accounts WHERE status='approved'").fetchall()
        oa_list = []
        for r in rows:
            oa = dict(r)
            arts = conn.execute("SELECT * FROM oa_articles WHERE oa_id=? ORDER BY id DESC", (oa['id'],)).fetchall()
            oa['articles'] = [dict(a) for a in arts]
            # Get follower count
            oa['followers_count'] = conn.execute("SELECT count(*) FROM oa_follows WHERE oa_id=?", (oa['id'],)).fetchone()[0]
            # Check if current user is following
            is_f = conn.execute("SELECT 1 FROM oa_follows WHERE oa_id=? AND username=?", (oa['id'], session['user'])).fetchone()
            oa['is_following'] = True if is_f else False
            oa_list.append(oa)
        return jsonify({'success': True, 'accounts': oa_list})

    elif act == 'my_oa':
        oa_id = data.get('oa_id')
        if oa_id:
            oa = conn.execute("SELECT * FROM official_accounts WHERE id=? AND owner=?", (oa_id, session['user'])).fetchone()
        else:
            oa = conn.execute("SELECT * FROM official_accounts WHERE owner=?", (session['user'],)).fetchone()
            
        if not oa: return jsonify({'success': False, 'message': '公众号不存在或权限不足'})
        oa_dict = dict(oa)
        arts = conn.execute("SELECT * FROM oa_articles WHERE oa_id=? ORDER BY id DESC", (oa_dict['id'],)).fetchall()
        oa_dict['articles'] = [dict(a) for a in arts]
        oa_dict['followers_count'] = conn.execute("SELECT count(*) FROM oa_follows WHERE oa_id=?", (oa_dict['id'],)).fetchone()[0]
        return jsonify({'success': True, 'oa': oa_dict})

    elif act == 'post_article':
        oa_id = data.get('oa_id')
        title = data.get('title')
        content = data.get('content')
        # Verify ownership
        oa = conn.execute("SELECT id FROM official_accounts WHERE id=? AND owner=?", (oa_id, session['user'])).fetchone()
        if not oa: return jsonify({'success': False, 'message': '权限不足'})
        
        conn.execute("INSERT INTO oa_articles (oa_id, title, content, created_at) VALUES (?, ?, ?, ?)", (oa_id, title, content, dt))
        conn.commit()
        return jsonify({'success': True})

    elif act == 'delete_article':
        art_id = data.get('id')
        oa_id = data.get('oa_id')
        oa = conn.execute("SELECT id FROM official_accounts WHERE id=? AND owner=?", (oa_id, session['user'])).fetchone()
        if not oa: return jsonify({'success': False, 'message': '权限不足'})
        
        conn.execute("DELETE FROM oa_articles WHERE id=? AND oa_id=?", (art_id, oa_id))
        conn.commit()
        return jsonify({'success': True})

    elif act == 'update_config':
        oa_id = data.get('oa_id')
        oa = conn.execute("SELECT id FROM official_accounts WHERE id=? AND owner=?", (oa_id, session['user'])).fetchone()
        if not oa: return jsonify({'success': False, 'message': '权限不足'})
        
        if 'page_config' in data: conn.execute("UPDATE official_accounts SET page_config=? WHERE id=?", (data['page_config'], oa_id))
        if 'bot_enabled' in data: conn.execute("UPDATE official_accounts SET bot_enabled=? WHERE id=?", (data['bot_enabled'], oa_id))
        if 'bot_config' in data: conn.execute("UPDATE official_accounts SET bot_config=? WHERE id=?", (data['bot_config'], oa_id))
        if 'hulling_code' in data: conn.execute("UPDATE official_accounts SET hulling_code=? WHERE id=?", (data['hulling_code'], oa_id))
        
        conn.commit()
        return jsonify({'success': True})

    elif act == 'update_info':
        oa_id = data.get('oa_id')
        oa = conn.execute("SELECT id FROM official_accounts WHERE id=? AND owner=?", (oa_id, session['user'])).fetchone()
        if not oa: return jsonify({'success': False, 'message': '权限不足'})
        
        name = data.get('name')
        desc = data.get('desc')
        icon = data.get('icon')
        color = data.get('color')
        
        if name: conn.execute("UPDATE official_accounts SET name=? WHERE id=?", (name, oa_id))
        if desc: conn.execute("UPDATE official_accounts SET description=? WHERE id=?", (desc, oa_id))
        if icon: conn.execute("UPDATE official_accounts SET icon=? WHERE id=?", (icon, oa_id))
        if color: conn.execute("UPDATE official_accounts SET color=? WHERE id=?", (color, oa_id))
        
        conn.commit()
        return jsonify({'success': True})

    elif act == 'follow':
        oa_id = data.get('id')
        try:
            conn.execute("INSERT INTO oa_follows (oa_id, username, created_at) VALUES (?, ?, ?)", (oa_id, session['user'], dt))
            conn.commit()
        except sqlite3.IntegrityError: pass
        return jsonify({'success': True})

    elif act == 'unfollow':
        oa_id = data.get('id')
        conn.execute("DELETE FROM oa_follows WHERE oa_id=? AND username=?", (oa_id, session['user']))
        conn.commit()
        return jsonify({'success': True})

    elif act == 'subscribers':
        oa_id = data.get('oa_id')
        # Check ownership
        oa = conn.execute("SELECT id FROM official_accounts WHERE id=? AND owner=?", (oa_id, session['user'])).fetchone()
        if not oa: return jsonify({'success': False, 'message': '权限不足'})
        
        subs = conn.execute("""
            SELECT u.username, u.avatar, u.mc_uuid, u.qq, u.uid, f.created_at
            FROM oa_follows f
            JOIN users u ON f.username = u.username
            WHERE f.oa_id=?
            ORDER BY f.created_at DESC
        """, (oa_id,)).fetchall()
        
        sub_list = []
        for s in subs:
            sd = dict(s)
            sd['avatar'] = get_computed_avatar(sd)
            sub_list.append(sd)
        return jsonify({'success': True, 'subscribers': sub_list})

    elif act == 'conversations':
        oa_id = data.get('oa_id')
        oa = conn.execute("SELECT id FROM official_accounts WHERE id=? AND owner=?", (oa_id, session['user'])).fetchone()
        if not oa: return jsonify({'success': False, 'message': '权限不足'})
        
        # Get distinct users who interactive with this OA
        convos = conn.execute("""
            SELECT m1.*, u.avatar, u.mc_uuid, u.qq, u.uid as user_uid, u.username as user_name
            FROM messages m1
            INNER JOIN (
                SELECT MAX(id) as id, 
                       CASE WHEN sender=:oa THEN receiver ELSE sender END as other_party
                FROM messages
                WHERE (sender=:oa OR receiver=:oa) AND receiver != 'group'
                GROUP BY CASE WHEN sender=:oa THEN receiver ELSE sender END
            ) m2 ON m1.id = m2.id
            JOIN users u ON m2.other_party = u.username
            ORDER BY m1.id DESC
        """, {'oa': str(oa_id)}).fetchall()
        
        res_list = []
        for c in convos:
            cd = dict(c)
            cd['avatar'] = get_computed_avatar(cd)
            res_list.append(cd)
        return jsonify({'success': True, 'conversations': res_list})

    elif act == 'edit_article':
        art_id = data.get('id')
        oa_id = data.get('oa_id')
        title = data.get('title')
        content = data.get('content')
        # Verify ownership
        oa = conn.execute("SELECT id FROM official_accounts WHERE id=? AND owner=?", (oa_id, session['user'])).fetchone()
        if not oa: return jsonify({'success': False, 'message': '权限不足'})
        
        conn.execute("UPDATE oa_articles SET title=?, content=? WHERE id=? AND oa_id=?", (title, content, art_id, oa_id))
        conn.commit()
        return jsonify({'success': True})

    elif act == 'broadcast':
        oa_id = data.get('oa_id')
        content = data.get('content')
        if not content: return jsonify({'success': False, 'message': '内容不能为空'})
        
        # Verify ownership and get OA info
        oa = conn.execute("SELECT id, name FROM official_accounts WHERE id=? AND owner=?", (oa_id, session['user'])).fetchone()
        if not oa: return jsonify({'success': False, 'message': '权限不足'})
        
        # Get all followers
        followers = conn.execute("SELECT username FROM oa_follows WHERE oa_id=?", (oa_id,)).fetchall()
        
        # Send message to each follower
        for f in followers:
            conn.execute("INSERT INTO messages (sender, receiver, content, type, created_at) VALUES (?, ?, ?, 'text', ?)",
                         (oa_id, f['username'], content, dt))
        
        conn.commit()
        return jsonify({'success': True, 'count': len(followers)})

    elif act == 'stats':
        oa_id = data.get('oa_id')
        oa = conn.execute("SELECT id FROM official_accounts WHERE id=? AND owner=?", (oa_id, session['user'])).fetchone()
        if not oa: return jsonify({'success': False, 'message': '权限不足'})
        
        f_count = conn.execute("SELECT count(*) FROM oa_follows WHERE oa_id=?", (oa_id,)).fetchone()[0]
        a_count = conn.execute("SELECT count(*) FROM oa_articles WHERE oa_id=?", (oa_id,)).fetchone()[0]
        
        # Get last 7 days growth (simplified for now as we don't have historical snapshots, but can count recent joins)
        recent_joins = conn.execute("SELECT count(*) FROM oa_follows WHERE oa_id=? AND created_at > datetime('now', '-7 days')", (oa_id,)).fetchone()[0]
        
        return jsonify({'success': True, 'stats': {
            'followers': f_count, 
            'articles': a_count,
            'recent_growth': recent_joins
        }})

    return jsonify({'success': False})

@app.route('/api/admin/oa/list', methods=['POST'])
def admin_oa_list():
    if session.get('role') != 'admin': return jsonify({'success': False})
    conn = get_db()
    rows = conn.execute("SELECT * FROM official_accounts ORDER BY id DESC").fetchall()
    return jsonify({'success': True, 'accounts': [dict(r) for r in rows]})

@app.route('/api/admin/oa/action', methods=['POST'])
def admin_oa_action():
    if session.get('role') != 'admin': return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    oa_id = data.get('id')
    conn = get_db()
    
    if act == 'approve':
        conn.execute("UPDATE official_accounts SET status='approved' WHERE id=?", (oa_id,))
    elif act == 'reject':
        conn.execute("UPDATE official_accounts SET status='rejected' WHERE id=?", (oa_id,))
    elif act == 'delete':
        conn.execute("DELETE FROM official_accounts WHERE id=?", (oa_id,))
        conn.execute("DELETE FROM oa_articles WHERE oa_id=?", (oa_id,))
    
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/task/action', methods=['POST'])
def task_action():
    if 'user' not in session: return jsonify({'success': False})
    data = request.json
    act = data.get('action')
    conn = get_db()
    today = datetime.date.today().isoformat()
    
    if act == 'list':
        # Ensure default tasks exist
        if conn.execute("SELECT count(*) FROM daily_tasks").fetchone()[0] == 0:
            tasks = [
                ('签到任务', '每日点击签到', 10, 'sign', 1),
                ('私聊达人', '发送 5 条私聊消息', 20, 'chat', 5),
                ('空间动态', '在这这里发布 1 条动态', 15, 'moment', 1)
            ]
            conn.executemany("INSERT INTO daily_tasks (name, description, reward, type, target_count) VALUES (?, ?, ?, ?, ?)", tasks)
            conn.commit()
            
        tasks = conn.execute("SELECT * FROM daily_tasks").fetchall()
        user_tasks = conn.execute("SELECT * FROM user_tasks WHERE username=? AND date=?", (session['user'], today)).fetchall()
        ut_dict = {ut['task_id']: ut for ut in user_tasks}
        
        res = []
        for t in tasks:
            ut = ut_dict.get(t['id'])
            res.append({
                'id': t['id'],
                'name': t['name'],
                'description': t['description'],
                'reward': t['reward'],
                'target': t['target_count'],
                'current': ut['count'] if ut else 0,
                'claimed': ut['is_claimed'] if ut else 0
            })
        return jsonify({'success': True, 'tasks': res})
        
    elif act == 'claim':
        tid = data.get('id')
        ut = conn.execute("SELECT ut.*, t.reward FROM user_tasks ut JOIN daily_tasks t ON ut.task_id = t.id WHERE ut.username=? AND ut.task_id=? AND ut.date=?", (session['user'], tid, today)).fetchone()
        if not ut: return jsonify({'success': False, 'message': '任务未完成'})
        if ut['is_claimed']: return jsonify({'success': False, 'message': '奖励已领取'})
        
        t = conn.execute("SELECT * FROM daily_tasks WHERE id=?", (tid,)).fetchone()
        if ut['count'] < t['target_count']: return jsonify({'success': False, 'message': '任务进度不足'})
        
        conn.execute("UPDATE user_tasks SET is_claimed=1 WHERE username=? AND task_id=? AND date=?", (session['user'], tid, today))
        # Tasks now only reward experience (5x reward value as exp)
        exp_reward = ut['reward'] * 5
        conn.execute("UPDATE users SET exp = exp + ? WHERE username=?", (exp_reward, session['user']))
        conn.commit()
        return jsonify({'success': True, 'message': f"领取成功！获得 {exp_reward} 经验值"})

    return jsonify({'success': False})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)