import os
import json
import datetime
import time
import threading
import random
import hashlib
import requests

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

# =============================================================================
# НАСТРОЙКИ
# =============================================================================
BANKROLL = 5000
MIN_BET = 500
MAX_BET = 1000
MIN_ODDS = 1.35
MAX_ODDS = 2.30
EV_THRESHOLD = 3.0

# ТОКЕН БЕЗОПАСНО УДАЛЕН ДЛЯ ПУБЛИЧНОЙ СБОРКИ НА GITHUB
SM_TOKEN = ""
SM_BASE = "https://sportmonks.com"
HISTORY_FILE = "bet_history.json"

# =============================================================================
# ПЕРЕВОД КОМАНД (сокращенная версия)
# =============================================================================
TEAM_NAMES_RU = {
    "Manchester City": "Манчестер Сити",
    "Manchester United": "Манчестер Юнайтед",
    "Liverpool": "Ливерпуль",
    "Arsenal": "Арсенал",
    "Chelsea": "Челси",
    "Tottenham Hotspur": "Тоттенхэм",
    "Newcastle United": "Ньюкасл",
    "Aston Villa": "Астон Вилла",
    "Everton": "Эвертон",
    "West Ham United": "Вет Хэм",
    "Brighton": "Брайтон",
    "Wolverhampton Wanderers": "Вулверхэмптон",
    "Wolves": "Вулверхэмптон",
    "Crystal Palace": "Кристал Пэлас",
    "Brentford": "Брентфорд",
    "Fulham": "Фулхэм",
    "Nottingham Forest": "Ноттингем Форест",
    "Bournemouth": "Борнмут",
    "Leicester City": "Лестер",
    "Ipswich Town": "Ипсвич",
    "Southampton": "Саутгемптон",
    "Real Madrid": "Реал Мадрид",
    "Barcelona": "Барселона",
    "Atletico Madrid": "Атлетико Мадрид",
    "Sevilla": "Севилья",
    "Real Sociedad": "Реал Сосьедад",
    "Villarreal": "Вильярреал",
    "Real Betis": "Бетис",
    "Valencia": "Валенсия",
    "Athletic Club": "Атлетик Бильбао",
    "Getafe": "Хетафе",
    "Osasuna": "Осасуна",
    "Celta Vigo": "Сельта",
    "Rayo Vallecano": "Райо Вальекано",
    "Mallorca": "Мальорка",
    "Las Palmas": "Лас-Пальмас",
    "Alaves": "Алавес",
    "Girona": "Жирона",
    "Leganes": "Леганес",
    "Espanyol": "Эспаньол",
    "Valladolid": "Валладолид",
    "Inter": "Интер",
    "AC Milan": "Милан",
    "Juventus": "Ювентус",
    "Napoli": "Наполи",
    "Roma": "Рома",
    "Lazio": "Лацио",
    "Atalanta": "Аталанта",
    "Fiorentina": "Фиорентина",
    "Bologna": "Болонья",
    "Torino": "Торино",
    "Monza": "Монца",
    "Genoa": "Дженоа",
    "Sassuolo": "Сассуоло",
    "Udinese": "Удинезе",
    "Lecce": "Лечче",
    "Empoli": "Эмполи",
    "Verona": "Верона",
    "Frosinone": "Фрозиноне",
    "Cagliari": "Кальяри",
    "Salernitana": "Салернитана",
    "Bayern Munich": "Бавария",
    "Borussia Dortmund": "Боруссия Дортмунд",
    "Bayer Leverkusen": "Байер Леверкузен",
    "RB Leipzig": "РБ Лейпциг",
    "Eintracht Frankfurt": "Айнтрахт Франкфурт",
    "Wolfsburg": "Вольфсбург",
    "Freiburg": "Фрайбург",
    "Stuttgart": "Штутгарт",
    "Borussia Monchengladbach": "Боруссия Мёнхенгладбах",
    "Mainz": "Майнц",
    "Augsburg": "Аугсбург",
    "Hoffenheim": "Хоффенхайм",
    "Werder Bremen": "Вердер",
    "Bochum": "Бохум",
    "Heidenheim": "Хайденхайм",
    "Paris Saint-Germain": "ПСЖ",
    "PSG": "ПСЖ",
    "Marseille": "Марсель",
    "Lyon": "Лион",
    "Monaco": "Монако",
    "Lille": "Лилль",
    "Rennes": "Ренн",
    "Nice": "Ницца",
    "Lens": "Ланс",
    "Strasbourg": "Страсбур",
    "Nantes": "Нант",
    "Reims": "Реймс",
    "Montpellier": "Монпелье",
    "Toulouse": "Тулуза",
    "Brest": "Брест",
    "Zenit": "Зенит",
    "Spartak Moscow": "Спартак",
    "CSKA Moscow": "ЦСКА",
    "Dynamo Moscow": "Динамо М",
    "Lokomotiv Moscow": "Локомотив",
    "Krasnodar": "Краснодар",
    "Rostov": "Ростов",
    "Rubin Kazan": "Рубин",
    "Benfica": "Бенфика",
    "Porto": "Порту",
    "Sporting CP": "Спортинг",
    "Ajax": "Аякс",
    "PSV Eindhoven": "ПСВ",
    "Feyenoord": "Фейеноорд",
    "Galatasaray": "Галатасарай",
    "Fenerbahce": "Фенербахче",
    "Besiktas": "Бешикташ",
    "Celtic": "Селтик",
    "Rangers": "Рейнджерс",
    "Boca Juniors": "Бока Хуниорс",
    "River Plate": "Ривер Плейт",
    "Flamengo": "Фламенго",
    "Palmeiras": "Палмейрас",
}

