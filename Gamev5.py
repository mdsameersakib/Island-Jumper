import sys
import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class Bullet:
    def __init__(self, x, y, z, angle):
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle
        self.speed = bullet_speed
        self.radius = 1.0
        self.start_x = x
        self.start_y = y
        self.start_z = z
    
    def update(self):
        rad = math.radians(self.angle)
        dx = -self.speed * math.sin(rad) * (1/60.0)
        dz = -self.speed * math.cos(rad) * (1/60.0)
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

def draw_shooting_line():
    global fire_bullet
    if not shooting_mode or game_state != 'AIMING':
        return
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(180, 0, 1, 0)
    glRotatef(player_angle, 0, 1, 0)
    torso_height, leg_height = 20.0, 15.0
    hand_x = 7
    hand_y = leg_height + 5 + torso_height - 5
    hand_z = 0
    glTranslatef(hand_x, hand_y, hand_z)
    glRotatef(-90, 0, 0, 1)
    glRotatef(90, 1, 0, 0)
    arm_height = 15.0
    glTranslatef(0, 0, 0)
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
        bullet_angle = player_angle - 90
        bullets.append(Bullet(x, y, z, bullet_angle))
        fire_bullet = False
    glPopMatrix()

def draw_player_aiming():
    """Draws the player character in an aiming pose, holding a gun with one hand forward."""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(180, 0, 1, 0)
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
    glRotatef(-90, 0, 0, 1)
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

def draw_shot_coconut():
    """Draws a single coconut (used for shot coconut)."""
    glColor3f(0.35, 0.18, 0.07)
    glutSolidSphere(0.30, 12, 12)

#Game Configuration & Constants  
PICKED_POWER_UP = False
PURPLE_TILE_ACTIVE = False
PURPLE_TILE_START_TIME = 0
PURPLE_TILE_DURATION = 5.0
MAX_PURPLE_AFFECTED_TILES = 5
PURPLE_TILE_AFFECTED_TILES = 0
PICKED_POWER_UP_ACTIVE_TILES = 0
MAX_PICKED_POWER_UP_TILES = 5

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
BOAT_FORWARD_SPEED = 300.0
BOAT_STRAFE_SPEED = 1500
OBSTACLE_VERTICAL_SPACING = 350.0

# Frenzy mode constants
frenzy_mode = False
last_jump_time = None
FRENZY_COLLAPSE_TIME = 2.0

# Tile-based progression system
tile_count = 0
current_game_mode = 0
game_modes = [
    {"name": "purple_power", "duration": 1, "description": "Purple power-up tile appears"},
    {"name": "safe", "duration": 12, "description": "Safe tiles only"},
    {"name": "moving", "duration": 8, "description": "Moving tiles introduced"},
    {"name": "mixed", "duration": 12, "description": "Mixed safe and moving tiles"},
    {"name": "frenzy", "duration": 10, "description": "Frenzy mode - yellow tiles"},
    {"name": "trap", "duration": 8, "description": "Trap tiles introduced"},
    {"name": "coconut", "duration": 10, "description": "Coconut trees"},
    {"name": "chaos", "duration": 15, "description": "All tile types mixed"}
]
mode_tiles_remaining = 0

# Game progression variables
boat_obstacles_passed = 0
boat_exit_generated = False
current_stage = "Island Jumping"

# Shooting system variables
bullets = []
bullet_speed = 70.0
bullet_max_distance = 60 * 7
fire_bullet = False
shooting_mode = False

# Boat coconut system
boat_coconuts = []
coconut_spacing = 800
boat_coconuts_spawned = 0
MAX_BOAT_COCONUTS = 10
boat_coconuts_collected = 0

#Game State Variables  
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

#Camera Configuration  
camera_offset = [0, 150, 220]

#Player Parts Data for Boat Pose  
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

def get_current_stage():
    global score, boat_obstacles_passed, current_stage
    if game_state == 'BOAT_MODE':
        current_stage = "Boat Mode"
    else:
        current_stage = "Endless Island Adventure"
    return current_stage

def reset_game():
    global last_jump_time, game_state, score, player_pos, player_angle, arrow_angle, tiles, obstacles
    global jump_anim_arm_angle, jump_anim_leg_angle, obstacle_spawn_count, tile_spawn_count
    global frenzy_mode, autoplay_active, shooting_mode, fire_bullet, bullets
    global tile_count, current_game_mode, mode_tiles_remaining
    global autoplay_active, frenzy_mode, boat_obstacles_passed, boat_exit_generated
    global shooting_mode, bullets, fire_bullet, boat_coconuts
    
    last_jump_time = None
    game_state = 'AIMING'
    score = 0
    boat_obstacles_passed = 0
    boat_exit_generated = False
    player_pos = [0.0, TILE_HEIGHT / 2, 0.0]
    player_angle = 0.0
    arrow_angle = 0.0
    jump_anim_arm_angle = 0.0
    jump_anim_leg_angle = 0.0
    frenzy_mode = False
    autoplay_active = False
    shooting_mode = False
    fire_bullet = False
    bullets.clear()
    boat_coconuts.clear()
    boat_coconuts_spawned = 0
    boat_coconuts_collected = 0
    PICKED_POWER_UP = False
    PURPLE_TILE_ACTIVE = False
    PURPLE_TILE_AFFECTED_TILES = 0
    PICKED_POWER_UP_ACTIVE_TILES = 0
    tiles.clear()
    obstacles.clear()
    obstacle_spawn_count = 0
    tile_spawn_count = 0
    tile_count = 0
    current_game_mode = 0
    mode_tiles_remaining = game_modes[0]["duration"]
    
    # Add initial tile
    tiles.append({
        'pos': [0, 0, 0], 'size': TILE_SIZE, 'type': 'safe',
        'color': [0.5, 0.5, 0.5], 'origin_x': 0, 'player_on_tile': False
    })
    
    # Generate initial tiles
    for _ in range(3):
        generate_new_tile()

