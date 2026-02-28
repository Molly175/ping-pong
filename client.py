from multiprocessing.util import is_exiting

from pygame import *
import socket, json
from threading import Thread
from CTkFile import MainWindow
from time import sleep
from math import ceil

WIDTH, HEIGHT = 800, 600
init()
mixer.init()

SCENE_MAIN = "main_menu"
SCENE_GAME = "game"
SCENE_SETTING = "setting"
SCENE_PAUSE = "pause"
SCENE_SHOP = "shop"
scene = SCENE_MAIN
app = None
with open("data.json", "r") as f:
    data = json.load(f)
    name = data["name"]
selected_color = (0, 255, 0)
colors_shop = [
    ((255,0,0), "red"),((0,255,0), "green"),((0,0,255), "blue"),
    ((255,255,0), "yellow"),((255,0,255), "pink"),((0,255,255), "cyan")
]

screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Ping-Pong")

def draw_button(text, x, y, w, h):
    rect = Rect(x, y, w, h)
    draw.rect(screen, (70,70,70), rect)
    draw.rect(screen, (255,255,255), rect, 2)
    t = font_main.render(text, True, (255,255,255))
    screen.blit(t, (x + w//2 - t.get_width()//2, y + h//2 - t.get_height()//2))
    return rect
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            with open("data.json", "r") as f:
                data = json.load(f)
            custom_data = {
                "color": data["platform_color"]
            }
            client.send((json.dumps(custom_data) + "\n").encode())
            return my_id, game_state, buffer, client
        except (ConnectionRefusedError, ConnectionAbortedError):
            print("Server not running")
            exit()
def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

font_win = font.Font(None, 72)
font_main = font.Font(None, 36)

wall_hit = mixer.Sound("wall_hit.wav")
plat_hit = mixer.Sound("plat_hit.wav")
plat_hit.set_volume(0.5)

game_bg = image.load("game_bg.png")

game_over = False
winner = None
you_winner = None

def main_scene():
    global scene
    clock.tick(60)
    screen.fill((15, 15, 30))

    title = font_win.render("PING-PONG", True, (255, 255, 255))
    title_rect = title.get_rect(center=(WIDTH//2, 100))
    screen.blit(title, title_rect)

    play_btn = draw_button("Play", WIDTH // 2 - 100, 250, 200, 50)
    shop_btn = draw_button("Shop", WIDTH // 2 - 100, 320, 200, 50)
    sett_btn = draw_button("Settings", WIDTH // 2 - 100, 390, 200, 50)
    quit_btn = draw_button("Quit", WIDTH // 2 - 100, 460, 200, 50)

    if play_btn.collidepoint(mouse.get_pos()) and mouse.get_pressed()[0]:
        global my_id, game_state, buffer, client
        my_id, game_state, buffer, client = connect_to_server()
        Thread(target=receive, daemon=True).start()
        scene = SCENE_GAME
    if shop_btn.collidepoint(mouse.get_pos()) and mouse.get_pressed()[0]:
        scene = SCENE_SHOP
    if sett_btn.collidepoint(mouse.get_pos()) and mouse.get_pressed()[0]:
        scene = SCENE_SETTING
    if quit_btn.collidepoint(mouse.get_pos()) and mouse.get_pressed()[0]:
        sleep(0.1)
        exit()
def pause_scene():
    global scene
    screen.fill((20, 20, 20))
    title = font_win.render("PAUSED", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - 120, 100))

    resume_btn = draw_button("Resume", WIDTH // 2 - 100, 250, 200, 50)
    leave_btn = draw_button("Leave", WIDTH // 2 - 100, 330, 200, 50)

    if key.get_pressed()[K_ESCAPE]: scene = SCENE_GAME
    if resume_btn.collidepoint(mouse.get_pos()) and mouse.get_pressed()[0]: scene = SCENE_GAME
    if leave_btn.collidepoint(mouse.get_pos()) and mouse.get_pressed()[0]: scene = SCENE_MAIN
def shop_scene():
    global scene
    screen.fill((40, 40, 40))

    title = font_win.render("SHOP", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - 80, 50))

    x = 150
    for color in colors_shop:
        rect = Rect(x, 200, 60, 60)
        draw.rect(screen, color[0], rect)
        if rect.collidepoint(mouse.get_pos()) and mouse.get_pressed()[0]:
            selected_platform_color = color[0]
            with open("data.json", "r") as f:
                data = json.load(f)
            with open("data.json", "w") as f:
                for color_name in colors_shop:
                    if color_name[0] == selected_platform_color:
                        data["platform_color"] = color_name[1]
                        json.dump(data, f)
                        break
        with open("data.json", "r") as f:
            data = json.load(f)
        if color[1] == data["platform_color"]:
            draw.rect(screen, (255, 255, 255), rect, 5)
        x += 100

    back_btn = draw_button("Back", WIDTH // 2 - 100, 500, 200, 50)
    if back_btn.collidepoint(mouse.get_pos()) and mouse.get_pressed()[0]:
        sleep(0.1)
        scene = SCENE_MAIN
def setting_scene():
    global scene, name, app
    screen.fill((40, 40, 40))

    title = font_main.render("SETTING", True, (255, 255, 255))
    title_rect = title.get_rect(center=(WIDTH // 2, 25))
    screen.blit(title, title_rect)

    name_lbl = font_main.render(name, True, (255, 255, 255))
    name_lbl_rect = name_lbl.get_rect(center=(WIDTH // 2, 150))
    screen.blit(name_lbl, name_lbl_rect)

    edit_name = draw_button("Edit name", WIDTH // 2 - 100, 200, 200, 50)
    if edit_name.collidepoint(mouse.get_pos()) and mouse.get_pressed()[0] and app is None:
        app = MainWindow()
        app.mainloop()
        app = None
        with open("data.json", "r") as f:
            data = json.load(f)
            new_name = data["name"]
        if isinstance(new_name, str):
            name = new_name

    back_btn = draw_button("Back", WIDTH // 2 - 100, 500, 200, 50)
    if back_btn.collidepoint(mouse.get_pos()) and mouse.get_pressed()[0]:
        sleep(0.1)
        scene = SCENE_MAIN
def game_scene():
    global scene, you_winner
    if key.get_pressed()[K_ESCAPE]: scene = SCENE_PAUSE

    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.fill((0, 0, 0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        return

    if "winner" in game_state and game_state["winner"] is not None:
        screen.fill((20, 20, 20))

        if you_winner is None:
            if game_state["winner"] == my_id:
                you_winner = True
            else:
                you_winner = False

        if you_winner:
            text = "You win!"
        else:
            text = "You lose!"

        win_text = font_win.render(text, True, (255, 215, 0))
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        text = font_win.render('R - restart', True, (255, 215, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(text, text_rect)

        display.update()
        return

    if game_state:
        screen.fill((0, 0, 0))
        for y in range(ceil(HEIGHT/60)):
            for x in range(ceil(WIDTH/60)):
                screen.blit(game_bg, (x*60, y*60))
        draw.rect(screen, (0, 255, 0), (20, game_state['paddles']['0'], 20, 100))
        draw.rect(screen, (255, 0, 255), (WIDTH - 40, game_state['paddles']['1'], 20, 100))
        draw.circle(screen, (255, 255, 255), (game_state['ball']['x'], game_state['ball']['y']), 10)
        score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH // 2 -25, 20))

        if game_state['sound_event']:
            if game_state['sound_event'] == 'wall_hit':
                wall_hit.play()
            if game_state['sound_event'] == 'platform_hit':
                plat_hit.play()
    else:
        waiting_text = font_main.render(f"Waiting players...", True, (255, 255, 255))
        waiting_text_rect = waiting_text.get_rect(center=(WIDTH // 2, 25))
        screen.blit(waiting_text, waiting_text_rect)

        back_btn = draw_button("Back", WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
        if back_btn.collidepoint(mouse.get_pos()) and mouse.get_pressed()[0]:
            scene = SCENE_MAIN

    keys = key.get_pressed()
    try:
        if keys[K_w]:
            client.send(b"UP")
        elif keys[K_s]:
            client.send(b"DOWN")
    except ConnectionResetError:
        print("Connection was reset")
        exit()

while True:
    clock.tick(60)
    screen.fill((0,0,0))
    for e in event.get():
        if e.type == QUIT:
            exit()
    if scene == SCENE_MAIN:
        main_scene()
    if scene == SCENE_SHOP:
        shop_scene()
    if scene == SCENE_SETTING:
        setting_scene()
    if scene == SCENE_GAME:
        game_scene()
    if scene == SCENE_PAUSE:
        pause_scene()
    display.flip()