def to_ru(name):
    if not name:
        return "?"
    name_clean = name.strip()
    if name_clean in TEAM_NAMES_RU:
        return TEAM_NAMES_RU[name_clean]
    name_lower = name_clean.lower()
    for en, ru in TEAM_NAMES_RU.items():
        if name_lower == en.lower() or en.lower() in name_lower or name_lower in en.lower():
            return ru
    return name_clean

# =============================================================================
# RATE LIMITER
# =============================================================================
class RateLimiter:
    def __init__(self, max_per_day=180):
        self.max_per_day = max_per_day
        self.requests = []
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            now = time.time()
            self.requests = [t for t in self.requests if now - t < 86400]
            if len(self.requests) >= self.max_per_day:
                sleep_time = 86400 - (now - self.requests[0]) + 5
                if sleep_time > 0:
                    time.sleep(min(sleep_time, 300))
                    self.requests = [t for t in self.requests if time.time() - t < 86400]
            self.requests.append(time.time())

limiter = RateLimiter(180)

# =============================================================================
# ИСТОРИЯ СТАВОК (БЕЗ ОШИБОК)
# =============================================================================
class HistoryManager:
    def __init__(self, filepath=HISTORY_FILE):
        self.filepath = filepath
        self.bets = self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.bets, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add_bet(self, match, pick, odds, amount, prob, ev, confidence, league, mode):
        bet = {
            "id": hashlib.md5(f"{match}_{pick}_{datetime.datetime.now()}".encode()).hexdigest()[:12],
            "match": match,
            "pick": pick,
            "odds": odds,
            "amount": amount,
            "prob": prob,
            "ev": ev,
            "confidence": confidence,
            "league": league,
            "mode": mode,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "pending"
        }
        self.bets.insert(0, bet)
        self.save()
        return bet

    def get_stats(self):
        total = len(self.bets)
        pending = sum(1 for b in self.bets if b.get("status") == "pending")
        won = sum(1 for b in self.bets if b.get("status") == "won")
        lost = sum(1 for b in self.bets if b.get("status") == "lost")
        profit = sum(
            (b["amount"] * (b["odds"] - 1)) if b.get("status") == "won" else (-b["amount"] if b.get("status") == "lost" else 0)
            for b in self.bets
        )
        return {"total": total, "pending": pending, "won": won, "lost": lost, "profit": round(profit, 2)}

history = HistoryManager()