def get_current_game_mode():
    """Randomly select a game mode for endless gameplay"""
    global tile_count, current_game_mode, mode_tiles_remaining, game_modes
    
    if mode_tiles_remaining <= 0:
        current_game_mode = random.randint(0, len(game_modes) - 1)
        base_duration = game_modes[current_game_mode]["duration"]
        mode_tiles_remaining = random.randint(max(3, base_duration - 3), base_duration + 5)
    
    return game_modes[current_game_mode]

def generate_new_tile():
    global tiles, score, tile_spawn_count, frenzy_mode, tile_count, mode_tiles_remaining
    global PICKED_POWER_UP, PURPLE_TILE_ACTIVE, PURPLE_TILE_START_TIME, PURPLE_TILE_AFFECTED_TILES
    global PICKED_POWER_UP_ACTIVE_TILES
    
    # Apply power-up effects
    current_tile_size = TILE_SIZE
    current_jump_duration = PLAYER_JUMP_DURATION
    current_move_speed_multiplier = 1.0
    
    if PICKED_POWER_UP:
        current_tile_size = 80
        current_jump_duration = 0.09
        PICKED_POWER_UP_ACTIVE_TILES += 1
        if PICKED_POWER_UP_ACTIVE_TILES >= MAX_PICKED_POWER_UP_TILES:
            PICKED_POWER_UP = False
            PICKED_POWER_UP_ACTIVE_TILES = 0
            print("Power-up expired after 5 tiles!")
    
    if PURPLE_TILE_ACTIVE:
        current_tile_size = int(TILE_SIZE * 1.25)
        current_jump_duration = PLAYER_JUMP_DURATION * 0.7
        current_move_speed_multiplier = 0.20
        PURPLE_TILE_AFFECTED_TILES += 1    
        # Check if we've reached the limit
        if PURPLE_TILE_AFFECTED_TILES >= MAX_PURPLE_AFFECTED_TILES:
            PURPLE_TILE_ACTIVE = False
            PURPLE_TILE_AFFECTED_TILES = 0
            print("Purple tile effect expired after 5 tiles!")
    
    # Random boat dock generation
    boat_dock_chance = 0.08
    last_tile_type = tiles[-1]['type'] if tiles else None
    if tile_count > 10 and random.random() < boat_dock_chance and last_tile_type != 'boat_dock':
        tiles.append({
            'pos': [0, 0, tiles[-1]['pos'][2] - JUMP_DISTANCE], 'size': current_tile_size * 1.5,
            'type': 'boat_dock', 'color': [0.4, 0.2, 0.0], 'origin_x': 0, 'player_on_tile': False
        })
        return
    
    # Get current game mode
    current_mode = get_current_game_mode()
    mode_tiles_remaining -= 1
    tile_count += 1
    
    last_tile_pos = tiles[-1]['pos']
    tile_spawn_count += 1
    new_pos_z = last_tile_pos[2] - JUMP_DISTANCE
    
    # Set frenzy mode based on current mode
    frenzy_mode = (current_mode["name"] == "frenzy")
    
    # Determine positioning based on mode
    if frenzy_mode:
        new_pos_x = 0
    else:
        # Normal zig-zag pattern
        if tile_spawn_count % 2 == 0:
            new_pos_x = last_tile_pos[0]
        else:
            random_angle_deg = random.uniform(-40, 40)
            angle_rad = math.radians(random_angle_deg)
            new_pos_x = last_tile_pos[0] - JUMP_DISTANCE * math.sin(angle_rad)
    
    # Clamp within river boundaries
    new_pos_x = max(-RIVER_WIDTH + current_tile_size/2, min(RIVER_WIDTH - current_tile_size/2, new_pos_x))
    new_pos = [new_pos_x, 0, new_pos_z]
    
    # Default properties
    tile_type = 'safe'
    color = [0.5, 0.5, 0.5]
    
    # Determine tile type and color based on current mode
    mode_name = current_mode["name"]
    last_tile_type = tiles[-1]['type'] if tiles else 'safe'
    
    # Random coconut tree generation (can appear in any mode)
    coconut_chance = 0.15
    if random.random() < coconut_chance and last_tile_type != 'coconut':
        tile_type = 'coconut'
        color = [0.7, 0.5, 0.2]
    else:
        # Original mode-based tile generation
        if mode_name == "safe":
            tile_type = 'safe'
            color = [0.5, 0.5, 0.5]
        
        elif mode_name == "purple_power":
            # Spawn purple power-up tile
            tile_type = 'power_up'
            color = [0.6, 0.0, 0.8]
            PURPLE_TILE_ACTIVE = True
            PURPLE_TILE_START_TIME = time.time()
            PURPLE_TILE_AFFECTED_TILES = 0
        
        elif mode_name == "moving":
            if random.random() < 0.7:
                tile_type = 'moving'
                color = [0.0, 0.8, 1.0]
            else:
                tile_type = 'safe'
                color = [0.5, 0.5, 0.5]
        
        elif mode_name == "mixed":
            rand_choice = random.random()
            if rand_choice < 0.4:
                tile_type = 'moving'
                color = [0.0, 0.8, 1.0]
            else:
                tile_type = 'safe'
                color = [0.5, 0.5, 0.5]
        
        elif mode_name == "frenzy":
            tile_type = 'safe'
            color = [0.8, 0.8, 0.0]
        
        elif mode_name == "trap":
            rand_choice = random.random()
            if rand_choice < 0.4:
                tile_type = 'trap'
                color = [0.8, 0.2, 0.2]
            else:
                tile_type = 'safe'
                color = [0.5, 0.5, 0.5]
        
        elif mode_name == "coconut":
            rand_choice = random.random()
            if rand_choice < 0.5 and last_tile_type not in ['trap', 'coconut']:
                tile_type = 'coconut'
                color = [0.7, 0.5, 0.2]
            else:
                tile_type = 'safe'
                color = [0.5, 0.5, 0.5]
        
        elif mode_name == "chaos":
            rand_choice = random.random()
            if rand_choice < 0.2:
                tile_type = 'trap'
                color = [0.8, 0.2, 0.2]
            elif rand_choice < 0.4:
                tile_type = 'moving'
                color = [0.0, 0.8, 1.0]
            elif rand_choice < 0.6 and last_tile_type not in ['trap', 'coconut']:
                tile_type = 'coconut'
                color = [0.7, 0.5, 0.2]
            else:
                tile_type = 'safe'
                color = [0.5, 0.5, 0.5]
    
    # Build tile dictionary
    new_tile = {
        'pos': new_pos, 'size': current_tile_size, 'type': tile_type,
        'color': color, 'origin_x': new_pos_x, 'player_on_tile': False
    }
    
    # Add type-specific properties
    if tile_type == 'moving':
        new_tile.update({
            'move_dir': random.choice([-1, 1]),
            'move_range': random.uniform(40, 80),
            'move_speed': (10 + (score * 0.75)) * current_move_speed_multiplier
        })
    elif tile_type == 'trap':
        new_tile.update({'is_active': False, 'pulse_start_time': 0})
    elif tile_type == 'coconut':
        new_tile['tree_shot'] = False
    
    tiles.append(new_tile)
    if len(tiles) > 7:
        tiles.pop(0)

