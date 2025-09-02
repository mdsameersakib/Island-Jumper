import sys
import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

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

# --- Game State Variables ---
game_state = 'AIMING'
score = 0
player_pos = [0.0, TILE_HEIGHT / 2, 0.0]
player_angle = 0.0
arrow_angle = 0.0

# Jump animation variables
jump_start_pos = None
jump_end_pos = None
jump_start_time = 0.0
jump_anim_arm_angle = 0.0
jump_anim_leg_angle = 0.0

# Drown animation variable
drown_start_time = 0.0

# List to hold all tile data
tiles = []

# --- Camera Configuration ---
camera_offset = [0, 150, 220]

def reset_game():
    """Resets all game variables to their initial state."""
    global game_state, score, player_pos, player_angle, arrow_angle, tiles
    global jump_anim_arm_angle, jump_anim_leg_angle
    game_state = 'AIMING'
    score = 0
    player_pos = [0.0, TILE_HEIGHT / 2, 0.0]
    player_angle = 0.0
    arrow_angle = 0.0
    jump_anim_arm_angle = 0.0
    jump_anim_leg_angle = 0.0
    tiles.clear()
    tiles.append({
        'pos': [0, 0, 0], 'size': TILE_SIZE, 'type': 'safe',
        'color': [0.5, 0.5, 0.5], 'origin_x': 0
    })
    generate_new_tile()
    generate_new_tile()
    generate_new_tile()


