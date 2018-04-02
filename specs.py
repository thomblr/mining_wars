import colored, random


def start_game(config_name, player_types):
    """
    The main function to start the game.

    Version
    -------
    specification: Thomas Blanchy (v.2 09/03/2018)

    Parameters
    ----------
    config_name: the name of the file configuration (str)
    player_types: the types of the players (list)
    """

    # All the data structures that will be used
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
    game_board = {}
    ships_ingame = {}
    players = {}

    # Load information from the config file
    info = load_file(config_name)
    game_board['size'] = load_size(info)
    game_board['portals'] = load_portals(info)
    game_board['asteroids'] = load_asteroids(info)

    # interpret_orders('dave:scout olivaw:*32-4 robbie:lock speedy:release dave:@21-4', ships_type)

    # Create names for the players
    for player in player_types:
        if player is 'human':
            name = input('Name of the player %d ? (unique)' % (player_types.index(player) + 1))
        else:
            print('Random name for player %d ...' % (player_types.index(player) + 1))
            name = 'IA#%d' % random.randint(0, 999)

        players[name] = {}
        players[name]['type'] = player
        players[name]['ships'] = []

    user_input = True

    while user_input:
        new_input = input('Continue?')

        if new_input.startswith('board'):
            draw_board(game_board, ships_ingame, ships_structure)
        elif new_input.startswith('end'):
            user_input = False
        elif new_input.startswith('players'):
            print(players)
        elif new_input.startswith('game'):
            for player in players:
                if players[player]['type'] is 'human':
                    order = input('Order of %s: ' % player)
                    interpret_orders(order, player, ships_type)

    print('Game Over!')

#
#   UI
#


def draw_board(info, ships, ships_structure):
    """
    Draw the game board and refresh every round.

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)

    Parameters
    ----------
    info: the information of the game (dictionary)
    ships: the ships in game (dictionary)
    ships_structure: the structure of the ships (dictionary)
    """

    board = []
    build_empty_board(info, board)
    add_portals_to_board(board, info)
    add_ships_to_board(board, ships, ships_structure)
    add_asteroids_to_board(board, info)

    for row in board:
        for col in row:
            print(col, end=' ')
        print('')


def build_empty_board(info, board):
    """
    Build the empty board with the size and the length of the config.

    Parameters
    ----------
    info: all the information of the game (dictionary)
    board: the current game board (list)
    """

    for i in range(info['size'][0]):
        sub_list = []
        for j in range(info['size'][1]):
            sub_list.append('◻')
        board.append(sub_list)


def add_ships_to_board(board, ships, ships_structure):
    """
    Add the ships in game to the board.

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)

    Parameters
    ----------
    board: the current game board (list)
    ships: the ships in game (dictionary)
    ships_structure: the structure of the ships (dictionary)
    """

    for ship in ships:
        ship_x = ships[ship]['position'][0]
        ship_y = ships[ship]['position'][1]
        ship_type = ships[ship]['type']

        structure = ships_structure[ship_type]

        for pos in structure:
            board[ship_x + int(pos[0]) - 1][ship_y + int(pos[1]) - 1] = '◼'


def add_asteroids_to_board(board, info):
    """
    Add the asteroids to the board.

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)

    Parameters
    ----------
    board: the current game board (list)
    info: the data structure with the asteroids (dictionary)
    """

    for asteroid in info['asteroids']:
        pos_x = asteroid['pos'][0]
        pos_y = asteroid['pos'][1]
        ore = asteroid['ore']
        color = colored.fg('red') if ore > 0 else colored.fg('white')
        board[int(pos_x) - 1][int(pos_y) - 1] = color + '✹' + colored.attr('reset')


def add_portals_to_board(board, info):
    """
    Add the portals to the board.

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)

    Parameters
    ----------
    board: the current game board (list)
    info: the data structure with the portals (dictionary)
    """

    for portal in info['portals']:
        pos_x = portal['pos'][0]
        pos_y = portal['pos'][1]
        for i in range(-2, 3):
            for j in range(-2, 3):
                board[int(pos_x) + i - 1][int(pos_y) + j - 1] = '◍'


#
#   Actions
#