def generate_boat_exit():
    """Generate exit dock for boat mode"""
    global tiles
    tiles.clear()
    tiles.append({
        'pos': [player_pos[0], 0, player_pos[2] - 150], 'size': TILE_SIZE * 2.0,
        'type': 'exit_dock', 'color': [0.2, 0.6, 0.2], 'origin_x': player_pos[0],
        'player_on_tile': False
    })

def generate_new_obstacle():
    global obstacles, obstacle_spawn_count, player_pos
    last_pos = [0, 0, player_pos[2] - 800]
    if obstacles:
        last_pos = obstacles[-1]['pos']
    
    new_pos_z = last_pos[2] - OBSTACLE_VERTICAL_SPACING
    obstacle_spawn_count += 1
    
    # 40% chance to spawn directly in front of player, 60% chance for normal spawn
    if random.random() < 0.4:
        new_pos_x = player_pos[0] + random.uniform(-30, 30)
    else:
        # Normal spawn logic
        if obstacle_spawn_count % 2 == 0:
            new_pos_x = last_pos[0]
        else:
            new_pos_x = last_pos[0] + random.uniform(-120, 120)
    
    new_pos_x = max(-RIVER_WIDTH + 50, min(RIVER_WIDTH - 50, new_pos_x))
    obstacles.append({'pos': [new_pos_x, 0, new_pos_z], 'size': random.uniform(40, 60), 'passed': False})

def generate_boat_coconut():
    """Generate a floating coconut for boat mode"""
    global boat_coconuts, player_pos
    coconut_x = random.uniform(-RIVER_WIDTH + 20, RIVER_WIDTH - 20)
    coconut_z = player_pos[2] - random.uniform(200, 400)
    coconut_y = random.uniform(40, 60)
    boat_coconuts.append({
        'pos': [coconut_x, coconut_y, coconut_z],
        'collected': False,
        'radius': 5.0
    })

def draw_text(x, y, text, font=None):
    if font is None:
        from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
        font = GLUT_BITMAP_HELVETICA_18
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
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(180, 0, 1, 0)
    glRotatef(player_angle, 0, 1, 0)
    
    torso_height, head_radius, leg_height, arm_height = 20.0, 5.0, 15.0, 15.0
    
    # Legs
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
    glPushMatrix()
    glTranslatef(boat_pos[0] + player_boat_pose["overall_pos"][0],
                 boat_pos[1] + player_boat_pose["overall_pos"][1],
                 boat_pos[2] + player_boat_pose["overall_pos"][2])
    glRotatef(180, 0, 1, 0)
    
    # Draw Torso
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
    
    # Draw Head
    head = player_boat_pose["head"]
    glColor3fv(head["color"])
    glPushMatrix()
    glTranslatef(part["pos"][0], part["pos"][1], part["pos"][2])
    glRotatef(part["rot"][0], 1, 0, 0)
    glRotatef(part["rot"][1], 0, 1, 0)
    glRotatef(part["rot"][2], 0, 0, 1)
    glTranslatef(head["pos"][0], head["pos"][1], head["pos"][2])
    glutSolidSphere(head["radius"], 20, 20)
    glPopMatrix()
    
    # Draw Limbs
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
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1]+10, player_pos[2])
    
    outer_radius, inner_radius, length, segments = 15.0, 13.0, 60.0, 20
    
    # Draw boat hull
    for radius, color in [(outer_radius, [0.4, 0.2, 0.0]), (inner_radius, [0.3, 0.15, 0.0])]:
        glColor3fv(color)
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = math.pi * (i / segments) + math.pi
            y, x = radius * math.sin(angle), radius * math.cos(angle)
            glVertex3f(x, y, length / 2)
            glVertex3f(x, y, -length / 2)
        glEnd()
    
    glPopMatrix()

