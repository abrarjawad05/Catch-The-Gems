from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

win_width = 500
win_height = 800
drop_velocity = 0.001

bucket_pos_x = 0
bucket_pos_y = 50
is_paused = False
gem_pos_x = random.randint(-240, 240)
gem_pos_y = 200
gem_width = 20
gem_height = 10

game_score = 0


def draw_pixel(x, y):
    glPointSize(3)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


def draw_segment(x1, y1, x2, y2):
    zone = detect_zone(x1, y1, x2, y2)
    x1, y1, x2, y2 = convert_to_zone0(zone, x1, y1, x2, y2)
    pixels = midpoint_zone0(x1, y1, x2, y2)
    revert_zone(zone, pixels)


def midpoint_zone0(x1, y1, x2, y2):
    points = []
    dx = x2 - x1
    dy = y2 - y1
    d = dy - (dx / 2)
    x, y = int(x1), int(y1)
    points.append([x, y])

    for x in range(int(x1) + 1, int(x2) + 1):
        if d < 0:
            d += dy
        else:
            d += (dy - dx)
            y += 1
        points.append([x, y])

    return points


def detect_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx > 0 and dy >= 0:
        return 0 if abs(dx) > abs(dy) else 1
    elif dx <= 0 <= dy:
        return 3 if abs(dx) > abs(dy) else 2
    elif dx < 0 and dy < 0:
        return 4 if abs(dx) > abs(dy) else 5
    else:
        return 7 if abs(dx) > abs(dy) else 6


def convert_to_zone0(zone, x1, y1, x2, y2):
    transforms = [
        lambda x, y: (x, y),
        lambda x, y: (y, x),
        lambda x, y: (y, -x),
        lambda x, y: (-x, y),
        lambda x, y: (-x, -y),
        lambda x, y: (-y, -x),
        lambda x, y: (-y, x),
        lambda x, y: (x, -y),
    ]
    x1, y1 = transforms[zone](x1, y1)
    x2, y2 = transforms[zone](x2, y2)
    return x1, y1, x2, y2


def revert_zone(zone, points):
    transforms = [
        lambda x, y: (x, y),
        lambda x, y: (y, x),
        lambda x, y: (-y, x),
        lambda x, y: (-x, y),
        lambda x, y: (-x, -y),
        lambda x, y: (-y, -x),
        lambda x, y: (y, -x),
        lambda x, y: (x, -y),
    ]
    for x, y in points:
        draw_pixel(*transforms[zone](x, y))


def render_gem(x, y, w, h):
    draw_segment(x, y, x + w // 2, y - h)
    draw_segment(x + w // 2, y - h, x + w, y)
    draw_segment(x, y, x + w // 2, y + h)
    draw_segment(x + w // 2, y + h, x + w, y)


def game_display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 200, 0, 0, 0, 0, 1, 0)

    # Draw Gem
    global gem_pos_x, gem_pos_y
    glColor3f(0.6, 0.9, 0.95)
    render_gem(gem_pos_x, gem_pos_y, gem_width, gem_height)

    # Gem respawn if missed
    if gem_pos_y <= -250:
        gem_pos_x = random.randint(-240, 240)
        gem_pos_y = 200

    # Buttons
    glColor3f(0.98, 0.92, 0.37)
    if is_paused:
        draw_segment(-10, 225, 10, 235)
        draw_segment(10, 235, -10, 245)
        draw_segment(-10, 245, -10, 225)
    else:
        draw_segment(-4, 225, -4, 245)
        draw_segment(4, 225, 4, 245)

    glColor3f(0.44, 0.68, 0.94)
    draw_segment(-240, 235, -230, 245)
    draw_segment(-240, 235, -230, 225)
    draw_segment(-240, 235, -215, 235)

    glColor3f(0.88, 0.21, 0.21)
    draw_segment(240, 225, 220, 245)
    draw_segment(240, 245, 220, 225)

    # Catcher
    glColor3f(1.0, 1.0, 1.0)
    draw_segment(bucket_pos_x - 70, -235, bucket_pos_x + 70, -235)
    draw_segment(bucket_pos_x - 50, -250, bucket_pos_x + 50, -250)
    draw_segment(bucket_pos_x - 50, -250, bucket_pos_x - 70, -235)
    draw_segment(bucket_pos_x + 50, -250, bucket_pos_x + 70, -235)

    glutSwapBuffers()


def handle_keys(key, x, y):
    global bucket_pos_x
    move = 20
    if key == GLUT_KEY_LEFT and bucket_pos_x - 70 > -250 and not is_paused:
        bucket_pos_x -= move
    elif key == GLUT_KEY_RIGHT and bucket_pos_x + 70 < 250 and not is_paused:
        bucket_pos_x += move
    glutPostRedisplay()


def handle_mouse(button, state, x, y):
    global gem_pos_x, gem_pos_y, bucket_pos_x, is_paused, drop_velocity, game_score
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if 230 <= x <= 260 and 0 <= y <= 50:
            is_paused = not is_paused
        elif 10 <= x <= 30 and 25 <= y <= 40:
            print("Starting Over!")
            bucket_pos_x = 0
            gem_pos_x = random.randint(-240, 240)
            gem_pos_y = 200
            is_paused = False
            drop_velocity = 0.01
            game_score = 0
        elif 445 <= x <= 490 and 10 <= y <= 50:
            print("Goodbye. Final Score:", game_score)
            glutLeaveMainLoop()
    glutPostRedisplay()


def update_frame():
    global gem_pos_y, gem_pos_x, bucket_pos_x, drop_velocity, game_score, is_paused
    if not is_paused:
        gem_pos_y -= drop_velocity
        drop_velocity += 0.0001
        if bucket_pos_x - 70 <= gem_pos_x <= bucket_pos_x + 70 and gem_pos_y <= -240:
            game_score += 1
            print("Score:", game_score)
            gem_pos_x = random.randint(-240, 240)
            gem_pos_y = 200
        elif gem_pos_y <= -250:
            print("Game Over! Final Score:", game_score)
            bucket_pos_x = 0
            gem_pos_x = random.randint(-240, 240)
            gem_pos_y = 200
            drop_velocity = 0.01
            game_score = 0
            is_paused = False
    glutPostRedisplay()


def setup():
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, 1, 1, 1000.0)


glutInit()
glutInitWindowSize(win_width, win_height)
glutInitWindowPosition(500, 0)
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
glutCreateWindow(b"Catch the Diamonds")
setup()
glutDisplayFunc(game_display)
glutIdleFunc(update_frame)
glutSpecialFunc(handle_keys)
glutMouseFunc(handle_mouse)
glutMainLoop()
