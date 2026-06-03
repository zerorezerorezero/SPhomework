import math

SCREEN_W = 1280
SCREEN_H = 720
FPS = 60

BODY_RADIUS = 28
LEG_SEG_LEN = 42
LEG_COUNT = 4
LEG_BASE_DEG = [330, 30, 150, 210]
HIP_RANGE = 80
KNEE_RANGE = 140

MAX_SPEED = 3.5
GAIT_CYCLE_FRAMES = 35
JUMP_POWER = 14
JUMP_FRAMES = 25

LIDAR_RAYS = 32
LIDAR_RANGE = 280

CANNON_LEN = 55
CANNON_W = 7
MAG_SIZE = 8
AUTO_LOAD_TICKS = 50
MAG_RELOAD_TICKS = 150
FIRE_COOLDOWN_TICKS = 15
PROJ_SPEED = 14

OBSTACLE_COUNT = 10
OBST_MIN_R = 18
OBST_MAX_R = 45

TERRAIN_TYPES = [
    {"name": "平地", "color": (80, 140, 60), "speed_factor": 1.0, "jump_factor": 1.0},
    {"name": "斜坡", "color": (160, 130, 70), "speed_factor": 0.6, "jump_factor": 0.8},
    {"name": "崎嶇地", "color": (120, 100, 80), "speed_factor": 0.5, "jump_factor": 0.7},
]

COXIA_L = 15
STEP_H = 50
STEP_D = 55
BODY_H = 30