def draw_tree(tile=None):
    glPushMatrix()
    scale = 20.0
    glScalef(scale, scale, scale)
    # If tree is shot, draw coconut lower than the others, unless player is on this tile
    if tile and tile.get('tree_shot', False) and not tile.get('player_on_tile', False):
        glPushMatrix()
        glTranslatef(-1.2, 1, 2)
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

def update_bullet_coconut_collision():
    global score
    for tile in tiles:
        if tile['type'] == 'coconut' and not tile.get('tree_shot', False):
            tree_offset = tile['size'] * 0.35
            trunk_x = tile['pos'][0] + tree_offset
            trunk_z = tile['pos'][2]
            trunk_y_min = tile['pos'][1] + TILE_HEIGHT/2
            trunk_y_max = trunk_y_min + 20
            for bullet in bullets[:]:
                dist_xz = math.sqrt((bullet.x - trunk_x)**2 + (bullet.z - trunk_z)**2)
                if dist_xz < 20 and trunk_y_min <= bullet.y <= trunk_y_max + 20:
                    print("Coconut tree shot!")
                    bullets.remove(bullet)
                    tile['tree_shot'] = True
                    score += 5
                    break

def update_boat_coconut_collision():
    """Check collision between bullets and boat coconuts"""
    global score, boat_coconuts_collected
    for coconut in boat_coconuts[:]:
        if not coconut['collected']:
            coconut_x, coconut_y, coconut_z = coconut['pos']
            for bullet in bullets[:]:
                dist = math.sqrt((bullet.x - coconut_x)**2 + (bullet.y - coconut_y)**2 + (bullet.z - coconut_z)**2)
                if dist < coconut['radius'] + bullet.radius:
                    print("Boat coconut shot! +5 points")
                    bullets.remove(bullet)
                    coconut['collected'] = True
                    score += 5
                    boat_coconuts_collected += 1
                    break

def draw_boat_coconuts():
    """Draw floating coconuts in boat mode"""
    for coconut in boat_coconuts:
        if not coconut['collected']:
            glPushMatrix()
            glTranslatef(coconut['pos'][0], 10, coconut['pos'][2])
            glColor3f(0.35, 0.18, 0.07)
            glutSolidSphere(coconut['radius'], 12, 12)
            glPopMatrix()

def draw_obstacles():
    glColor3f(0.3, 0.3, 0.3)
    for obstacle in obstacles:
        glPushMatrix()
        glTranslatef(obstacle['pos'][0], obstacle['size']/2 - TILE_HEIGHT/2, obstacle['pos'][2])
        glScalef(obstacle['size'], obstacle['size'], obstacle['size'])
        glutSolidCube(1)
        glPopMatrix()

def draw_tiles_with_outlines():
    for tile in tiles:
        glPushMatrix()
        glTranslatef(tile['pos'][0], tile['pos'][1], tile['pos'][2])
        
        # Draw tile
        glColor3fv(tile['color'])
        glPushMatrix()
        glScalef(tile['size'], TILE_HEIGHT, tile['size'])
        glutSolidCube(1)
        glPopMatrix()
        
        # Draw tree for coconut tiles
        if tile['type'] == 'coconut':
            glPushMatrix()
            tree_offset = tile['size'] * 0.35
            glTranslatef(tree_offset, TILE_HEIGHT/2, 0)
            draw_tree(tile)
            glPopMatrix()
        
        # Draw special effect for power-up tiles
        if tile['type'] == 'power_up':
            glPushMatrix()
            glTranslatef(0, TILE_HEIGHT/2 + 5, 0)
            glColor3f(1.0, 1.0, 1.0)
            glutSolidSphere(3, 8, 8)
            glColor3f(0.6, 0.0, 0.8)
            glutSolidSphere(2, 8, 8)
            glPopMatrix()
        
        # Draw outline
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
    if game_state != 'AIMING' or autoplay_active or shooting_mode:
        return
    
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1] + 1, player_pos[2])
    glRotatef(arrow_angle, 0, 1, 0)
    glColor3f(1.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0,0,0)
    glVertex3f(0,0,-ARROW_LENGTH)
    glEnd()
    glBegin(GL_TRIANGLES)
    glVertex3f(-5,0,-ARROW_LENGTH)
    glVertex3f(5,0,-ARROW_LENGTH)
    glVertex3f(0,0,-ARROW_LENGTH-10)
    glEnd()
    glPopMatrix()

