from OpenGL.GL import * #(Nashita)
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

window_width = 1000
window_height = 800

difficulty_levels = ["EASY", "MEDIUM", "HARD"]
current_level = 0  # 0=Easy, 1=Medium, 2=Hard (auto-progression based on chocolates)
game_state = "MENU"
score = 0
lives = 5
special_chocolates_collected = 0  # Track special chocolates

GRID_LENGTH = 600
title_size = 20
grid_size = 20

cam_distance = 300
cam_height = 300
cam_angle = 45
cam_speed = 5
cam_height_speed = 10
min_cam_height = 50
camera_mode = "third_person"
cam_x_offset = 0  # Camera horizontal offset for A/D keys
cam_y_offset = 0  # Camera vertical offset for W/S keys
cam_offset_speed = 10  # Speed of camera panning

player_x = 0
player_y = 0
player_z = 0
player_angle = 0
player_speed = 8  # Faster player movement
gun_rotation_speed = 4

# Beautiful gradient colors for levels
level_colors = [
    [[0.95, 0.95, 1.0], [0.7, 0.9, 1.0]],
    [[0.9, 0.85, 1.0], [0.7, 0.6, 0.9]],
    [[0.85, 0.75, 1.0], [0.5, 0.4, 0.8]]
]

# Vibrant wall colors
wall_colors = [
    [[0.0, 1.0, 0.5], [0.0, 0.5, 1.0], [1.0, 0.0, 0.8], [0.8, 0.0, 1.0]],
    [[0.0, 0.9, 0.4], [0.0, 0.4, 0.9], [0.9, 0.0, 0.7], [0.7, 0.0, 0.9]],
    [[0.0, 0.8, 0.3], [0.0, 0.3, 0.8], [0.8, 0.0, 0.6], [0.6, 0.0, 0.8]]
]

# Main game variables - CHANGED
chocolate_pairs = []  # Now stores pairs of chocolates
chocolate_spawn_rate = 3.0  # Slower spawn rate
last_chocolate_time = 0
chocolate_fall_speed = 2.0  # Slower fall speed
catch_distance = 45
catcher_size = 30
chocolates_collected = 0
chocolates_missed = 0
max_misses = 2  # 2 misses = -1 life
spawn_radius = 80  # Chocolates spawn within this radius of player

# Special golden chocolate with pulsing glow
golden_chocolate_active = False
golden_chocolate_pos = [0, 0, 0]
golden_spawn_interval = 10
chocolates_until_golden = 5

# Thieves system - CHANGED
thieves = []
thief_active = False  # Only one thief at a time
thief_spawn_rate = 25.0  # Spawn rate for thieves
last_thief_time = 0
thief_speed = 0.3  # Very slow walking speed
thief_size = 15
thief_catch_distance = 20
thief_target_x = 0  # Thief moves towards initial catcher position
thief_target_y = 0

# Bomb system for HARD level
bombs = []  # List of falling bombs
bomb_spawn_rate = 8.0  # Bombs spawn every 8 seconds in hard mode
last_bomb_time = 0
bomb_fall_speed = 2.0

# Bonus game variables
bonus_game_active = False
bonus_score = 0
bonus_lives_earned = 0
bonus_distance = 0
bonus_player_lane = 1
bonus_speed = 1.5  # SLOWER initial speed
bonus_max_speed = 3.0  # SLOWER max speed
bonus_acceleration = 0.005  # SLOWER acceleration

bonus_obstacles = []
bonus_treasures = []  # Golden treasures to collect
bonus_spawn_distance = 100
bonus_last_spawn = 0
bonus_lane_width = 40
bonus_obstacle_spacing = 120  # More space between obstacles

# Grace period before obstacles appear
bonus_start_time = 0
bonus_grace_period = 10.0  # 10 seconds of no obstacles

# Treasure collection system
bonus_treasures_collected = 0
bonus_treasures_needed_for_life = 5

# Obstacle hit tracking
bonus_hits_taken = 0
bonus_max_hits = 3  # Can hit 3 obstacles before game ends

# Jumping mechanics (not used, but keeping for compatibility)
bonus_player_z = 0
bonus_is_jumping = False
bonus_jump_velocity = 0
bonus_gravity = -1.0
bonus_jump_force = 12
bonus_ground_level = 0

