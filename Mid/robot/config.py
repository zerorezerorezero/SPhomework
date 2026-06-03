BODY_LENGTH = 100
BODY_WIDTH = 70
BODY_HEIGHT = 28

COXIA_L = 22
FEMUR_L = 55
TIBIA_L = 65

DEFAULT_BODY_HEIGHT = 75
STEP_LENGTH = 25
STEP_HEIGHT = 22

JOINT_LIMITS = {
    'coxia': (-50, 50),
    'femur': (-140, 40),
    'tibia': (-150, -10),
}

LEG_ORDER = ['RF', 'RB', 'LB', 'LF']

LEG_LAYOUT = {
    'RF': {'pos': (BODY_LENGTH / 2, -BODY_WIDTH / 2), 'side_sign': -1},
    'RB': {'pos': (-BODY_LENGTH / 2, -BODY_WIDTH / 2), 'side_sign': -1},
    'LB': {'pos': (-BODY_LENGTH / 2, BODY_WIDTH / 2), 'side_sign': 1},
    'LF': {'pos': (BODY_LENGTH / 2, BODY_WIDTH / 2), 'side_sign': 1},
}

TROT_PAIRS = [('RF', 'LB'), ('RB', 'LF')]