def buy_ships():
    """
    Add the new ships according to the orders.

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)

    Returns
    -------
    ships: the new ships to add (dictionary)
    """
    pass


def move_ship(info, ships, ship_name, pos_x, pos_y):
    """
    Move the ship to the position (x,y)

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)

    Parameters
    ----------
    info: the information of the game (dictionary)
    ships: the ships in game (dictionary)
    ship_name: the name of the ship to move (str)
    pos_x: the horizontal position (int)
    pos_y: the vertical position (int)
    """
    pass


def attack_ship(info, ships, ship_name, target_name):
    """
    Launch an attack based on the ship concerned.

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)

    Parameters
    ----------
    info: the information of the game (dictionary)
    ships: the ships in game (dictionary)
    ship_name: the name of the attacker's ship (str)
    target_name: the name of the target's ship (str)
    """
    pass


def collect_ores(info):
    """
    Collect the ores from the asteroids locked by a ship and unload the ores in the portal if a ship is locked

    Version
    -------
    specification: Thomas Blanchy (v.2 09/03/2018)

    Parameters
    ----------
    info: the information of the game (dictionary)
    """
    pass


def lock_ship(ships, ship_name):
    """
    Lock a ship to a certain position, asteroid or portal.

    Version
    -------
    specification: Thomas Blanchy (v.2 09/03/2018)

    Parameters
    ----------
    ships: the ships in game (dictionary)
    ship_name: the name of the ship to lock (str)
    """
    pass


def unlock_ship(ships, ship_name):
    """
    Unlock a ship if it is locked to an asteroid or a portal.

    Version
    -------
    specification: Thomas Blanchy (v.2 09/03/2018)

    Parameters
    ----------
    ships: the ships in game (dictionary)
    ship_name: the name of the ship to unlock (str)
    """
    pass


#
#   File loading
#


def load_file(config_name):
    """
    Get all the information in the game file.

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)

    Parameters
    ----------
    config_name: the name of the config file (str)

    Returns
    -------
    info: the information of the game file (list)
    """

    fh = open(config_name, 'r')
    info = fh.readlines()
    for line in info:
        info[info.index(line)] = line.replace('\n', '')
    return info


def load_size(file_info):
    """
    Get the size of the board.

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)

    Parameters
    ----------
    file_info: the information of the game file (list)

    Returns
    -------
    size: the size of the game board (list)
    """

    coords = file_info[1].split(' ')
    size = [int(coords[0]), int(coords[1])]
    return size


def load_portals(file_info):
    """
    Get the portals of the game.

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)

    Parameters
    ----------
    file_info: the information of the game file (list)

    Returns
    -------
    portals: the position of each portals (list)
    """

    portals = file_info[file_info.index('portals:') + 1:file_info.index('asteroids:')]
    portals_pos = []
    for portal in portals:
        portal_pos = {}
        coords = portal.split(' ')
        pos = [int(coords[0]), int(coords[1])]
        portal_pos['pos'] = pos
        portal_pos['life'] = 100
        portals_pos.append(portal_pos)
    return portals_pos


def load_asteroids(file_info):
    """
    Get all the asteroids in the game.

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)

    Parameters
    ----------
    file_info: the information of the game file (list)

    Returns
    -------
    asteroids: all the asteroids (list)
    """

    asteroids = file_info[file_info.index('asteroids:') + 1:]
    asteroids_info = []
    for asteroid in asteroids:
        infos = asteroid.split(' ')
        aster = {
            'pos': [int(infos[0]), int(infos[1])],
            'ore': int(infos[2]),
            'rate': int(infos[3])
        }
        asteroids_info.append(aster)
    return asteroids_info


#
#   Orders
#


def interpret_orders(orders, player_name, types_of_ship):
    """
    Get all the orders written by a player and translate them.

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)

    Parameters
    ----------
    orders: the orders written by a player (str)
    player_name: the name of the player who did the order (str)
    types_of_ship: the types of the ships (dictionary)
    """

    all_orders = orders.split(' ')
    for order in all_orders:
        order_name = order.split(':')[1]

        if order_name.startswith('@'):
            new_move_order(order, player_name)
        elif order_name.startswith('*'):
            new_attack_order(order, player_name)
        elif order_name.startswith('release'):
            new_unlock_order(order, player_name)
        elif order_name.startswith('lock'):
            new_lock_order(order, player_name)
        elif order_name in types_of_ship.keys():
            new_buy_order(order, player_name)


