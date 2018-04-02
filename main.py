#
#   DATA
#


ships_type = {
    "Scout": {
        "size": 9,
        "life": 3,
        "attack": 1,
        "range": 3,
        "cost:": 3
    },
    "Warship": {
        "size": 21,
        "life": 18,
        "attack": 3,
        "range": 5,
        "cost": 9
    },
    "Excavator-S": {
        "size": 1,
        "tonnage": 1,
        "life": 2,
        "cost": 1
    },
    "Excavator-M": {
        "size": 5,
        "tonnage": 4,
        "life": 3,
        "cost": 2
    },
    "Excavator-L": {
        "size": 9,
        "tonnage": 8,
        "life": 6,
        "cost": 4
    }
}

ships_structure = {
    "Scout": [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)],
    "Warship": [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1), (-2, -1), (-2, 0),
                (-2, 1), (-1, 2), (0, 2), (1, 2), (2, 1), (2, 0), (2, -1), (1, -2), (0, -2), (-1, -2)],
    "Excavator-S": [(0, 0)],
    "Excavator-M": [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)],
    "Excavator-L": [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (2, 0), (0, 2), (-2, 0), (0, -2)]
}

ships_ingame = {
    'thom': {
        'type': 'Scout',
        'position': [12, 12],
        'life': 4
    },
    'cyril': {
        'type': 'Warship',
        'position': [6, 17],
        'life': 21
    },
    'two': {
        'type': 'Excavator-M',
        'position': [23, 3],
        'life': 3,
        'ore': 0
    },
    'one': {
        'type': 'Excavator-L',
        'position': [24, 24],
        'life': 6,
        'ore': 5
    },
    'three': {
        'type': 'Excavator-L',
        'position': [27, 27],
        'life': 6,
        'ore': 0
    }
}

# Deprecated
ships_team = {
    'player_1': ['thom', 'cyril'],
    'player_2': ['one', 'two', 'three']
}

players = {
    'player_1': {
        'type': 'human',
        'ore': 10,
        'ships': []
    },
    'player_2': {
        'type': 'ia',
        'ore': 5,
        'ships': []
    }
}

game_board = {
    'size': [30, 30],
    'portals': [
        {
            'position': [15, 6],
            'life': 100,
            'ships_locked': []
        },
        {
            'position': [15, 24],
            'life': 100,
            'ships_locked': []
        }
    ],
    'asteroids': [
        {
            'position': [5, 5],
            'ore': 5,
            'rate': 1,
            'ships_locked': []
        },
        {
            'position': [25, 5],
            'ore': 5,
            'rate': 2,
            'ships_locked': []
        },
        {
            'position': [5, 25],
            'ore': 5,
            'rate': 2,
            'ships_locked': []
        },
        {
            'position': [25, 25],
            'ore': 5,
            'rate': 1,
            'ships_locked': []
        }
    ]
}


#
#   Get DATA functions
#

# Ships
def get_ship_structure(ship_type, center_position):
    base_structure = ships_structure[ship_type]
    new_structure = []

    for pos in base_structure:
        new_structure.append((center_position[0] + int(pos[0]), center_position[1] + int(pos[1])))

    return new_structure


def get_ship_radius(ship_type):
    types = {
        'Scout': 1,
        'Warship': 2,
        'Excavator-S': 0,
        'Excavator-M': 1,
        'Excavator-L': 2
    }

    return types[ship_type]


#
#   Game functions
#


def start_game(info):
    for i in range(info['size'][0]):
        sub_list = []
        for j in range(info['size'][1]):
            sub_list.append('◻')
        info['board'].append(sub_list)


def add_ships_to_board(info, ships):
    for ship in ships:
        ship_x = ships[ship]['position'][0]
        ship_y = ships[ship]['position'][1]
        ship_type = ships[ship]['type']

        structure = ships_structure[ship_type]

        for pos in structure:
            info['board'][ship_x + int(pos[0])][ship_y + int(pos[1])] = '◼'


def add_asteroids_to_board(info):
    for asteroid in info['asteroids']:
        pos_x = asteroid['pos'][0]
        pos_y = asteroid['pos'][1]
        info['board'][int(pos_x)][int(pos_y)] = '✹'


def add_portals_to_board(info):
    for portal in info['portals']:
        pos_x = portal['pos'][0]
        pos_y = portal['pos'][1]
        for i in range(-2, 2):
            for j in range(-2, 2):
                info['board'][int(pos_x) + i][int(pos_y) + j] = '◍'


def move_ship(info, ships, ship_name, pos_x, pos_y):
    current_pos = ships[ship_name]['position']
    ship_type = ships[ship_name]['type']
    ship_radius = get_ship_radius(ship_type)

    if abs(int(current_pos[0] - pos_x)) <= 1 and abs(int(current_pos[1] - pos_y)) <= 1:
        if pos_x - ship_radius >= 0 and pos_y - ship_radius >= 0 and pos_x + ship_radius <= int(info['size'][0]) - 1 \
                and pos_y + ship_radius <= int(info['size'][1]) - 1:
            ships[ship_name]['position'] = [pos_x, pos_y]
            print('Ship %s moved from (%d, %d) to (%d, %d)' %
                  (ship_name, int(current_pos[0]), int(current_pos[1]), pos_x, pos_y))
            # Update board
        else:
            print('Ship out of board')
    else:
        print('Movement too far')


start_game(game_board)
add_ships_to_board(game_board, ships_ingame)
add_asteroids_to_board(game_board)
add_portals_to_board(game_board)
move_ship(game_board, ships_ingame, 'thom', 13, 12)
move_ship(game_board, ships_ingame, 'thom', 15, 12)
move_ship(game_board, ships_ingame, 'three', 28, 27)
