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

def draw_tree():
    glPushMatrix()
    glScalef(10.0, 10.0, 10.0)  # scale the whole tree

    # ----------------
    # Draw trunk upright along Y
    # ----------------
    glPushMatrix()
    glColor3f(0.55, 0.27, 0.07)  # brown
    trunk = gluNewQuadric()
    glRotatef(-90, 1, 0, 0)  # rotate cylinder to align with Y-axis
    # Make trunk longer (height=3.5)
    gluCylinder(trunk, 0.2, 0.15, 3.5, 20, 20)
    glPopMatrix()

    # ----------------
    # Draw 4 leaves from top of trunk
    # ----------------
    glColor3f(0.0, 0.8, 0.0)  # green
    glPushMatrix()
    glTranslatef(0.0, 3.5, 0.0)  # move to top of trunk (Y=3.5)

    leaf_length = 1.2  # shorter leaves
    leaf_width = 0.6   # wider triangles
    leaf_angle = 45  # tilt from vertical

    # Draw 4 coconuts, each at the base of a leaf

    # Align 4 leaves at equal angles, each with a coconut
    for i in range(4):
        angle_deg = i * 90.0
        glPushMatrix()
        glRotatef(angle_deg, 0, 1, 0)  # rotate around Y axis
        glRotatef(leaf_angle, 1, 0, 0) # tilt leaf
        # Coconut
        glPushMatrix()
        glTranslatef(0, -0.02, 0.6)
        glColor3f(0.35, 0.18, 0.07)
        glutSolidSphere(0.30, 12, 12)
        glPopMatrix()
        # Leaf
        glColor3f(0.0, 0.8, 0.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, 0)
        glVertex3f(leaf_width, 0.7, leaf_length)
        glVertex3f(-leaf_width, 0.7, leaf_length)
        glEnd()
        glPopMatrix()

    # Leaf 1 (+Z direction)
    glColor3f(0.0, 0.8, 0.0)  # green
    glPushMatrix()
    glRotatef(leaf_angle, 1, 0, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(leaf_width, 0.7, leaf_length)
    glVertex3f(-leaf_width, 0.7, leaf_length)
    glEnd()
    glPopMatrix()

    # Leaf 2 (-Z direction)
    glColor3f(0.0, 0.8, 0.0)  # green
    glPushMatrix()
    glRotatef(-leaf_angle, 1, 0, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(leaf_width, 0.7, -leaf_length)
    glVertex3f(-leaf_width, 0.7, -leaf_length)
    glEnd()
    glPopMatrix()

    # Leaf 3 (+X direction)
    glColor3f(0.0, 0.8, 0.0)  # green
    glPushMatrix()
    glRotatef(-leaf_angle, 0, 0, 1)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(leaf_length, 0.7, leaf_width)
    glVertex3f(leaf_length, 0.7, -leaf_width)
    glEnd()
    glPopMatrix()

    # Leaf 4 (-X direction)
    glColor3f(0.0, 0.8, 0.0)  # green
    glPushMatrix()
    glRotatef(leaf_angle, 0, 0, 1)
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 0, 0)
    glVertex3f(-leaf_length, 0.7, leaf_width)
    glVertex3f(-leaf_length, 0.7, -leaf_width)
    glEnd()
    glPopMatrix()

    glPopMatrix()  # pop leaves
    glPopMatrix()  # pop whole tree

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
    draw_tree()

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