def draw_environment():
    z_near = player_pos[2] + 500
    z_far = player_pos[2] - 5000
    
    # Water
    glColor3f(0.2, 0.5, 0.9)
    glBegin(GL_QUADS)
    glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2,z_near)
    glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2,z_near)
    glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2,z_far)
    glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2,z_far)
    glEnd()
    
    # Shore lines
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2+1,z_near)
    glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2+1,z_far)
    glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2+1,z_near)
    glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2+1,z_far)
    glEnd()
    
    # Land
    glColor3f(0.1, 0.7, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-RIVER_WIDTH-1000,-TILE_HEIGHT/2,z_near)
    glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2,z_near)
    glVertex3f(-RIVER_WIDTH,-TILE_HEIGHT/2,z_far)
    glVertex3f(-RIVER_WIDTH-1000,-TILE_HEIGHT/2,z_far)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2,z_near)
    glVertex3f(RIVER_WIDTH+1000,-TILE_HEIGHT/2,z_near)
    glVertex3f(RIVER_WIDTH+1000,-TILE_HEIGHT/2,z_far)
    glVertex3f(RIVER_WIDTH,-TILE_HEIGHT/2,z_far)
    glEnd()

def keyboardListener(key, x, y):
    global arrow_angle, player_angle, player_pos, autoplay_active, shooting_mode, score
    global game_state, jump_start_pos, jump_end_pos, jump_start_time
    
    key = key.lower() if isinstance(key, bytes) else key
    
    # Toggle autoplay
    if key == b'p':
        autoplay_active = not autoplay_active
        if autoplay_active:
            shooting_mode = False
    
    # Toggle shooting mode
    if key == b'x' and game_state == 'AIMING':
        shooting_mode = not shooting_mode
    
    # Movement controls
    if not autoplay_active:
        if key == b'a':
            arrow_angle += 4.0
        elif key == b'd':
            arrow_angle -= 4.0
        
        if game_state == 'AIMING':
            player_angle = arrow_angle
        
        # Jump
        elif key == b' ' and game_state == 'AIMING':
            angle_rad = math.radians(arrow_angle)
            jump_distance = JUMP_DISTANCE
            game_state = 'JUMPING'
            jump_start_pos = list(player_pos)
            jump_end_pos = [
                player_pos[0] - jump_distance * math.sin(angle_rad),
                player_pos[1],
                player_pos[2] - jump_distance * math.cos(angle_rad)
            ]
            jump_start_time = time.time()
    
    # Boat movement
    if game_state == 'BOAT_MODE' and not autoplay_active:
        if key == b'a':
            player_pos[0] -= BOAT_STRAFE_SPEED * (1/60.0)
        elif key == b'd':
            player_pos[0] += BOAT_STRAFE_SPEED * (1/60.0)
        player_pos[0] = max(-RIVER_WIDTH + 25, min(RIVER_WIDTH - 25, player_pos[0]))
    
    # Restart game logic
    if key == b'r':
        if game_state == 'GAME_OVER':
            print("Restarting game from beginning!")
            reset_game()
        elif score >= 10:
            score = max(0, score - 10)
            print("Game reset! Lost 10 points.")
            reset_score = score
            reset_game()
            score = reset_score
        else:
            game_state = 'GAME_OVER'
            print(f"Cannot restart! Need at least 10 points. Current score: {score}")
            print("GAME OVER - No points left to restart!")