def generate_new_tile():
    """
    Generates a new tile at a guaranteed reachable distance and angle.
    """
    global tiles, score

    last_tile_pos = tiles[-1]['pos']
    
    max_angle_scatter = 40 
    random_angle_deg = random.uniform(-max_angle_scatter, max_angle_scatter)
    angle_rad = math.radians(random_angle_deg)

    new_pos_x = last_tile_pos[0] - JUMP_DISTANCE * math.sin(angle_rad)
    new_pos_z = last_tile_pos[2] - JUMP_DISTANCE * math.cos(angle_rad)
    
    new_pos_x = max(-RIVER_WIDTH + TILE_SIZE/2, min(RIVER_WIDTH - TILE_SIZE/2, new_pos_x))

    new_pos = [new_pos_x, 0, new_pos_z]

    tile_type = 'safe'
    color = [0.5, 0.5, 0.5]

    if score > 15:
        rand_choice = random.random()
        if rand_choice < 0.3:
            tile_type = 'trap'
        elif rand_choice < 0.7:
            tile_type = 'moving'
            color = [0.0, 0.8, 1.0]
    elif score > 5:
        if random.random() < 0.5:
            tile_type = 'moving'
            color = [0.0, 0.8, 1.0]

    new_tile = {
        'pos': new_pos, 'size': TILE_SIZE, 'type': tile_type,
        'color': color, 'origin_x': new_pos_x
    }
    
    if tile_type == 'moving':
        new_tile.update({'move_dir': 1, 'move_range': 50, 'move_speed': 25 + (score * 0.5)})
    
    if tile_type == 'trap':
        new_tile.update({'is_active': False, 'pulse_start_time': 0})

    tiles.append(new_tile)
    if len(tiles) > 6:
        tiles.pop(0)


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draws text on the screen at a specified 2D coordinate."""
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


def draw_player():
    """Draws a composite player character with animations."""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 1, 0)

    torso_height, head_radius, leg_height, arm_height = 20.0, 5.0, 15.0, 15.0

    # --- Legs ---
    glColor3f(0.1, 0.2, 0.8)
    for i in [-.8, .8]:
        glPushMatrix()
        # Move pivot to the hip, apply animation, then draw
        glTranslatef(i * 4, leg_height, 0)
        glRotatef(jump_anim_leg_angle, 1, 0, 0)
        glTranslatef(0, -leg_height, 0) # move back to draw
        
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 2.5, 2.5, leg_height, 10, 10)
        glPopMatrix()

    # --- Torso ---
    glColor3f(0.1, 0.8, 0.2)
    glPushMatrix()
    glTranslatef(0, leg_height + 10, 0)
    glScalef(12.0, torso_height, 6.0)
    glutSolidCube(1)
    glPopMatrix()

    # --- Head ---
    glColor3f(1.0, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(0, leg_height + 5 + torso_height, 0)
    glutSolidSphere(head_radius, 20, 20)
    glPopMatrix()

    # --- Arms ---
    glColor3f(1.0, 0.8, 0.6)
    for i in [-1, 1]:
        glPushMatrix()
        glTranslatef(i * 7, leg_height + 5 + torso_height - 5, 0)
        
        if game_state == 'DROWNING':
            # Arms straight up for drowning
            glRotatef(-160, 1, 0, 0)
        else:
            # Arms swing sideways for jumping
            glRotatef(i * jump_anim_arm_angle, 0, 0, 1)

        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 2.0, 2.0, arm_height, 10, 10)
        glPopMatrix()

    glPopMatrix()


def draw_tiles_with_outlines():
    """Draws all tiles with a manually drawn black outline."""
    for tile in tiles:
        glPushMatrix()
        glTranslatef(tile['pos'][0], tile['pos'][1], tile['pos'][2])
        
        # Step 1: Draw the solid, colored cube
        glColor3fv(tile['color'])
        glPushMatrix()
        glScalef(tile['size'], TILE_HEIGHT, tile['size'])
        glutSolidCube(1)
        glPopMatrix()

        # Step 2: Manually draw the 12 edges of the cube for the outline
        glColor3f(0.0, 0.0, 0.0) # Black color for lines
        
        s = tile['size'] / 2.0
        h = TILE_HEIGHT / 2.0

        glBegin(GL_LINES)
        # Top face
        glVertex3f(-s, h, -s); glVertex3f(s, h, -s)
        glVertex3f(s, h, -s); glVertex3f(s, h, s)
        glVertex3f(s, h, s); glVertex3f(-s, h, s)
        glVertex3f(-s, h, s); glVertex3f(-s, h, -s)
        # Bottom face
        glVertex3f(-s, -h, -s); glVertex3f(s, -h, -s)
        glVertex3f(s, -h, -s); glVertex3f(s, -h, s)
        glVertex3f(s, -h, s); glVertex3f(-s, -h, s)
        glVertex3f(-s, -h, s); glVertex3f(-s, -h, -s)
        # Vertical edges
        glVertex3f(-s, h, -s); glVertex3f(-s, -h, -s)
        glVertex3f(s, h, -s); glVertex3f(s, -h, -s)
        glVertex3f(s, h, s); glVertex3f(s, -h, s)
        glVertex3f(-s, h, s); glVertex3f(-s, -h, s)
        glEnd()

        glPopMatrix()


def draw_aiming_arrow():
    """Draws the arrow used to aim the jump."""
    if game_state != 'AIMING':
        return

    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1] + 1, player_pos[2])
    glRotatef(arrow_angle, 0, 1, 0)

    glColor3f(1.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, -ARROW_LENGTH)
    glEnd()
    glBegin(GL_TRIANGLES)
    glVertex3f(-5, 0, -ARROW_LENGTH)
    glVertex3f(5, 0, -ARROW_LENGTH)
    glVertex3f(0, 0, -ARROW_LENGTH - 10)
    glEnd()
    glPopMatrix()

def draw_environment():
    """Draws the water and the riverbanks to create a perspective view."""
    glColor3f(0.2, 0.5, 0.9)
    glBegin(GL_QUADS)
    glVertex3f(-RIVER_WIDTH, -TILE_HEIGHT/2, 500)
    glVertex3f(RIVER_WIDTH, -TILE_HEIGHT/2, 500)
    glVertex3f(RIVER_WIDTH, -TILE_HEIGHT/2, -5000)
    glVertex3f(-RIVER_WIDTH, -TILE_HEIGHT/2, -5000)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(-RIVER_WIDTH, -TILE_HEIGHT/2 + 1, 500)
    glVertex3f(-RIVER_WIDTH, -TILE_HEIGHT/2 + 1, -5000)
    glVertex3f(RIVER_WIDTH, -TILE_HEIGHT/2 + 1, 500)
    glVertex3f(RIVER_WIDTH, -TILE_HEIGHT/2 + 1, -5000)
    glEnd()

    glColor3f(0.1, 0.7, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-RIVER_WIDTH - 1000, -TILE_HEIGHT/2, 500)
    glVertex3f(-RIVER_WIDTH, -TILE_HEIGHT/2, 500)
    glVertex3f(-RIVER_WIDTH, -TILE_HEIGHT/2, -5000)
    glVertex3f(-RIVER_WIDTH - 1000, -TILE_HEIGHT/2, -5000)
    glVertex3f(RIVER_WIDTH, -TILE_HEIGHT/2, 500)
    glVertex3f(RIVER_WIDTH + 1000, -TILE_HEIGHT/2, 500)
    glVertex3f(RIVER_WIDTH + 1000, -TILE_HEIGHT/2, -5000)
    glVertex3f(RIVER_WIDTH, -TILE_HEIGHT/2, -5000)
    glEnd()


def keyboardListener(key, x, y):
    """Handles keyboard inputs."""
    global arrow_angle, player_angle
    
    if game_state == 'AIMING':
        if key == b'a':
            arrow_angle += 4.0
        if key == b'd':
            arrow_angle -= 4.0
        player_angle = arrow_angle

    if key == b'r' and game_state == 'GAME_OVER':
        reset_game()

def mouseListener(button, state, x, y):
    """Handles mouse inputs for jumping."""
    global game_state, jump_start_pos, jump_end_pos, jump_start_time, player_angle

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and game_state == 'AIMING':
        game_state = 'JUMPING'
        jump_start_pos = list(player_pos)
        
        angle_rad = math.radians(arrow_angle)
        jump_end_pos = [
            player_pos[0] - JUMP_DISTANCE * math.sin(angle_rad),
            player_pos[1],
            player_pos[2] - JUMP_DISTANCE * math.cos(angle_rad)
        ]
        
        jump_start_time = time.time()
        player_angle = arrow_angle


def setupCamera():
    """Configures the camera's projection and view settings."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(55, (1000 / 800), 0.1, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    cam_x = 0 + camera_offset[0] 
    cam_y = player_pos[1] + camera_offset[1]
    cam_z = player_pos[2] + camera_offset[2]

    look_at_x = 0
    look_at_y = player_pos[1]
    look_at_z = player_pos[2]

    gluLookAt(cam_x, cam_y, cam_z,
              look_at_x, look_at_y, look_at_z,
              0, 1, 0)


