import pygame, random, traceback, textwrap, glob, os, math, json
from array import array

try:
    pygame.mixer.pre_init(22050, -16, 1, 512)
except Exception:
    pass
pygame.init()
try:
    screen = pygame.display.set_mode((0, 0))
except Exception:
    screen = pygame.display.set_mode((1080, 1920))
W, H = screen.get_size()
clock = pygame.time.Clock()
V = pygame.Vector2
FD = getattr(pygame, "FINGERDOWN", -1)
FM = getattr(pygame, "FINGERMOTION", -1)
FU = getattr(pygame, "FINGERUP", -1)


# ---------- шрифт с поддержкой русского ----------
def cyr_ok(f):
    try:
        m = f.metrics("Жяд")
        return bool(m) and all(x is not None for x in m)
    except Exception:
        return False


FONT_PATH = None
cands = []
try:
    mp = pygame.font.match_font("roboto,notosans,droidsans,dejavusans,arial")
    if mp:
        cands.append(mp)
except Exception:
    pass
cands += ["/system/fonts/Roboto-Regular.ttf", "/system/fonts/NotoSans-Regular.ttf",
          "/system/fonts/DroidSans.ttf", "/system/fonts/RobotoStatic-Regular.ttf"]
try:
    cands += sorted(glob.glob("/system/fonts/*.ttf")) + sorted(glob.glob("/system/fonts/*.otf"))
except Exception:
    pass
for fp_ in cands:
    try:
        if os.path.exists(fp_) and cyr_ok(pygame.font.Font(fp_, 24)):
            FONT_PATH = fp_
            break
    except Exception:
        pass
CYR = FONT_PATH is not None
if not CYR:
    try:
        CYR = cyr_ok(pygame.font.Font(None, 24))
    except Exception:
        CYR = False
LANG = "ru" if CYR else "en"


def mkfont(size):
    return pygame.font.Font(FONT_PATH, size)


