bullets = []  # List to store active bullets

bullet_speed = 70.0  # You can change this value to adjust bullet speed
bullet_max_distance = 60 * 7  # Bullet disappears after 3 tile distance

class Bullet:
    def __init__(self, x, y, z, angle):
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle  # in degrees
        self.speed = bullet_speed  # Use local variable
        self.radius = 1.0  # Half of previous value (was 2.0)
        self.start_x = x
        self.start_y = y
        self.start_z = z
    def update(self):
        # Rotate trajectory by 90 degrees
        rad = math.radians(self.angle + 90)
        dx = self.speed * math.sin(rad) * (1/60.0)
        dz = self.speed * math.cos(rad) * (1/60.0)
        self.x += dx
        self.z += dz
    def has_expired(self):
        dist = math.sqrt((self.x - self.start_x)**2 + (self.y - self.start_y)**2 + (self.z - self.start_z)**2)
        return dist > bullet_max_distance
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(1.0, 0.2, 0.2)
        glutSolidSphere(self.radius, 12, 12)
        glPopMatrix()


fire_bullet = False  # Global flag for shooting

def draw_shooting_line():
    global fire_bullet
    if not shooting_mode or game_state != 'AIMING':
        return
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(180, 0, 1, 0)
    glRotatef(player_angle, 0, 1, 0)
    torso_height, leg_height = 20.0, 15.0
    hand_x = 7  # (or your desired value for X offset)
    hand_y = leg_height + 5 + torso_height - 5
    hand_z = 0
    glTranslatef(hand_x, hand_y, hand_z)
    glRotatef(-90, 0, 0, 1)
    glRotatef(90, 1, 0, 0)
    arm_height = 15.0
    glTranslatef(0, 0, 0)  # No Z offset for gun tip
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 240)
    glEnd()
    if fire_bullet:
        angle_rad = math.radians(player_angle)
        x, y, z = player_pos[0], player_pos[1], player_pos[2]
        hand_world_x = hand_x * math.cos(angle_rad) - hand_z * math.sin(angle_rad)
        hand_world_z = hand_x * math.sin(angle_rad) + hand_z * math.cos(angle_rad)
        x += hand_world_x
        y += hand_y
        z += hand_world_z
        # No Z offset for gun tip
        bullets.append(Bullet(x, y, z, player_angle))
        fire_bullet = False
    glPopMatrix()


shooting_mode = False