def update_game_state():
    """Main logic update function, called continuously from idle."""
    global game_state, player_pos, score, jump_anim_arm_angle, jump_anim_leg_angle, drown_start_time

    for tile in tiles:
        if tile.get('is_active'):
            elapsed = time.time() - tile['pulse_start_time']
            if elapsed > TRAP_FUSE_TIME:
                game_state = 'GAME_OVER'
                return
            
            brightness = 0.5 + 0.5 * math.sin(elapsed * TRAP_PULSE_SPEED)
            tile['color'] = [1.0, brightness * 0.5, brightness * 0.5]

    if game_state == 'JUMPING':
        elapsed_time = time.time() - jump_start_time
        progress = min(elapsed_time / PLAYER_JUMP_DURATION, 1.0)

        player_pos[0] = (1 - progress) * jump_start_pos[0] + progress * jump_end_pos[0]
        player_pos[2] = (1 - progress) * jump_start_pos[2] + progress * jump_end_pos[2]
        parabola = 4 * (progress - progress**2)
        player_pos[1] = jump_start_pos[1] + parabola * PLAYER_JUMP_HEIGHT

        # Calculate animation angles based on jump progress
        jump_anim_arm_angle = 90 * math.sin(progress * math.pi) # Swings sideways
        jump_anim_leg_angle = -45 * math.sin(progress * math.pi)


        if progress >= 1.0:
            game_state = 'LANDED'
            jump_anim_arm_angle = 0.0
            jump_anim_leg_angle = 0.0

    elif game_state == 'LANDED':
        landed_safely = False
        active_trap = False
        for tile in tiles:
            dist_x = abs(player_pos[0] - tile['pos'][0])
            dist_z = abs(player_pos[2] - tile['pos'][2])
            if dist_x < tile['size'] / 2 and dist_z < tile['size'] / 2:
                landed_safely = True
                player_pos[0], player_pos[2] = tile['pos'][0], tile['pos'][2]
                player_pos[1] = TILE_HEIGHT / 2
                
                if tile['type'] == 'moving':
                    tile['type'] = 'safe'
                    tile['color'] = [0.5, 0.5, 0.5]
                
                if tile['type'] == 'trap' and not tile.get('is_active'):
                    tile['is_active'] = True
                    tile['pulse_start_time'] = time.time()
                    active_trap = True
                break
        
        if landed_safely:
            if not active_trap:
                score += 1
                generate_new_tile()
            game_state = 'AIMING'
        else:
            if abs(player_pos[0]) < RIVER_WIDTH:
                 game_state = 'DROWNING'
                 drown_start_time = time.time()
            else:
                 game_state = 'GAME_OVER'
    
    elif game_state == 'DROWNING':
        elapsed_time = time.time() - drown_start_time
        if elapsed_time > DROWN_DURATION:
            game_state = 'GAME_OVER'
        else:
            # Sink the player
            player_pos[1] -= 20 * (1/60.0) # Sink at a fixed rate

    for tile in tiles:
        if tile['type'] == 'moving':
            tile['pos'][0] += tile['move_speed'] * tile['move_dir'] * (1/60.0)
            
            # Check if the tile has hit the edge of the river
            tile_left_edge = tile['pos'][0] - tile['size'] / 2
            tile_right_edge = tile['pos'][0] + tile['size'] / 2

            if (tile_right_edge > RIVER_WIDTH and tile['move_dir'] > 0) or \
               (tile_left_edge < -RIVER_WIDTH and tile['move_dir'] < 0):
                tile['move_dir'] *= -1
            # Original check for move range is now secondary
            elif abs(tile['pos'][0] - tile['origin_x']) > tile['move_range']:
                 tile['move_dir'] *= -1


def idle():
    """Idle function that runs continuously."""
    update_game_state()
    glutPostRedisplay()


def showScreen():
    """Display function to render the entire game scene."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    draw_environment()
    draw_tiles_with_outlines()
    draw_player()
    draw_aiming_arrow()

    draw_text(10, 770, f"Score: {score}")
    draw_text(10, 740, f"Cam Offset (x,y,z): {camera_offset}")

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

    # Only using functions from the original template + GL_DEPTH_TEST
    glEnable(GL_DEPTH_TEST)
    
    reset_game()
    glutMainLoop()

if __name__ == "__main__":
    main()