def new_move_order(order, player_name, players, ships_ingame, info):
    """
    Insert a new move order.

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)

    Parameters
    ----------
    order: the move order (str)
    player_name: the name of the player who did the order (str)
    players: the information of the players (dictionary)
    """

    # Extract the new position from the order
    ship_name = order.split(':')[0]
    new_position = order.split(':')[1].remove('@')
    new_position = new_position.split('-')
    new_position = [int(new_position[0]), int(new_position[1])]

    # Check if the player own the ship
    if ship_name not in players[player_name]['ships']:
        print('You do not own that ship.')
        return False

    # Check if the new pos is in the board
    current_pos = ships_ingame[ship_name]['position']
    if abs(new_position[0] - current_pos[0]) > 1 or abs(new_position[1] - current_pos[1]) > 1:
        print('Movement too far (>1)')
        return False

    board_size = info['size']

    print('New move order : %s for %s' % (order, player_name))


def new_attack_order(order, player_name):
    """
    Insert a new attack order.

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)

    Parameters
    ----------
    order: the attack order (str)
    player_name: the name of the player who did the order (str)
    """
    print('New attack order : %s for %s' % (order, player_name))


def new_buy_order(order, player_name):
    """
    Insert a new buy order.

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)

    Parameters
    ----------
    order: the buy order (str)
    player_name: the name of the player who did the order (str)
    """
    print('New buy order : %s for %s' % (order, player_name))


def new_lock_order(order, player_name):
    """
    Register a new order with the name of the ship to lock

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)

    Parameters
    ----------
    order: the order containing the name of the ship to lock (str)
    player_name: the name of the player who did the order (str)
    """
    print('New lock order : %s for %s' % (order, player_name))


def new_unlock_order(order, player_name):
    """
    Register a new order with the name of the ship to unlock

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)

    Parameters
    ----------
    order: the order containing the name of the ship to unlock (str)
    player_name: the name of the player who did the order (str)
    """
    print('New unlock order : %s for %s' % (order, player_name))


#
#   End Game
#


def check_end_game():
    """
    Check if a portal is destroyed or no damage has been done for 20 turns.

    Version
    -------
    specification: Cyril Weber (v.1 04/03/2018)

    Returns
    -------
    ended: if the game is ended (bool)
    """
    pass


def end_game():
    """
    Make the steps to end the game, write the winner.

    Version
    -------
    specification: Cyril Weber (v.1 04/03/2018)

    """
    pass


def get_winner():
    """
    Returns the winner's name of the game according to the damage and the ore.

    Version
    -------
    specification: Cyril Weber (v.1 04/03/2018)

    Returns
    -------
    winner: the name of the winner (str)
    """
    pass

#
#   Help functions
#


def get_ship_radius(ship_type):
    """
    Get the radius of a specific type of ship

    Parameters
    ----------
    ship_type: the type of the ship (str)

    Returns
    -------
    radius: the radius of the ship (int)
    """

    types = {
        'Scout': 1,
        'Warship': 2,
        'Excavator-S': 0,
        'Excavator-M': 1,
        'Excavator-L': 2
    }

    return types[ship_type]


def check_range(attacker, target):
    """
    Check if a ship is in the range of another ship.

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)

    Parameters
    ----------
    attacker: the name of the attacker's ship (str)
    target: the name of the target's ship (str)

    Returns
    -------
    range: if the ships are close enough (bool)
    """
    pass


def can_recolt(info, ship_name, asteroid_position):
    """
    Check either or not a ship can recolt on an asteroid.

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)

    Parameters
    ----------
    info: the information of the game (dictionary)
    ship_name: the name of the ship that wants to recolt (str)
    asteroid_position: the position of the asteroid to recolt to (list)

    Returns
    -------
    recolt: if the ship can recolt (bool)
    """
    pass


start_game('game.txt', ['human', 'ia'])
