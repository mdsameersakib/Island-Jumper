import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# --- Camera State ---
camera_angle = 0.0
camera_distance = 200.0
camera_height = 100.0

# --- Player State (for drawing) ---
player_pos = [0.0, 0.0, 0.0] # Centered at the origin
player_angle = 0.0

def draw_player():
    """
    Draws a composite player character.
    The model's origin (0,0,0) is at the player's feet, centered between them.
    All parts are drawn upwards from this point.
    
    EDIT THIS FUNCTION TO CHANGE THE MODEL'S APPEARANCE
    """
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(-player_angle, 0, 1, 0)

    # --- Proportions ---
    torso_height = 20.0
    head_radius = 5.0
    leg_height = 15.0
    arm_height = 15.0

    # --- Legs ---
    glColor3f(0.1, 0.2, 0.8) # Blue
    for i in [-.8, .8]:
        glPushMatrix()
        glTranslatef(i * 4, 0, 0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 2.5, 2.5, leg_height, 10, 10)
        glPopMatrix()

    # --- Torso ---
    glColor3f(0.1, 0.8, 0.2) # Green
    glPushMatrix()
    glTranslatef(0, leg_height+10, 0)
    glScalef(12.0, torso_height, 6.0)
    glutSolidCube(1)
    glPopMatrix()

    # --- Head ---
    glColor3f(1.0, 0.8, 0.6) # Skin color
    glPushMatrix()
    glTranslatef(0, leg_height + 5 + torso_height, 0)
    glutSolidSphere(head_radius, 20, 20)
    glPopMatrix()

    # --- Arms ---
    glColor3f(1.0, 0.8, 0.6) # Skin color
    for i in [-1, 1]:
        glPushMatrix()
        glTranslatef(i * 7, leg_height + 5 + torso_height - 5, 0)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 2.0, 2.0, arm_height, 10, 10)
        glPopMatrix()

    glPopMatrix()

def display():
    """The main display callback."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # --- Setup Camera ---
    # Calculate camera position based on angle and distance
    cam_x = camera_distance * math.sin(math.radians(camera_angle))
    cam_z = camera_distance * math.cos(math.radians(camera_angle))
    # Use the new camera_height variable for the Y position
    gluLookAt(cam_x, camera_height, cam_z,  # Camera position
              0, 50, 0,                      # Look at the center of the model
              0, 1, 0)                      # Up is Y

    # --- Draw a simple grid for reference ---
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    for i in range(-100, 101, 20):
        glVertex3f(i, 0, -100)
        glVertex3f(i, 0, 100)
        glVertex3f(-100, 0, i)
        glVertex3f(100, 0, i)
    glEnd()

    # --- Draw the player model ---
    draw_player()

    glutSwapBuffers()

def reshape(w, h):
    """Window reshape callback."""
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h, 0.1, 1000.0) # Increased far clip plane
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def specialKeyListener(key, x, y):
    """Handle arrow key presses for rotation and zoom."""
    global camera_angle, camera_distance
    if key == GLUT_KEY_LEFT:
        camera_angle -= 5.0
    if key == GLUT_KEY_RIGHT:
        camera_angle += 5.0
    if key == GLUT_KEY_UP:
        camera_distance -= 5.0 # Zoom in
    if key == GLUT_KEY_DOWN:
        camera_distance += 5.0 # Zoom out
    glutPostRedisplay()

def keyboardListener(key, x, y):
    """Handle regular key presses for camera height."""
    global camera_height
    if key == b'w':
        camera_height += 5.0 # Move camera up
    if key == b's':
        camera_height -= 5.0 # Move camera down
    glutPostRedisplay()


def main():
    """Main function to set up the window and run the loop."""
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Character Model Viewer")

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutSpecialFunc(specialKeyListener)
    glutKeyboardFunc(keyboardListener) # Register the new listener

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.2, 1.0) # Dark blue background

    print("Controls:")
    print("  Left/Right Arrows: Rotate Camera")
    print("  Up/Down Arrows: Zoom In/Out")
    print("  'W'/'S' Keys: Move Camera Up/Down")

    glutMainLoop()

if __name__ == "__main__":
    main()