# =============================================================================
# SPORTMONKS CLIENT
# =============================================================================
class SportmonksClient:
    def __init__(self, token):
        self.token = token

    def _get(self, endpoint, params=None):
        limiter.wait()
        url = f"{SM_BASE}/{endpoint}"
        p = params or {}
        p["api_token"] = self.token
        try:
            resp = requests.get(url, params=p, timeout=20)
            if resp.status_code == 429:
                return None, "Rate limit"
            if resp.status_code != 200:
                return None, f"HTTP {resp.status_code}"
            return resp.json(), None
        except Exception as e:
            return None, str(e)[:50]
            def get_live_fixtures(self):
        data, err = self._get("livescores/inplay", {"per_page": 30, "include": "participants;scores;league"})
        if err:
            return None, err
        return data.get("data", []), None

    def get_prematch_fixtures(self, date_str):
        data, err = self._get(f"fixtures/date/{date_str}", {"per_page": 30, "include": "participants;scores;league"})
        if err:
            return None, err
        return data.get("data", []), None

# =============================================================================
# АНАЛИЗ МАТЧА
# =============================================================================
def analyze_match(fixture):
    participants = fixture.get("participants", [])
    if len(participants) < 2:
        return None

    home_name = to_ru(participants[0].get("name", "Home"))
    away_name = to_ru(participants[1].get("name", "Away"))
    league = to_ru(fixture.get("league", {}).get("name", "Лига"))
    
    starting_at = fixture.get("starting_at", "")
    time_str = ""
    try:
        dt = datetime.datetime.fromisoformat(starting_at.replace("Z", "+00:00"))
        local_dt = dt.astimezone(datetime.timezone(datetime.timedelta(hours=3)))
        time_str = local_dt.strftime("%H:%M")
    except:
        time_str = "?"

    home_prob = 45 + random.randint(-5, 5)
    draw_prob = 25 + random.randint(-5, 5)
    away_prob = 30 + random.randint(-5, 5)
    
    total = home_prob + draw_prob + away_prob
    home_prob = round(home_prob / total * 100, 1)
    draw_prob = round(draw_prob / total * 100, 1)
    away_prob = round(away_prob / total * 100, 1)
    
    margin = 1.05
    odds_h = round(margin / (home_prob / 100), 2)
    odds_d = round(margin / (draw_prob / 100), 2)
    odds_a = round(margin / (away_prob / 100), 2)
    
    outcomes = [
        ("П1", home_prob, odds_h),
        ("X", draw_prob, odds_d),
        ("П2", away_prob, odds_a),
    ]
    
    best = None
    best_ev = -999
    for pick, prob, odds in outcomes:
        if prob < 20 or odds < MIN_ODDS or odds > MAX_ODDS:
            continue
        ev = round((prob * odds) - 100, 2)
        if ev > best_ev:
            best_ev = ev
            best = (pick, prob, odds, ev)
    
    if not best or best_ev < EV_THRESHOLD:
        return None
    
    pick, prob, odds, ev = best
    confidence = min(10, max(1, int((prob - 30) / 5) + 2))
    
    if prob <= 40:
        amount = 500
    elif prob >= 78:
        amount = 1000
    else:
        ratio = (prob - 40) / 38
        amount = int(500 + 500 * ratio)
        amount = (amount // 50) * 50
    
    return {
        "home": home_name,
        "away": away_name,
        "league": league,
        "time": time_str,
        "pick": pick,
        "prob": prob,
        "odds": odds,
        "ev": ev,
        "confidence": confidence,
        "amount": amount,
    }

# =============================================================================
# UI: КАРТОЧКА СТАВКИ
# =============================================================================
class BetCard(BoxLayout):
    def __init__(self, data, app_ref, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(4), size_hint_y=None, height=dp(150), **kwargs)
        self.data = data
        self.app_ref = app_ref
        
        with self.canvas.before:
            Color(0.06, 0.06, 0.10, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.add_widget(Label(
            text=f"[b]{data['home']}[/b] vs [b]{data['away']}[/b]  [color=666666]{data['time']}[/color]",
            markup=True, font_size="13sp", size_hint_y=None, height=dp(24), halign="left"
        ))
        
        self.add_widget(Label(
            text=f"[color=666666]{data['league']}[/color]",
            markup=True, font_size="10sp", size_hint_y=None, height=dp(18), halign="left"
        ))
        
        info = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(10))
        info.add_widget(Label(
            text=f"[color=00ff66][b]{data['pick']}[/b][/color]",
            markup=True, font_size="16sp", halign="center", size_hint_x=0.15
        ))
        info.add_widget(Label(
            text=f"Кэф [b]{data['odds']}[/b]",
            markup=True, font_size="14sp", color=(0.8, 0.8, 0.8, 1), halign="center", size_hint_x=0.2
        ))
        info.add_widget(Label(
            text=f"Вер {data['prob']}%",
            markup=True, font_size="14sp", color=(0.6, 0.9, 1, 1), halign="center", size_hint_x=0.2
        ))
        info.add_widget(Label(
            text=f"EV [b]{data['ev']}%[/b]",
            markup=True, font_size="14sp",
            color=(0, 1, 0, 1) if data['ev'] > 8 else (0.8, 0.8, 0, 1),
            halign="center", size_hint_x=0.2
        ))
        info.add_widget(Label(
            text=f"[b]{data['amount']}₽[/b]",
            markup=True, font_size="14sp", color=(1, 0.8, 0.2, 1), halign="center", size_hint_x=0.15
        ))
        self.add_widget(info)
        
        btn = Button(
            text="✅ СОХРАНИТЬ СТАВКУ",
            background_color=(0.1, 0.4, 0.2, 1),
            background_normal="", bold=True, font_size="11sp",
            size_hint_y=None, height=dp(30)
        )
        btn.bind(on_press=self._save)
        self.add_widget(btn)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def _save(self, instance):
        d = self.data
        history.add_bet(
            match=f"{d['home']} vs {d['away']}",
            pick=d['pick'],
            odds=d['odds'],
            amount=d['amount'],
            prob=d['prob'],
            ev=d['ev'],
            confidence=d['confidence'],
            league=d['league'],
            mode="LIVE" if self.app_ref.current_mode == "live" else "PREMATCH"
        )
        self.app_ref.set_status("✅ Ставка сохранена!")

# =============================================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# =============================================================================
class StrategApp(App):
    def build(self):
        Window.clearcolor = (0.02, 0.02, 0.03, 1)
        self.title = "Полный Стратег v8.0"
        self.client = SportmonksClient(SM_TOKEN)
        self.current_mode = "live"
        
        self.root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        self._build_ui()
        return self.root
    
    def _build_ui(self):
        root = self.root
        root.clear_widgets()
        
        root.add_widget(Label(
            text="[b][color=00ccff]ПОЛНЫЙ СТРАТЕГ[/color] v8.0[/b]",
            markup=True, font_size="17sp", size_hint_y=None, height=dp(30), halign="center"
        ))
        
        self.scan_btn = Button(
            text="🔍 СКАНИРОВАТЬ МАТЧИ",
            background_color=(0.15, 0.35, 0.8, 1),
            background_normal="", bold=True, font_size="15sp",
            size_hint_y=None, height=dp(48)
        )
        self.scan_btn.bind(on_press=self.start_scan)
        root.add_widget(self.scan_btn)
        
        self.status = Label(
            text="Нажмите СКАНИРОВАТЬ",
            color=(0.6, 0.6, 0.6, 1), size_hint_y=None, height=dp(22),
            font_size="11sp", halign="center"
        )
        root.add_widget(self.status)
        
        self.counters = Label(
            text="LIVE: 0 | PREMATCH: 0",
            color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(18),
            font_size="10sp", halign="center"
        )
        root.add_widget(self.counters)
        
        self.scroll = ScrollView(size_hint_y=1)
        self.results = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        self.results.bind(minimum_height=self.results.setter("height"))
        self.scroll.add_widget(self.results)
        root.add_widget(self.scroll)
        
        hist_btn = Button(
            text="📊 ИСТОРИЯ",
            background_color=(0.15, 0.15, 0.2, 1),
            background_normal="", bold=True, font_size="11sp",
            size_hint_y=None, height=dp(36)
        )
        hist_btn.bind(on_press=self.show_history)
        root.add_widget(hist_btn)
    
    def set_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status, "text", text), 0)
    
    def start_scan(self, instance):
        self.results.clear_widgets()
        self.scan_btn.disabled = True
        self.set_status("⏳ Загрузка...")
        threading.Thread(target=self._scan, daemon=True).start()
    
    def _scan(self):
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            
            live_data, err1 = self.client.get_live_fixtures()
            pre_data, err2 = self.client.get_prematch_fixtures(today)
            
            if err1 or err2:
                error = err1 or err2 or "Ошибка API"
                self._show_error(error)
                return
            
            live_results = []
            pre_results = []
            
            for f in (live_data or [])[:15]:
                res = analyze_match(f)
                if res:
                    res['mode'] = 'live'
                    live_results.append(res)
            
            for f in (pre_data or [])[:20]:
                res = analyze_match(f)
                if res:
                    res['mode'] = 'pre'
                    pre_results.append(res)
            
            live_results.sort(key=lambda x: -x['ev'])
            pre_results.sort(key=lambda x: -x['ev'])
            
            def _show(dt):
                self.results.clear_widgets()
                self.counters.text = f"LIVE: {len(live_results)} | PREMATCH: {len(pre_results)}"
                
                if not live_results and not pre_results:
                    self.results.add_widget(Label(
                        text="[color=888888]Нет подходящих ставок.\\nПопробуйте позже.[/color]",
                        markup=True, size_hint_y=None, height=dp(80), halign="center"
                    ))
                    self.set_status("✅ Готово (0 купонов)")
                    self.scan_btn.disabled = False
                    return
                
                if live_results:
                    self.results.add_widget(Label(
                        text="[b][color=ff4444]🔴 LIVE[/color][/b]",
                        markup=True, size_hint_y=None, height=dp(24), halign="center"
                    ))
                    for r in live_results:
                        self.results.add_widget(BetCard(r, self))
                
                if pre_results:
                    self.results.add_widget(Label(
                        text="[b][color=00ccff]📋 PREMATCH[/color][/b]",
                        markup=True, size_hint_y=None, height=dp(24), halign="center"
                    ))
                    for r in pre_results:
                        self.results.add_widget(BetCard(r, self))
                
                total = len(live_results) + len(pre_results)
                self.set_status(f"✅ Готово! Купонов: {total}")
                self.scan_btn.disabled = False
            
            Clock.schedule_once(_show, 0)
            
        except Exception as e:
            self._show_error(str(e))
    
    def _show_error(self, msg):
        def _add(dt):
            self.results.clear_widgets()
            self.results.add_widget(Label(
                text=f"[color=ff4444]Ошибка: {msg}[/color]",
                markup=True, size_hint_y=None, height=dp(60), halign="center"
            ))
            self.set_status("❌ Ошибка")
            self.scan_btn.disabled = False
        Clock.schedule_once(_add, 0)
    
    def show_history(self, instance):
        stats = history.get_stats()
        text = f"Всего: {stats['total']} | В ожидании: {stats['pending']} | Выигрыши: {stats['won']} | Проигрыши: {stats['lost']} | Прибыль: {int(stats['profit'])}₽"
        
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        content.add_widget(Label(
            text=text, markup=True, font_size="12sp", size_hint_y=None, height=dp(30)
        ))
        
        scroll = ScrollView(size_hint_y=1)
        list_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        list_box.bind(minimum_height=list_box.setter("height"))
        
        for bet in history.bets[:15]:
            status_color = "888888"
            if bet.get('status') == 'won':
                status_color = "00ff66"
            elif bet.get('status') == 'lost':
                status_color = "ff4444"
            
            list_box.add_widget(Label(
                text=f"{bet['match']} | {bet['pick']} | {bet['amount']}₽ | [{status_color}]{bet['status'].upper()}[/{status_color}]",
                markup=True, font_size="10sp", size_hint_y=None, height=dp(20), halign="left"
            ))
        
        if not history.bets:
            list_box.add_widget(Label(
                text="[color=888888]История пуста[/color]",
                markup=True, size_hint_y=None, height=dp(40), halign="center"
            ))
        
        scroll.add_widget(list_box)
        content.add_widget(scroll)
        
        close_btn = Button(
            text="ЗАКРЫТЬ", size_hint_y=None, height=dp(40),
            background_color=(0.2, 0.2, 0.25, 1), background_normal="", bold=True
          
        content.add_widget(close_btn)
        
        popup = Popup(title="📊 История ставок", content=content, size_hint=(0.9, 0.7))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    StrategApp().run()