def draw_player_aiming():
    """Draws the player character in an aiming pose, holding a gun with one hand forward."""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(180, 0, 1, 0) # Orient player to face negative Z
    glRotatef(player_angle, 0, 1, 0)

    torso_height, head_radius, leg_height, arm_height = 20.0, 5.0, 15.0, 15.0

    # Legs (same as standing)
    glColor3f(0.1, 0.2, 0.8)
    for i in [-.8, .8]:
        glPushMatrix()
        glTranslatef(i * 4, leg_height, 0)
        glRotatef(jump_anim_leg_angle, 1, 0, 0)
        glTranslatef(0, -leg_height, 0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 2.5, 2.5, leg_height, 10, 10)
        glPopMatrix()

    # Torso
    glColor3f(0.1, 0.8, 0.2)
    glPushMatrix()
    glTranslatef(0, leg_height + 10, 0)
    glScalef(12.0, torso_height, 6.0)
    glutSolidCube(1)
    glPopMatrix()

    # Head
    glColor3f(1.0, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(0, leg_height + 5 + torso_height, 0)
    gluSphere(gluNewQuadric(), head_radius, 20, 20)
    glPopMatrix()

    # Arms
    # Left arm (forward, holding gun)
    glColor3f(1.0, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(-7, leg_height + 5 + torso_height - 5, 0)
    glRotatef(-90, 0, 0, 1)  # Forward
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 2.0, 2.0, arm_height, 10, 10)
    # Draw gun at end of arm
    glPushMatrix()
    glTranslatef(0, 0, arm_height)
    glColor3f(0.2, 0.2, 0.2)
    glScalef(1.2, 1.2, 4.0)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

    # Right arm (down)
    glColor3f(1.0, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(7, leg_height + 5 + torso_height - 5, 0)
    glRotatef(20, 0, 0, 1)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 2.0, 2.0, arm_height, 10, 10)
    glPopMatrix()

    glPopMatrix()
import sys
import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


fire_bullet = False
# --- Game Configuration & Constants ---
PLAYER_JUMP_HEIGHT = 40.0
PLAYER_JUMP_DURATION = 0.4
JUMP_DISTANCE = 150.0
ARROW_LENGTH = 75.0
TILE_SIZE = 60.0
TILE_HEIGHT = 10.0
RIVER_WIDTH = 200.0
TRAP_PULSE_SPEED = 8.0
TRAP_FUSE_TIME = 3.0
DROWN_DURATION = 2.0
BOAT_FORWARD_SPEED = 20.0
BOAT_STRAFE_SPEED = 300.0
OBSTACLE_VERTICAL_SPACING = 350.0

# --- Game State Variables ---
game_state = 'AIMING'
score = 0
player_pos = [0.0, TILE_HEIGHT / 2, 0.0]
player_angle = 0.0
arrow_angle = 0.0
autoplay_active = False

# Jump animation variables
jump_start_pos = None
jump_end_pos = None
jump_start_time = 0.0
jump_anim_arm_angle = 0.0
jump_anim_leg_angle = 0.0

# Drown animation variable
drown_start_time = 0.0

# Lists to hold all game objects
tiles = []
obstacles = []
obstacle_spawn_count = 0
tile_spawn_count = 0

# --- Camera Configuration ---
camera_offset = [0, 150, 220]

# --- Finalized Player Parts Data for Boat Pose ---
player_boat_pose = {
    "overall_pos": [0.0, 7.0, 9.0],
    "torso": {
        "pos": [0.0, 5.0, 0.0], "rot": [-45.0, 0.0, 0.0],
        "scale": [12.0, 20.0, 6.0], "color": [0.1, 0.8, 0.2]
    },
    "head": {
        "pos": [0.0, 14.0, 2.0], "rot": [0.0, 0.0, 0.0],
        "radius": 5.0, "color": [1.0, 0.8, 0.6]
    },
    "left_leg": {
        "pos": [-4.0, -9.0, 2.0], "rot": [40.0, -15.0, 0.0],
        "length": 15.0, "radius": 2.5, "color": [0.1, 0.2, 0.8]
    },
    "right_leg": {
        "pos": [4.0, -9.0, 2.0], "rot": [40.0, 15.0, 0.0],
        "length": 15.0, "radius": 2.5, "color": [0.1, 0.2, 0.8]
    },
    "left_arm": {
        "pos": [-4.0, 8.0, 1.0], "rot": [335.0, 210.0, 0.0],
        "length": 12.0, "radius": 2.0, "color": [1.0, 0.8, 0.6]
    },
    "right_arm": {
        "pos": [4.0, 8.0, 1.0], "rot": [335.0, 145.0, 0.0],
        "length": 12.0, "radius": 2.0, "color": [1.0, 0.8, 0.6]
    }
}

def reset_game():
    """Resets all game variables to their initial state."""
    global game_state, score, player_pos, player_angle, arrow_angle, tiles, obstacles, autoplay_active
    global jump_anim_arm_angle, jump_anim_leg_angle, obstacle_spawn_count, tile_spawn_count
    game_state = 'AIMING'
    score = 0
    player_pos = [0.0, TILE_HEIGHT / 2, 0.0]
    player_angle = 0.0
    arrow_angle = 0.0
    jump_anim_arm_angle = 0.0
    jump_anim_leg_angle = 0.0
    tiles.clear()
    obstacles.clear()
    obstacle_spawn_count = 0
    autoplay_active = False
    tile_spawn_count = 0
    tiles.append({
        'pos': [0, 0, 0], 'size': TILE_SIZE, 'type': 'safe',
        'color': [0.5, 0.5, 0.5], 'origin_x': 0
    })
    generate_new_tile()
    generate_new_tile()
    generate_new_tile()


def generate_new_tile():
    """Generates a new tile."""
    global tiles, score, tile_spawn_count

    if score == 5:
        tiles.append({
            'pos': [0, 0, tiles[-1]['pos'][2] - JUMP_DISTANCE], 'size': TILE_SIZE * 1.5,
            'type': 'boat_dock', 'color': [0.4, 0.2, 0.0], 'origin_x': 0
        })
        return

    last_tile_pos = tiles[-1]['pos']
    tile_spawn_count += 1
    
    new_pos_z = last_tile_pos[2] - JUMP_DISTANCE
    
    if tile_spawn_count % 2 == 0:
        new_pos_x = last_tile_pos[0]
    else:
        random_angle_deg = random.uniform(-40, 40)
        angle_rad = math.radians(random_angle_deg)
        new_pos_x = last_tile_pos[0] - JUMP_DISTANCE * math.sin(angle_rad)

    new_pos_x = max(-RIVER_WIDTH + TILE_SIZE/2, min(RIVER_WIDTH - TILE_SIZE/2, new_pos_x))
    new_pos = [new_pos_x, 0, new_pos_z]

    tile_type = 'safe'
    color = [0.7, 0.5, 0.2]

    trap_chance = max(0, (score - 15) * 0.025) 
    moving_chance = max(0, (score - 5) * 0.04)
    coconut_chance = max(0, (score - 5) * 0.08)
    rand_choice = random.random()

    # Check last 4 tiles for coconut type
    recent_coconut = any(t['type'] == 'coconut' for t in tiles[-4:])

    if rand_choice < trap_chance and tiles[-1]['type'] != 'trap':
        tile_type = 'trap'
        color = [0.0, 0.8, 1.0]
    elif rand_choice < trap_chance + moving_chance:
        tile_type = 'moving'
        color = [0.0, 0.8, 1.0]
    elif rand_choice < trap_chance + moving_chance + coconut_chance and not recent_coconut:
        tile_type = 'coconut'
        color = [0.7, 0.5, 0.2]  # brownish color for coconut tile

    new_tile = {'pos': new_pos, 'size': TILE_SIZE, 'type': tile_type, 'color': color, 'origin_x': new_pos_x, 'player_on_tile': False}

    if tile_type == 'moving':
        # Reduce move_speed to slow down moving tiles
        new_tile.update({'move_dir': random.choice([-1, 1]), 'move_range': random.uniform(40, 80), 'move_speed': 10 + (score * 0.3)})
    if tile_type == 'trap':
        new_tile.update({'is_active': False, 'pulse_start_time': 0})
    if tile_type == 'coconut':
        new_tile['tree_shot'] = False

    tiles.append(new_tile)
    if len(tiles) > 7:
        tiles.pop(0)

def generate_new_obstacle():
    """Generates a new obstacle in a fair, sequential path."""
    global obstacles, obstacle_spawn_count
    last_pos = [0, 0, player_pos[2] - 800]
    if obstacles:
        last_pos = obstacles[-1]['pos']

    new_z = last_pos[2] - OBSTACLE_VERTICAL_SPACING
    obstacle_spawn_count += 1
    
    if obstacle_spawn_count % 2 == 0:
        new_x = last_pos[0]
    else:
        new_x = last_pos[0] + random.uniform(-120, 120)

    new_x = max(-RIVER_WIDTH + 50, min(RIVER_WIDTH - 50, new_x))
    obstacles.append({'pos': [new_x, 0, new_z], 'size': random.uniform(40, 60), 'passed': False})


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draws text on the screen."""
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player_standing():
    """Draws the standing/jumping player character."""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(180, 0, 1, 0) # Orient player to face negative Z
    glRotatef(player_angle, 0, 1, 0)

    torso_height, head_radius, leg_height, arm_height = 20.0, 5.0, 15.0, 15.0

    glColor3f(0.1, 0.2, 0.8)
    for i in [-.8, .8]:
        glPushMatrix()
        glTranslatef(i * 4, leg_height, 0)
        glRotatef(jump_anim_leg_angle, 1, 0, 0)
        glTranslatef(0, -leg_height, 0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 2.5, 2.5, leg_height, 10, 10)
        glPopMatrix()

    glColor3f(0.1, 0.8, 0.2)
    glPushMatrix()
    glTranslatef(0, leg_height + 10, 0)
    glScalef(12.0, torso_height, 6.0)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(1.0, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(0, leg_height + 5 + torso_height, 0)
    gluSphere(gluNewQuadric(), head_radius, 20, 20)
    glPopMatrix()

    glColor3f(1.0, 0.8, 0.6)
    for i in [-1, 1]:
        glPushMatrix()
        glTranslatef(i * 7, leg_height + 5 + torso_height - 5, 0)
        if game_state == 'DROWNING':
            glRotatef(-160, 1, 0, 0)
        else:
            glRotatef(i * jump_anim_arm_angle, 0, 0, 1)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 2.0, 2.0, arm_height, 10, 10)
        glPopMatrix()
    glPopMatrix()

def draw_player_sitting(boat_pos):
    """Draws the modular player character in the final sitting pose."""
    glPushMatrix()
    glTranslatef(boat_pos[0] + player_boat_pose["overall_pos"][0],
                 boat_pos[1] + player_boat_pose["overall_pos"][1],
                 boat_pos[2] + player_boat_pose["overall_pos"][2])
    glRotatef(180, 0, 1, 0) # Orient player to face negative Z
    
    # --- Draw Torso ---
    part = player_boat_pose["torso"]
    glColor3fv(part["color"])
    glPushMatrix()
    glTranslatef(part["pos"][0], part["pos"][1], part["pos"][2])
    glRotatef(part["rot"][0], 1, 0, 0)
    glRotatef(part["rot"][1], 0, 1, 0)
    glRotatef(part["rot"][2], 0, 0, 1)
    glScalef(part["scale"][0], part["scale"][1], part["scale"][2])
    glutSolidCube(1)
    glPopMatrix()

    # --- Draw Head (relative to torso) ---
    head = player_boat_pose["head"]
    glColor3fv(head["color"])
    glPushMatrix()
    glTranslatef(part["pos"][0], part["pos"][1], part["pos"][2])
    glRotatef(part["rot"][0], 1, 0, 0)
    glRotatef(part["rot"][1], 0, 1, 0)
    glRotatef(part["rot"][2], 0, 0, 1)
    glTranslatef(head["pos"][0], head["pos"][1], head["pos"][2])
    glRotatef(head["rot"][0], 1, 0, 0)
    glRotatef(head["rot"][1], 0, 1, 0)
    glRotatef(head["rot"][2], 0, 0, 1)
    glutSolidSphere(head["radius"], 20, 20)
    glPopMatrix()

    # --- Draw Limbs (relative to torso) ---
    for name in ["left_leg", "right_leg", "left_arm", "right_arm"]:
        limb = player_boat_pose[name]
        glColor3fv(limb["color"])
        glPushMatrix()
        glTranslatef(part["pos"][0], part["pos"][1], part["pos"][2])
        glRotatef(part["rot"][0], 1, 0, 0)
        glRotatef(part["rot"][1], 0, 1, 0)
        glRotatef(part["rot"][2], 0, 0, 1)
        glTranslatef(limb["pos"][0], limb["pos"][1], limb["pos"][2])
        glRotatef(limb["rot"][0], 1, 0, 0)
        glRotatef(limb["rot"][1], 0, 1, 0)
        glRotatef(limb["rot"][2], 0, 0, 1)
        gluCylinder(gluNewQuadric(), limb["radius"], limb["radius"], limb["length"], 10, 10)
        glPopMatrix()

    glPopMatrix()

def draw_boat():
    """Draws a hollow boat with wall thickness."""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1]+10, player_pos[2])
    
    glColor3f(0.4, 0.2, 0.0)

    outer_radius, inner_radius, length, segments = 15.0, 13.0, 60.0, 20

    for radius, color in [(outer_radius, [0.4, 0.2, 0.0]), (inner_radius, [0.3, 0.15, 0.0])]:
        glColor3fv(color)
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = math.pi * (i / segments) + math.pi
            y, x = radius * math.sin(angle), radius * math.cos(angle)
            glVertex3f(x, y, length / 2)
            glVertex3f(x, y, -length / 2)
        glEnd()

    glColor3f(0.45, 0.25, 0.05)
    for z in [-length/2, length/2]:
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = math.pi * (i/segments)
            if angle >= 0:
                ox, oy = outer_radius * math.cos(angle), outer_radius * math.sin(angle)
                ix, iy = inner_radius * math.cos(angle), inner_radius * math.sin(angle)
                glVertex3f(ox, 0, z)
                glVertex3f(ix, 0, z)
        glEnd()

    for z_offset in [-length / 2, length / 2]:
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = math.pi * (i / segments) + math.pi
            outer_y, outer_x = outer_radius * math.sin(angle), outer_radius * math.cos(angle)
            inner_y, inner_x = inner_radius * math.sin(angle), inner_radius * math.cos(angle)
            glVertex3f(outer_x, outer_y, z_offset)
            glVertex3f(inner_x, inner_y, z_offset)
        glEnd()
    
    glPopMatrix()

def draw_shot_coconut():
    """Draws a single coconut (used for shot coconut)."""
    glColor3f(0.35, 0.18, 0.07)
    glutSolidSphere(0.30, 12, 12)


def draw_tree(tile=None):
    glPushMatrix()
    scale = 20.0
    glScalef(scale, scale, scale)
    # If tree is shot, draw coconut lower than the others, unless player is on this tile
    if tile and tile.get('tree_shot', False) and not tile.get('player_on_tile', False):
        glPushMatrix()
        glTranslatef(-1.2, 1, 2)  # Lower than the coconuts in the leaves
        draw_shot_coconut()
        glPopMatrix()
    glPushMatrix()
    glColor3f(0.55, 0.27, 0.07)
    trunk = gluNewQuadric()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(trunk, 0.2, 0.15, 3.5, 20, 20)
    glPopMatrix()
    glColor3f(0.0, 0.8, 0.0)
    glPushMatrix()
    glTranslatef(0.0, 3.5, 0.0)
    leaf_length = 1.2
    leaf_width = 0.6
    leaf_angle = 45
    for i in range(4):
        angle_deg = i * 90.0
        glPushMatrix()
        glRotatef(angle_deg, 0, 1, 0)
        glRotatef(leaf_angle, 1, 0, 0)
        if i == 0:
            # Only draw coconut if tree not shot and player not on tile
            if not (tile and tile.get('tree_shot', False)) and not (tile and tile.get('player_on_tile', False)):
                glPushMatrix()
                glTranslatef(0, -0.02, 0.6)
                draw_shot_coconut()
                glPopMatrix()
        else:
            glPushMatrix()
            glTranslatef(0, -0.02, 0.6)
            glColor3f(0.35, 0.18, 0.07)
            glutSolidSphere(0.30, 12, 12)
            glPopMatrix()
        glColor3f(0.0, 0.8, 0.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, 0)
        glVertex3f(leaf_width, 0.7, leaf_length)
        glVertex3f(-leaf_width, 0.7, leaf_length)
        glEnd()
        glPopMatrix()
    glColor3f(0.0, 0.8, 0.0)
    glPushMatrix()
    glRotatef(leaf_angle, 1, 0, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(leaf_width, 0.7, leaf_length)
    glVertex3f(-leaf_width, 0.7, leaf_length)
    glEnd()
    glPopMatrix()
    glColor3f(0.0, 0.8, 0.0)
    glPushMatrix()
    glRotatef(-leaf_angle, 1, 0, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(leaf_width, 0.7, -leaf_length)
    glVertex3f(-leaf_width, 0.7, -leaf_length)
    glEnd()
    glPopMatrix()
    glColor3f(0.0, 0.8, 0.0)
    glPushMatrix()
    glRotatef(-leaf_angle, 0, 0, 1)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(leaf_length, 0.7, leaf_width)
    glVertex3f(leaf_length, 0.7, -leaf_width)
    glEnd()
    glPopMatrix()
    glColor3f(0.0, 0.8, 0.0)
    glPushMatrix()
    glRotatef(leaf_angle, 0, 0, 1)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(-leaf_length, 0.7, leaf_width)
    glVertex3f(-leaf_length, 0.7, -leaf_width)
    glEnd()
    glPopMatrix()
    glPopMatrix()
    glPopMatrix()

def draw_obstacles():
    """Draws all obstacles in boat mode."""
    glColor3f(0.3, 0.3, 0.3)
    for obstacle in obstacles:
        glPushMatrix()
        glTranslatef(obstacle['pos'][0], obstacle['size']/2 - TILE_HEIGHT/2, obstacle['pos'][2])
        glScalef(obstacle['size'], obstacle['size'], obstacle['size'])
        glutSolidCube(1)
        glPopMatrix()


def draw_tiles_with_outlines():
    """Draws all tiles with a manually drawn black outline."""
    for tile in tiles:
        glPushMatrix()
        glTranslatef(tile['pos'][0], tile['pos'][1], tile['pos'][2])

        glColor3fv(tile['color'])
        glPushMatrix()
        glScalef(tile['size'], TILE_HEIGHT, tile['size'])
        glutSolidCube(1)
        glPopMatrix()

        # Draw tree if tile is coconut
        if tile['type'] == 'coconut':
            glPushMatrix()
            # Move tree to the right side, but not to the edge
            tree_offset = tile['size'] * 0.35  # 0.5 would be edge, 0.35 is safe
            glTranslatef(tree_offset, TILE_HEIGHT/2, 0)
            draw_tree(tile)
            glPopMatrix()
            # Removed draw_shot_coconut_fallen; coconut at center no longer drawn

        glColor3f(0.0, 0.0, 0.0)
        s, h = tile['size'] / 2.0, TILE_HEIGHT / 2.0
        glBegin(GL_LINES)
        verts = [(-s,h,-s), (s,h,-s), (s,h,s), (-s,h,s), (-s,-h,-s), (s,-h,-s), (s,-h,s), (-s,-h,s)]
        edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
        for edge in edges:
            for vertex in edge:
                glVertex3fv(verts[vertex])
        glEnd()
        glPopMatrix()


def draw_aiming_arrow():
    """Draws the arrow used to aim the jump."""
    global shooting_mode
    if game_state != 'AIMING' or autoplay_active or shooting_mode: return
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1] + 1, player_pos[2])
    glRotatef(arrow_angle, 0, 1, 0)
    glColor3f(1.0, 1.0, 0.0)
    glBegin(GL_LINES); glVertex3f(0,0,0); glVertex3f(0,0,-ARROW_LENGTH); glEnd()
    glBegin(GL_TRIANGLES); glVertex3f(-5,0,-ARROW_LENGTH); glVertex3f(5,0,-ARROW_LENGTH); glVertex3f(0,0,-ARROW_LENGTH-10); glEnd()
    glPopMatrix()

def draw_environment():
    """Draws the endless, player-relative environment."""
    z_near = player_pos[2] + 500
    z_far = player_pos[2] - 5000
    glColor3f(0.2, 0.5, 0.9)
    glBegin(GL_QUADS); glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2,z_near); glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2,z_near); glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2,z_far); glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2,z_far); glEnd()
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES); glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2+1,z_near); glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2+1,z_far); glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2+1,z_near); glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2+1,z_far); glEnd()
    glColor3f(0.1, 0.7, 0.2)
    glBegin(GL_QUADS); glVertex3f(-RIVER_WIDTH-1000,-TILE_HEIGHT/2,z_near); glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2,z_near); glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2,z_far); glVertex3f(-RIVER_WIDTH-1000,-TILE_HEIGHT/2,z_far); glEnd()
    glBegin(GL_QUADS); glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2,z_near); glVertex3f(RIVER_WIDTH+1000,-TILE_HEIGHT/2,z_near); glVertex3f(RIVER_WIDTH+1000,-TILE_HEIGHT/2,z_far); glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2,z_far); glEnd()

def draw_axes():
    """Draws X, Y, Z axis lines at the origin."""
    glBegin(GL_LINES)
    glColor3f(1,0,0); glVertex3f(0,0,0); glVertex3f(100,0,0)
    glColor3f(0,1,0); glVertex3f(0,0,0); glVertex3f(0,100,0)
    glColor3f(0,0,1); glVertex3f(0,0,0); glVertex3f(0,0,100)
    glEnd()


def keyboardListener(key, x, y):
    """Handles keyboard inputs."""
    global arrow_angle, player_angle, player_pos, autoplay_active, shooting_mode
    if key == b'p':
        autoplay_active = not autoplay_active
        if autoplay_active:
            global shooting_mode
            shooting_mode = False
    if key == b'x' and game_state == 'AIMING':
        shooting_mode = not shooting_mode
    if not autoplay_active:
        if game_state == 'AIMING':
            if key == b'a': arrow_angle += 1.0
            if key == b'd': arrow_angle -= 1.0
            player_angle = arrow_angle
        elif game_state == 'BOAT_MODE':
            if key == b'a': player_pos[0] -= BOAT_STRAFE_SPEED * (1/60.0)
            if key == b'd': player_pos[0] += BOAT_STRAFE_SPEED * (1/60.0)
            player_pos[0] = max(-RIVER_WIDTH + 25, min(RIVER_WIDTH - 25, player_pos[0]))
    if key == b'r' and game_state == 'GAME_OVER': reset_game()
player_aiming_mode = False

def mouseListener(button, state, x, y):
    global fire_bullet
    """Handles mouse inputs for jumping."""
    global game_state, jump_start_pos, jump_end_pos, jump_start_time, player_angle, shooting_mode
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and game_state == 'AIMING' and not autoplay_active:
        if shooting_mode:
            fire_bullet = True
            return
        current_tile_index = -1
        for i, tile in enumerate(tiles):
            if math.isclose(tile['pos'][0], player_pos[0], abs_tol=0.1) and \
               math.isclose(tile['pos'][2], player_pos[2], abs_tol=0.1):
                current_tile_index = i
                break
        if current_tile_index != -1 and current_tile_index + 1 < len(tiles):
            game_state = 'JUMPING'
            jump_start_pos = list(player_pos)
            target_tile = tiles[current_tile_index + 1]
            dx_target = target_tile['pos'][0] - player_pos[0]
            dz_target = target_tile['pos'][2] - player_pos[2]
            actual_dist_to_tile = math.sqrt(dx_target**2 + dz_target**2)
            angle_rad = math.radians(arrow_angle)
            jump_end_pos = [player_pos[0] - actual_dist_to_tile*math.sin(angle_rad), player_pos[1], player_pos[2] - actual_dist_to_tile*math.cos(angle_rad)]
            player_angle = arrow_angle
            jump_start_time = time.time()

def setupCamera():
    """Configures the camera's projection and view settings."""
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluPerspective(55,(1000/800),0.1,5000)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    cam_x = 0 + camera_offset[0]
    cam_y = player_pos[1] + camera_offset[1]
    cam_z = player_pos[2] + camera_offset[2]
    look_at_x, look_at_y, look_at_z = 0, player_pos[1], player_pos[2]
    gluLookAt(cam_x, cam_y, cam_z, look_at_x, look_at_y, look_at_z, 0, 1, 0)

def update_bullet_coconut_collision():
    for tile in tiles:
        if tile['type'] == 'coconut' and not tile.get('tree_shot', False):
            tree_offset = tile['size'] * 0.35
            trunk_x = tile['pos'][0] + tree_offset
            trunk_z = tile['pos'][2]
            trunk_y_min = tile['pos'][1] + TILE_HEIGHT/2
            trunk_y_max = trunk_y_min + 20  # approximate trunk height
            for bullet in bullets[:]:
                dist_xz = math.sqrt((bullet.x - trunk_x)**2 + (bullet.z - trunk_z)**2)
                if dist_xz < 20 and trunk_y_min <= bullet.y <= trunk_y_max + 20:
                    print("shot")
                    bullets.remove(bullet)
                    tile['tree_shot'] = True
                    break

def update_game_state():
    """Main logic update function."""
    global game_state, player_pos, score, jump_anim_arm_angle, jump_anim_leg_angle, drown_start_time
    global obstacles, arrow_angle, player_angle, jump_start_pos, jump_end_pos, jump_start_time
    global bullets  # added for bullet updates

    # --- Update bullets ---
    for bullet in bullets:
        bullet.update()
    bullets = [b for b in bullets if not b.has_expired()]
    update_bullet_coconut_collision()

    # --- Autoplay / AIMING logic ---
    if autoplay_active:
        if game_state == 'AIMING' and len(tiles) > 1:
            current_tile_index = next(
                (i for i, t in enumerate(tiles) if math.isclose(t['pos'][0], player_pos[0]) 
                 and math.isclose(t['pos'][2], player_pos[2])), -1)
            if current_tile_index != -1 and current_tile_index + 1 < len(tiles):
                target_tile = tiles[current_tile_index + 1]
                target_pos_x = target_tile['pos'][0]
                if target_tile['type'] == 'moving':
                    sim_pos, sim_dir = target_tile['pos'][0], target_tile['move_dir']
                    for _ in range(int(PLAYER_JUMP_DURATION * 60)):
                        sim_pos += target_tile['move_speed'] * sim_dir * (1/60.0)
                        if not (-RIVER_WIDTH < sim_pos - target_tile['size']/2 and sim_pos + target_tile['size']/2 < RIVER_WIDTH):
                            sim_dir *= -1
                    target_pos_x = sim_pos
                dx, dz = target_pos_x - player_pos[0], target_tile['pos'][2] - player_pos[2]
                target_angle_rad = math.atan2(-dx, -dz)
                target_angle_deg = math.degrees(target_angle_rad)
                angle_diff = (target_angle_deg - arrow_angle + 180) % 360 - 180
                arrow_angle += angle_diff * 0.15
                player_angle = arrow_angle
                if abs(angle_diff) < 1.0:
                    game_state = 'JUMPING'
                    jump_start_pos = list(player_pos)
                    jump_end_pos = [target_tile['pos'][0], player_pos[1], target_tile['pos'][2]]
                    jump_start_time = time.time()
        elif game_state == 'BOAT_MODE':
            closest_obs = min(
                [obs for obs in obstacles if obs['pos'][2] < player_pos[2]], 
                key=lambda o: player_pos[2]-o['pos'][2], default=None)
            if closest_obs and player_pos[2] - closest_obs['pos'][2] < 600:
                player_pos[0] += -BOAT_STRAFE_SPEED * (1/60.0) if player_pos[0] < closest_obs['pos'][0] else BOAT_STRAFE_SPEED * (1/60.0)
                player_pos[0] = max(-RIVER_WIDTH+25, min(RIVER_WIDTH-25, player_pos[0]))

    # --- Trap tile updates ---
    if game_state not in ['BOAT_MODE', 'GAME_OVER']:
        for tile in tiles:
            if tile.get('is_active'):
                elapsed = time.time() - tile['pulse_start_time']
                if elapsed > TRAP_FUSE_TIME and game_state == 'AIMING' and abs(player_pos[0]-tile['pos'][0]) < tile['size']/2 and abs(player_pos[2]-tile['pos'][2]) < tile['size']/2:
                    game_state = 'GAME_OVER'
                    return
                tile['color'] = [
                    1.0, 
                    0.5 * (0.5 + 0.5 * math.sin(elapsed * TRAP_PULSE_SPEED)), 
                    0.5 * (0.5 + 0.5 * math.sin(elapsed * TRAP_PULSE_SPEED))
                ]

    # --- Jumping logic ---
    if game_state == 'JUMPING':
        progress = min((time.time() - jump_start_time) / PLAYER_JUMP_DURATION, 1.0)
        player_pos[0] = (1 - progress) * jump_start_pos[0] + progress * jump_end_pos[0]
        player_pos[2] = (1 - progress) * jump_start_pos[2] + progress * jump_end_pos[2]
        player_pos[1] = jump_start_pos[1] + (4 * (progress - progress**2)) * PLAYER_JUMP_HEIGHT
        jump_anim_arm_angle = 90 * math.sin(progress * math.pi)
        jump_anim_leg_angle = -45 * math.sin(progress * math.pi)
        if progress >= 1.0:
            game_state = 'LANDED'
            jump_anim_arm_angle, jump_anim_leg_angle = 0.0, 0.0

    # --- Landed logic ---
    elif game_state == 'LANDED':
        landed_safely = False
        for tile in tiles:
            # Set player_on_tile True only for the tile the player is on, False for others
            if abs(player_pos[0]-tile['pos'][0]) < tile['size']/2 and abs(player_pos[2]-tile['pos'][2]) < tile['size']/2:
                landed_safely = True
                player_pos[0], player_pos[2], player_pos[1] = tile['pos'][0], tile['pos'][2], TILE_HEIGHT/2
                tile['player_on_tile'] = True
                if tile['type'] == 'boat_dock':
                    game_state = 'BOAT_MODE'
                    player_pos[1] = 0.0
                    tiles.clear()
                    return
                if tile['type'] == 'moving':
                    tile['type'] = 'safe'
                    tile['color'] = [0.5, 0.5, 0.5]
                if tile['type'] == 'trap' and not tile.get('is_active'):
                    tile['is_active'] = True
                    tile['pulse_start_time'] = time.time()
                if not tile.get('is_active'):
                    # If landed on a shot coconut tile, score 5 instead of 1
                    if tile['type'] == 'coconut' and tile.get('tree_shot', False):
                        score += 5
                    else:
                        score += 1
                    generate_new_tile()
                game_state = 'AIMING'
                break
            else:
                tile['player_on_tile'] = False
        if not landed_safely:
            game_state = 'DROWNING' if abs(player_pos[0]) < RIVER_WIDTH else 'GAME_OVER'
            if game_state == 'DROWNING':
                drown_start_time = time.time()

    # --- Drowning logic ---
    elif game_state == 'DROWNING':
        if time.time() - drown_start_time > DROWN_DURATION:
            game_state = 'GAME_OVER'
        else:
            player_pos[1] -= 20 * (1/60.0)

    # --- Moving tile updates ---
    if game_state != 'BOAT_MODE':
        for tile in tiles:
            if tile['type'] == 'moving':
                tile['pos'][0] += tile['move_speed'] * tile['move_dir'] * (1/60.0)
                if not (-RIVER_WIDTH < tile['pos'][0]-tile['size']/2 and tile['pos'][0]+tile['size']/2 < RIVER_WIDTH):
                    tile['move_dir'] *= -1

    # --- Boat mode logic ---
    if game_state == 'BOAT_MODE':
        player_pos[2] -= BOAT_FORWARD_SPEED * (1/60.0)
        player_angle = 0
        if not obstacles or obstacles[-1]['pos'][2] > player_pos[2] - OBSTACLE_VERTICAL_SPACING:
            generate_new_obstacle()
        for obs in obstacles:
            if abs(player_pos[0]-obs['pos'][0]) < 25 + obs['size']/2 and abs(player_pos[2]-obs['pos'][2]) < 50 + obs['size']/2:
                game_state = 'GAME_OVER'
                return
            if not obs['passed'] and obs['pos'][2] > player_pos[2]:
                obs['passed'] = True
                score += 1
        obstacles[:] = [obs for obs in obstacles if obs['pos'][2] < player_pos[2] + 200]


def idle():
    """Idle function that runs continuously."""
    update_game_state()
    glutPostRedisplay()


def showScreen():
    """Display function to render the entire game scene."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity(); glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_axes()
    draw_environment()
    if game_state == 'BOAT_MODE':
        draw_boat(); draw_obstacles(); draw_player_sitting(player_pos)
    else:
        draw_tiles_with_outlines()
        if shooting_mode:
            draw_player_aiming()
            draw_shooting_line()
            # Draw bullets after player body and gun
            for bullet in bullets:
                bullet.draw()
        else:
            draw_aiming_arrow()
            draw_player_standing()
            # Draw bullets after player body
            for bullet in bullets:
                bullet.draw()
    draw_text(10, 770, f"Score: {score}")
    draw_text(10, 740, f"Cam Offset (x,y,z): {camera_offset}")
    draw_text(10, 710, f"Autoplay: {'ON' if autoplay_active else 'OFF'}")
    if game_state == 'GAME_OVER':
        draw_text(400, 400, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(380, 360, f"Final Score: {score}")
        draw_text(390, 320, "Press 'R' to Restart")
    glutSwapBuffers()


def main():
    """Main function to set up OpenGL window and loop."""
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"Island Jumper")
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glEnable(GL_DEPTH_TEST)
    reset_game()
    glutMainLoop()

if __name__ == "__main__":
    main()