lives_threshold = 100
lives_collected_in_bonus = 0

# Cheat mode
cheat_mode = False
cheat_speed = 12  # Speed for auto-movement in cheat mode

# Animation variables
pulse_time = 0
sparkle_time = 0

def init():
    pass

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, window_width / window_height, 1.0, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if bonus_game_active:
        # Temple run style camera - behind and above the player
        eye_x = (bonus_player_lane - 1) * bonus_lane_width
        eye_y = -100  # Behind the player
        eye_z = 50    # Above the player
        look_x = (bonus_player_lane - 1) * bonus_lane_width
        look_y = 150  # Looking forward
        look_z = 20   # Looking slightly down
        gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 0, 1)
    else:
        if camera_mode == "first_person":
            eye_x = player_x + cam_x_offset
            eye_y = player_y + cam_y_offset
            eye_z = player_z + 25
            look_x = eye_x
            look_y = eye_y + 10
            look_z = eye_z + 50
            gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 0, 1)
        else:
            cam_x = cam_distance * math.sin(math.radians(cam_angle)) + cam_x_offset
            cam_y = -cam_distance * math.cos(math.radians(cam_angle)) + cam_y_offset
            cam_z = cam_height
            gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
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

def draw_checkerboard():
    color1, color2 = level_colors[current_level]
    for i in range(-grid_size//2, grid_size//2):
        for j in range(-grid_size//2, grid_size//2):
            if (i + j) % 2 == 0:
                glColor3f(*color1)
            else:
                glColor3f(*color2)
            glBegin(GL_QUADS)
            glVertex3f(i*title_size, j*title_size, 0)
            glVertex3f((i+1)*title_size, j*title_size, 0)
            glVertex3f((i+1)*title_size, (j+1)*title_size, 0)
            glVertex3f(i*title_size, (j+1)*title_size, 0)
            glEnd()

def draw_boundaries():
    wall_height = 40
    wall_thickness = 2
    colors = wall_colors[current_level]

    for idx, color in enumerate(colors):
        glColor3f(*color)
        glPushMatrix()
        if idx == 0:
            glTranslatef(grid_size//2 * title_size, 0, wall_height/2)
            glScalef(wall_thickness, grid_size*title_size, wall_height)
        elif idx == 1:
            glTranslatef(-grid_size//2 * title_size, 0, wall_height/2)
            glScalef(wall_thickness, grid_size*title_size, wall_height)
        elif idx == 2:
            glTranslatef(0, grid_size//2 * title_size, wall_height/2)
            glScalef(grid_size*title_size, wall_thickness, wall_height)
        else:
            glTranslatef(0, -grid_size//2 * title_size, wall_height/2)
            glScalef(grid_size*title_size, wall_thickness, wall_height)
        glutSolidCube(1)
        glPopMatrix()

def draw_player_with_catcher():
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z + 5)
    
    glColor3f(0.2, 0.7, 1.0)
    glPushMatrix()
    glScalef(12, 12, 12)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(1.0, 0.85, 0.7)
    glPushMatrix()
    glTranslatef(0, 0, 12)
    glutSolidSphere(7, 20, 20)
    glPopMatrix()
    
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(-3, 5, 14)
    glutSolidSphere(1, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(3, 5, 14)
    glutSolidSphere(1, 10, 10)
    glPopMatrix()
    
    # Simple square bucket catcher
    glColor3f(0.6, 0.4, 0.2)  # Brown bucket color
    glPushMatrix()
    glTranslatef(0, 0, 18)
    
    # Bucket bottom
    glPushMatrix()
    glScalef(catcher_size*1.2, catcher_size*1.2, 0.5)
    glutSolidCube(1)
    glPopMatrix()
    
    # Bucket walls (4 sides)
    wall_thickness = 0.3
    wall_height = 4
    
    # Front wall
    glPushMatrix()
    glTranslatef(0, catcher_size*0.6, wall_height/2)
    glScalef(catcher_size*1.2, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()
    
    # Back wall
    glPushMatrix()
    glTranslatef(0, -catcher_size*0.6, wall_height/2)
    glScalef(catcher_size*1.2, wall_thickness, wall_height)
    glutSolidCube(1)
    glPopMatrix()
    
    # Left wall
    glPushMatrix()
    glTranslatef(-catcher_size*0.6, 0, wall_height/2)
    glScalef(wall_thickness, catcher_size*1.2, wall_height)
    glutSolidCube(1)
    glPopMatrix()
    
    # Right wall
    glPushMatrix()
    glTranslatef(catcher_size*0.6, 0, wall_height/2)
    glScalef(wall_thickness, catcher_size*1.2, wall_height)
    glutSolidCube(1)
    glPopMatrix()
    
    glPopMatrix()
    glPopMatrix()

def draw_menu():
    pulse = abs(math.sin(pulse_time * 2))
    glColor3f(1.0, 0.8 + pulse * 0.2, 0.0)
    draw_text(window_width/2 - 200, window_height - 80, "CHOCOLATE CATCHER 3D", GLUT_BITMAP_HELVETICA_18)
    
    glColor3f(0.8, 0.8, 1.0)
    controls_y = 450
    draw_text(window_width/2 - 100, controls_y, "GAME INFO:", GLUT_BITMAP_HELVETICA_18)
    draw_text(window_width/2 - 250, controls_y - 40, "Start at EASY level, progress automatically!", GLUT_BITMAP_HELVETICA_18)
    draw_text(window_width/2 - 250, controls_y - 60, "5 chocolates -> MEDIUM (1 thief appears)", GLUT_BITMAP_HELVETICA_18)
    draw_text(window_width/2 - 250, controls_y - 80, "10 chocolates -> HARD (thieves + bombs!)", GLUT_BITMAP_HELVETICA_18)
    
    glColor3f(1.0, 1.0, 0.3)
    draw_text(window_width/2 - 100, controls_y - 120, "CONTROLS:", GLUT_BITMAP_HELVETICA_18)
    draw_text(window_width/2 - 250, controls_y - 150, "Arrow Keys: Move player to catch chocolates", GLUT_BITMAP_HELVETICA_18)
    draw_text(window_width/2 - 250, controls_y - 170, "Catch at least one chocolate per pair!", GLUT_BITMAP_HELVETICA_18)
    draw_text(window_width/2 - 250, controls_y - 190, "Avoid BOMBS in hard mode!", GLUT_BITMAP_HELVETICA_18)
    draw_text(window_width/2 - 250, controls_y - 210, "Thieves steal 2 collected chocolates!", GLUT_BITMAP_HELVETICA_18)
    draw_text(window_width/2 - 250, controls_y - 230, "Catch GOLDEN chocolate for BONUS GAME!", GLUT_BITMAP_HELVETICA_18)
    draw_text(window_width/2 - 250, controls_y - 260, "S: Restart | M: Menu", GLUT_BITMAP_HELVETICA_18)
    
    pulse2 = abs(math.sin(pulse_time * 3))
    glColor3f(pulse2, 1.0, pulse2)
    draw_text(window_width/2 - 80, 80, "Press ENTER to start!", GLUT_BITMAP_HELVETICA_18)

def spawn_chocolate_pair():
    """Spawn two chocolates near the player's current position"""
    # Spawn chocolates within spawn_radius of player
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(20, spawn_radius)
    
    base_x = player_x + distance * math.cos(angle)
    base_y = player_y + distance * math.sin(angle)
    z = 200
    
    # Clamp to grid bounds
    half_grid = grid_size//2 * title_size - 40
    base_x = max(-half_grid, min(half_grid, base_x))
    base_y = max(-half_grid, min(half_grid, base_y))
    
    # Create two chocolates with slight offset
    offset = 25
    chocolates = []
    
    for i in range(2):
        if i == 0:
            x = base_x - offset
            y = base_y
        else:
            x = base_x + offset
            y = base_y
        
        # Clamp each chocolate
        x = max(-half_grid, min(half_grid, x))
        y = max(-half_grid, min(half_grid, y))
        
        color = [
            random.uniform(0.5, 1.0),
            random.uniform(0.3, 0.7),
            random.uniform(0.1, 0.4)
        ]
        rotation = random.uniform(0, 360)
        size = random.uniform(7, 11)
        
        chocolates.append({
            'x': x, 'y': y, 'z': z,
            'color': color, 'rotation': rotation, 'size': size,
            'caught': False
        })
    
    chocolate_pairs.append(chocolates)

def spawn_golden_chocolate():
    global golden_chocolate_active, golden_chocolate_pos
    
    if golden_chocolate_active:
        return
    
    # Spawn near player
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(30, spawn_radius)
    
    x = player_x + distance * math.cos(angle)
    y = player_y + distance * math.sin(angle)
    z = 200
    
    half_grid = grid_size//2 * title_size - 40
    x = max(-half_grid, min(half_grid, x))
    y = max(-half_grid, min(half_grid, y))
    
    golden_chocolate_pos = [x, y, z, 0]
    golden_chocolate_active = True

def check_win_condition():
    """Check if player has won by collecting 30 chocolates"""
    global game_state
    
    if chocolates_collected >= 30:
        game_state = "WIN"
        print(f"CONGRATULATIONS! You won by collecting 30 chocolates!")

def check_level_progression():
    """Auto-upgrade level based on chocolates collected"""
    global current_level
    
    if chocolates_collected >= 10 and current_level < 2:
        current_level = 2  # HARD
        print(f"Level upgraded to HARD! Bombs and thieves incoming!")
    elif chocolates_collected >= 5 and current_level < 1:
        current_level = 1  # MEDIUM
        print(f"Level upgraded to MEDIUM! Thieves will appear!")

def spawn_bomb():
    """Spawn a bomb near player position (HARD level only)"""
    global bombs
    
    # Spawn near player
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(20, spawn_radius)
    
    x = player_x + distance * math.cos(angle)
    y = player_y + distance * math.sin(angle)
    z = 200
    
    half_grid = grid_size//2 * title_size - 40
    x = max(-half_grid, min(half_grid, x))
    y = max(-half_grid, min(half_grid, y))
    
    bombs.append({'x': x, 'y': y, 'z': z, 'rotation': 0})

def spawn_thief():
    """Spawn thief at edge, moving towards initial catcher position (0,0)"""
    global thief_active, thieves
    
    # Only one thief at a time
    if thief_active:
        return
    
    half_grid = grid_size//2 * title_size - 40
    
    edge = random.choice(['top', 'bottom', 'left', 'right'])
    
    if edge == 'top':
        x = random.uniform(-half_grid, half_grid)
        y = half_grid
    elif edge == 'bottom':
        x = random.uniform(-half_grid, half_grid)
        y = -half_grid
    elif edge == 'left':
        x = -half_grid
        y = random.uniform(-half_grid, half_grid)
    else:
        x = half_grid
        y = random.uniform(-half_grid, half_grid)
    
    z = 0
    
    # Random walking direction (angle in radians)
    direction = math.atan2(thief_target_y - y, thief_target_x - x)  # Direction towards (0,0)
    # Store: [x, y, z, edge, direction, time_until_direction_change]
    thieves.append([x, y, z, edge, direction, random.uniform(3, 6)])
    thief_active = True

def update_chocolates():
    global chocolate_pairs, chocolates_collected, chocolates_missed, lives
    global chocolates_until_golden, game_state
    
    pairs_to_remove = []
    
    for pair_idx, pair in enumerate(chocolate_pairs):
        for choc in pair:
            if not choc['caught']:
                choc['z'] -= chocolate_fall_speed
                choc['rotation'] = (choc['rotation'] + 3) % 360
                
                # Check if caught
                dx = player_x - choc['x']
                dy = player_y - choc['y']
                dz = (player_z + 20) - choc['z']
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if dist < catch_distance and choc['z'] > 5 and choc['z'] < 35:
                    choc['caught'] = True
                    chocolates_collected += 1
                    chocolates_until_golden -= 1
                    
                    # Check for win condition
                    check_win_condition()
                    
                    # Check for level progression
                    check_level_progression()
                    
                    if chocolates_until_golden <= 0:
                        spawn_golden_chocolate()
                        chocolates_until_golden = 5
        
        # Check if pair should be removed (both below ground)
        if all(choc['z'] < 0 for choc in pair):
            # Check if at least ONE was missed (not both caught)
            if not all(choc['caught'] for choc in pair):
                chocolates_missed += 1
                print(f"Missed a chocolate! Total missed: {chocolates_missed}")
                
                # Every 2 missed chocolates = -1 life
                if chocolates_missed >= max_misses:
                    lives -= 1
                    chocolates_missed = 0  # Reset counter after losing a life
                    print(f"Lost 1 life! Lives remaining: {lives}")
                    
                    if lives <= 0:
                        print("All 5 lives lost! Game Over!")
                        game_state = "GAME_OVER"
            
            pairs_to_remove.append(pair_idx)
    
    for idx in sorted(pairs_to_remove, reverse=True):
        if idx < len(chocolate_pairs):
            chocolate_pairs.pop(idx)

def update_thieves():
    """Thieves move towards (0,0) and steal chocolates from catcher"""
    global thieves, chocolates_collected, game_state, thief_active
    
    thieves_to_remove = []
    half_grid = grid_size//2 * title_size - 40
    
    for i, thief in enumerate(thieves):
        # Move towards initial position (0,0)
        dx = thief_target_x - thief[0]
        dy = thief_target_y - thief[1]
        dist_to_target = math.sqrt(dx*dx + dy*dy)
        
        if dist_to_target > 5:  # Still moving towards target
            thief[0] += (dx / dist_to_target) * thief_speed
            thief[1] += (dy / dist_to_target) * thief_speed
        
        # Check if player collides with thief
        dx_player = player_x - thief[0]
        dy_player = player_y - thief[1]
        dist_to_player = math.sqrt(dx_player*dx_player + dy_player*dy_player)
        
        if dist_to_player < thief_catch_distance:
            thieves_to_remove.append(i)
            # Thief steals 2 chocolates
            if chocolates_collected >= 2:
                chocolates_collected -= 2
                print(f"Thief stole 2 chocolates! Remaining: {chocolates_collected}")
            else:
                chocolates_collected = 0
                print(f"Thief stole all chocolates!")
        
        # Remove if reached target or out of bounds
        if dist_to_target < 5 or abs(thief[0]) > half_grid + 50 or abs(thief[1]) > half_grid + 50:
            thieves_to_remove.append(i)
    
    for i in sorted(thieves_to_remove, reverse=True):
        if i < len(thieves):
            thieves.pop(i)
            thief_active = False  # Allow new thief to spawn (Nashita)

def update_golden_chocolate():
    global golden_chocolate_active, golden_chocolate_pos, bonus_game_active, special_chocolates_collected
    
    if not golden_chocolate_active:
        return
    
    golden_chocolate_pos[2] -= chocolate_fall_speed * 0.5
    golden_chocolate_pos[3] = (golden_chocolate_pos[3] + 5) % 360
    
    dx = player_x - golden_chocolate_pos[0]
    dy = player_y - golden_chocolate_pos[1]
    dz = (player_z + 20) - golden_chocolate_pos[2]
    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    if dist < catch_distance + 10 and golden_chocolate_pos[2] > 5 and golden_chocolate_pos[2] < 35:
        golden_chocolate_active = False
        special_chocolates_collected += 1
        start_bonus_game()  # This will now properly start bonus game
    
    elif golden_chocolate_pos[2] < 0:
        golden_chocolate_active = False

def update_bombs():
    """Update falling bombs (HARD level only)"""
    global bombs, lives, game_state
    
    bombs_to_remove = []
    
    for i, bomb in enumerate(bombs):
        bomb['z'] -= bomb_fall_speed
        bomb['rotation'] = (bomb['rotation'] + 5) % 360
        
        # Check if caught (BAD!)
        dx = player_x - bomb['x']
        dy = player_y - bomb['y']
        dz = (player_z + 20) - bomb['z']
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if dist < catch_distance and bomb['z'] > 5 and bomb['z'] < 35:
            bombs_to_remove.append(i)
            lives -= 1
            print(f"BOMB CAUGHT! Lost 1 life! Lives: {lives}")
            
            if lives <= 0:
                game_state = "GAME_OVER"
        
        # Remove if below ground
        if bomb['z'] < 0:
            bombs_to_remove.append(i)
    
    
    for i in sorted(bombs_to_remove, reverse=True):
        if i < len(bombs):
            bombs.pop(i) #(Nashita)
def draw_chocolate(choc):
    if choc['caught']:
        return
    
    x, y, z = choc['x'], choc['y'], choc['z']
    color = choc['color']
    rotation = choc['rotation']
    size = choc['size']
    
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 1)
    
    glColor3f(color[0] * 0.6, color[1] * 0.6, color[2] * 0.6)
    glPushMatrix()
    glScalef(size*1.0, size*0.8, size*0.6)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8)
    glPushMatrix()
    glScalef(size*0.95, size*0.75, size*0.55)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(*color)
    glPushMatrix()
    glScalef(size*0.9, size*0.7, size*0.5)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(min(1.0, color[0]*1.5), min(1.0, color[1]*1.5), min(1.0, color[2]*1.5))
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (i + j) % 2 == 0:
                glPushMatrix()
                glTranslatef(i * size * 0.25, j * size * 0.2, size * 0.3)
                glutSolidSphere(size * 0.1, 10, 10)
                glPopMatrix()
    
    glPopMatrix()

def draw_golden_chocolate():
    if not golden_chocolate_active:
        return
    
    x, y, z, rotation = golden_chocolate_pos
    
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 1)
    
    pulse = abs(math.sin(pulse_time * 6))
    glow_size = 12 + pulse * 4
    
    glColor3f(1.0, 0.5, 0.0)
    glutSolidSphere(glow_size + 6, 20, 20)
    
    glColor3f(1.0, 0.8, 0.0)
    glutSolidSphere(glow_size + 4, 20, 20)
    
    glColor3f(1.0, 1.0, 0.0)
    glutSolidSphere(glow_size + 2, 20, 20)
    
    glColor3f(1.0, 1.0, 0.5)
    glutSolidSphere(glow_size, 20, 20)
    
    glColor3f(1.0, 0.84, 0.0)
    glPushMatrix()
    glScalef(7, 5.5, 4)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(1.0, 1.0, 0.5)
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (i + j) % 2 == 0:
                glPushMatrix()
                glTranslatef(i * 1.5, j * 1.2, 1.5)
                glutSolidSphere(0.6, 10, 10)
                glPopMatrix()
    
    glColor3f(1.0, 1.0, 1.0)
    for angle in range(0, 360, 45):
        glPushMatrix()
        glRotatef(angle + rotation * 2, 0, 0, 1)
        glTranslatef(10, 0, 0)
        glutSolidSphere(0.8, 10, 10)
        glPopMatrix()
    
    glPopMatrix()

def draw_bomb(bomb):
    x, y, z = bomb['x'], bomb['y'], bomb['z']
    rotation = bomb['rotation']
    
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 1, 1, 0)
    
    pulse = abs(math.sin(pulse_time * 10))
    
    glColor3f(1.0, 0.0, 0.0)
    glutSolidSphere(12 + pulse * 2, 20, 20)
    
    glColor3f(0.5, 0.0, 0.0)
    glutSolidSphere(10, 20, 20)
    
    glColor3f(0.1, 0.1, 0.1)
    glutSolidSphere(8, 20, 20)
    
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 8)
    glutSolidSphere(3, 10, 10)
    glPopMatrix()
    
    glColor3f(0.0, 0.0, 0.0)
    for angle in range(0, 360, 90):
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glTranslatef(10, 0, 0)
        glutSolidSphere(1.5, 10, 10)
        glPopMatrix()
    
    glPopMatrix()

def draw_thief(x, y, z, edge, direction=0, timer=0):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    glColor3f(0.4, 0.25, 0.1)
    glPushMatrix()
    glTranslatef(-3, 0, 6)
    glScalef(3, 3, 12)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(3, 0, 6)
    glScalef(3, 3, 12)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, 0, 18)
    glScalef(10, 6, 12)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(-7, 0, 18)
    glScalef(3, 3, 10)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(7, 0, 18)
    glScalef(3, 3, 10)
    glutSolidCube(1)
    glPopMatrix()
    
    glColor3f(0.9, 0.75, 0.6)
    glPushMatrix()
    glTranslatef(0, 0, 28)
    glutSolidSphere(5, 20, 20)
    glPopMatrix()
    
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(-2, 4, 28)
    glutSolidSphere(0.8, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(2, 4, 28)
    glutSolidSphere(0.8, 10, 10)
    glPopMatrix()
    
    pulse = abs(math.sin(pulse_time * 8))
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 35 + pulse * 2)
    glRotatef(180, 1, 0, 0)
    glutSolidSphere(4, 10, 10)
    glPopMatrix()
    
    glPopMatrix()

def draw_chocolates():
    for pair in chocolate_pairs:
        for choc in pair:
            draw_chocolate(choc)

def draw_thieves():
    for thief in thieves:
        draw_thief(*thief)

def draw_bombs():
    for bomb in bombs:
        draw_bomb(bomb)

def start_bonus_game():
    global bonus_game_active, bonus_score, bonus_distance, bonus_player_lane
    global bonus_obstacles, bonus_treasures, bonus_last_spawn, bonus_speed
    global lives_collected_in_bonus, bonus_lives_earned
    global chocolate_pairs, thieves, golden_chocolate_active, bombs, thief_active
    global bonus_start_time, bonus_treasures_collected, bonus_hits_taken
    global bonus_player_z, bonus_is_jumping, bonus_jump_velocity
    
    chocolate_pairs = []
    thieves = []
    bombs = []
    thief_active = False
    golden_chocolate_active = False
    
    bonus_game_active = True
    bonus_score = 0
    bonus_distance = 0
    bonus_player_lane = 1
    bonus_obstacles = []
    bonus_treasures = []
    bonus_last_spawn = 0
    bonus_speed = 1.5
    lives_collected_in_bonus = 0
    bonus_lives_earned = 0
    bonus_start_time = time.time()
    bonus_treasures_collected = 0
    bonus_hits_taken = 0
    
    bonus_player_z = 0
    bonus_is_jumping = False
    bonus_jump_velocity = 0
    
    print("Bonus level started! You have 10 seconds of safe travel before obstacles appear!")

def end_bonus_game():
    global bonus_game_active, lives, bonus_treasures_collected, game_state
    global last_chocolate_time, last_thief_time, last_bomb_time, thief_active
    
    bonus_game_active = False
    
    if bonus_treasures_collected >= bonus_treasures_needed_for_life:
        lives += 1
        print(f"Bonus level complete! Collected {bonus_treasures_collected} treasures. +1 Life! Total lives: {lives}")
    else:
        print(f"Bonus level ended. Collected {bonus_treasures_collected}/5 treasures. No life earned.")
    
    game_state = "PLAYING"
    
    last_chocolate_time = time.time()
    last_thief_time = time.time()
    last_bomb_time = time.time()
    thief_active = False
    
    print("Returning to main game...")

def spawn_bonus_items(distance):
    num_obstacles = random.randint(1, 2)
    for _ in range(num_obstacles):
        lane = random.choice([0, 1, 2])
        x = (lane - 1) * bonus_lane_width
        y = distance + random.uniform(-30, 30)
        bonus_obstacles.append([x, y, 0, False])
    
    num_treasures = random.randint(1, 2)
    for _ in range(num_treasures):
        if random.random() < 0.7:
            lane = random.choice([0, 1, 2])
            x = (lane - 1) * bonus_lane_width
            y = distance + random.uniform(-40, 40)
            bonus_treasures.append([x, y, 5])

def update_bonus_game():
    global bonus_distance, bonus_obstacles, bonus_treasures, bonus_last_spawn
    global bonus_score, bonus_speed, bonus_treasures_collected, bonus_hits_taken
    global bonus_start_time, bonus_player_z, bonus_is_jumping, bonus_jump_velocity
    
    if bonus_is_jumping:
        bonus_player_z += bonus_jump_velocity
        bonus_jump_velocity += bonus_gravity
        
        if bonus_player_z <= bonus_ground_level:
            bonus_player_z = bonus_ground_level
            bonus_is_jumping = False
            bonus_jump_velocity = 0
    
    if bonus_speed < bonus_max_speed:
        bonus_speed += bonus_acceleration
    
    bonus_distance += bonus_speed
    
    time_elapsed = time.time() - bonus_start_time
    grace_period_active = time_elapsed < bonus_grace_period
    
    obstacles_to_remove = []
    for i, obs in enumerate(bonus_obstacles):
        obs[1] -= bonus_speed
        
        if not grace_period_active:
            if abs(obs[1]) < 20 and abs(obs[1]) > -20:
                player_x_bonus = (bonus_player_lane - 1) * bonus_lane_width
                if abs(player_x_bonus - obs[0]) < 20 and bonus_player_z < 25:
                    if not obs[3]:
                        obs[3] = True
                        bonus_hits_taken += 1
                        print(f"Hit obstacle! {bonus_hits_taken}/{bonus_max_hits} hits taken")
                        
                        if bonus_hits_taken >= bonus_max_hits:
                            print("Hit 3 obstacles! Returning to main game...")
                            end_bonus_game()
                            return
        
        if obs[1] < -50:
            obstacles_to_remove.append(i)
    
    for i in sorted(obstacles_to_remove, reverse=True):
        bonus_obstacles.pop(i)
    
    treasures_to_remove = []
    for i, treasure in enumerate(bonus_treasures):
        treasure[1] -= bonus_speed
        treasure[2] = 5 + math.sin(treasure[1] * 0.1) * 2
        
        if abs(treasure[1]) < 20 and abs(treasure[1]) > -20:
            player_x_bonus = (bonus_player_lane - 1) * bonus_lane_width
            if abs(player_x_bonus - treasure[0]) < 20:
                treasures_to_remove.append(i)
                bonus_treasures_collected += 1
                print(f"Treasure collected! {bonus_treasures_collected}/{bonus_treasures_needed_for_life}")
                
                if bonus_treasures_collected >= bonus_treasures_needed_for_life:
                    print("Collected 5 treasures! Earning 1 life!")
                    end_bonus_game()
                    return
        
        if treasure[1] < -50:
            treasures_to_remove.append(i)
    
    for i in sorted(treasures_to_remove, reverse=True):
        bonus_treasures.pop(i)
    
    if not grace_period_active and bonus_distance - bonus_last_spawn > bonus_obstacle_spacing:
        spawn_bonus_items(bonus_last_spawn + bonus_obstacle_spacing * 6)
        bonus_last_spawn += bonus_obstacle_spacing

def draw_bonus_ground():
    glBegin(GL_QUADS)
    glColor3f(0.85, 0.75, 0.55)
    glVertex3f(-200, -100, 0)
    glVertex3f(200, -100, 0)
    glColor3f(0.75, 0.65, 0.45)
    glVertex3f(200, 600, 0)
    glVertex3f(-200, 600, 0)
    glEnd()
    
    glColor3f(1.0, 1.0, 1.0)
    for x in [-bonus_lane_width, bonus_lane_width]:
        glBegin(GL_LINES)
        for y in range(-100, 600, 30):
            glVertex3f(x, y, 0.1)
            glVertex3f(x, y + 15, 0.1)
        glEnd()
    
    glColor3f(1.0, 1.0, 0.0)
    glBegin(GL_LINES)
    for y in range(-100, 600, 30):
        glVertex3f(0, y, 0.1)
        glVertex3f(0, y + 15, 0.1)
    glEnd()

def draw_bonus_obstacles():
    for obs in bonus_obstacles:
        x, y, z, hit = obs
        glPushMatrix()
        glTranslatef(x, y, z + 12)
        
        if hit:
            glColor3f(0.4, 0.2, 0.2)
        else:
            glColor3f(0.2, 0.2, 0.2)
        
        glPushMatrix()
        glScalef(18, 15, 20)
        glutSolidCube(1)
        glPopMatrix()
        
        glColor3f(0.15, 0.15, 0.15)
        glPushMatrix()
        glTranslatef(-6, -4, 8)
        glutSolidSphere(5, 12, 12)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(6, 4, 8)
        glutSolidSphere(4, 12, 12)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, 0, 12)
        glutSolidSphere(4.5, 12, 12)
        glPopMatrix()
        
        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(0, 0, -10)
        glScalef(20, 17, 2)
        glutSolidCube(1)
        glPopMatrix()
        
        glPopMatrix()

