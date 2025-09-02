import sys
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# --- Camera State ---
camera_angle = 0.0
camera_distance = 150.0
camera_height = 50.0

# --- Player Overall Position State ---
player_overall_pos = [0.0, 15.0, -10.0]

# --- Finalized Player Parts Data (Normalized from your images) ---
player_parts = {
    "torso": {
        "pos": [0.0, 5.0, 0.0],
        "rot": [-45.0, 0.0, 0.0], # Normalized -360 to 0
        "scale": [12.0, 20.0, 6.0],
        "color": [0.1, 0.8, 0.2]
    },
    "head": {
        "pos": [0.0, 14.0, 2.0],
        "rot": [0.0, 0.0, 0.0],
        "radius": 5.0,
        "color": [1.0, 0.8, 0.6]
    },
    "left_leg": {
        "pos": [-4.0, -9.0, 2.0],
        "rot": [40.0, -15.0, 0.0], # Normalized 400 to 40
        "length": 15.0,
        "radius": 2.5,
        "color": [0.1, 0.2, 0.8]
    },
    "right_leg": {
        "pos": [4.0, -9.0, 2.0],
        "rot": [40.0, 15.0, 0.0], # Normalized 400 to 40
        "length": 15.0,
        "radius": 2.5,
        "color": [0.1, 0.2, 0.8]
    },
    "left_arm": {
        "pos": [-4.0, 8.0, 1.0],
        "rot": [335.0, 210.0, 0.0], # Normalized 1415 to 335
        "length": 12.0,
        "radius": 2.0,
        "color": [1.0, 0.8, 0.6]
    },
    "right_arm": {
        "pos": [4.0, 8.0, 1.0],
        "rot": [335.0, 145.0, 0.0], # Normalized 695 to 335
        "length": 12.0,
        "radius": 2.0,
        "color": [1.0, 0.8, 0.6]
    }
}

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draws text on the screen at a specified 2D coordinate."""
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600)
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


def draw_boat():
    """Draws a hollow boat with wall thickness and no floor."""
    glPushMatrix()
    glTranslatef(0, 15, 0)
    
    glColor3f(0.4, 0.2, 0.0) # Brown color for the boat

    outer_radius = 15.0
    inner_radius = 13.0 # Slightly smaller for thickness
    length = 60.0
    segments = 20

    # --- Draw Outer and Inner Hulls ---
    for radius, color in [(outer_radius, [0.4, 0.2, 0.0]), (inner_radius, [0.3, 0.15, 0.0])]:
        glColor3fv(color)
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = math.pi * (i / segments) + math.pi
            y, x = radius * math.sin(angle), radius * math.cos(angle)
            glVertex3f(x, y, length / 2)
            glVertex3f(x, y, -length / 2)
        glEnd()

    # --- Draw the Rim connecting the hulls ---
    glColor3f(0.45, 0.25, 0.05)
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = math.pi * (i / segments)
        if angle >= 0: # Only draw the top rim
            outer_x, outer_y = outer_radius * math.cos(angle), outer_radius * math.sin(angle)
            inner_x, inner_y = inner_radius * math.cos(angle), inner_radius * math.sin(angle)
            glVertex3f(outer_x, 0, length / 2)
            glVertex3f(inner_x, 0, length / 2)
    glEnd()
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = math.pi * (i / segments)
        if angle >= 0:
            outer_x, outer_y = outer_radius * math.cos(angle), outer_radius * math.sin(angle)
            inner_x, inner_y = inner_radius * math.cos(angle), inner_radius * math.sin(angle)
            glVertex3f(outer_x, 0, -length / 2)
            glVertex3f(inner_x, 0, -length / 2)
    glEnd()


    # --- Draw the End Caps ---
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


def draw_player():
    """Draws the modular player character based on the dictionary."""
    glPushMatrix()
    # Use the new overall position variable
    glTranslatef(player_overall_pos[0], player_overall_pos[1], player_overall_pos[2])
    
    # --- Draw Torso ---
    part = player_parts["torso"]
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
    head = player_parts["head"]
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
        limb = player_parts[name]
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

def display():
    """The main display callback."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    cam_x = camera_distance * math.sin(math.radians(camera_angle))
    cam_z = camera_distance * math.cos(math.radians(camera_angle))
    gluLookAt(cam_x, camera_height, cam_z, 0, 20, 0, 0, 1, 0)

    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    for i in range(-100, 101, 20):
        glVertex3f(i, 0, -100); glVertex3f(i, 0, 100)
        glVertex3f(-100, 0, i); glVertex3f(100, 0, i)
    glEnd()

    draw_boat()
    draw_player()
    
    # --- Draw UI Text ---
    draw_text(10, 580, f"Player Pos: {player_overall_pos[0]:.1f}, {player_overall_pos[1]:.1f}, {player_overall_pos[2]:.1f}")
    
    glutSwapBuffers()

def reshape(w, h):
    """Window reshape callback."""
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / (h or 1), 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def specialKeyListener(key, x, y):
    """Handle arrow key presses for camera."""
    global camera_angle, camera_distance, camera_height
    if key == GLUT_KEY_LEFT: camera_angle -= 5.0
    if key == GLUT_KEY_RIGHT: camera_angle += 5.0
    if key == GLUT_KEY_UP: camera_height += 5.0
    if key == GLUT_KEY_DOWN: camera_height -= 5.0
    glutPostRedisplay()

def keyboardListener(key, x, y):
    """Handles regular key presses for moving the player."""
    global player_overall_pos
    if key == b'w': player_overall_pos[2] -= 1.0 # Forward
    if key == b's': player_overall_pos[2] += 1.0 # Backward
    if key == b'a': player_overall_pos[0] -= 1.0 # Left
    if key == b'd': player_overall_pos[0] += 1.0 # Right
    if key == b'r': player_overall_pos[1] += 1.0 # Up
    if key == b'f': player_overall_pos[1] -= 1.0 # Down
    glutPostRedisplay()

def main():
    """Main function to set up the window and run the loop."""
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Final Player Pose Viewer")
    
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutSpecialFunc(specialKeyListener)
    glutKeyboardFunc(keyboardListener)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.2, 1.0)
    
    print("--- Controls ---")
    print("Camera: Arrow Keys to rotate and move up/down")
    print("Player Position: W/A/S/D (XZ) and R/F (Y)")
    
    glutMainLoop()

if __name__ == "__main__":
    main()