font = mkfont(max(26, H // 32))
big = mkfont(max(40, H // 18))
huge = mkfont(max(60, H // 11))
fsmall = mkfont(max(20, H // 46))

STR = {
    "title": ("ЛЕС: ВЫЖИВАНИЕ", "FOREST SURVIVAL"),
    "subtitle": ("остров, пещеры и тайны", "island, caves and secrets"),
    "play": ("ИГРАТЬ", "PLAY"),
    "continue": ("ПРОДОЛЖИТЬ", "CONTINUE"),
    "new": ("НОВАЯ ИГРА", "NEW GAME"),
    "howto": ("КАК ИГРАТЬ", "HOW TO PLAY"),
    "lang": ("Язык: Русский", "Language: English"),
    "quit": ("ВЫХОД", "QUIT"),
    "tap_back": ("Коснись экрана, чтобы вернуться", "Tap the screen to go back"),
    "help0": ("Коснись левой части экрана, и появится джойстик.",
              "Touch the left side of the screen to get a joystick."),
    "help1": ("АТАКА бьёт или стреляет, СМЕНА меняет оружие.",
              "ATK hits or shoots, SW switches weapons."),
    "help2": ("Руби деревья и неси дрова к костру, чтобы он не погас.",
              "Chop trees and bring wood to the fire so it keeps burning."),
    "help3": ("Ночью приходят аборигены, костёр их отпугивает. У их хижин можно найти припасы.",
              "Natives come at night, the fire scares them. Their huts hold supplies."),
    "help4": ("В пещерах живут мутанты и спрятано оружие.",
              "Mutants live in the caves and weapons are hidden there."),
    "help5": ("Ешь зайцев, оленей и рыбу, чтобы лечиться.",
              "Eat rabbits, deer and fish to heal."),
    "help6": ("Не плыви далеко в океан, там акулы!",
              "Do not swim far into the ocean, there are sharks!"),
    "help7": ("Найди базу в горе и реши, кого спасти.",
              "Find the base in the mountain and decide who to save."),
    "hud": ("Здоровье %d   Дерево %d   Костёр %d   Убито %d",
            "HP %d   Wood %d   Fire %d   Kills %d"),
    "island": ("Остров", "Island"), "ocean": ("Океан", "Ocean"),
    "day": ("День", "DAY"), "night": ("Ночь", "NIGHT"),
    "weapon": ("Оружие: %s", "Weapon: %s"),
    "found_w": ("Найдено: %s!", "Found: %s!"),
    "plane_med": ("В самолёте нашёл аптечку +30 HP и обычный топор!",
                  "Found a first aid kit +30 HP and a regular axe in the plane!"),
    "crater_sup": ("Припасы в воронке! +10 дерева", "Found supplies in the crater! +10 wood"),
    "fly": ("Над островом пролетает самолёт! Найди базу в горе.",
            "A plane is flying over the island! Find the base in the mountain."),
    "timmy_ok": ("Тимми с тобой! Отведи его на базу в горе.",
                 "Timmy is with you! Take him to the mountain base."),
    "boss_first": ("Сначала победи монстра!", "Defeat the monster first!"),
    "boss_dead": ("Монстр повержен! На полу лежит мёртвая девочка.", "The monster is dead! A dead girl lies on the floor."),
    "hut_wood": ("В хижине нашёл дрова: +%d", "Found wood in the hut: +%d"),
    "hut_heal": ("В хижине нашёл еду: +%d HP", "Found food in the hut: +%d HP"),
    "sharks": ("Акулы! Плыви к берегу!", "Sharks! Swim back to shore!"),
    "ate": ("Съел: %s +%d HP", "Ate %s +%d HP"),
    "with_timmy": ("Тимми с тобой", "Timmy is with you"),
    "boss_name": ("МОНСТР", "MONSTER"),
    "only_one": ("Спасти можно только ОДНОГО!", "Only ONE can be saved!"),
    "plane_over": ("Над островом самолёт.", "A plane is overhead."),
    "bring": ("Сначала приведи Тимми.", "Bring Timmy here first."),
    "save_plane": ("СПАСТИ САМОЛЁТ", "SAVE PLANE"),
    "save_timmy": ("СПАСТИ ТИММИ", "SAVE TIMMY"),
    "dead": ("Ты погиб. Коснись экрана.", "You died. Tap to restart"),
    "again": ("Коснись экрана, чтобы начать заново", "Tap to play again"),
    "timmy": ("Тимми", "Timmy"),
    "atk": ("АТАКА", "ATK"), "sw": ("СМЕНА", "SW"),
    "mo": ("МОЛОТОВ", "MOLOTOV"),
    "no_molo": ("Нет коктейлей Молотова!", "No Molotov cocktails!"),
    "found_molo": ("Найдены коктейли Молотова: +%d", "Found Molotov cocktails: +%d"),
    "hut_molo": ("В хижине нашёл коктейли Молотова: +%d", "Found Molotov cocktails in the hut: +%d"),
    "berries": ("Съел ягоды: +6 HP", "Ate berries: +6 HP"),
    "plane2": ("Вторая часть самолёта! Аптечка +20 HP и коктейли Молотова +3",
               "Second plane part! First aid +20 HP and Molotov cocktails +3"),
    "help8": ("Кусты с ягодами лечат. Коктейли Молотова нужно бросать: враги горят!",
              "Berry bushes heal. Throw Molotov cocktails to set enemies on fire!"),
    "help9": ("У лука и пистолета свои боеприпасы. Стрелы можно подобрать с убитых, патроны нет. С мини-боссов падает броня.",
              "Bow and pistol need ammo. Arrows can be picked up from kills, bullets cannot. Mini-bosses drop armor."),
    "arrows": ("Стрелы", "Arrows"), "bullets": ("Патроны", "Bullets"),
    "no_arrows": ("Нет стрел!", "No arrows!"), "no_bullets": ("Нет патронов!", "No bullets!"),
    "found_arrows": ("Найдены стрелы: +%d", "Found arrows: +%d"),
    "found_bullets": ("Найдены патроны: +%d", "Found bullets: +%d"),
    "got_arrows": ("Подобрал стрелы: +%d", "Picked up arrows: +%d"),
    "got_armor": ("Надел броню: +%d", "Armor equipped: +%d"),
    "armor_drop": ("Из мини-босса выпала броня!", "The mini-boss dropped armor!"),
    "sound_on": ("Звук: вкл", "Sound: on"), "sound_off": ("Звук: выкл", "Sound: off"),
    "loading": ("Загрузка звука...", "Loading sound..."),
    "it_climb": ("Альпинистский топор", "Climbing axe"), "it_scuba": ("Акваланг", "Scuba gear"),
    "it_rocks": ("Камни: %d", "Stones: %d"),
    "got_climb": ("Нашёл альпинистский топор! Теперь можно лезть на обрыв.",
                  "Found a climbing axe! You can climb the cliff now."),
    "got_scuba": ("Нашёл акваланг! Теперь можно нырять.", "Found scuba gear! You can dive now."),
    "need_climb": ("Обрыв слишком крутой. Нужен альпинистский топор!",
                   "The cliff is too steep. You need a climbing axe!"),
    "need_scuba": ("Здесь вода. Нужен акваланг!", "Water ahead. You need scuba gear!"),
    "need_gate": ("Ворота закрыты. Найди способ их открыть!", "The gate is closed. Find a way to open it!"),
    "got_stone": ("Подобрал камень: %d", "Picked up a stone: %d"),
    "slot": ("Камень на месте: %d из 3", "Stone placed: %d of 3"),
    "gate_open": ("Ворота открываются!", "The gate is opening!"),
    "found_med": ("Аптечка: +%d HP", "First aid kit: +%d HP"),
    "found_ammo": ("Найдены стрелы +%d и патроны +%d", "Found arrows +%d and bullets +%d"),
    "note": ("Рисунок Тимми", "Timmy's drawing"),
    "cliff": ("ОБРЫВ", "CLIFF"), "lever": ("РЫЧАГ", "LEVER"),
    "help10": ("В пещерах есть загадки: ищи рисунки Тимми, они подсказывают путь.",
               "Caves have puzzles: look for Timmy's drawings, they show the way."),
    "help11": ("Следи за голодом, жаждой и силами: ешь, пей из озёр и не беги без передышки.",
               "Watch hunger, thirst and stamina: eat, drink from lakes and do not sprint nonstop."),
    "tap": ("Нажми!", "Tap!"), "tap_close": ("Нажми, чтобы закрыть", "Tap to close"),
    "tired": ("Нет сил! Отдохни.", "Out of breath! Rest."),
    "hungry": ("Хочется есть...", "You are hungry..."),
    "thirsty": ("Хочется пить...", "You are thirsty..."),
    "drink": ("Пьёшь воду", "Drinking water"),
    "got_card": ("Нашёл ключ-карту у одного из тел!", "Found a keycard on one of the bodies!"),
    "need_card": ("Дверь заперта. Нужна ключ-карта!", "The door is locked. You need a keycard!"),
    "need_gold": ("Дверь заперта. Нужна золотая ключ-карта!", "The door is locked. You need the golden keycard!"),
    "door_open": ("Дверь открывается!", "The door opens!"),
    "it_card": ("Ключ-карта", "Keycard"), "it_gold": ("Золотая ключ-карта", "Golden keycard"),
    "it_girl": ("Несёшь девочку", "Carrying the girl"),
    "girl_pick": ("Ты берёшь мёртвую девочку. Отнеси её к алтарю.", "You pick up the dead girl. Take her to the altar."),
    "altar_reject": ("Алтарь отвергает её. Она не подходит! Из него выпала золотая ключ-карта.",
                     "The altar rejects her. She is not right! A golden keycard falls out of it."),
    "timmy_sleep": ("Тимми лежит без сознания. Алтарь требует жертву.", "Timmy lies unconscious. The altar demands a sacrifice."),
    "cold_warn": ("Холодно! Найди костёр или уйди с мороза.", "It is freezing! Find a fire or leave the cold."),
    "help12": ("В зимнем биоме смертельно холодно: долго там не стой, грейся у костров.",
               "The winter biome is deadly cold: do not stay long, warm up by the fires."),
    "settings": ("НАСТРОЙКИ", "SETTINGS"),
    "music": ("Музыка: %d", "Music: %d"), "sfx": ("Звуки: %d", "Sounds: %d"),
    "gfx": ("Графика: %s", "Graphics: %s"), "ui": ("Размер кнопок: %s", "Button size: %s"),
    "fps_on": ("Показывать FPS: да", "Show FPS: yes"), "fps_off": ("Показывать FPS: нет", "Show FPS: no"),
    "back": ("НАЗАД", "BACK"),
    "gfx_hint": ("Низкая графика ускоряет игру на слабых телефонах",
                 "Low graphics make the game faster on weak phones"),
    "set_tip": ("Громкость: нажимай левую или правую часть кнопки",
                "Volume: tap the left or right part of the button"),
}


def L(pair):
    return pair[0] if LANG == "ru" else pair[1]


def T(key):
    return L(STR[key])


# ---------- звук и музыка (создаются кодом, файлы не нужны) ----------
sound_on = True
SND_OK = False
SND = {}
TRACKS = {}
music_ch = None
cur_track = [None]
SETTINGS_FILE = "forest_settings.json"
music_vol = 7
sfx_vol = 10
gfx = 1
ui_size = 1
show_fps = False
GFX_NAMES = (("Низкая", "Low"), ("Средняя", "Medium"), ("Высокая", "High"))
UI_NAMES = (("Малый", "Small"), ("Средний", "Medium"), ("Большой", "Large"))
UI_SCALE = (0.8, 1.0, 1.25)


def save_settings():
    try:
        with open(SETTINGS_FILE, "w") as fh:
            json.dump(dict(lang=LANG, sound=sound_on, music=music_vol, sfx=sfx_vol,
                           gfx=gfx, ui=ui_size, fps=show_fps), fh)
    except Exception:
        pass


def load_settings():
    global LANG, sound_on, music_vol, sfx_vol, gfx, ui_size, show_fps
    try:
        with open(SETTINGS_FILE) as fh:
            d = json.load(fh)
        if CYR and d.get("lang") in ("ru", "en"):
            LANG = d["lang"]
        sound_on = bool(d.get("sound", True))
        music_vol = min(10, max(0, int(d.get("music", 7))))
        sfx_vol = min(10, max(0, int(d.get("sfx", 10))))
        gfx = min(2, max(0, int(d.get("gfx", 1))))
        ui_size = min(2, max(0, int(d.get("ui", 1))))
        show_fps = bool(d.get("fps", False))
    except Exception:
        pass
# ===== конец части 1, ниже вставь часть 2 =====
def build_audio():
    global SND_OK, music_ch
    try:
        info = pygame.mixer.get_init()
        if not info:
            pygame.mixer.init(22050, -16, 1, 512)
            info = pygame.mixer.get_init()
        if not info or info[1] != -16 or int(info[2]) not in (1, 2):
            return
        sr = int(info[0])
        nch = int(info[2])
    except Exception:
        return
    try:
        screen.fill((8, 14, 30))
        t0 = font.render(T("loading"), True, (230, 230, 230))
        screen.blit(t0, (W // 2 - t0.get_width() // 2, H // 2))
        pygame.display.flip()
    except Exception:
        pass
    try:
        def snd(samples, vol=0.6):
            buf = array("h")
            for x in samples:
                v = int(max(-1.0, min(1.0, x)) * 32767 * vol)
                buf.append(v)
                if nch == 2:
                    buf.append(v)
            return pygame.mixer.Sound(buffer=buf.tobytes())

        def noise(dur, decay, vol, a):
            out = []
            prev = 0.0
            for i in range(int(sr * dur)):
                prev += (random.uniform(-1, 1) - prev) * a
                out.append(prev * math.exp(-decay * i / sr) * vol)
            return out

        def tone(freq, dur, decay, vol, sweep=0.0):
            out = []
            ph = 0.0
            for i in range(int(sr * dur)):
                t = i / sr
                ph += 2 * math.pi * (freq + sweep * t) / sr
                out.append(math.sin(ph) * math.exp(-decay * t) * vol)
            return out

        def mix(*lists):
            n = max(len(q) for q in lists)
            return [sum(q[i] for q in lists if i < len(q)) for i in range(n)]

        SND["gun"] = snd(mix(noise(0.22, 18, 0.9, 0.6), tone(140, 0.22, 20, 0.7, -300)))
        SND["arrow"] = snd(mix(tone(420, 0.16, 22, 0.6, -1500), noise(0.1, 30, 0.3, 0.3)))
        SND["swing"] = snd(noise(0.16, 9, 0.5, 0.25))
        SND["hit"] = snd(mix(tone(160, 0.12, 28, 0.9, -400), noise(0.1, 30, 0.5, 0.4)))
        SND["throw"] = snd(noise(0.25, 6, 0.45, 0.12))
        SND["boom"] = snd(mix(noise(0.7, 5, 0.9, 0.2), tone(70, 0.7, 6, 0.8, -30)))
        SND["pickup"] = snd(tone(660, 0.07, 10, 0.6) + tone(880, 0.1, 12, 0.6))
        SND["chest"] = snd(tone(523, 0.1, 8, 0.6) + tone(659, 0.1, 8, 0.6) + tone(784, 0.22, 7, 0.6))
        SND["armor"] = snd(mix(tone(900, 0.2, 15, 0.5), tone(1350, 0.2, 15, 0.4), noise(0.08, 40, 0.3, 0.6)))
        SND["hurt"] = snd(mix(tone(110, 0.2, 12, 0.8, -150), noise(0.2, 15, 0.4, 0.3)))
        SND["die"] = snd(tone(300, 0.7, 3, 0.7, -400))
        SND["click"] = snd(tone(1000, 0.04, 60, 0.5))

        def make_track(kind):
            msr = sr // 2
            n = msr * 8
            out = [0.0] * n

            def note(freq, start, dur, vol, harm=0.25):
                s0 = int(start * msr)
                cnt = int(dur * msr)
                w0 = 2 * math.pi * freq / msr
                for i in range(cnt):
                    j = s0 + i
                    if j >= n:
                        break
                    env = math.sin(math.pi * i / cnt) ** 1.5
                    out[j] += (math.sin(w0 * i) + harm * math.sin(2 * w0 * i)) * env * vol

            def ping(start, freq, vol):
                s0 = int(start * msr)
                w0 = 2 * math.pi * freq / msr
                for i in range(int(0.45 * msr)):
                    j = s0 + i
                    if j >= n:
                        break
                    out[j] += math.sin(w0 * i) * math.exp(-9.0 * i / msr) * vol

            if kind == "calm":
                chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63),
                          (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]
                for k, chd in enumerate(chords):
                    for fr in chd:
                        note(fr, 2.0 * k, 2.0, 0.16)
                note(659.25, 0.4, 1.4, 0.06, 0)
                note(523.25, 2.6, 1.4, 0.06, 0)
                note(587.33, 4.4, 1.4, 0.06, 0)
                note(440.0, 6.2, 1.6, 0.06, 0)
            elif kind == "night":
                note(73.42, 0, 8, 0.28, 0.4)
                note(110.0, 0, 8, 0.18, 0.3)
                note(155.56, 2.0, 4.0, 0.07, 0.2)
            else:
                note(82.41, 0, 8, 0.30, 0.5)
                note(116.54, 0, 8, 0.14, 0.3)
                ping(1.1, 1500, 0.10)
                ping(3.3, 1180, 0.09)
                ping(5.0, 1700, 0.08)
                ping(6.6, 1320, 0.10)
            res = []
            for i in range(n - 1):
                res.append(out[i])
                res.append((out[i] + out[i + 1]) * 0.5)
            res.append(out[n - 1])
            res.append(out[n - 1])
            return res

        for nm in ("calm", "night", "cave"):
            TRACKS[nm] = snd(make_track(nm), 0.55)
        pygame.mixer.set_reserved(1)
        music_ch = pygame.mixer.Channel(0)
        SND_OK = True
    except Exception:
        SND.clear()
        TRACKS.clear()
        SND_OK = False


build_audio()
load_settings()


def apply_volumes():
    if not SND_OK:
        return
    try:
        for sd in SND.values():
            sd.set_volume(sfx_vol / 10.0)
        if music_ch is not None:
            music_ch.set_volume(0.5 * music_vol / 10.0)
    except Exception:
        pass


apply_volumes()


def play(name):
    if SND_OK and sound_on:
        sd = SND.get(name)
        if sd is not None:
            try:
                sd.play()
            except Exception:
                pass


def want_track():
    if state != "game":
        return "calm"
    m = g["mode"]
    if m == -1:
        return "night" if ((g["day"] % 60) > 30 and on_land(g["p"])) else "calm"
    if m == 6:
        return "calm"
    return "cave"


def update_music():
    if not SND_OK or music_ch is None:
        return
    try:
        if not sound_on:
            if cur_track[0] is not None:
                music_ch.stop()
                cur_track[0] = None
            return
        wt = want_track()
        if wt != cur_track[0]:
            cur_track[0] = wt
            music_ch.play(TRACKS[wt], loops=-1, fade_ms=1200)
            music_ch.set_volume(0.5 * music_vol / 10.0)
    except Exception:
        pass


WORLD = 3000
BEACH = 150
OCEAN = 1000
CW, CH = 1400, 1000
SNOW_Y = 900
SPAWN = V(1500, 2000)
FIRE = SPAWN + V(90, 0)
PLANE = SPAWN + V(-230, -140)
PLANE2 = V(700, 650)
CRATER = V(2300, 1700)
CRATER_CAVE = V(2150, 1860)
MOUNTAIN = V(2600, 420)
MOUNTAINS = [(MOUNTAIN, 1.0), (V(2120, 360), 0.7), (V(2330, 650), 0.5)]
BASE_DOOR = MOUNTAIN + V(0, 150)
CAVES = [V(1950, 2150), V(1200, 450), V(2650, 2650)]
CAVE_W = ["axe", "bow", "pistol"]
LAKES = [(V(900, 1600), 150), (V(2300, 1250), 180), (V(1500, 1200), 120),
         (V(600, 2300), 130), (V(2700, 2000), 110), (V(2000, 650), 140)]
VILLAGES = [V(700, 1950), V(2200, 2500), V(1800, 1500), V(1500, 600)]
CHEST = V(CW / 2, 130)
MOLO_CHEST = {0: V(200, 210), 1: V(1200, 230), 2: V(210, 800)}
AMMO_CHEST = {1: V(200, 260), 2: V(1200, 780)}
TIMMY_POS = V(600, 120)
ALTAR = V(1840, 900)
COT = V(1840, 1100)
CONSOLE = V(800, 150)
RADAR = V(1300, 260)
MEDBAY = (80, 700, 420, 300)

SIZES = {0: (1400, 2000), 1: (1400, 2600), 2: (1400, 2000), 3: (900, 1900),
         4: (1400, 1000), 5: (2000, 1500), 6: (1600, 1100), 7: (1400, 2800)}
PORTALS = {
    0: [(V(700, 1930), -1, None, "exit")],
    1: [(V(700, 2530), -1, None, "exit")],
    2: [(V(700, 1930), -1, None, "exit")],
    3: [(V(450, 1870), -1, None, "exit"), (V(450, 55), 4, V(700, 800), "fwd")],
    4: [(V(700, 970), -1, None, "climb"), (V(700, 85), 5, V(800, 1300), "lab")],
    5: [(V(800, 1370), 4, V(700, 190), "back"), (V(210, 1060), 7, V(700, 2680), "fwd")],
    6: [(V(800, 1070), 7, V(700, 300), "back")],
    7: [(V(700, 2760), 5, V(290, 1060), "back"), (V(700, 220), 6, V(800, 950), "fwd")],
}
PLABEL = dict(exit=("ВЫХОД", "EXIT"), fwd=("ВПЕРЁД", "FORWARD"),
              climb=("ВЫЛЕЗТИ", "CLIMB OUT"), lab=("ЛАБОРАТОРИЯ", "LAB"),
              back=("НАЗАД", "BACK"))
ENTRY_SPAWN = {0: V(700, 1820), 1: V(700, 2420), 2: V(700, 1820),
               3: V(450, 1750), 6: V(800, 950)}
ENT = [(CAVES[0], 0), (CAVES[1], 1), (CAVES[2], 2), (CRATER_CAVE, 3)]
# геометрия пещер-головоломок: прямоугольники (x, y, ширина, высота)
CAVE_GEO = {
    # пещера 1: обрыв (нужен альпинистский топор), слева топор, справа припасы
    0: dict(floor=[(250, 1350, 900, 620), (600, 1000, 200, 350), (200, 700, 1000, 180),
                   (200, 300, 200, 400), (1000, 300, 200, 400), (100, 60, 500, 240), (800, 60, 500, 240)],
            cliff=[(600, 880, 200, 120)], water=[], gate=[]),
    # пещера 2: ворота с рычагом, длинный туннель к луку, слева припасы
    1: dict(floor=[(250, 1950, 900, 620), (600, 1600, 200, 350), (200, 1300, 1000, 300),
                   (200, 900, 200, 400), (100, 660, 500, 240), (1000, 1000, 200, 300),
                   (1000, 700, 200, 260), (700, 700, 500, 180), (700, 480, 200, 400),
                   (700, 480, 500, 160), (1000, 250, 200, 230), (700, 40, 600, 210)],
            cliff=[], water=[], gate=[(1000, 960, 200, 40)]),
    # пещера 3: два подводных пути (нужен акваланг), справа пистолет, слева припасы
    2: dict(floor=[(250, 1350, 900, 620), (100, 300, 550, 430), (750, 300, 550, 430)],
            cliff=[], water=[(300, 700, 200, 650), (900, 700, 200, 650)], gate=[]),
    # лаборатория: зал, комната босса, комната с алтарём и две двери
    5: dict(floor=[(500, 700, 1100, 700), (350, 1000, 150, 120), (180, 980, 130, 160),
                   (1600, 1000, 100, 100), (1700, 780, 280, 560), (900, 600, 200, 100),
                   (400, 60, 1200, 500)],
            cliff=[], water=[], gate=[],
            doors=[((900, 560, 200, 40), "boss", "card"), ((310, 1000, 40, 120), "gold1", "gold")]),
    # подземный ход к управлению: обрыв, вода, ворота с камнями и золотая дверь
    7: dict(floor=[(500, 2200, 400, 600), (500, 1500, 400, 500), (300, 700, 800, 550),
                   (600, 400, 200, 260), (550, 150, 300, 210)],
            cliff=[(600, 2000, 200, 200)], water=[(600, 1250, 200, 250)], gate=[(600, 660, 200, 40)],
            doors=[((600, 360, 200, 40), "gold2", "gold")]),
}
ROCKCOL = {5: ((34, 38, 46), (120, 132, 148)), 7: ((20, 18, 28), (95, 90, 110))}
DIM = ("Ты попал в другое измерение...", "You entered another dimension...")
ENT_MSG = {0: DIM, 1: DIM, 2: DIM,
           3: ("Длинная тёмная тропа ведёт к воронке...", "A long dark path leads to the crater..."),
           6: ("База в горе. Пункт управления наверху.", "The mountain base. The control room is at the top.")}
PORTAL_MSG = {4: ("Дно воронки. Впереди светится металлическая дверь.",
                  "The bottom of the crater. A metal door glows ahead."),
              5: ("Лаборатория. Всюду тела, кровь и следы взрывов. Ищи ключ-карту.",
                  "The laboratory. Bodies, blood and blast marks everywhere. Find a keycard."),
              6: ("Пункт управления в горе. Здесь решается судьба острова.",
                  "The control room in the mountain. The island's fate is decided here."),
              7: ("Подземный ход к горе. Придётся лезть, нырять и открывать ворота.",
                  "The passage to the mountain. You will have to climb, dive and open a gate.")}
FLOOR = {0: (75, 62, 90), 1: (75, 62, 90), 2: (75, 62, 90), 3: (82, 70, 68),
         4: (95, 70, 45), 5: (205, 210, 222), 6: (50, 60, 75), 7: (80, 84, 98)}
PLACE = {0: ("Пещера 1", "Cave 1"), 1: ("Пещера 2", "Cave 2"), 2: ("Пещера 3", "Cave 3"),
         3: ("Тропа к воронке", "Crater Path"), 4: ("Дно воронки", "Crater Bottom"),
         5: ("Лаборатория", "Laboratory"), 6: ("Пункт управления", "Control Room"),
         7: ("Подземный ход", "Underground Passage")}
ZONES = {"med": ("МЕДПУНКТ", "MEDBAY"), "ctl": ("УПРАВЛЕНИЕ", "CONTROL"),
         "rad": ("РАДАР", "RADAR"), "sto": ("СКЛАД", "STORAGE")}
DARK_MODES = (0, 1, 2, 3, 7)
ENDINGS = {
    "plane": (("ТЫ СПАС ПАССАЖИРОВ", "YOU SAVED THE PASSENGERS"),
              ("Ты направил аварийную энергию базы на маяк. Самолёт нашёл полосу и "
               "благополучно сел, все на борту остались живы. Тимми не успели вылечить. "
               "Многие спасены, но ты всегда будешь думать о том, кого не смог спасти.",
               "You sent the base's emergency power to the beacon. The plane found "
               "the runway and landed safely, and everyone on board lived. Timmy "
               "could not be treated in time. Many were saved, but you will always "
               "wonder about the one you could not.")),
    "timmy": (("ТЫ СПАС ТИММИ", "YOU SAVED TIMMY"),
              ("Ты направил всю энергию в алтарь лаборатории. Тимми открыл глаза и "
               "улыбнулся. Над головой огни самолёта растворились в облаках. "
               "Одна жизнь спасена, многие потеряны.",
               "You sent all the power to the laboratory altar. Timmy opened his eyes "
               "and smiled. Overhead, the lights of the plane faded into the clouds. "
               "One life was saved, and many others were lost.")),
}
# ===== конец части 2, ниже вставь часть 3 =====
WEAPONS = {
    "fists": dict(name=("Кулаки", "Fists"), dmg=6, rng=45, cd=0.5, ranged=False, speed=0),
    "oldaxe": dict(name=("Обычный топор", "Axe"), dmg=26, rng=62, cd=0.6, ranged=False, speed=0),
    "axe": dict(name=("Современный топор", "Modern Axe"), dmg=42, rng=78, cd=0.5, ranged=False, speed=0),
    "bow": dict(name=("Современный лук", "Modern Bow"), dmg=30, rng=0, cd=0.9, ranged=True, speed=520,
                ammo="arrows"),
    "pistol": dict(name=("Пистолет", "Pistol"), dmg=22, rng=0, cd=0.35, ranged=True, speed=750,
                   ammo="bullets"),
}
FOOD = dict(rabbit=8, deer=20, fish=5)
HUNGER = dict(rabbit=18, deer=40, fish=12)
ANIMAL_HP = dict(rabbit=10, deer=30, fish=5)
ANAME = dict(rabbit=("заяц", "rabbit"), deer=("олень", "deer"), fish=("рыба", "fish"))

# ---------- кнопки и джойстик ----------
def apply_layout():
    global S, JR, PAD, BTN, PC, PR
    S = int(min(W, H) // 8 * UI_SCALE[ui_size])
    JR = int(S * 1.3)
    PAD = V(2.2 * S, H - 2.2 * S)
    BTN = {
        "atk": (V(W - 1.8 * S, H - 2 * S), 1.0 * S),
        "sw": (V(W - 1.8 * S, H - 4.2 * S), 0.7 * S),
        "mo": (V(W - 4.0 * S, H - 1.4 * S), 0.8 * S),
    }
    PC = (W - int(S * 0.7), int(S * 0.7))
    PR = int(S * 0.42)


apply_layout()
BW_, BH_ = int(W * 0.42), int(H * 0.12)
RECT_PLANE = (int(W * 0.05), int(H * 0.30), BW_, BH_)
RECT_TIMMY = (int(W * 0.53), int(H * 0.30), BW_, BH_)

night = pygame.Surface((W, H))
night.fill((0, 0, 30))
try:
    night = night.convert()
except Exception:
    pass


def make_light(r):
    sf = pygame.Surface((2 * r, 2 * r))
    sf.fill((0, 0, 0))
    for i in range(10):
        rr = int(r * (1 - i / 10.0))
        v = int(115 * (i + 1) / 10.0)
        pygame.draw.circle(sf, (v, int(v * 0.75), int(v * 0.35)), (r, r), rr)
    try:
        sf = sf.convert()
    except Exception:
        pass
    return sf


LIGHTS = [make_light(124), make_light(132)]


def text_c(fnt, s, col, cx, cy):
    t = fnt.render(s, True, col)
    screen.blit(t, (int(cx - t.get_width() // 2), int(cy - t.get_height() // 2)))


def inrect(pos, r):
    return r[0] <= pos[0] <= r[0] + r[2] and r[1] <= pos[1] <= r[1] + r[3]


def show_error():
    err = traceback.format_exc()
    print(err)
    small = pygame.font.Font(None, max(22, H // 45))
    lines = []
    for ln in err.strip().split("\n")[-8:]:
        lines += textwrap.wrap(ln, 45) or [" "]
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
        screen.fill((0, 0, 0))
        for i, ln in enumerate(lines):
            screen.blit(small.render(ln, True, (255, 90, 90)),
                        (10, 10 + i * (small.get_height() + 4)))
        pygame.display.flip()
        clock.tick(10)


def on_land(q):
    return 0 <= q.x <= WORLD and 0 <= q.y <= WORLD


def in_lake(q, pad=0):
    return any(q.distance_to(c) < r + pad for c, r in LAKES)


def rand_land(m):
    return V(random.randint(BEACH + m, WORLD - BEACH - m),
             random.randint(BEACH + m, WORLD - BEACH - m))


def rand_tree():
    while True:
        q = rand_land(60)
        if in_lake(q, 25):
            continue
        if any(q.distance_to(c) < 110 for c in
               CAVES + [SPAWN, FIRE, PLANE, PLANE2, CRATER, CRATER_CAVE, BASE_DOOR]):
            continue
        if any(q.distance_to(c) < 170 for c in VILLAGES):
            continue
        if any(q.distance_to(mc_) < 300 * mk_ for mc_, mk_ in MOUNTAINS):
            continue
        return q


SPOTS = CAVES + [SPAWN, FIRE, PLANE, PLANE2, CRATER, CRATER_CAVE, BASE_DOOR] + VILLAGES


def free_spot(m, pad):
    for _ in range(200):
        q = rand_land(m)
        if in_lake(q, 20) or any(q.distance_to(mc_) < 300 * mk_ for mc_, mk_ in MOUNTAINS):
            continue
        if any(q.distance_to(c) < pad for c in SPOTS):
            continue
        return q
    return rand_land(m)


def toward(a, b, speed):
    d = b - a
    if d.length() < 1:
        return V(0, 0)
    return d.normalize() * speed


def mk(pos, kind, lvl=0):
    hp = 40 if kind == "native" else 60 + 15 * lvl
    return dict(p=V(pos), hp=hp, max=hp, kind=kind, home=None, burn=0.0)


def mkmini(pos, lvl=0):
    hp = 140 + 30 * lvl
    return dict(p=V(pos), hp=hp, max=hp, kind="miniboss", home=None, burn=0.0)


def new_animal(kind, lake=None):
    if kind == "fish":
        c, r = LAKES[lake]
        pos = c + V(random.uniform(0, r * 0.7), 0).rotate(random.randint(0, 359))
    else:
        while True:
            pos = rand_land(40)
            if not in_lake(pos, 20):
                break
    hp = ANIMAL_HP[kind]
    return dict(p=pos, hp=hp, max=hp, kind=kind, lake=lake,
                dir=V(0, 0), t=random.uniform(0, 2))


def make_lab_decor():
    hall = (560, 760, 980, 580)
    boss = (470, 110, 1060, 400)
    altar = (1740, 830, 200, 450)
    avoid = [ALTAR, COT, V(800, 1330), V(1000, 640), V(230, 1060)]

    def pick(rect):
        for _ in range(80):
            q = V(random.randint(rect[0], rect[0] + rect[2]), random.randint(rect[1], rect[1] + rect[3]))
            if all(q.distance_to(a) > 110 for a in avoid):
                return q
        return V(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)

    corpses = []
    for rect, n in ((hall, 8), (boss, 3), (altar, 1)):
        for _ in range(n):
            corpses.append(dict(p=pick(rect), ang=random.randint(0, 359),
                                kind=random.choice(("coat", "coat", "soldier")),
                                trail=random.choice((None, random.randint(0, 359)))))
    blood = [(int(c["p"].x), int(c["p"].y), random.randint(18, 30)) for c in corpses]
    for rect, n in ((hall, 7), (boss, 4), (altar, 2)):
        for _ in range(n):
            q = pick(rect)
            blood.append((int(q.x), int(q.y), random.randint(10, 24)))
    scorch = []
    for rect, n in ((hall, 5), (boss, 4)):
        for _ in range(n):
            q = pick(rect)
            scorch.append((int(q.x), int(q.y), random.randint(30, 55)))
    glass = []
    for rect, n in ((hall, 12), (boss, 6)):
        for _ in range(n):
            q = pick(rect)
            glass.append((int(q.x), int(q.y), random.randint(0, 359)))
    pebbles = []
    for rect, n in ((hall, 6), (boss, 4)):
        for _ in range(n):
            q = pick(rect)
            pebbles.append((int(q.x), int(q.y), random.randint(4, 8)))
    ci = random.randrange(8)
    card = dict(p=corpses[ci]["p"] + V(24, 12), got=False)
    return dict(corpses=corpses, blood=blood, scorch=scorch, glass=glass, pebbles=pebbles, card=card)


def new_game():
    caves = []

    def ch(x, y, kind, n=0, m=0):
        return dict(p=V(x, y), kind=kind, got=False, n=n, m=m)

    def band(n, x0, x1, y0, y1, lvl):
        return [mk(V(random.randint(x0, x1), random.randint(y0, y1)), "mutant", lvl) for _ in range(n)]

    # пещера 1: обрыв и альпинистский топор
    ms = band(5, 380, 1020, 1480, 1760, 0) + [mkmini(V(700, 1600), 0)]
    ms += band(2, 500, 900, 740, 840, 0)
    ms += band(1, 220, 380, 380, 640, 0)
    ms += band(1, 1020, 1180, 380, 640, 0)
    ms += [mkmini(V(350, 235), 0)] + band(random.randint(1, 2), 160, 540, 120, 200, 0)
    caves.append(dict(en=ms,
                      chests=[ch(350, 130, "axe"), ch(880, 130, "med", 40),
                              ch(1050, 130, "molo", random.randint(3, 5)),
                              ch(1200, 130, "ammo", 5, 8), ch(1000, 230, "med", 40)],
                      items=[dict(p=V(400, 1500), kind="climb", got=False)],
                      notes=[dict(p=V(470, 1560), kind="climb")],
                      torches=[V(290, 160), V(410, 160)]))
    # пещера 2: ворота, рычаг, камни и длинный туннель к луку
    ms = band(7, 380, 1020, 2080, 2360, 1) + [mkmini(V(700, 2200), 1)]
    ms += band(2, 300, 1100, 1380, 1520, 1)
    ms += band(1, 240, 360, 960, 1240, 1)
    ms += [mk(V(1100, 1230), "mutant", 1)]
    ms += [mk(V(1100, 820), "mutant", 1), mk(V(800, 780), "mutant", 1),
           mk(V(800, 560), "mutant", 1), mk(V(1100, 560), "mutant", 1)]
    ms += [mkmini(V(1000, 190), 1)] + band(random.randint(1, 2), 760, 1240, 70, 140, 1)
    caves.append(dict(en=ms,
                      chests=[ch(1000, 110, "bow"), ch(180, 720, "med", 40),
                              ch(330, 720, "molo", random.randint(3, 5)),
                              ch(480, 720, "arrows", random.randint(10, 14)), ch(330, 840, "med", 40)],
                      items=[], notes=[dict(p=V(1040, 1120), kind="lever")],
                      stones=[V(1040, 1200), V(1160, 1190), V(1060, 1260), V(1150, 1270)],
                      lever=V(1100, 1070), slots=0, gate=False,
                      torches=[V(940, 135), V(1060, 135)]))
    # пещера 3: подводные пути и акваланг
    ms = band(9, 380, 1020, 1480, 1760, 2) + [mkmini(V(700, 1620), 2)]
    ms += [mkmini(V(1000, 520), 2)] + band(random.randint(1, 2), 800, 1250, 600, 700, 2)
    caves.append(dict(en=ms,
                      chests=[ch(1000, 360, "pistol"), ch(180, 360, "med", 40),
                              ch(330, 360, "molo", random.randint(3, 5)),
                              ch(480, 360, "bullets", random.randint(18, 26)), ch(330, 480, "med", 40)],
                      items=[dict(p=V(480, 1420), kind="scuba", got=False)],
                      notes=[dict(p=V(700, 1400), kind="scuba")],
                      torches=[V(940, 385), V(1060, 385)]))
    tun = [mk(V(random.randint(280, 620), 250 + 130 * i), "mutant", 1) for i in range(10)]
    caves.append(dict(en=tun, chests=[]))
    cb = [mk(V(random.randint(450, 950), random.randint(300, 650)), "mutant", 1)
          for _ in range(5)]
    cb.append(mkmini(V(CW / 2, CH / 2 - 40), 3))
    caves.append(dict(en=cb, chests=[]))
    boss = dict(p=V(1000, 250), hp=650, max=650, kind="boss", ch=0.0, cd=3.0,
                dir=V(0, 1), m1=False, m2=False, burn=0.0, slam=0.0, stun=0.0, flash=0.0, nxt=0)
    decor = make_lab_decor()
    caves.append(dict(en=[boss], chests=[], doors=dict(boss=False, gold1=False),
                      decor=decor, card=decor["card"], girl=None))
    caves.append(dict(en=[], chests=[]))
    caves.append(dict(en=[mk(V(700, 1800), "mutant", 3), mk(V(620, 900), "mutant", 3), mk(V(820, 1000), "mutant", 3)],
                      chests=[], doors=dict(gold2=False), items=[], notes=[],
                      stones=[V(420, 1100), V(980, 1040)], lever=V(700, 770), slots=0, gate=False))
    an = [new_animal("rabbit") for _ in range(8)] + [new_animal("deer") for _ in range(4)]
    for i, (lc, lr) in enumerate(LAKES):
        an += [new_animal("fish", i) for _ in range(max(1, int((lr - 60) / 30)))]
    vil = []
    huts = []
    for vc in VILLAGES:
        for k in range(4):
            huts.append(dict(p=vc + V(95, 0).rotate(90 * k + 45), looted=False, molo=0))
        for k in range(3):
            n = mk(vc + V(40, 0).rotate(120 * k), "native")
            n["home"] = V(vc)
            vil.append(n)
    huts[random.randrange(len(huts))]["molo"] = random.randint(2, 5)
    bushes = [dict(p=free_spot(60, 110), ok=True, t=0.0) for _ in range(14)]
    stones = [free_spot(-60, 70) for _ in range(30)]
    return dict(mode=-1, p=V(SPAWN), back=V(SPAWN),
                trees=[rand_tree() for _ in range(220)],
                en=[], vil=vil, huts=huts, an=an, proj=[], sharks=[], swim=0.0,
                shark_warn=False, caves=caves, hp=100.0, wood=0, fire=100.0,
                t=0.0, face=V(0, 1), owned=["fists"], cur="fists",
                cd=0.0, swing=0.0, plane=False, plane2=False, crater=False,
                msg="", msg_t=0.0, kills=0, molo=0, flames=[], armor=0.0, arrows=0, bullets=0,
                drops=[], hurt_cd=0.0, dead_snd=False,
                climb=False, scuba=False, rocks=0, blk=0.0,
                card=False, gold=False, carry=False, cold=0.0, warn_c=False, eproj=[],
                hunger=100.0, thirst=100.0, stam=100.0, tired=False, day=0.0, note_open=None,
                warn_h=False, warn_t=False, drinking=False,
                bushes=bushes, stones=stones,
                boss_dead=False, timmy=False, ending=None, end_t=0.0,
                fly_said=False)
g = new_game()
state = "menu"
started = False


def say(text):
    g["msg"] = text
    g["msg_t"] = 3.5


def hurt(x):
    if x <= 0:
        return
    if g["armor"] > 0:
        take = min(g["armor"], x)
        g["armor"] -= take
        x -= take
    g["hp"] -= x
    if g["hurt_cd"] <= 0:
        g["hurt_cd"] = 0.45
        play("hurt")


def cur_en():
    if g["mode"] == -1:
        return g["en"] + g["vil"]
    return g["caves"][g["mode"]]["en"]


def targets():
    if g["mode"] == -1:
        return g["en"] + g["vil"] + g["an"]
    return g["caves"][g["mode"]]["en"]


def ui_hit(pos):
    q = V(pos)
    for name, (c, r) in BTN.items():
        if q.distance_to(c) < r:
            return name
    return None


def in_rects(q, rects):
    for r in rects:
        if r[0] <= q.x <= r[0] + r[2] and r[1] <= q.y <= r[1] + r[3]:
            return True
    return False


def zone_at(q):
    geo = CAVE_GEO[g["mode"]]
    if in_rects(q, geo["floor"]):
        return "floor"
    if in_rects(q, geo["cliff"]):
        return "cliff"
    if in_rects(q, geo["water"]):
        return "water"
    if in_rects(q, geo["gate"]):
        return "gate"
    for r, nm, need in geo.get("doors", []):
        if in_rects(q, [r]):
            return "door"
    return "rock"


def walk_ok(q):
    z = zone_at(q)
    if z == "floor":
        return True, None
    if z == "cliff":
        return (True, None) if g["climb"] else (False, "climb")
    if z == "water":
        return (True, None) if g["scuba"] else (False, "scuba")
    if z == "gate":
        return (True, None) if g["caves"][g["mode"]].get("gate") else (False, "gate")
    if z == "door":
        cvd = g["caves"][g["mode"]]
        for r, nm, need in CAVE_GEO[g["mode"]]["doors"]:
            if in_rects(q, [r]):
                return (True, None) if cvd["doors"].get(nm) else (False, "card" if need == "card" else "gold")
    return False, None


def step_player(old, delta):
    new = old + delta
    ok, why = walk_ok(new)
    if ok:
        return new
    nx = V(new.x, old.y)
    ny = V(old.x, new.y)
    if walk_ok(nx)[0]:
        res = nx
    elif walk_ok(ny)[0]:
        res = ny
    else:
        res = old
    if why and g["blk"] <= 0 and delta.length() > 0:
        g["blk"] = 2.5
        say(T("need_" + why))
    return res


def enemy_ok(q):
    m = g["mode"]
    if m not in CAVE_GEO:
        return True
    geo = CAVE_GEO[m]
    if in_rects(q, geo["floor"]):
        return True
    return bool(g["caves"][m].get("gate")) and in_rects(q, geo["gate"])
# ===== конец части 3, ниже вставь часть 4 =====
def emove(pos, delta):
    new = pos + delta
    if enemy_ok(new):
        return new
    nx = V(new.x, pos.y)
    ny = V(pos.x, new.y)
    if enemy_ok(nx):
        return nx
    if enemy_ok(ny):
        return ny
    return pos


def update_en(lst, p, dt, aggro, fire_on):
    land_ok = on_land(p)
    for en in lst:
        ep = en["p"]
        d = ep.distance_to(p)
        mut = en["kind"] in ("mutant", "miniboss")
        if mut and d > aggro:
            continue
        if not mut and g["mode"] == -1 and not land_ok:
            continue
        home = en.get("home")
        if home is not None and d > 320:
            en["wt"] = en.get("wt", 0.0) - dt
            if en["wt"] <= 0:
                en["wt"] = random.uniform(1, 3)
                en["wd"] = V(1, 0).rotate(random.randint(0, 359)) if random.random() < 0.6 else V(0, 0)
            if ep.distance_to(home) > 130:
                en["p"] = ep + toward(ep, home, 50) * dt
            else:
                en["p"] = ep + en.get("wd", V(0, 0)) * 30 * dt
            continue
        spd = {"mutant": 95, "miniboss": 80}.get(en["kind"], 90)
        if fire_on and g["fire"] > 0 and ep.distance_to(FIRE) < 150:
            en["p"] = emove(ep, -toward(ep, FIRE, spd) * dt)
        else:
            en["p"] = emove(ep, toward(ep, p, spd) * dt)
        reach = 42 if en["kind"] == "miniboss" else 26
        if d < reach:
            hurt({"mutant": 35, "miniboss": 45}.get(en["kind"], 25) * dt)


def spawn_minions(lst, b):
    for _ in range(3):
        q = b["p"] + V(90, 0).rotate(random.randint(0, 359))
        q.x = min(max(q.x, 440), 1560)
        q.y = min(max(q.y, 100), 520)
        lst.append(mk(q, "mutant", 1))


def update_boss(b, p, dt, lst):
    ph2 = b["hp"] < b["max"] * 0.5
    bp = V(b["p"])
    if b["flash"] > 0:
        b["flash"] -= dt
    if b["stun"] > 0:
        b["stun"] -= dt
    elif b["slam"] > 0:
        b["slam"] -= dt
        if b["slam"] <= 0:
            if p.distance_to(bp) < 190:
                hurt(40)
            b["stun"] = 0.7
            b["flash"] = 0.3
            play("boom")
    elif b["ch"] > 0:
        b["ch"] -= dt
        bp = emove(bp, b["dir"] * 380 * dt)
    else:
        b["cd"] -= dt
        bp = emove(bp, toward(bp, p, 105 if ph2 else 90) * dt)
        if b["cd"] <= 0:
            b["cd"] = 3.0 if ph2 else 4.2
            k = b["nxt"]
            b["nxt"] = (k + 1) % 3
            d = p - bp
            if k == 0:
                b["ch"] = 0.7
                b["dir"] = d.normalize() if d.length() > 0 else V(0, 1)
            elif k == 1:
                b["slam"] = 1.0
            else:
                n = 14 if ph2 else 10
                base = random.randint(0, 359)
                for i in range(n):
                    dv = V(1, 0).rotate(base + 360.0 * i / n)
                    g["eproj"].append(dict(p=V(bp), v=dv * 250, life=1.9, dmg=14))
                play("throw")
    b["p"] = bp
    if bp.distance_to(p) < 56:
        hurt((55 if b["ch"] > 0 else 35) * dt)
    frac = b["hp"] / b["max"]
    if frac < 0.66 and not b["m1"]:
        b["m1"] = True
        spawn_minions(lst, b)
    if frac < 0.33 and not b["m2"]:
        b["m2"] = True
        spawn_minions(lst, b)


def update_animals(dt, p):
    lo = BEACH + 30
    hi = WORLD - BEACH - 30
    for a in g["an"]:
        k = a["kind"]
        a["t"] -= dt
        if a["t"] <= 0:
            a["t"] = random.uniform(1, 3)
            if random.random() < (0.4 if k == "fish" else 0.7):
                a["dir"] = V(1, 0).rotate(random.randint(0, 359))
            else:
                a["dir"] = V(0, 0)
        if k == "fish":
            c, r = LAKES[a["lake"]]
            d = a["p"] - c
            if d.length() > r * 0.8:
                a["dir"] = -d.normalize()
            a["p"] = a["p"] + a["dir"] * 12 * dt
        else:
            dist = a["p"].distance_to(p)
            fr = 220 if k == "rabbit" else 260
            if 0 < dist < fr:
                step = (a["p"] - p).normalize() * (190 if k == "rabbit" else 150) * dt
            else:
                step = a["dir"] * 40 * dt
            np_ = a["p"] + step
            np_.x = min(max(np_.x, lo), hi)
            np_.y = min(max(np_.y, lo), hi)
            if not in_lake(np_, 10):
                a["p"] = np_


def update_sharks(dt, p):
    if on_land(p):
        g["swim"] = 0.0
        g["sharks"] = []
        g["shark_warn"] = False
        return
    g["swim"] += dt
    if g["swim"] > 4 and not g["shark_warn"]:
        g["shark_warn"] = True
        say(T("sharks"))
    if g["swim"] > 5.5 and len(g["sharks"]) < 3 and random.random() < 0.05:
        q = p + V(380, 0).rotate(random.randint(0, 359))
        if not on_land(q):
            g["sharks"].append(dict(p=q))
    for s in g["sharks"]:
        s["p"] = s["p"] + toward(s["p"], p, 160) * dt
        if s["p"].distance_to(p) < 34:
            hurt(40 * dt)


def reap():
    areas = [(-1, g["en"]), (-1, g["vil"])] + [(i, c["en"]) for i, c in enumerate(g["caves"])]
    for area, lst in areas:
        dead = [e for e in lst if e["hp"] <= 0]
        if dead:
            lst[:] = [e for e in lst if e["hp"] > 0]
            g["kills"] += len(dead)
            for e in dead:
                if e.get("stuck", 0) > 0:
                    g["drops"].append(dict(p=V(e["p"]), kind="arrows", n=e["stuck"], mode=area))
                if e["kind"] == "miniboss":
                    g["drops"].append(dict(p=V(e["p"]), kind="armor", n=35, mode=area))
                    say(T("armor_drop"))
                if e["kind"] == "boss":
                    g["boss_dead"] = True
                    g["caves"][5]["girl"] = dict(p=V(e["p"]), state="lying")
                    say(T("boss_dead"))
                    play("boom")
    for a in g["an"][:]:
        if a["hp"] <= 0:
            g["an"].remove(a)
            if a.get("stuck", 0) > 0:
                g["drops"].append(dict(p=V(a["p"]), kind="arrows", n=a["stuck"], mode=-1))
            heal = FOOD[a["kind"]]
            g["hp"] += heal
            g["hunger"] = min(100.0, g["hunger"] + HUNGER[a["kind"]])
            say(T("ate") % (L(ANAME[a["kind"]]), heal))
            g["an"].append(new_animal(a["kind"], a["lake"]))


def do_attack():
    w = WEAPONS[g["cur"]]
    p = g["p"]
    am = w.get("ammo")
    if w["ranged"] and am and g[am] <= 0:
        g["cd"] = 0.5
        say(T("no_arrows") if am == "arrows" else T("no_bullets"))
        play("click")
        return
    if not w["ranged"]:
        if g["stam"] < 5:
            g["cd"] = 0.4
            say(T("tired"))
            return
        g["stam"] -= 5
    g["cd"] = w["cd"]
    g["swing"] = 0.15
    pool = [e for e in cur_en() if e["p"].distance_to(p) < 450]
    if not pool and g["mode"] == -1:
        pool = [a for a in g["an"] if a["p"].distance_to(p) < 450]
    if pool:
        n = min(pool, key=lambda e: e["p"].distance_to(p))
        d = n["p"] - p
        if d.length() > 0:
            g["face"] = d.normalize()
    if w["ranged"]:
        if am:
            g[am] -= 1
        g["proj"].append(dict(p=V(p), v=g["face"] * w["speed"], dmg=w["dmg"], life=1.0,
                              arrow=(am == "arrows")))
        play("arrow" if am == "arrows" else "gun")
    else:
        hit_any = False
        for en in targets():
            dd = en["p"].distance_to(p)
            if dd < w["rng"] + 16:
                hit_any = True
                en["hp"] -= w["dmg"]
                if dd > 0 and en["kind"] in ("native", "mutant"):
                    en["p"] = emove(en["p"], (en["p"] - p).normalize() * (40 if g["cur"] == "axe" else 25))
        play("hit" if hit_any else "swing")


def throw_molo():
    if g["ending"]:
        return
    if g["molo"] <= 0:
        say(T("no_molo"))
        return
    p = g["p"]
    pool = [e for e in cur_en() if e["p"].distance_to(p) < 520]
    life = 0.7
    d = g["face"]
    if pool:
        n = min(pool, key=lambda e: e["p"].distance_to(p))
        dv = n["p"] - p
        if dv.length() > 0:
            d = dv.normalize()
            life = min(1.3, max(0.3, dv.length() / 420))
            g["face"] = d
    g["molo"] -= 1
    play("throw")
    g["proj"].append(dict(p=V(p), v=d * 420, dmg=0, life=life, molo=True))


def draw_burn(x, y, r):
    f = int(g["t"] * 12) % 3
    pygame.draw.circle(screen, (255, 110, 20), (x, y - r), 9 + 2 * f)
    pygame.draw.circle(screen, (255, 215, 80), (x, y - r - 3), 4 + f)
    pygame.draw.circle(screen, (255, 110, 20), (x - 10, y - r + 6), 6)
    pygame.draw.circle(screen, (255, 110, 20), (x + 10, y - r + 6), 6)


def draw_enemy(en, cam):
    x = int(en["p"].x - cam.x)
    y = int(en["p"].y - cam.y)
    if x < -70 or x > W + 70 or y < -70 or y > H + 70:
        return
    if en["kind"] == "miniboss":
        pygame.draw.circle(screen, (70, 25, 100), (x - 30, y + 6), 11)
        pygame.draw.circle(screen, (70, 25, 100), (x + 30, y + 6), 11)
        pygame.draw.polygon(screen, (220, 210, 190), [(x - 14, y - 20), (x - 22, y - 42), (x - 6, y - 24)])
        pygame.draw.polygon(screen, (220, 210, 190), [(x + 14, y - 20), (x + 22, y - 42), (x + 6, y - 24)])
        pygame.draw.circle(screen, (95, 50, 130), (x, y), 26)
        pygame.draw.circle(screen, (255, 60, 40), (x - 9, y - 6), 4)
        pygame.draw.circle(screen, (255, 60, 40), (x + 9, y - 6), 4)
        pygame.draw.line(screen, (20, 0, 0), (x - 10, y + 10), (x + 10, y + 10), 3)
        pygame.draw.rect(screen, (60, 0, 0), (x - 25, y - 52, 50, 6))
        pygame.draw.rect(screen, (230, 80, 20), (x - 25, y - 52, max(0, int(50 * en["hp"] / en["max"])), 6))
        return
    if en["kind"] == "boss":
        if en["slam"] > 0:
            pygame.draw.circle(screen, (120, 25, 25), (x, y), max(1, int(190 * (1.0 - en["slam"]))))
            pygame.draw.circle(screen, (230, 60, 50), (x, y), 190, 4)
        if en["flash"] > 0:
            pygame.draw.circle(screen, (255, 230, 200), (x, y), 200, 8)
        col = (205, 70, 20) if en["ch"] > 0 else ((150, 30, 70) if en["hp"] < en["max"] * 0.5 else (110, 25, 40))
        for k in (-1, 1):
            pygame.draw.circle(screen, (60, 15, 25), (x + k * 48, y + 10), 18)
            pygame.draw.line(screen, (90, 25, 40), (x + k * 40, y), (x + k * 70, y + 34), 8)
        pygame.draw.line(screen, (230, 220, 200), (x - 24, y - 36), (x - 40, y - 64), 6)
        pygame.draw.line(screen, (230, 220, 200), (x + 24, y - 36), (x + 40, y - 64), 6)
        pygame.draw.circle(screen, col, (x, y), 44)
        pygame.draw.circle(screen, (255, 230, 0), (x - 15, y - 12), 6)
        pygame.draw.circle(screen, (255, 230, 0), (x + 15, y - 12), 6)
        pygame.draw.line(screen, (20, 0, 0), (x - 16, y + 16), (x + 16, y + 16), 5)
        if en["ch"] <= 0 and en["slam"] <= 0 and en["cd"] < 0.6:
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 54, 3)
        return
    if en["kind"] == "mutant":
        pygame.draw.circle(screen, (110, 40, 140), (x - 17, y + 4), 8)
        pygame.draw.circle(screen, (110, 40, 140), (x + 17, y + 4), 8)
        pygame.draw.circle(screen, (60, 130, 60), (x, y), 18)
        pygame.draw.circle(screen, (255, 230, 0), (x - 6, y - 5), 3)
        pygame.draw.circle(screen, (255, 230, 0), (x + 6, y - 5), 3)
    else:
        pygame.draw.line(screen, (120, 90, 50), (x + 12, y + 16), (x + 12, y - 18), 3)
        pygame.draw.circle(screen, (150, 40, 30), (x, y), 14)
        pygame.draw.circle(screen, (240, 230, 200), (x - 4, y - 3), 2)
        pygame.draw.circle(screen, (240, 230, 200), (x + 4, y - 3), 2)
    if en["hp"] < en["max"]:
        pygame.draw.rect(screen, (60, 0, 0), (x - 16, y - 28, 32, 5))
        pygame.draw.rect(screen, (0, 220, 0), (x - 16, y - 28, max(0, int(32 * en["hp"] / en["max"])), 5))


def draw_animal(a, cam):
    x = int(a["p"].x - cam.x)
    y = int(a["p"].y - cam.y)
    if x < -60 or x > W + 60 or y < -60 or y > H + 60:
        return
    k = a["kind"]
    if k == "rabbit":
        pygame.draw.rect(screen, (235, 235, 235), (x - 7, y - 21, 4, 12))
        pygame.draw.rect(screen, (235, 235, 235), (x + 3, y - 21, 4, 12))
        pygame.draw.circle(screen, (235, 235, 235), (x, y), 10)
        pygame.draw.circle(screen, (20, 20, 20), (x - 4, y - 2), 2)
        pygame.draw.circle(screen, (255, 255, 255), (x + 10, y + 4), 4)
    elif k == "deer":
        for lx in (-14, -6, 6, 14):
            pygame.draw.line(screen, (90, 60, 30), (x + lx, y + 6), (x + lx, y + 22), 3)
        pygame.draw.ellipse(screen, (150, 100, 55), (x - 20, y - 10, 40, 22))
        pygame.draw.circle(screen, (150, 100, 55), (x + 22, y - 12), 8)
        pygame.draw.line(screen, (215, 190, 140), (x + 20, y - 18), (x + 14, y - 32), 2)
        pygame.draw.line(screen, (215, 190, 140), (x + 25, y - 18), (x + 31, y - 32), 2)
        pygame.draw.circle(screen, (20, 20, 20), (x + 25, y - 13), 2)
    else:
        pygame.draw.ellipse(screen, (255, 150, 50), (x - 9, y - 5, 18, 10))
        pygame.draw.polygon(screen, (255, 150, 50), [(x - 8, y), (x - 16, y - 5), (x - 16, y + 5)])
        pygame.draw.circle(screen, (20, 20, 20), (x + 5, y - 1), 1)
    if a["hp"] < a["max"]:
        pygame.draw.rect(screen, (60, 0, 0), (x - 14, y - 34, 28, 4))
        pygame.draw.rect(screen, (0, 220, 0), (x - 14, y - 34, max(0, int(28 * a["hp"] / a["max"])), 4))


def draw_shark(s, cam):
    x = int(s["p"].x - cam.x)
    y = int(s["p"].y - cam.y)
    if x < -90 or x > W + 90 or y < -90 or y > H + 90:
        return
    pygame.draw.ellipse(screen, (90, 100, 112), (x - 38, y - 12, 76, 24))
    pygame.draw.polygon(screen, (70, 80, 92), [(x - 6, y - 10), (x + 8, y - 10), (x, y - 34)])
    pygame.draw.polygon(screen, (70, 80, 92), [(x - 36, y), (x - 56, y - 14), (x - 56, y + 14)])
    pygame.draw.circle(screen, (10, 10, 10), (x + 26, y - 3), 3)


def draw_hut(h, cam):
    x = int(h["p"].x - cam.x)
    y = int(h["p"].y - cam.y)
    if x < -80 or x > W + 80 or y < -90 or y > H + 80:
        return
    pygame.draw.circle(screen, (125, 90, 55), (x, y), 30)
    pygame.draw.polygon(screen, (160, 120, 65), [(x - 38, y - 6), (x, y - 54), (x + 38, y - 6)])
    pygame.draw.polygon(screen, (110, 80, 40), [(x - 38, y - 6), (x, y - 54), (x + 38, y - 6)], 3)
    pygame.draw.rect(screen, (40, 25, 15) if h["looted"] else (20, 10, 5), (x - 7, y + 2, 14, 24))
    if not h["looted"]:
        pygame.draw.circle(screen, (255, 215, 60), (x, y - 62), 5)


# ---------- меню ----------
def menu_items():
    keys = ["continue", "new"] if started else ["play"]
    keys.append("howto")
    keys.append("settings")
    keys.append("quit")
    bw, bh = int(W * 0.62), int(H * 0.075)
    x = (W - bw) // 2
    y0 = int(H * 0.38)
    gap = int(bh * 1.3)
    return [(k, (x, y0 + i * gap, bw, bh)) for i, k in enumerate(keys)]
# ===== конец части 4, ниже вставь часть 5 =====
def draw_menu():
    screen.fill((8, 14, 30))
    pygame.draw.circle(screen, (235, 235, 210), (int(W * 0.8), int(H * 0.1)), int(S * 0.45))
    base = int(H * 0.8)
    for i in range(14):
        tx = int(W * (i + 0.5) / 14)
        th = int(H * 0.04 + H * 0.012 * ((i * 7) % 5))
        pygame.draw.rect(screen, (40, 28, 18), (tx - 8, base - 20, 16, 60))
        pygame.draw.polygon(screen, (12, 45, 25), [(tx - 55, base), (tx, base - 2 * th), (tx + 55, base)])
    pygame.draw.rect(screen, (10, 28, 18), (0, base + 30, W, H))
    text_c(huge, T("title"), (235, 235, 210), W // 2, int(H * 0.17))
    text_c(font, T("subtitle"), (150, 190, 160), W // 2, int(H * 0.17) + huge.get_height())
    for key, rect in menu_items():
        pygame.draw.rect(screen, (35, 70, 55), rect)
        pygame.draw.rect(screen, (150, 210, 170), rect, 4)
        label = (T("sound_on") if sound_on else T("sound_off")) if key == "sound" else T(key)
        text_c(big, label, (240, 245, 240), rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)


def settings_items():
    keys = []
    if CYR:
        keys.append("lang")
    if SND_OK:
        keys += ["sound", "music", "sfx"]
    keys += ["gfx", "ui", "fps", "back"]
    bw, bh = int(W * 0.8), int(H * 0.062)
    x = (W - bw) // 2
    y0 = int(H * 0.17)
    gap = int(bh * 1.22)
    return [(k, (x, y0 + i * gap, bw, bh)) for i, k in enumerate(keys)]


def setting_label(key):
    if key == "lang":
        return T("lang")
    if key == "sound":
        return T("sound_on") if sound_on else T("sound_off")
    if key == "music":
        return T("music") % music_vol
    if key == "sfx":
        return T("sfx") % sfx_vol
    if key == "gfx":
        return T("gfx") % L(GFX_NAMES[gfx])
    if key == "ui":
        return T("ui") % L(UI_NAMES[ui_size])
    if key == "fps":
        return T("fps_on") if show_fps else T("fps_off")
    return T("back")


def fit_text(label, rect, col):
    t = None
    for fnt in (big, font, fsmall):
        t = fnt.render(label, True, col)
        if t.get_width() <= rect[2] - 30:
            break
    screen.blit(t, (rect[0] + (rect[2] - t.get_width()) // 2, rect[1] + (rect[3] - t.get_height()) // 2))


def draw_settings():
    screen.fill((8, 14, 30))
    text_c(big, T("settings"), (235, 235, 210), W // 2, int(H * 0.07))
    text_c(fsmall, T("gfx_hint"), (150, 190, 160), W // 2, int(H * 0.115))
    for key, rect in settings_items():
        pygame.draw.rect(screen, (35, 70, 55), rect)
        pygame.draw.rect(screen, (150, 210, 170), rect, 4)
        fit_text(setting_label(key), rect, (240, 245, 240))
        if key in ("music", "sfx"):
            text_c(big, "-", (255, 230, 150), rect[0] + rect[2] // 12, rect[1] + rect[3] // 2)
            text_c(big, "+", (255, 230, 150), rect[0] + rect[2] - rect[2] // 12, rect[1] + rect[3] // 2)
    text_c(fsmall, T("set_tip"), (150, 190, 160), W // 2, int(H * 0.95))


def draw_help():
    screen.fill((8, 14, 30))
    text_c(big, T("howto"), (235, 235, 210), W // 2, int(H * 0.08))
    cw = max(1, font.size("n")[0])
    cpl = max(12, (W - int(W * 0.12)) // cw)
    ty = int(H * 0.15)
    for i in range(13):
        for ln in textwrap.wrap(T("help%d" % i), cpl):
            screen.blit(font.render(ln, True, (225, 230, 225)), (int(W * 0.06), ty))
            ty += font.get_height() + 4
        ty += font.get_height() // 2
    text_c(font, T("tap_back"), (120, 255, 160), W // 2, int(H * 0.93))
# ===== конец части 5, ниже вставь часть 6 =====
def update_game(dt, mv, atk):
    p = g["p"]
    mode = g["mode"]
    # ---------- движение ----------
    if mv.length() > 0:
        g["face"] = mv.normalize()
    push = mv.length()
    sprint = push > 0.85 and g["stam"] > 0 and not g["tired"]
    speed = 230 if sprint else (100 if g["tired"] else 150)
    if g["carry"]:
        speed *= 0.85
    swim = mode == -1 and (in_lake(p) or not on_land(p))
    if swim:
        speed = min(speed, 100)
    move = mv.normalize() * min(1.0, push / 0.5) if push > 0 else V(0, 0)
    if mode in CAVE_GEO:
        zn = zone_at(p)
        if zn == "cliff":
            speed = min(speed, 90)
        elif zn == "water":
            speed = min(speed, 120)
            swim = True
        p = step_player(p, move * speed * dt)
    else:
        p = p + move * speed * dt
    if swim and push > 0:
        g["stam"] = max(0.0, g["stam"] - 5 * dt)
    elif sprint:
        g["stam"] = max(0.0, g["stam"] - 16 * dt)
    else:
        g["stam"] = min(100.0, g["stam"] + (14 if (g["hunger"] > 20 and g["thirst"] > 20) else 6) * dt)
    if g["stam"] <= 0 and not g["tired"]:
        g["tired"] = True
        say(T("tired"))
    elif g["tired"] and g["stam"] >= 30:
        g["tired"] = False
    if mode == -1:
        p.x = min(max(p.x, -OCEAN), WORLD + OCEAN)
        p.y = min(max(p.y, -OCEAN), WORLD + OCEAN)
    else:
        sw_, sh_ = SIZES[mode]
        p.x = min(max(p.x, 20), sw_ - 20)
        p.y = min(max(p.y, 20), sh_ - 20)
    g["p"] = p

    # голод и жажда
    ocean = mode == -1 and not on_land(p)
    g["hunger"] = max(0.0, g["hunger"] - 0.17 * dt)
    g["thirst"] = max(0.0, g["thirst"] - (0.5 if ocean else 0.25) * dt)
    drink = (mode == -1 and in_lake(p)) or (mode in CAVE_GEO and zone_at(p) == "water")
    if drink:
        if g["thirst"] < 98:
            g["thirst"] = min(100.0, g["thirst"] + 30 * dt)
            if not g["drinking"]:
                g["drinking"] = True
                say(T("drink"))
    else:
        g["drinking"] = False
    if g["hunger"] <= 0:
        g["hp"] -= 1.2 * dt
    if g["thirst"] <= 0:
        g["hp"] -= 1.6 * dt
    if g["hunger"] < 20 and not g["warn_h"]:
        g["warn_h"] = True
        say(T("hungry"))
    elif g["hunger"] > 40:
        g["warn_h"] = False
    if g["thirst"] < 20 and not g["warn_t"]:
        g["warn_t"] = True
        say(T("thirsty"))
    elif g["thirst"] > 40:
        g["warn_t"] = False
    # холод в зимнем биоме
    snowy = mode == -1 and BEACH < p.y < SNOW_Y and 0 < p.x < WORLD
    heat = mode == -1 and ((g["fire"] > 0 and p.distance_to(FIRE) < 150) or any(p.distance_to(v) < 110 for v in VILLAGES))
    if snowy and not heat:
        g["cold"] = min(100.0, g["cold"] + 2.0 * dt)
    else:
        g["cold"] = max(0.0, g["cold"] - (6.0 if mode == -1 else 9.0) * dt)
    if g["cold"] >= 100:
        g["hp"] -= 3.0 * dt
    if g["cold"] > 60 and not g["warn_c"]:
        g["warn_c"] = True
        say(T("cold_warn"))
    elif g["cold"] < 25:
        g["warn_c"] = False
    if g["note_open"]:
        nts = g["caves"][mode].get("notes", []) if mode in CAVE_GEO else []
        if not any(p.distance_to(nt["p"]) < 100 for nt in nts):
            g["note_open"] = None

    g["cd"] = max(0, g["cd"] - dt)
    g["hurt_cd"] = max(0.0, g["hurt_cd"] - dt)
    g["blk"] = max(0.0, g["blk"] - dt)
    g["swing"] = max(0, g["swing"] - dt)
    g["msg_t"] = max(0, g["msg_t"] - dt)
    if atk and g["cd"] <= 0:
        do_attack()

    # ---------- снаряды ----------
    lst = targets()
    burnable = cur_en()
    for pr in g["proj"][:]:
        pr["p"] = pr["p"] + pr["v"] * dt
        pr["life"] -= dt
        if pr.get("molo"):
            boom = pr["life"] <= 0 or any(en["p"].distance_to(pr["p"]) < 24 for en in burnable)
            if boom:
                g["flames"].append(dict(p=V(pr["p"]), t=5.0))
                play("boom")
                g["proj"].remove(pr)
            continue
        hit = False
        for en in lst:
            if en["p"].distance_to(pr["p"]) < 22:
                en["hp"] -= pr["dmg"]
                if pr.get("arrow"):
                    en["stuck"] = en.get("stuck", 0) + 1
                play("hit")
                hit = True
                break
        if hit or pr["life"] <= 0:
            g["proj"].remove(pr)
    for fl in g["flames"][:]:
        fl["t"] -= dt
        if fl["t"] <= 0:
            g["flames"].remove(fl)
            continue
        for en in burnable:
            if en["p"].distance_to(fl["p"]) < 75:
                en["burn"] = max(en.get("burn", 0.0), 4.0)
    for en in burnable:
        if en.get("burn", 0.0) > 0:
            en["burn"] -= dt
            en["hp"] -= 12 * dt
    for ep in g["eproj"][:]:
        ep["p"] = ep["p"] + ep["v"] * dt
        ep["life"] -= dt
        if ep["p"].distance_to(p) < 22:
            hurt(ep["dmg"])
            g["eproj"].remove(ep)
        elif ep["life"] <= 0 or not enemy_ok(ep["p"]):
            g["eproj"].remove(ep)

    g["t"] += dt
    if mode == -1:
        g["day"] += dt
    is_night = (g["day"] % 60) > 30
    moved = False

    if mode == -1:
        if not g["fly_said"] and (g["day"] % 90) < 12:
            g["fly_said"] = True
            say(T("fly"))
        for tr in g["trees"][:]:
            if p.distance_to(tr) < 30:
                g["trees"].remove(tr)
                g["trees"].append(rand_tree())
                g["wood"] += 3 if "axe" in g["owned"] else (2 if "oldaxe" in g["owned"] else 1)
        for h in g["huts"]:
            if not h["looted"] and p.distance_to(h["p"]) < 42:
                h["looted"] = True
                if h.get("molo", 0) > 0:
                    g["molo"] += h["molo"]
                    say(T("hut_molo") % h["molo"])
                elif random.random() < 0.5:
                    n = random.randint(3, 6)
                    g["wood"] += n
                    say(T("hut_wood") % n)
                    play("pickup")
                else:
                    n = random.randint(10, 20)
                    g["hp"] += n
                    g["hunger"] = min(100.0, g["hunger"] + 25)
                    say(T("hut_heal") % n)
                    play("pickup")
        if not g["plane"] and p.distance_to(PLANE) < 90:
            g["plane"] = True
            g["hp"] += 30
            g["owned"].append("oldaxe")
            if g["cur"] == "fists":
                g["cur"] = "oldaxe"
            say(T("plane_med"))
            play("pickup")
        if not g["plane2"] and p.distance_to(PLANE2) < 80:
            g["plane2"] = True
            g["hp"] += 20
            g["molo"] += 3
            say(T("plane2"))
            play("pickup")
        for bu in g["bushes"]:
            if bu["ok"]:
                if (g["hp"] < 100 or g["hunger"] < 92) and p.distance_to(bu["p"]) < 34:
                    bu["ok"] = False
                    bu["t"] = 60.0
                    g["hp"] += 6
                    g["hunger"] = min(100.0, g["hunger"] + 8)
                    g["thirst"] = min(100.0, g["thirst"] + 4)
                    say(T("berries"))
                    play("pickup")
            else:
                bu["t"] -= dt
                if bu["t"] <= 0:
                    bu["ok"] = True
        if not g["crater"] and p.distance_to(CRATER) < 60:
            g["crater"] = True
            g["wood"] += 10
            say(T("crater_sup"))
            play("pickup")
        if p.distance_to(FIRE) < 60 and g["wood"] > 0:
            g["fire"] = min(100, g["fire"] + g["wood"] * 10)
            g["wood"] = 0
        g["fire"] = max(0, g["fire"] - 3 * dt)
        warm = g["fire"] > 0 and p.distance_to(FIRE) < 150
        if warm:
            g["hp"] += 5 * dt
        if is_night and on_land(p) and random.random() < 0.006 and len(g["en"]) < 4:
            q = p + V(600, 0).rotate(random.randint(0, 359))
            q.x = min(max(q.x, BEACH), WORLD - BEACH)
            q.y = min(max(q.y, BEACH), WORLD - BEACH)
            g["en"].append(mk(q, "native"))
        if not is_night and g["en"] and random.random() < 0.05:
            g["en"].pop()
        update_en(g["en"], p, dt, 99999, True)
        update_en(g["vil"], p, dt, 99999, True)
        update_animals(dt, p)
        update_sharks(dt, p)
        for c, mi in ENT:
            if p.distance_to(c) < 45:
                g["back"] = V(c)
                g["mode"] = mi
                g["p"] = V(ENTRY_SPAWN[mi])
                g["proj"] = []
                g["flames"] = []
                g["eproj"] = []
                say(L(ENT_MSG[mi]))
                break
    else:
        cv = g["caves"][mode]
        lst2 = cv["en"]
        if p.y < 600:
            for bo in [e for e in lst2 if e["kind"] == "boss"]:
                update_boss(bo, p, dt, lst2)
        update_en([e for e in lst2 if e["kind"] != "boss"], p, dt, 380, False)
        for chs in cv["chests"]:
            if not chs["got"] and p.distance_to(chs["p"]) < 50:
                chs["got"] = True
                play("chest")
                if chs["kind"] == "molo":
                    g["molo"] += chs["n"]
                    say(T("found_molo") % chs["n"])
                elif chs["kind"] == "med":
                    g["hp"] = min(100.0, g["hp"] + chs["n"])
                    say(T("found_med") % chs["n"])
                elif chs["kind"] == "ammo":
                    g["arrows"] += chs["n"]
                    g["bullets"] += chs["m"]
                    say(T("found_ammo") % (chs["n"], chs["m"]))
                elif chs["kind"] == "arrows":
                    g["arrows"] += chs["n"]
                    say(T("found_arrows") % chs["n"])
                elif chs["kind"] == "bullets":
                    g["bullets"] += chs["n"]
                    say(T("found_bullets") % chs["n"])
                else:
                    g["owned"].append(chs["kind"])
                    g["cur"] = chs["kind"]
                    say(T("found_w") % L(WEAPONS[chs["kind"]]["name"]))
        for it in cv.get("items", []):
            if not it["got"] and p.distance_to(it["p"]) < 42:
                it["got"] = True
                play("chest")
                if it["kind"] == "climb":
                    g["climb"] = True
                    say(T("got_climb"))
                else:
                    g["scuba"] = True
                    say(T("got_scuba"))
        for st in cv.get("stones", [])[:]:
            if p.distance_to(st) < 36:
                cv["stones"].remove(st)
                g["rocks"] += 1
                play("pickup")
                say(T("got_stone") % g["rocks"])
        if "lever" in cv and g["rocks"] > 0 and cv["slots"] < 3 and p.distance_to(cv["lever"]) < 70:
            put = min(g["rocks"], 3 - cv["slots"])
            g["rocks"] -= put
            cv["slots"] += put
            play("hit")
            say(T("slot") % cv["slots"])
            if cv["slots"] >= 3 and not cv["gate"]:
                cv["gate"] = True
                play("boom")
                say(T("gate_open"))
        if mode == 5:
            cdd = cv["card"]
            if not cdd["got"] and p.distance_to(cdd["p"]) < 40:
                cdd["got"] = True
                g["card"] = True
                play("chest")
                say(T("got_card"))
            gl = cv["girl"]
            if gl is not None:
                if gl["state"] == "lying" and p.distance_to(gl["p"]) < 50:
                    gl["state"] = "carried"
                    g["carry"] = True
                    play("pickup")
                    say(T("girl_pick"))
                elif gl["state"] == "carried" and p.distance_to(ALTAR) < 110:
                    gl["state"] = "placed"
                    gl["p"] = V(ALTAR.x + 75, ALTAR.y + 45)
                    g["carry"] = False
                    g["gold"] = True
                    play("armor")
                    say(T("altar_reject"))
            if p.distance_to(COT) < 90 and g["msg_t"] <= 0:
                say(T("timmy_sleep"))
        geo_d = CAVE_GEO.get(mode)
        if geo_d is not None:
            for drect, dname, dneed in geo_d.get("doors", []):
                if not cv["doors"].get(dname):
                    have = g["card"] if dneed == "card" else g["gold"]
                    if have and p.distance_to(V(drect[0] + drect[2] / 2, drect[1] + drect[3] / 2)) < 110:
                        cv["doors"][dname] = True
                        play("chest")
                        say(T("door_open"))
        if mode == 6:
            mx, my, mw, mh = MEDBAY
            if mx < p.x < mx + mw and my < p.y < my + mh:
                g["hp"] += 15 * dt
        for ppos, to, spawn, key in PORTALS[mode]:
            if p.distance_to(ppos) < 55:
                if to == -1:
                    g["mode"] = -1
                    g["p"] = g["back"] + V(0, 80)
                else:
                    g["mode"] = to
                    g["p"] = V(spawn)
                    if to in PORTAL_MSG:
                        say(L(PORTAL_MSG[to]))
                g["proj"] = []
                g["flames"] = []
                g["eproj"] = []
                moved = True
                break
        if moved:
            return True

    for dr in g["drops"][:]:
        if dr["mode"] == g["mode"] and g["p"].distance_to(dr["p"]) < 38:
            g["drops"].remove(dr)
            if dr["kind"] == "arrows":
                g["arrows"] += dr["n"]
                say(T("got_arrows") % dr["n"])
                play("pickup")
            else:
                g["armor"] = min(100.0, g["armor"] + dr["n"])
                say(T("got_armor") % dr["n"])
                play("armor")
    reap()
    g["hp"] = max(0.0, min(100.0, g["hp"]))
    if g["hp"] <= 0 and not g["dead_snd"]:
        g["dead_snd"] = True
        play("die")
    return False


def kid(cx, cy, k, mask=False):
    hy = cy - k // 2 - k // 3
    w2 = max(3, k // 6)
    pygame.draw.line(screen, (60, 90, 200), (cx, cy - k // 2), (cx, cy + k // 2), max(4, k // 4))
    pygame.draw.line(screen, (60, 90, 200), (cx, cy - k // 3), (cx - k // 2, cy + k // 6), w2)
    pygame.draw.line(screen, (60, 90, 200), (cx, cy - k // 3), (cx + k // 2, cy + k // 6), w2)
    pygame.draw.line(screen, (50, 50, 90), (cx, cy + k // 2), (cx - k // 3, cy + k), w2)
    pygame.draw.line(screen, (50, 50, 90), (cx, cy + k // 2), (cx + k // 3, cy + k), w2)
    pygame.draw.circle(screen, (240, 200, 170), (cx, hy), k // 3)
    pygame.draw.circle(screen, (60, 40, 20), (cx - k // 9, hy), max(2, k // 14))
    pygame.draw.circle(screen, (60, 40, 20), (cx + k // 9, hy), max(2, k // 14))
    if mask:
        pygame.draw.rect(screen, (60, 160, 220), (cx - k // 4, hy - k // 8, k // 2, k // 4))
        pygame.draw.rect(screen, (120, 140, 160), (cx - k // 2 - k // 6, cy - k // 3, k // 4, k // 2))
# ===== конец части 6, ниже вставь часть 7 =====
def icon_axe(x, y, k):
    pygame.draw.line(screen, (150, 110, 60), (x - k, y + k), (x + k // 2, y - k), max(3, k // 4))
    pygame.draw.polygon(screen, (170, 180, 195), [(x + k // 2 - 2, y - k), (x + k + k // 2, y - k + k // 3),
                                                   (x + k, y - k // 3), (x + k // 4, y - k // 2)])


def icon_cross(x, y, k):
    pygame.draw.rect(screen, (210, 40, 40), (x - k // 4, y - k, k // 2, 2 * k))
    pygame.draw.rect(screen, (210, 40, 40), (x - k, y - k // 4, 2 * k, k // 2))


def icon_gun(x, y, k):
    pygame.draw.rect(screen, (70, 70, 80), (x - k, y - k // 2, 2 * k, k // 2))
    pygame.draw.rect(screen, (70, 70, 80), (x - k // 2, y, k // 2, k))


def icon_check(x, y, k):
    pygame.draw.lines(screen, (40, 170, 70), False,
                      [(x - k, y), (x - k // 3, y + k * 2 // 3), (x + k, y - k * 2 // 3)], max(3, k // 3))


def icon_stone(x, y, r):
    pygame.draw.circle(screen, (130, 130, 138), (x, y), r)
    pygame.draw.circle(screen, (90, 90, 98), (x, y), r, 2)


def sketch_arrow(x1, y1, x2, y2, col):
    pygame.draw.line(screen, col, (x1, y1), (x2, y2), 4)
    d = V(x2 - x1, y2 - y1)
    if d.length() > 0:
        d = d.normalize()
        nrm = V(-d.y, d.x)
        tip = V(x2, y2)
        pa = tip - d * 14 + nrm * 8
        pb = tip - d * 14 - nrm * 8
        pygame.draw.polygon(screen, col, [(x2, y2), (int(pa.x), int(pa.y)), (int(pb.x), int(pb.y))])


def wave(x, y, w):
    pygame.draw.lines(screen, (60, 120, 200), False,
                      [(x, y), (x + w // 4, y - 6), (x + w // 2, y), (x + 3 * w // 4, y - 6), (x + w, y)], 3)


def draw_note(kind):
    pw = int(min(W * 0.8, H * 0.55))
    ph = int(pw * 0.8)
    px = (W - pw) // 2
    py = int(H * 0.08)
    pygame.draw.rect(screen, (236, 226, 196), (px, py, pw, ph))
    pygame.draw.rect(screen, (120, 90, 60), (px, py, pw, ph), 5)

    def X(u):
        return px + int(pw * u)

    def Y(v):
        return py + int(ph * v)

    ink = (50, 40, 35)
    k = max(10, pw // 20)
    if kind in ("climb", "scuba"):
        pygame.draw.line(screen, ink, (X(0.5), Y(0.76)), (X(0.5), Y(0.45)), 5)
        pygame.draw.line(screen, ink, (X(0.5), Y(0.45)), (X(0.22), Y(0.18)), 5)
        pygame.draw.line(screen, ink, (X(0.5), Y(0.45)), (X(0.78), Y(0.18)), 5)
        if kind == "climb":
            pygame.draw.lines(screen, (120, 70, 40), False,
                              [(X(0.40), Y(0.64)), (X(0.45), Y(0.58)), (X(0.50), Y(0.65)),
                               (X(0.55), Y(0.58)), (X(0.60), Y(0.64))], 5)
            icon_axe(X(0.16), Y(0.16), k)
            icon_check(X(0.30), Y(0.06), k // 2)
            icon_cross(X(0.84), Y(0.16), k)
            kid(X(0.5), Y(0.84), pw // 12)
        else:
            wave(X(0.28), Y(0.36), pw // 10)
            wave(X(0.62), Y(0.36), pw // 10)
            wave(X(0.42), Y(0.55), pw // 10)
            icon_cross(X(0.16), Y(0.16), k)
            icon_gun(X(0.84), Y(0.16), k)
            icon_check(X(0.70), Y(0.06), k // 2)
            kid(X(0.5), Y(0.84), pw // 12, True)
    else:
        for i in range(3):
            icon_stone(X(0.10 + 0.10 * i), Y(0.25), k)
        text_c(font, "x3", ink, X(0.20), Y(0.42))
        sketch_arrow(X(0.40), Y(0.25), X(0.50), Y(0.25), ink)
        pygame.draw.rect(screen, (90, 90, 100), (X(0.52), Y(0.30), pw // 9, ph // 12))
        pygame.draw.line(screen, ink, (X(0.56), Y(0.30)), (X(0.62), Y(0.14)), 6)
        pygame.draw.circle(screen, (200, 40, 40), (X(0.62), Y(0.14)), max(5, k // 2))
        sketch_arrow(X(0.68), Y(0.25), X(0.77), Y(0.25), ink)
        gx, gy, gw, gh = X(0.80), Y(0.10), int(pw * 0.16), int(ph * 0.34)
        pygame.draw.rect(screen, ink, (gx, gy, gw, gh), 4)
        for i in range(1, 4):
            pygame.draw.line(screen, ink, (gx + gw * i // 4, gy), (gx + gw * i // 4, gy + gh), 3)
        kid(X(0.5), Y(0.80), pw // 12)
        icon_stone(X(0.5) + pw // 18, Y(0.80) - pw // 40, max(5, k // 2))
    text_c(font, T("note"), ink, W // 2, py + ph + font.get_height())
    text_c(font, T("tap_close"), (200, 200, 200), W // 2, py + ph + 2 * font.get_height() + 6)


def draw_door(dr, cv, ox, oy):
    rect, name, need = dr
    x, y, w_, h_ = ox + rect[0], oy + rect[1], rect[2], rect[3]
    col = (170, 175, 190) if need == "card" else (212, 172, 48)
    if cv["doors"].get(name):
        pygame.draw.rect(screen, (50, 55, 62), (x, y, w_, h_))
        pygame.draw.rect(screen, col, (x, y, w_, h_), 3)
        return
    pygame.draw.rect(screen, (62, 72, 90), (x, y, w_, h_))
    pygame.draw.rect(screen, col, (x, y, w_, h_), 4)
    cx, cy = x + w_ // 2, y + h_ // 2
    pygame.draw.line(screen, (40, 46, 60), (cx, y), (cx, y + h_), 4)
    pygame.draw.rect(screen, (25, 28, 36), (cx - 12, cy - 9, 24, 18))
    pygame.draw.rect(screen, col, (cx - 8, cy - 5, 16, 10))
    pygame.draw.circle(screen, (220, 50, 40), (cx, cy - 16), 4)


def draw_corpse(x, y, ang, kind):
    d = V(1, 0).rotate(ang)
    n = V(-d.y, d.x)
    coat = (232, 232, 238) if kind == "coat" else (95, 105, 70)

    def P(v):
        return (int(x + v.x), int(y + v.y))
    pygame.draw.line(screen, (60, 60, 75), P(d * -10), P(d * -34 + n * 7), 7)
    pygame.draw.line(screen, (60, 60, 75), P(d * -10), P(d * -34 - n * 7), 7)
    pygame.draw.line(screen, coat, P(d * -12), P(d * 12), 16)
    pygame.draw.line(screen, (150, 25, 28), P(d * 0 + n * 2), P(d * 8 - n * 2), 5)
    pygame.draw.line(screen, coat, P(d * 8 + n * 6), P(d * 22 + n * 18), 5)
    pygame.draw.line(screen, coat, P(d * 8 - n * 6), P(d * 22 - n * 18), 5)
    pygame.draw.circle(screen, (226, 190, 160), P(d * 20), 9)


def draw_girl(x, y):
    pygame.draw.line(screen, (200, 120, 160), (x - 14, y), (x + 8, y), 12)
    pygame.draw.line(screen, (200, 120, 160), (x - 14, y), (x - 28, y + 5), 5)
    pygame.draw.line(screen, (200, 120, 160), (x - 14, y), (x - 28, y - 5), 5)
    pygame.draw.circle(screen, (240, 200, 170), (x + 18, y), 8)
    pygame.draw.line(screen, (90, 60, 40), (x + 14, y - 7), (x + 26, y - 3), 3)


def draw_lab(cv, ox, oy):
    dc = cv["decor"]
    for r in CAVE_GEO[5]["floor"]:
        for gx in range(r[0] - r[0] % 100 + 100, r[0] + r[2], 100):
            pygame.draw.line(screen, (180, 186, 198), (ox + gx, oy + r[1]), (ox + gx, oy + r[1] + r[3]), 1)
        for gy in range(r[1] - r[1] % 100 + 100, r[1] + r[3], 100):
            pygame.draw.line(screen, (180, 186, 198), (ox + r[0], oy + gy), (ox + r[0] + r[2], oy + gy), 1)

    def vis(x, y):
        return -100 < ox + x < W + 100 and -100 < oy + y < H + 100
    for bx, by, br in dc["blood"]:
        if vis(bx, by):
            pygame.draw.circle(screen, (105, 16, 20), (ox + bx, oy + by), br)
            pygame.draw.circle(screen, (130, 24, 28), (ox + bx + br // 3, oy + by - br // 4), max(3, br // 2))
    for c in dc["corpses"]:
        if c["trail"] is not None and vis(int(c["p"].x), int(c["p"].y)):
            for i in range(1, 7):
                tq = c["p"] + V(i * 14, 0).rotate(c["trail"])
                pygame.draw.circle(screen, (100, 15, 20), (int(ox + tq.x), int(oy + tq.y)), 4)
    for sx, sy, sr in dc["scorch"]:
        if vis(sx, sy):
            pygame.draw.circle(screen, (28, 26, 28), (ox + sx, oy + sy), sr)
            pygame.draw.circle(screen, (70, 60, 55), (ox + sx, oy + sy), sr + 6, 3)
            for k in range(5):
                dv = V(sr + 16, 0).rotate(k * 72 + (sx + sy) % 60)
                pygame.draw.line(screen, (60, 55, 52), (ox + sx, oy + sy), (int(ox + sx + dv.x), int(oy + sy + dv.y)), 2)
    for gx_, gy_, ga in dc["glass"]:
        if vis(gx_, gy_):
            pts = [(int(ox + gx_ + q.x), int(oy + gy_ + q.y))
                   for q in (V(9, 0).rotate(ga), V(-4, 6).rotate(ga), V(-4, -6).rotate(ga))]
            pygame.draw.polygon(screen, (190, 225, 238), pts)
            pygame.draw.polygon(screen, (120, 170, 190), pts, 1)
    for px_, py_, pr_ in dc["pebbles"]:
        if vis(px_, py_):
            pygame.draw.circle(screen, (130, 130, 136), (ox + px_, oy + py_), pr_)
            pygame.draw.circle(screen, (95, 95, 102), (ox + px_, oy + py_), pr_, 1)
    for c in dc["corpses"]:
        if vis(int(c["p"].x), int(c["p"].y)):
            draw_corpse(int(ox + c["p"].x), int(oy + c["p"].y), c["ang"], c["kind"])
    cd = dc["card"]
    if not cd["got"]:
        cx_, cy_ = int(ox + cd["p"].x), int(oy + cd["p"].y)
        pygame.draw.circle(screen, (255, 255, 150), (cx_, cy_), 18, 2)
        pygame.draw.rect(screen, (160, 185, 215), (cx_ - 10, cy_ - 7, 20, 14))
        pygame.draw.rect(screen, (60, 80, 120), (cx_ - 10, cy_ - 2, 20, 4))
    ax, ay = int(ox + ALTAR.x), int(oy + ALTAR.y)
    pygame.draw.rect(screen, (90, 85, 98), (ax - 56, ay - 34, 112, 68))
    pygame.draw.rect(screen, (130, 124, 140), (ax - 56, ay - 34, 112, 68), 4)
    pygame.draw.circle(screen, (200, 60, 60), (ax, ay), 22 + int(g["t"] * 6) % 4, 3)
    for k in (-1, 1):
        pygame.draw.rect(screen, (230, 225, 200), (ax + k * 40 - 4, ay - 52, 8, 18))
        pygame.draw.circle(screen, (255, 190, 60), (ax + k * 40, ay - 58), 5 + int(g["t"] * 9) % 3)
    tx, ty = int(ox + COT.x), int(oy + COT.y)
    pygame.draw.rect(screen, (150, 150, 160), (tx - 38, ty - 62, 76, 124))
    pygame.draw.rect(screen, (90, 100, 115), (tx - 38, ty - 62, 76, 124), 4)
    pygame.draw.rect(screen, (90, 110, 170), (tx - 32, ty - 16, 64, 72))
    pygame.draw.circle(screen, (240, 200, 170), (tx, ty - 36), 14)
    pygame.draw.circle(screen, (60, 40, 20), (tx - 5, ty - 38), 2)
    pygame.draw.circle(screen, (60, 40, 20), (tx + 5, ty - 38), 2)
    text_c(font, T("timmy"), (40, 40, 60), tx, ty - 82)
    gl = cv["girl"]
    if gl is not None and gl["state"] in ("lying", "placed"):
        draw_girl(int(ox + gl["p"].x), int(oy + gl["p"].y))


def draw_torch(x, y):
    pygame.draw.line(screen, (90, 60, 35), (x, y + 30), (x, y + 2), 5)
    pygame.draw.circle(screen, (226, 220, 200), (x, y - 8), 14)
    pygame.draw.rect(screen, (226, 220, 200), (x - 8, y + 2, 16, 8))
    pygame.draw.circle(screen, (30, 25, 25), (x - 5, y - 10), 4)
    pygame.draw.circle(screen, (30, 25, 25), (x + 5, y - 10), 4)
    pygame.draw.polygon(screen, (40, 30, 30), [(x, y - 5), (x - 3, y), (x + 3, y)])
    for tx in (-4, 0, 4):
        pygame.draw.line(screen, (90, 85, 80), (x + tx, y + 3), (x + tx, y + 9), 1)
    f = int(g["t"] * 10) % 3
    pygame.draw.circle(screen, (255, 120, 20), (x, y - 26), 9 + f)
    pygame.draw.circle(screen, (255, 210, 80), (x, y - 28), 5 + f // 2)


def draw_geo(mode, ox, oy):
    geo = CAVE_GEO[mode]
    cv = g["caves"][mode]
    rock_c, edge_c = ROCKCOL.get(mode, ((20, 16, 26), (95, 85, 105)))
    screen.fill(rock_c)
    for r in geo["floor"] + geo["water"] + geo["cliff"] + geo["gate"] + [d_[0] for d_ in geo.get("doors", [])]:
        pygame.draw.rect(screen, edge_c, (ox + r[0] - 10, oy + r[1] - 10, r[2] + 20, r[3] + 20))
    for r in geo["water"]:
        rx, ry = ox + r[0], oy + r[1]
        pygame.draw.rect(screen, (30, 90, 160), (rx, ry, r[2], r[3]))
        for yy in range(ry + 30, ry + r[3], 60):
            pygame.draw.line(screen, (90, 150, 220), (rx + 20, yy), (rx + r[2] - 20, yy), 2)
    for r in geo["cliff"]:
        rx, ry = ox + r[0], oy + r[1]
        pygame.draw.rect(screen, (118, 84, 56), (rx, ry, r[2], r[3]))
        for yy in range(ry + 12, ry + r[3], 24):
            pygame.draw.line(screen, (80, 56, 36), (rx, yy), (rx + r[2], yy), 3)
        text_c(font, T("cliff"), (240, 220, 190), rx + r[2] // 2, ry + r[3] // 2)
    for r in geo["gate"]:
        rx, ry = ox + r[0], oy + r[1]
        if cv.get("gate"):
            pygame.draw.rect(screen, (60, 60, 70), (rx, ry, r[2], 6))
        else:
            pygame.draw.rect(screen, (60, 60, 72), (rx, ry, r[2], r[3]))
            for xx in range(rx + 8, rx + r[2], 26):
                pygame.draw.rect(screen, (170, 175, 185), (xx, ry, 8, r[3]))
    for r in geo["floor"]:
        pygame.draw.rect(screen, FLOOR[mode], (ox + r[0], oy + r[1], r[2], r[3]))
    if mode == 5:
        draw_lab(cv, ox, oy)
    for dr_ in geo.get("doors", []):
        draw_door(dr_, cv, ox, oy)
    for it in cv.get("items", []):
        if it["got"]:
            continue
        x, y = int(ox + it["p"].x), int(oy + it["p"].y)
        pygame.draw.circle(screen, (255, 230, 120), (x, y), 26, 2)
        if it["kind"] == "climb":
            icon_axe(x, y, 14)
        else:
            pygame.draw.rect(screen, (120, 140, 160), (x - 8, y - 14, 16, 28))
            pygame.draw.circle(screen, (60, 160, 220), (x, y - 20), 9)
            pygame.draw.line(screen, (60, 60, 70), (x + 8, y - 8), (x + 18, y + 6), 3)
    for nt in cv.get("notes", []):
        x, y = int(ox + nt["p"].x), int(oy + nt["p"].y)
        pygame.draw.rect(screen, (236, 226, 196), (x - 14, y - 10, 28, 20))
        pygame.draw.rect(screen, (120, 90, 60), (x - 14, y - 10, 28, 20), 2)
        pygame.draw.line(screen, (90, 70, 50), (x - 8, y - 3), (x + 8, y - 3), 2)
        pygame.draw.line(screen, (90, 70, 50), (x - 8, y + 3), (x + 4, y + 3), 2)
    for st in cv.get("stones", []):
        icon_stone(int(ox + st.x), int(oy + st.y), 10)
    if "lever" in cv:
        lx, ly = int(ox + cv["lever"].x), int(oy + cv["lever"].y)
        pygame.draw.rect(screen, (90, 90, 100), (lx - 34, ly - 10, 68, 22))
        for i in range(3):
            sx = lx - 22 + 22 * i
            if i < cv["slots"]:
                icon_stone(sx, ly + 1, 8)
            else:
                pygame.draw.circle(screen, (40, 40, 48), (sx, ly + 1), 8)
        pygame.draw.line(screen, (60, 60, 70), (lx, ly - 10), (lx + 18, ly - 40), 6)
        pygame.draw.circle(screen, (200, 40, 40), (lx + 18, ly - 40), 7)
        text_c(font, T("lever"), (230, 230, 240), lx, ly + 34)
    for tq in cv.get("torches", []):
        draw_torch(int(ox + tq.x), int(oy + tq.y))


def draw_mountain(mc, k):
    ma, mb, mt = int(270 * k), int(190 * k), int(240 * k)
    pygame.draw.polygon(screen, (105, 105, 118), [(mc[0] - ma, mc[1] + mb), (mc[0], mc[1] - mt), (mc[0] + ma, mc[1] + mb)])
    pygame.draw.polygon(screen, (80, 80, 92), [(mc[0], mc[1] - mt), (mc[0] + ma, mc[1] + mb), (mc[0] + int(40 * k), mc[1] + mb)])
    pygame.draw.polygon(screen, (240, 245, 250), [(mc[0] - int(62 * k), mc[1] - int(120 * k)), (mc[0], mc[1] - mt),
                                                  (mc[0] + int(62 * k), mc[1] - int(120 * k))])
# ===== конец части 7, ниже вставь часть 8 =====
def draw_overworld(p, mode, cam, is_night):
    def sp(v):
        return (int(v.x - cam.x), int(v.y - cam.y))
    ox, oy = int(-cam.x), int(-cam.y)
    screen.fill((14, 56, 128))
    pygame.draw.rect(screen, (34, 104, 184), (ox - 260, oy - 260, WORLD + 520, WORLD + 520))
    pygame.draw.rect(screen, (232, 214, 152), (ox, oy, WORLD, WORLD))
    pygame.draw.rect(screen, (30, 110, 40),
                     (ox + BEACH, oy + BEACH, WORLD - 2 * BEACH, WORLD - 2 * BEACH))
    pygame.draw.rect(screen, (225, 235, 245),
                     (ox + BEACH, oy + BEACH, WORLD - 2 * BEACH, SNOW_Y - BEACH))
    pygame.draw.rect(screen, (205, 232, 250), (ox - 6, oy - 6, WORLD + 12, WORLD + 12), 6)
    for c, r in LAKES:
        pygame.draw.circle(screen, (60, 120, 200), sp(c), r)
        if gfx == 2:
            pygame.draw.circle(screen, (110, 170, 230), sp(c), r, 4)
    pygame.draw.circle(screen, (110, 80, 50), sp(CRATER), 95)
    pygame.draw.circle(screen, (70, 50, 30), sp(CRATER), 65)
    pygame.draw.circle(screen, (40, 28, 18), sp(CRATER), 30)
    pl = sp(PLANE)
    pygame.draw.circle(screen, (45, 45, 45), pl, 70)
    pygame.draw.rect(screen, (150, 150, 160), (pl[0] - 85, pl[1] - 18, 170, 36))
    pygame.draw.rect(screen, (125, 125, 135), (pl[0] - 20, pl[1] - 75, 40, 150))
    pygame.draw.rect(screen, (110, 110, 120), (pl[0] - 95, pl[1] - 35, 20, 36))
    p2 = sp(PLANE2)
    pygame.draw.circle(screen, (170, 180, 192), p2, 62)
    pygame.draw.rect(screen, (150, 150, 160), (p2[0] - 50, p2[1] - 14, 100, 28))
    pygame.draw.rect(screen, (240, 245, 250), (p2[0] - 50, p2[1] - 18, 100, 6))
    pygame.draw.polygon(screen, (125, 125, 135),
                        [(p2[0] + 30, p2[1] - 14), (p2[0] + 48, p2[1] - 74),
                         (p2[0] + 62, p2[1] - 74), (p2[0] + 56, p2[1] - 14)])
    pygame.draw.polygon(screen, (110, 110, 120),
                        [(p2[0] + 20, p2[1] + 14), (p2[0] + 70, p2[1] + 34), (p2[0] + 52, p2[1] + 14)])
    pygame.draw.circle(screen, (45, 45, 45), (p2[0] - 50, p2[1]), 16)
    for c in CAVES:
        pygame.draw.circle(screen, (100, 100, 100), sp(c), 48)
        pygame.draw.circle(screen, (15, 15, 15), sp(c), 36)
    pygame.draw.circle(screen, (125, 90, 70), sp(CRATER_CAVE), 48)
    pygame.draw.circle(screen, (15, 15, 15), sp(CRATER_CAVE), 36)
    # горы (входа в гору больше нет)
    for mpos, mk_ in MOUNTAINS:
        draw_mountain(sp(mpos), mk_)
    # деревни
    for vc in VILLAGES:
        vp = sp(vc)
        pygame.draw.circle(screen, (60, 40, 25), vp, 14)
        pygame.draw.circle(screen, (230, 120, 20), vp, 8)
    for st in (g["stones"] if gfx >= 1 else []):
        x, y = sp(st)
        if -20 < x < W + 20 and -20 < y < H + 20:
            pygame.draw.circle(screen, (130, 130, 135), (x, y), 5)
            pygame.draw.circle(screen, (105, 105, 112), (x + 8, y + 3), 4)
            pygame.draw.circle(screen, (150, 150, 156), (x - 6, y + 4), 3)
    for bu in g["bushes"]:
        x, y = sp(bu["p"])
        if -30 < x < W + 30 and -30 < y < H + 30:
            pygame.draw.circle(screen, (22, 90, 35), (x, y), 16)
            pygame.draw.circle(screen, (30, 110, 45), (x - 10, y + 4), 10)
            pygame.draw.circle(screen, (30, 110, 45), (x + 10, y + 5), 10)
            if bu["ok"]:
                for bx, by in ((-5, -4), (6, -2), (0, 7), (-11, 5), (11, 6)):
                    pygame.draw.circle(screen, (200, 30, 70), (x + bx, y + by), 3)
    for h in g["huts"]:
        draw_hut(h, cam)
    pygame.draw.circle(screen, (255, 140, 0), sp(FIRE), int(10 + g["fire"] / 5))
    for a in g["an"]:
        draw_animal(a, cam)
    for tr in g["trees"]:
        x, y = sp(tr)
        if -40 < x < W + 40 and -40 < y < H + 40:
            snow = tr.y < SNOW_Y
            if gfx == 2:
                pygame.draw.ellipse(screen, (190, 205, 215) if snow else (20, 80, 32), (x - 20, y + 14, 40, 16))
            pygame.draw.rect(screen, (90, 55, 25), (x - 5, y, 10, 25))
            pygame.draw.circle(screen, (170, 205, 190) if snow else (15, 70, 25), (x, y), 22)
    for s in g["sharks"]:
        draw_shark(s, cam)
    # пролетающий самолёт (тень)
    ph = g["day"] % 90
    if ph < 12:
        fx = int(-150 + (W + 300) * ph / 12)
        fy = int(H * 0.22)
        sc = (20, 50, 28)
        pygame.draw.rect(screen, sc, (fx - 60, fy - 6, 120, 12))
        pygame.draw.polygon(screen, sc, [(fx - 5, fy), (fx - 35, fy - 48), (fx - 18, fy - 48), (fx + 25, fy)])
        pygame.draw.polygon(screen, sc, [(fx - 5, fy), (fx - 35, fy + 48), (fx - 18, fy + 48), (fx + 25, fy)])
        pygame.draw.polygon(screen, sc, [(fx - 60, fy), (fx - 75, fy - 20), (fx - 62, fy - 20), (fx - 45, fy)])


def draw_cave(p, mode, cam):
    def sp(v):
        return (int(v.x - cam.x), int(v.y - cam.y))
    sw_, sh_ = SIZES[mode]
    ox, oy = int(-cam.x), int(-cam.y)
    if mode in CAVE_GEO:
        draw_geo(mode, ox, oy)
    else:
        screen.fill((8, 6, 12))
        pygame.draw.rect(screen, FLOOR[mode], (ox, oy, sw_, sh_))
        pygame.draw.rect(screen, (95, 85, 105), (ox, oy, sw_, sh_), 8)
    if mode == 3:
        for yy in range(100, 1900, 200):
            pygame.draw.circle(screen, (45, 38, 38), (ox + 30, oy + yy), 40)
            pygame.draw.circle(screen, (45, 38, 38), (ox + 870, oy + yy + 100), 40)
    elif mode == 4:
        for rx, ry, rr_ in ((250, 300, 40), (1100, 350, 50), (400, 700, 35),
                            (1000, 750, 45), (700, 450, 30), (180, 850, 40)):
            pygame.draw.circle(screen, (70, 50, 32), (ox + rx, oy + ry), rr_)
            pygame.draw.circle(screen, (115, 88, 60), (ox + rx - 6, oy + ry - 6), rr_ - 12)
    elif mode == 6:
        for gx in range(0, 1601, 100):
            pygame.draw.line(screen, (62, 74, 92), (ox + gx, oy), (ox + gx, oy + 1100), 1)
        for gy in range(0, 1101, 100):
            pygame.draw.line(screen, (62, 74, 92), (ox, oy + gy), (ox + 1600, oy + gy), 1)
        zones = [(MEDBAY, (95, 55, 65), "med"), ((600, 60, 400, 240), (40, 70, 110), "ctl"),
                 ((1100, 100, 400, 320), (30, 70, 50), "rad"), ((80, 100, 400, 300), (75, 72, 50), "sto")]
        for rect, col, zk in zones:
            rx, ry, rw, rh = rect
            pygame.draw.rect(screen, col, (ox + rx, oy + ry, rw, rh))
            pygame.draw.rect(screen, (150, 160, 175), (ox + rx, oy + ry, rw, rh), 3)
            text_c(font, L(ZONES[zk]), (220, 230, 240), ox + rx + rw // 2, oy + ry + 24)
        mc2 = (ox + MEDBAY[0] + MEDBAY[2] // 2, oy + MEDBAY[1] + MEDBAY[3] // 2)
        pygame.draw.rect(screen, (230, 50, 50), (mc2[0] - 12, mc2[1] - 40, 24, 80))
        pygame.draw.rect(screen, (230, 50, 50), (mc2[0] - 40, mc2[1] - 12, 80, 24))
        for bx, by in ((150, 200), (240, 260), (330, 190)):
            pygame.draw.rect(screen, (120, 90, 50), (ox + bx, oy + by, 60, 50))
            pygame.draw.rect(screen, (70, 50, 30), (ox + bx, oy + by, 60, 50), 3)
        cp = sp(CONSOLE)
        pygame.draw.rect(screen, (25, 30, 45), (cp[0] - 70, cp[1] - 40, 140, 60))
        pygame.draw.rect(screen, (30, 200, 255), (cp[0] - 58, cp[1] - 32, 116, 36))
        rc = sp(RADAR)
        pygame.draw.circle(screen, (10, 40, 20), rc, 100)
        pygame.draw.circle(screen, (40, 200, 80), rc, 100, 3)
        pygame.draw.circle(screen, (40, 200, 80), rc, 50, 1)
        sweep = V(100, 0).rotate((g["t"] * 90) % 360)
        pygame.draw.line(screen, (40, 220, 90), rc, (int(rc[0] + sweep.x), int(rc[1] + sweep.y)), 2)
        blip = V(((g["t"] * 12) % 180) - 90, -30)
        if blip.length() < 95:
            pygame.draw.circle(screen, (255, 70, 70), (int(rc[0] + blip.x), int(rc[1] + blip.y)), 6)
    for chs in g["caves"][mode]["chests"]:
        if chs["got"]:
            continue
        cx, cy = sp(chs["p"])
        if chs["kind"] == "molo":
            pygame.draw.rect(screen, (110, 35, 30), (cx - 25, cy - 18, 50, 36))
            pygame.draw.rect(screen, (255, 140, 30), (cx - 25, cy - 4, 50, 8))
            pygame.draw.circle(screen, (255, 200, 60), (cx, cy - 24), 6)
        elif chs["kind"] == "med":
            pygame.draw.rect(screen, (235, 235, 240), (cx - 25, cy - 18, 50, 36))
            pygame.draw.rect(screen, (210, 40, 40), (cx - 4, cy - 14, 8, 28))
            pygame.draw.rect(screen, (210, 40, 40), (cx - 14, cy - 4, 28, 8))
        elif chs["kind"] in ("arrows", "bullets", "ammo"):
            pygame.draw.rect(screen, (50, 70, 100), (cx - 25, cy - 18, 50, 36))
            pygame.draw.rect(screen, (170, 190, 215), (cx - 25, cy - 4, 50, 8))
            pygame.draw.rect(screen, (170, 190, 215), (cx - 3, cy - 26, 6, 10))
        else:
            pygame.draw.rect(screen, (120, 80, 30), (cx - 25, cy - 18, 50, 36))
            pygame.draw.rect(screen, (230, 190, 40), (cx - 25, cy - 4, 50, 8))
    for ppos, to, spawn, key in PORTALS[mode]:
        px, py = sp(ppos)
        col = (60, 110, 200) if key in ("lab", "fwd") else (40, 160, 80)
        pygame.draw.circle(screen, col, (px, py), 45)
        text_c(font, L(PLABEL[key]), (255, 255, 255), px, py + (65 if ppos.y < 200 else -55))



def draw_entities(p, mode, cam, is_night):
    def sp(v):
        return (int(v.x - cam.x), int(v.y - cam.y))
    for dr in g["drops"]:
        if dr["mode"] != mode:
            continue
        dx, dy = sp(dr["p"])
        if -40 < dx < W + 40 and -40 < dy < H + 40:
            if dr["kind"] == "armor":
                pygame.draw.circle(screen, (60, 110, 190), (dx, dy), 20, 2)
                shape = [(dx - 12, dy - 10), (dx + 12, dy - 10), (dx + 8, dy + 12), (dx, dy + 17), (dx - 8, dy + 12)]
                pygame.draw.polygon(screen, (140, 190, 255), shape)
                pygame.draw.polygon(screen, (60, 110, 190), shape, 2)
            else:
                pygame.draw.line(screen, (200, 170, 110), (dx - 14, dy + 6), (dx + 14, dy - 6), 3)
                pygame.draw.line(screen, (200, 170, 110), (dx - 14, dy - 2), (dx + 14, dy - 14), 3)
                pygame.draw.polygon(screen, (220, 220, 230), [(dx + 14, dy - 6), (dx + 6, dy - 9), (dx + 8, dy - 1)])
                pygame.draw.polygon(screen, (220, 220, 230), [(dx + 14, dy - 14), (dx + 6, dy - 17), (dx + 8, dy - 9)])
    for fl in g["flames"]:
        fx, fy = sp(fl["p"])
        fj = int(g["t"] * 10) % 3
        pygame.draw.circle(screen, (150, 50, 10), (fx, fy), 66 + fj * 2)
        pygame.draw.circle(screen, (225, 105, 20), (fx, fy), 48 + fj * 2)
        pygame.draw.circle(screen, (255, 190, 60), (fx, fy), 26 + fj * 2)
    for en in cur_en():
        draw_enemy(en, cam)
    for en in cur_en():
        if en.get("burn", 0) > 0:
            bx, by = sp(en["p"])
            draw_burn(bx, by, 40 if en["kind"] == "boss" else (30 if en["kind"] == "miniboss" else 22))
    for pr in g["proj"]:
        a1 = sp(pr["p"])
        if pr.get("molo"):
            pygame.draw.circle(screen, (90, 50, 20), a1, 9)
            pygame.draw.circle(screen, (255, 150, 30), (a1[0], a1[1] - 5), 5)
        elif pr["v"].length() > 0:
            b1 = sp(pr["p"] - pr["v"].normalize() * 14)
            pygame.draw.line(screen, (240, 240, 240), a1, b1, 3)

    for ep in g["eproj"]:
        ex, ey = sp(ep["p"])
        pygame.draw.circle(screen, (40, 90, 30), (ex, ey), 11)
        pygame.draw.circle(screen, (140, 235, 90), (ex, ey), 7)
    pc = (W // 2, H // 2)
    w = WEAPONS[g["cur"]]
    if g["carry"]:
        pygame.draw.circle(screen, (200, 120, 160), (pc[0] + 14, pc[1] - 12), 10)
        pygame.draw.circle(screen, (240, 200, 170), (pc[0] + 14, pc[1] - 26), 7)
    if g["timmy"]:
        tpp = (int(pc[0] - g["face"].x * 32), int(pc[1] - g["face"].y * 32))
        pygame.draw.circle(screen, (60, 90, 200), tpp, 9)
        pygame.draw.circle(screen, (240, 200, 170), (tpp[0], tpp[1] - 12), 7)
    if g["swing"] > 0 and not w["ranged"]:
        end = (int(pc[0] + g["face"].x * w["rng"]), int(pc[1] + g["face"].y * w["rng"]))
        pygame.draw.line(screen, (255, 255, 255), pc, end, 5)
    pygame.draw.circle(screen, (240, 220, 180), pc, 14)
    if g["armor"] > 0:
        pygame.draw.circle(screen, (110, 170, 255), pc, 20, 3)
    pygame.draw.circle(screen, (60, 40, 20),
                       (int(pc[0] + g["face"].x * 9), int(pc[1] + g["face"].y * 9)), 4)

    # ночь (в пещерах тоже ночь, без тумана)
    if mode == -1 and is_night and gfx >= 1:
        night.set_alpha(130)
        screen.blit(night, (0, 0))
    elif mode in DARK_MODES:
        night.set_alpha(150)
        screen.blit(night, (0, 0))
        if mode in CAVE_GEO and gfx >= 1:
            lt = LIGHTS[int(g["t"] * 8) % 2]
            lw = lt.get_width() // 2
            for tq in g["caves"][mode].get("torches", []):
                tx, ty = sp(tq)
                if -lw < tx < W + lw and -lw < ty < H + lw:
                    screen.blit(lt, (tx - lw, ty - lw - 12), special_flags=pygame.BLEND_RGB_ADD)
# ===== конец части 8, ниже вставь часть 9 =====
def draw_ui(p, mode, cam, is_night, joy, knob, held, near_con):
    def sp(v):
        return (int(v.x - cam.x), int(v.y - cam.y))
    w = WEAPONS[g["cur"]]
    if g["cold"] > 40:
        pygame.draw.rect(screen, (210, 235, 255), (0, 0, W, H), int(2 + 26 * (g["cold"] - 40) / 60))
    # ---------- интерфейс ----------
    if joy is not None and knob is not None:
        o = joy["o"]
        pygame.draw.circle(screen, (200, 200, 200), (int(o.x), int(o.y)), JR, 3)
        pygame.draw.circle(screen, (150, 150, 150), (int(knob.x), int(knob.y)), int(JR * 0.45))
        pygame.draw.circle(screen, (230, 230, 230), (int(knob.x), int(knob.y)), int(JR * 0.45), 3)
    else:
        pygame.draw.circle(screen, (90, 90, 90), (int(PAD.x), int(PAD.y)), JR, 3)
        pygame.draw.circle(screen, (70, 70, 70), (int(PAD.x), int(PAD.y)), int(JR * 0.45))

    for name in BTN:
        c, r = BTN[name]
        col = (130, 130, 130) if name in held else (70, 70, 70)
        if name == "mo" and g["molo"] <= 0:
            col = (55, 40, 40)
        pygame.draw.circle(screen, col, (int(c.x), int(c.y)), int(r))
        pygame.draw.circle(screen, (210, 210, 210), (int(c.x), int(c.y)), int(r), 3)
        if name == "mo":
            fh0 = font.get_height()
            text_c(font, T("mo"), (255, 230, 200), c.x, c.y - fh0 * 0.4)
            text_c(font, "x%d" % g["molo"], (255, 200, 80), c.x, c.y + fh0 * 0.6)
        else:
            text_c(font, T(name), (255, 255, 255), c.x, c.y)

    # кнопка паузы
    pygame.draw.circle(screen, (60, 60, 60), PC, PR)
    pygame.draw.circle(screen, (210, 210, 210), PC, PR, 3)
    pygame.draw.rect(screen, (255, 255, 255), (PC[0] - 12, PC[1] - 16, 9, 32))
    pygame.draw.rect(screen, (255, 255, 255), (PC[0] + 3, PC[1] - 16, 9, 32))
    if show_fps:
        screen.blit(font.render("FPS %d" % int(clock.get_fps()), True, (255, 255, 120)),
                    (W - 190, PC[1] + PR + 10))

    pygame.draw.rect(screen, (80, 0, 0), (10, 10, 220, 20))
    pygame.draw.rect(screen, (220, 30, 30), (10, 10, int(220 * g["hp"] / 100), 20))
    pygame.draw.rect(screen, (25, 35, 55), (10, 34, 220, 12))
    pygame.draw.rect(screen, (100, 170, 240), (10, 34, int(220 * g["armor"] / 100), 12))
    pygame.draw.rect(screen, (190, 210, 235), (10, 34, 220, 12), 2)
    for idx, (val, scol) in enumerate(((g["hunger"], (230, 150, 40)), (g["thirst"], (70, 150, 230)),
                                       (g["stam"], (90, 210, 90)))):
        bx0 = 10 + idx * 76
        pygame.draw.rect(screen, (30, 30, 36), (bx0 + 16, 52, 56, 12))
        pygame.draw.rect(screen, scol, (bx0 + 16, 52, int(56 * val / 100), 12))
        pygame.draw.rect(screen, (190, 200, 215), (bx0 + 16, 52, 56, 12), 2)
    pygame.draw.circle(screen, (230, 150, 40), (18, 58), 7)
    pygame.draw.rect(screen, (240, 230, 200), (14, 55, 8, 3))
    pygame.draw.polygon(screen, (70, 150, 230), [(94, 49), (87, 60), (101, 60)])
    pygame.draw.circle(screen, (70, 150, 230), (94, 61), 6)
    pygame.draw.polygon(screen, (255, 220, 60), [(172, 49), (164, 60), (170, 60), (166, 69), (177, 57), (171, 57)])
    if g["cold"] > 1:
        pygame.draw.rect(screen, (30, 40, 55), (10, 68, 220, 8))
        pygame.draw.rect(screen, (170, 220, 255), (10, 68, int(220 * g["cold"] / 100), 8))
        pygame.draw.rect(screen, (190, 210, 235), (10, 68, 220, 8), 2)
    if mode == -1:
        if on_land(p):
            place = T("island") + " | " + (T("night") if is_night else T("day"))
        else:
            place = T("ocean")
    else:
        place = L(PLACE[mode])
    line = T("hud") % (g["hp"], g["wood"], g["fire"], g["kills"])
    fh = font.get_height()
    am_txt = ""
    if w.get("ammo") == "arrows":
        am_txt = "  |  " + T("arrows") + " " + str(g["arrows"])
    elif w.get("ammo") == "bullets":
        am_txt = "  |  " + T("bullets") + " " + str(g["bullets"])
    screen.blit(font.render(line, True, (255, 255, 255)), (10, 84))
    screen.blit(font.render(L(w["name"]) + am_txt + "  |  " + place, True, (255, 255, 120)), (10, 84 + fh))
    yy2 = 84 + 2 * fh
    if g["timmy"]:
        screen.blit(font.render(T("with_timmy"), True, (120, 220, 255)), (10, yy2))
        yy2 += fh
    its = []
    if g["climb"]:
        its.append(T("it_climb"))
    if g["scuba"]:
        its.append(T("it_scuba"))
    if g["rocks"] > 0:
        its.append(T("it_rocks") % g["rocks"])
    if g["card"]:
        its.append(T("it_card"))
    if g["gold"]:
        its.append(T("it_gold"))
    if g["carry"]:
        its.append(T("it_girl"))
    if its:
        screen.blit(font.render("  |  ".join(its), True, (190, 220, 255)), (10, yy2))
        yy2 += fh
    if g["msg_t"] > 0:
        cwm = max(16, (W - 40) // max(1, font.size("n")[0]))
        for mln in textwrap.wrap(g["msg"], cwm):
            screen.blit(font.render(mln, True, (120, 255, 160)), (10, yy2 + 6))
            yy2 += fh
    if g["sharks"]:
        text_c(big, T("sharks"), (255, 80, 80), W // 2, int(H * 0.15))

    if mode == 5:
        for e in cur_en():
            if e["kind"] == "boss":
                bx = PC[0] - PR - 30 - 320
                pygame.draw.rect(screen, (60, 0, 0), (bx, 10, 320, 18))
                pygame.draw.rect(screen, (230, 80, 20), (bx, 10, max(0, int(320 * e["hp"] / e["max"])), 18))
                screen.blit(font.render(T("boss_name"), True, (255, 255, 255)), (bx, 32))

    if near_con:
        text_c(font, T("only_one"), (255, 255, 255), W // 2, int(H * 0.25))
        for rect, lk, col in ((RECT_PLANE, "save_plane", (40, 90, 160)),
                              (RECT_TIMMY, "save_timmy", (160, 90, 40))):
            pygame.draw.rect(screen, col, rect)
            pygame.draw.rect(screen, (230, 230, 230), rect, 4)
            text_c(font, T(lk), (255, 255, 255), rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)

    if mode in CAVE_GEO:
        for nt in g["caves"][mode].get("notes", []):
            if p.distance_to(nt["p"]) < 95:
                nx, ny = sp(nt["p"])
                if g["note_open"] == nt["kind"]:
                    draw_note(nt["kind"])
                else:
                    text_c(big, T("tap"), (255, 240, 150), nx, ny - 40)
                break

    if g["hp"] <= 0:
        text_c(big, T("dead"), (255, 80, 80), W // 2, H // 2)

    if g["ending"]:
        screen.fill((0, 0, 0))
        title, body = ENDINGS[g["ending"]]
        text_c(big, L(title), (255, 220, 120), W // 2, int(H * 0.25))
        cpl = max(12, (W - 60) // max(1, font.size("n")[0]))
        ty = int(H * 0.33)
        for ln in textwrap.wrap(L(body), cpl):
            text_c(font, ln, (230, 230, 230), W // 2, ty)
            ty += fh + 6
        if g["end_t"] > 1.5:
            text_c(font, T("again"), (120, 255, 160), W // 2, ty + 50)


def draw_all(p, mode, cam, is_night, joy, knob, held, near_con):
    if mode == -1:
        draw_overworld(p, mode, cam, is_night)
    else:
        draw_cave(p, mode, cam)
    draw_entities(p, mode, cam, is_night)
    draw_ui(p, mode, cam, is_night, joy, knob, held, near_con)


touches = {}
joy = None
finger_mode = False
running = True
while running:
    try:
        dt = min(clock.tick((30, 40, 60)[gfx]) / 1000, 0.05)
        downs = []
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type in (FD, FM):
                finger_mode = True
                touches.pop("m", None)
                pos = (ev.x * W, ev.y * H)
                touches[ev.finger_id] = pos
                if ev.type == FD:
                    downs.append((ev.finger_id, pos))
            elif ev.type == FU:
                touches.pop(ev.finger_id, None)
            elif not finger_mode:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    touches["m"] = ev.pos
                    downs.append(("m", ev.pos))
                elif ev.type == pygame.MOUSEMOTION and "m" in touches:
                    touches["m"] = ev.pos
                elif ev.type == pygame.MOUSEBUTTONUP:
                    touches.pop("m", None)

        update_music()
        # ---------- меню ----------
        if state == "menu":
            act = None
            for fid, pos in downs:
                for key, rect in menu_items():
                    if inrect(pos, rect):
                        act = key
            if act:
                play("click")
            if act in ("play", "new"):
                g = new_game()
                started = True
                state = "game"
                touches.clear()
                joy = None
            elif act == "continue":
                state = "game"
                touches.clear()
                joy = None
            elif act == "howto":
                state = "help"
            elif act == "settings":
                state = "settings"
            elif act == "quit":
                running = False
            draw_menu()
            pygame.display.flip()
            continue
        if state == "settings":
            hit = None
            for fid, pos in downs:
                for key, rect in settings_items():
                    if inrect(pos, rect):
                        hit = (key, pos[0] - rect[0], rect[2])
            if hit:
                key, dx, bw_ = hit
                if key == "lang":
                    LANG = "en" if LANG == "ru" else "ru"
                elif key == "sound":
                    sound_on = not sound_on
                elif key == "music":
                    if dx > bw_ * 2 // 3:
                        music_vol = min(10, music_vol + 1)
                    elif dx < bw_ // 3:
                        music_vol = max(0, music_vol - 1)
                    apply_volumes()
                elif key == "sfx":
                    if dx > bw_ * 2 // 3:
                        sfx_vol = min(10, sfx_vol + 1)
                    elif dx < bw_ // 3:
                        sfx_vol = max(0, sfx_vol - 1)
                    apply_volumes()
                elif key == "gfx":
                    gfx = (gfx + 1) % 3
                elif key == "ui":
                    ui_size = (ui_size + 1) % 3
                    apply_layout()
                elif key == "fps":
                    show_fps = not show_fps
                elif key == "back":
                    state = "menu"
                play("click")
                save_settings()
            draw_settings()
            pygame.display.flip()
            continue
        if state == "help":
            if downs:
                state = "menu"
            draw_help()
            pygame.display.flip()
            continue

        mode = g["mode"]
        near_con = (mode == 6 and not g["ending"] and g["hp"] > 0
                    and g["p"].distance_to(CONSOLE) < 110)
        if g["ending"]:
            g["end_t"] += dt

        if (g["hp"] <= 0 or (g["ending"] and g["end_t"] > 1.5)) and downs:
            g = new_game()
            touches.clear()
            joy = None
            continue

        # ---------- кнопки и джойстик ----------
        go_menu = False
        for fid, pos in downs:
            if V(pos).distance_to(PC) < PR + 15:
                go_menu = True
                break
            if g["note_open"]:
                g["note_open"] = None
                continue
            if mode in CAVE_GEO:
                tapped = False
                for nt in g["caves"][mode].get("notes", []):
                    nsp = nt["p"] - g["p"] + V(W / 2, H / 2)
                    if g["p"].distance_to(nt["p"]) < 95 and V(pos).distance_to(nsp) < 90:
                        g["note_open"] = nt["kind"]
                        tapped = True
                        break
                if tapped:
                    continue
            if near_con:
                if inrect(pos, RECT_PLANE):
                    g["ending"] = "plane"
                    g["end_t"] = 0.0
                    continue
                if inrect(pos, RECT_TIMMY):
                    g["ending"] = "timmy"
                    g["end_t"] = 0.0
                    continue
            b = ui_hit(pos)
            if b == "sw":
                i = g["owned"].index(g["cur"])
                g["cur"] = g["owned"][(i + 1) % len(g["owned"])]
                say(T("weapon") % L(WEAPONS[g["cur"]]["name"]))
                play("click")
            elif b == "mo":
                throw_molo()
            elif b is None and joy is None and pos[0] < W * 0.6:
                joy = dict(id=fid, o=V(pos))
        if go_menu:
            state = "menu"
            touches.clear()
            joy = None
            continue

        mv = V(0, 0)
        knob = None
        if joy is not None:
            if joy["id"] in touches:
                dv = V(touches[joy["id"]]) - joy["o"]
                Ld = dv.length()
                if Ld > JR:
                    joy["o"] = joy["o"] + dv.normalize() * (Ld - JR)
                    dv = V(touches[joy["id"]]) - joy["o"]
                    Ld = dv.length()
                if Ld > JR * 0.12:
                    mv = dv.normalize() * min(1.0, Ld / JR)
                knob = joy["o"] + dv
            else:
                joy = None

        held = set()
        atk = False
        for fid, pos in list(touches.items()):
            if joy is not None and fid == joy["id"]:
                continue
            b = ui_hit(pos)
            if b:
                held.add(b)
                if b == "atk":
                    atk = True

        p = g["p"]
        mode = g["mode"]

        if g["hp"] > 0 and not g["ending"]:
            if update_game(dt, mv, atk):
                continue

        # ---------- рисуем ----------
        p = g["p"]
        mode = g["mode"]
        cam = p - V(W / 2, H / 2)
        is_night = (g["day"] % 60) > 30

        draw_all(p, mode, cam, is_night, joy, knob, held, near_con)
        pygame.display.flip()
    except Exception:
        show_error()
        running = False

pygame.quit()