def mouseListener(button, state, x, y):
    global fire_bullet, game_state, jump_start_pos, jump_end_pos, jump_start_time, player_angle
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if game_state == 'AIMING' and not autoplay_active:
            if shooting_mode:
                fire_bullet = True
                return
            # Normal jump
            current_tile_index = -1
            for i, tile in enumerate(tiles):
                if (math.isclose(tile['pos'][0], player_pos[0], abs_tol=0.1) and 
                    math.isclose(tile['pos'][2], player_pos[2], abs_tol=0.1)):
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
                jump_end_pos = [
                    player_pos[0] - actual_dist_to_tile*math.sin(angle_rad),
                    player_pos[1],
                    player_pos[2] - actual_dist_to_tile*math.cos(angle_rad)
                ]
                player_angle = arrow_angle
                jump_start_time = time.time()
        
        elif game_state == 'BOAT_MODE' and shooting_mode:
            fire_bullet = True

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(55, (1000/800), 0.1, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Third-person camera
    cam_x = 0 + camera_offset[0]
    cam_y = player_pos[1] + camera_offset[1]
    cam_z = player_pos[2] + camera_offset[2]
    look_at_x, look_at_y, look_at_z = 0, player_pos[1], player_pos[2]
    gluLookAt(cam_x, cam_y, cam_z, look_at_x, look_at_y, look_at_z, 0, 1, 0)

def update_game_state():
    global game_state, player_pos, score, jump_anim_arm_angle, jump_anim_leg_angle
    global drown_start_time, obstacles, arrow_angle, player_angle
    global jump_start_pos, jump_end_pos, jump_start_time
    global boat_obstacles_passed, boat_exit_generated, last_jump_time, frenzy_mode
    global boat_coconuts_spawned, boat_coconuts_collected
    global PICKED_POWER_UP, PURPLE_TILE_ACTIVE, PURPLE_TILE_START_TIME, PURPLE_TILE_AFFECTED_TILES
    global PICKED_POWER_UP_ACTIVE_TILES
    
    # Power-up effect: change jump duration and tile size
    if PICKED_POWER_UP:
        PLAYER_JUMP_DURATION = 0.09
    else:
        PLAYER_JUMP_DURATION = 0.4
    
    # Update bullets
    for bullet in bullets:
        bullet.update()
    bullets[:] = [b for b in bullets if not b.has_expired()]
    update_bullet_coconut_collision()
    update_boat_coconut_collision()
    
    # Autoplay logic
    if autoplay_active and game_state == 'AIMING' and len(tiles) > 1:
        current_tile_index = next((i for i, t in enumerate(tiles) 
                                 if math.isclose(t['pos'][0], player_pos[0]) and 
                                    math.isclose(t['pos'][2], player_pos[2])), -1)
        if current_tile_index != -1 and current_tile_index + 1 < len(tiles):
            target_tile = tiles[current_tile_index + 1]
            dx, dz = target_tile['pos'][0] - player_pos[0], target_tile['pos'][2] - player_pos[2]
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
    
    # Trap tile logic
    if game_state not in ['BOAT_MODE', 'GAME_OVER']:
        for tile in tiles:
            if tile.get('is_active'):
                elapsed = time.time() - tile['pulse_start_time']
                if (elapsed > TRAP_FUSE_TIME and game_state == 'AIMING' and
                    abs(player_pos[0] - tile['pos'][0]) < tile['size']/2 and
                    abs(player_pos[2] - tile['pos'][2]) < tile['size']/2):
                    if score >= 5:
                        score = max(0, score - 5)
                        player_pos[0], player_pos[2], player_pos[1] = 0.0, 0.0, TILE_HEIGHT/2
                        player_angle = 0.0
                        arrow_angle = 0.0
                        game_state = 'AIMING'
                        print("Trap activated! Lost 5 points and reset position.")
                    else:
                        game_state = 'GAME_OVER'
                        print(f"Trap activated but not enough points! Current score: {score}")
                        print("GAME OVER - No points left!")
                    return
                tile['color'] = [1.0, 
                               0.5 * (0.5 + 0.5 * math.sin(elapsed * TRAP_PULSE_SPEED)),
                               0.5 * (0.5 + 0.5 * math.sin(elapsed * TRAP_PULSE_SPEED))]
    
    # Frenzy mode collapse timer - only during yellow tile countdown
    if frenzy_mode and game_state == 'AIMING' and last_jump_time is not None:
        elapsed_since_jump = time.time() - last_jump_time
        if elapsed_since_jump > FRENZY_COLLAPSE_TIME:
            frenzy_mode = False
            last_jump_time = None
            return
    
    # Jumping animation
    if game_state == 'JUMPING':
        progress = min((time.time() - jump_start_time) / PLAYER_JUMP_DURATION, 1.0)
        player_pos[0] = (1-progress) * jump_start_pos[0] + progress * jump_end_pos[0]
        player_pos[2] = (1-progress) * jump_start_pos[2] + progress * jump_end_pos[2]
        player_pos[1] = jump_start_pos[1] + (4 * (progress - progress**2)) * PLAYER_JUMP_HEIGHT
        jump_anim_arm_angle = 90 * math.sin(progress * math.pi)
        jump_anim_leg_angle = -45 * math.sin(progress * math.pi)
        if progress >= 1.0:
            game_state = 'LANDED'
            jump_anim_arm_angle, jump_anim_leg_angle = 0.0, 0.0
    
    # Landing logic
    elif game_state == 'LANDED':
        landed_safely = False
        for tile in tiles:
            if (abs(player_pos[0] - tile['pos'][0]) < tile['size']/2 and
                abs(player_pos[2] - tile['pos'][2]) < tile['size']/2):
                landed_safely = True
                tile['player_on_tile'] = True
                player_pos[0], player_pos[2], player_pos[1] = tile['pos'][0], tile['pos'][2], TILE_HEIGHT/2
                
                if tile['type'] == 'boat_dock':
                    game_state = 'BOAT_MODE'
                    player_pos[1] = 0.0
                    tiles.clear()
                    boat_coconuts_spawned = 0
                    boat_coconuts_collected = 0
                    return
                elif tile['type'] == 'exit_dock':
                    game_state = 'AIMING'
                    score = 35
                    generate_new_tile()
                    generate_new_tile()
                    generate_new_tile()
                    return
                elif tile['type'] == 'moving':
                    tile['type'] = 'safe'
                    tile['color'] = [0.5, 0.5, 0.5]
                elif tile['type'] == 'trap' and not tile.get('is_active'):
                    tile['is_active'] = True
                    tile['pulse_start_time'] = time.time()
                elif tile['type'] == 'power_up':
                    PICKED_POWER_UP = True
                    PICKED_POWER_UP_ACTIVE_TILES = 0
                    print("Power-up collected! Jump duration: 0.09, Tile size: 80")
                
                # Award points and generate new tile (always generate regardless of tile state)
                tile_scored = False
                if not tile.get('is_active'):
                    if tile['type'] == 'coconut' and tile.get('tree_shot', False):
                        score += 1
                    
                    if frenzy_mode:
                        if tile['color'] == [0.8, 0.8, 0.0]:
                            last_jump_time = time.time()
                        score += 5
                        arrow_angle = 0
                        player_angle = 0
                    else:
                        score += 1
                    tile_scored = True
                
                # Always generate new tile when landing, regardless of tile state
                generate_new_tile()
                
                game_state = 'AIMING'
                break
            else:
                tile['player_on_tile'] = False
        
        if not landed_safely:
            penalty_points = 2 if abs(player_pos[0]) < RIVER_WIDTH else 5
            
            if score >= penalty_points:
                game_state = 'DROWNING'
                drown_start_time = time.time()
                score = max(0, score - penalty_points)
                if abs(player_pos[0]) < RIVER_WIDTH:
                    print("Fell in water! Lost 2 points.")
                else:
                    print("Fell outside bounds! Lost 5 points.")
            else:
                game_state = 'GAME_OVER'
                print(f"Not enough points for penalty! Current score: {score}, needed: {penalty_points}")
                print("GAME OVER - No points left!")
    
    # Drowning logic
    elif game_state == 'DROWNING':
        if time.time() - drown_start_time > DROWN_DURATION:
            player_pos[0], player_pos[2], player_pos[1] = 0.0, 0.0, TILE_HEIGHT/2
            player_angle = 0.0
            arrow_angle = 0.0
            game_state = 'AIMING'
            print("Fell in water! Reset to start position.")
        else:
            player_pos[1] -= 20 * (1/60.0)
    
    # Moving tiles update
    if game_state != 'BOAT_MODE':
        for tile in tiles:
            if tile['type'] == 'moving':
                tile['pos'][0] += tile['move_speed'] * tile['move_dir'] * (1/60.0)
                if not (-RIVER_WIDTH < tile['pos'][0] - tile['size']/2 and 
                       tile['pos'][0] + tile['size']/2 < RIVER_WIDTH):
                    tile['move_dir'] *= -1
    
    # Boat mode logic
    if game_state == 'BOAT_MODE':
        player_pos[2] -= BOAT_FORWARD_SPEED * (1/60.0)
        player_angle = 0
        if boat_coconuts_spawned < MAX_BOAT_COCONUTS and boat_obstacles_passed % 2 == 0 and boat_obstacles_passed > 0:
            expected_coconuts = boat_obstacles_passed // 2
            if boat_coconuts_spawned < expected_coconuts:
                generate_boat_coconut()
                boat_coconuts_spawned += 1
                print(f"Coconut spawned! Total spawned: {boat_coconuts_spawned} at obstacle milestone: {boat_obstacles_passed}")
        
        if autoplay_active:
            closest_obstacle = None
            min_distance = float('inf')
            
            for obs in obstacles:
                if obs['pos'][2] < player_pos[2] and obs['pos'][2] > player_pos[2] - 200:
                    distance = abs(player_pos[2] - obs['pos'][2])
                    if distance < min_distance:
                        min_distance = distance
                        closest_obstacle = obs
            
            if closest_obstacle:
                obs_x = closest_obstacle['pos'][0]
                obs_size = closest_obstacle['size']
                
                # If obstacle is too close to our path, move away
                if abs(player_pos[0] - obs_x) < obs_size/2 + 40:
                    if player_pos[0] < obs_x:
                        player_pos[0] -= BOAT_STRAFE_SPEED * (1/60.0)
                    else:
                        player_pos[0] += BOAT_STRAFE_SPEED * (1/60.0)                    
                    player_pos[0] = max(-RIVER_WIDTH + 25, min(RIVER_WIDTH - 25, player_pos[0]))
        
        # Generate obstacles
        if not obstacles or obstacles[-1]['pos'][2] > player_pos[2] - OBSTACLE_VERTICAL_SPACING:
            generate_new_obstacle()
        
        # Check obstacle collisions and scoring
        for obs in obstacles:
            if (abs(player_pos[0] - obs['pos'][0]) < 25 + obs['size']/2 and
                abs(player_pos[2] - obs['pos'][2]) < 50 + obs['size']/2):
                if score >= 3:
                    score = max(0, score - 3)
                    player_pos[0] = 0.0
                    print("Boat hit obstacle! Lost 3 points and reset position.")
                else:
                    game_state = 'GAME_OVER'
                    print(f"Boat collision but not enough points! Current score: {score}")
                    print("GAME OVER - No points left!")
                return
            # Mark obstacle as passed when player moves past it (player Z < obstacle Z)
            if not obs['passed'] and player_pos[2] < obs['pos'][2]:
                obs['passed'] = True
                boat_obstacles_passed += 1
                print(f"Obstacle passed! Total: {boat_obstacles_passed}")
        
        # Check coconut collisions and scoring
        for coconut in boat_coconuts[:]:
            if not coconut['collected']:
                coconut_x, coconut_y, coconut_z = coconut['pos']
                if (abs(player_pos[0] - coconut_x) < 25 + coconut['radius'] and
                    abs(player_pos[2] - coconut_z) < 50 + coconut['radius']):
                    print("Boat collided with coconut! +5 points")
                    coconut['collected'] = True
                    score += 5
                    boat_coconuts_collected += 1
                    boat_coconuts.remove(coconut)
        
        # Check if boat mode is complete (dynamic completion)
        # Complete boat mode after passing a random number of obstacles
        if boat_obstacles_passed >= random.randint(15, 25) and not boat_exit_generated:
            generate_boat_exit()
            boat_exit_generated = True
            print("Boat exit dock generated! Navigate to the green dock ahead.")
        
        # Check collision with exit dock
        if boat_exit_generated and tiles:
            exit_dock = tiles[0]
            if (abs(player_pos[0] - exit_dock['pos'][0]) < exit_dock['size']/2 and
                abs(player_pos[2] - exit_dock['pos'][2]) < exit_dock['size']/2):
                game_state = 'AIMING'
                player_pos[0] = exit_dock['pos'][0]
                player_pos[1] = TILE_HEIGHT / 2
                player_pos[2] = exit_dock['pos'][2]
                boat_exit_generated = False
                boat_obstacles_passed = 0
                boat_coconuts_spawned = 0
                boat_coconuts_collected = 0
                boat_coconuts.clear()
                obstacles.clear()
                generate_new_tile()
                generate_new_tile()
                generate_new_tile()
                print("Boat mode completed! Continuing endless adventure...")
                return
        
        # Clean up old obstacles and coconuts
        obstacles[:] = [obs for obs in obstacles if obs['pos'][2] < player_pos[2] + 200]
        boat_coconuts[:] = [coco for coco in boat_coconuts if coco['pos'][2] < player_pos[2] + 200]

def idle():
    if game_state != 'GAME_OVER':
        update_game_state()
    glutPostRedisplay()

def showScreen():
    global score, game_state, player_pos, player_angle, arrow_angle
    if game_state not in ['AIMING', 'JUMPING', 'LANDED', 'DROWNING', 'BOAT_MODE', 'GAME_OVER']:
        game_state = 'AIMING'
        player_pos[0], player_pos[2], player_pos[1] = 0.0, 0.0, TILE_HEIGHT/2
        player_angle = 0.0
        arrow_angle = 0.0
        print("Invalid game state detected - reset to AIMING")
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_environment()
    
    if game_state == 'BOAT_MODE':
        draw_boat()
        draw_obstacles()
        draw_boat_coconuts()
        if shooting_mode:
            draw_player_aiming()
            draw_shooting_line()
            for bullet in bullets:
                bullet.draw()
        else:
            draw_player_sitting(player_pos)
            for bullet in bullets:
                bullet.draw()
    else:
        draw_tiles_with_outlines()
        if shooting_mode:
            draw_player_aiming()
            draw_shooting_line()
            for bullet in bullets:
                bullet.draw()
        else:
            draw_aiming_arrow()
            draw_player_standing()
            for bullet in bullets:
                bullet.draw()
    
    # UI Text
    draw_text(10, 750, f"Score: {score}")
    draw_text(10, 720, f"Stage: {get_current_stage()}")
    
    # Show current game mode
    if score != 15:
        current_mode = get_current_game_mode()
        draw_text(10, 690, f"Mode: {current_mode['name'].title()} ({mode_tiles_remaining} tiles left)")
        draw_text(10, 660, f"Total Tiles: {tile_count}")
    
    draw_text(10, 630, f"Autoplay: {'ON' if autoplay_active else 'OFF'}")
    
    # Show power-up status
    if PICKED_POWER_UP:
        remaining_tiles = MAX_PICKED_POWER_UP_TILES - PICKED_POWER_UP_ACTIVE_TILES
        draw_text(10, 600, f"POWER-UP ACTIVE: Fast Jump + Large Tiles ({remaining_tiles} tiles left)")
    elif PURPLE_TILE_ACTIVE:
        remaining_tiles = MAX_PURPLE_AFFECTED_TILES - PURPLE_TILE_AFFECTED_TILES
        draw_text(10, 600, f"Purple Effect: {remaining_tiles} tiles left (Large tiles + Slow moving)")
    
    # Show shooting mode status (when no power-up is active)
    if not PICKED_POWER_UP and not PURPLE_TILE_ACTIVE:
        if shooting_mode:
            draw_text(10, 600, "Shooting Mode: ON (Press X to toggle)")
        else:
            draw_text(10, 600, "Shooting Mode: OFF (Press X on coconut tile to shoot)")
    
    # Show boat progress when in boat mode
    if game_state == 'BOAT_MODE':
        target_obstacles = 20
        draw_text(10, 570, f"Obstacles Avoided: {boat_obstacles_passed}")
        draw_text(10, 540, f"Coconuts Collected: {boat_coconuts_collected}/{boat_coconuts_spawned} (Max: {MAX_BOAT_COCONUTS})")
    
    if frenzy_mode and last_jump_time is not None:
        remaining = max(0, FRENZY_COLLAPSE_TIME - (time.time() - last_jump_time))
        draw_text(10, 510, f"Collapse in: {remaining:.2f}s")
    
    # Show reset instruction (only if player has enough points and not game over)
    if game_state != 'GAME_OVER':
        if score >= 10:
            draw_text(10, 480, "Press 'R' to reset game (-10 points)")
        else:
            draw_text(10, 480, f"Need 10+ points to reset (Current: {score})")
    
    # Game Over screen
    if game_state == 'GAME_OVER':
        glColor4f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(1000, 0)
        glVertex2f(1000, 800)
        glVertex2f(0, 800)
        glEnd()
        
        # Game Over text
        draw_text(400, 400, "GAME OVER")
        draw_text(350, 360, f"Final Score: {score}")
        draw_text(300, 320, "Not enough points to restart!")
        draw_text(280, 280, "Press 'R' to start new game from beginning")
        draw_text(320, 240, "Or close window to exit")
    
    glutSwapBuffers()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"Island Jumper - Linear Adventure")
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glEnable(GL_DEPTH_TEST)
    reset_game()
    glutMainLoop()

if __name__ == "__main__":
    main()
