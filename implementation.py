import colored
import random
import time


def start_game(config_name, player_types):
    """
    The main function to start the game.

    Parameters
    ----------
    config_name: the name of the file configuration (str)
    player_types: the types of the players (list)

    Version
    -------
    specification: Thomas Blanchy (v.2 09/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    # All the data structures that will be used
    ships_type = {
        'Scout': {
            'size': 9,
            'life': 3,
            'attack': 1,
            'range': 3,
            'cost': 3
        },
        'Warship': {
            'size': 21,
            'life': 18,
            'attack': 3,
            'range': 5,
            'cost': 9
        },
        'Excavator-S': {
            'size': 1,
            'tonnage': 1,
            'life': 2,
            'cost': 1
        },
        'Excavator-M': {
            'size': 5,
            'tonnage': 4,
            'life': 3,
            'cost': 2
        },
        'Excavator-L': {
            'size': 9,
            'tonnage': 8,
            'life': 6,
            'cost': 4
        }
    }
    ships_structure = {
        'Scout': [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)],
        'Warship': [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1), (-2, -1), (-2, 0),
                    (-2, 1), (-1, 2), (0, 2), (1, 2), (2, 1), (2, 0), (2, -1), (1, -2), (0, -2), (-1, -2)],
        'Excavator-S': [(0, 0)],
        'Excavator-M': [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)],
        'Excavator-L': [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (2, 0), (0, 2), (-2, 0), (0, -2)]
    }
    game_board = {}
    ships_ingame = {}
    players = {}

    # Load information from the config file
    info = load_file(config_name)
    game_board['size'] = load_size(info)
    game_board['portals'] = load_portals(info)
    game_board['asteroids'] = load_asteroids(info)
    game_board['empty_round_left'] = 50

    # Create names for the players
    for player in player_types:
        if player == 'human':
            name = input('Name of the player %d ? (unique)' % (player_types.index(player) + 1))
        else:
            print('Random name for player %d ...' % (player_types.index(player) + 1))
            name = 'IA#%d' % random.randint(0, 999)

        players[name] = {}
        players[name]['type'] = player
        players[name]['ore'] = 4
        players[name]['total_recolted'] = 0
        players[name]['ships'] = []

    no_damage_in_the_round = True

    while check_end_game(game_board, no_damage_in_the_round):
        time.sleep(1)
        new_orders = {
            'buy_orders': [],
            'lock_orders': [],
            'unlock_orders': [],
            'move_orders': [],
            'attack_orders': []
        }

        for player in players:
            if players[player]['type'] == 'human':
                order = input('Order of %s: ' % player)
                interpret_orders(new_orders, order, player, ships_type, players, ships_ingame, game_board)
            else:
                order = ia(player, players, ships_ingame, ships_type, game_board)
                interpret_orders(new_orders, order, player, ships_type, players, ships_ingame, game_board)

        # Buying Phase
        buy_ships(new_orders['buy_orders'], players, ships_ingame, ships_type, game_board)

        # Lock/Unlock Phase
        lock_ship(new_orders['lock_orders'], game_board, ships_ingame, players)
        unlock_ship(new_orders['unlock_orders'], game_board, ships_ingame, players)

        # Move Phase
        move_ship(new_orders['move_orders'], ships_ingame)

        # Attack Phase
        no_damage_in_the_round = attack_ship(new_orders['attack_orders'], game_board, ships_ingame, ships_type, players)

        # Recolt Phase
        collect_ores(game_board, ships_ingame, players, ships_type)

        # Show board
        draw_board(game_board, ships_ingame, ships_structure, players)

    end_game(players, game_board)
    print('Game Over!')


#
#   UI
#


def draw_board(info, ships, ships_structure, players):
    """
    Draw the game board and refresh every round.

    Parameters
    ----------
    info: the information of the game (dictionary)
    ships: the ships in game (dictionary)
    ships_structure: the structure of the ships (dictionary)
    players: the information of the players (dictionary)

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    board = []
    build_empty_board(info, board)
    add_portals_to_board(board, info)
    add_ships_to_board(board, ships, ships_structure, players)
    add_asteroids_to_board(board, info)

    for row in board:
        for col in row:
            print(col, end=' ')
        print('')
    print('-' * len(board))


def build_empty_board(info, board):
    """
    Build the empty board with the size and the length of the config.

    Parameters
    ----------
    info: all the information of the game (dictionary)
    board: the current game board (list)

    Version
    -------
    specification: Joaquim Peremans (v.1 15/04/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    for i in range(info['size'][0]):
        sub_list = []
        for j in range(info['size'][1]):
            sub_list.append('\u25A1')
        board.append(sub_list)


def add_ships_to_board(board, ships, ships_structure, players):
    """
    Add the ships in game to the board.

    Parameters
    ----------
    board: the current game board (list)
    ships: the ships in game (dictionary)
    ships_structure: the structure of the ships (dictionary)
    players: the information of the players (dictionary)

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    ship_colors = [1, 21]
    for ship in ships:
        owner_index = list(players.keys()).index(get_player_from_ship(ship, players))
        color = colored.fg(ship_colors[owner_index])
        ship_x = ships[ship]['position'][0]
        ship_y = ships[ship]['position'][1]
        ship_type = ships[ship]['type']

        structure = ships_structure[ship_type]

        for pos in structure:
            board[ship_x + int(pos[0]) - 1][ship_y + int(pos[1]) - 1] = color + '\u25A0' + colored.attr('reset')


def add_asteroids_to_board(board, info):
    """
    Add the asteroids to the board.

    Parameters
    ----------
    board: the current game board (list)
    info: the data structure with the asteroids (dictionary)

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    for asteroid in info['asteroids']:
        pos_x = asteroid['position'][0]
        pos_y = asteroid['position'][1]
        ore = asteroid['ore']
        color = colored.fg(2) if ore > 0.1 else colored.fg(15)
        board[int(pos_x) - 1][int(pos_y) - 1] = color + '\u25D8' + colored.attr('reset')


def add_portals_to_board(board, info):
    """
    Add the portals to the board.

    Parameters
    ----------
    board: the current game board (list)
    info: the data structure with the portals (dictionary)

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    portal_colors = [174, 45]
    for portal in info['portals']:
        portal_index = info['portals'].index(portal)
        color = colored.fg(portal_colors[portal_index])
        pos_x = portal['position'][0]
        pos_y = portal['position'][1]
        for i in range(-2, 3):
            for j in range(-2, 3):
                board[int(pos_x) + i - 1][int(pos_y) + j - 1] = color + '\u25CC' + colored.attr('reset')


#
#   Actions
#


def buy_ships(orders, players, ships_ingame, ships_type, info):
    """
    Add the new ships according to the orders.

    Parameters
    ----------
    orders: the buy orders of the round (list)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of the ships (dictionary)
    info: the data structure with the portals and the asteroids (dictionary)

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    for order in orders:
        ship_name = order['order'].split(':')[0]
        ship_type = order['order'].split(':')[1][0].upper() + order['order'].split(':')[1][1:]

        # Remove ore from player bank
        price = ships_type[ship_type]['cost']
        players[order['player_name']]['ore'] = players[order['player_name']]['ore'] - price

        # Add to ships_ingame -> 'name': (type, position, life, if exca: ore)
        ships_ingame[ship_name] = {}
        ships_ingame[ship_name]['type'] = ship_type

        # Get the portal of the player
        player_portal = get_portal_from_player(order['player_name'], players, info)

        ships_ingame[ship_name]['position'] = [player_portal['position'][0], player_portal['position'][1]]
        ships_ingame[ship_name]['life'] = ships_type[ship_type]['life']

        if ship_type in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
            ships_ingame[ship_name]['ore'] = 0

        # Add to players -> 'name' to players[player_name]['ships']
        players[order['player_name']]['ships'].append(ship_name)


def move_ship(orders, ships_ingame):
    """
    Move the ship to the position (x,y)

    Parameters
    ----------
    orders: the move orders of the round (list)
    ships_ingame: the information of the ships on the board (dictionary)

    Version
    -------
    specification: Joaquim Peremans (v.1 05/03/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """

    for order in orders:
        ship_name = order['order'].split(':')[0]
        new_position = order['order'].split(':')[1].replace('@', '')
        new_position = new_position.split('-')
        new_position = [int(new_position[0]), int(new_position[1])]
        ships_ingame[ship_name]['position'] = new_position


def attack_ship(orders, info, ships_ingame, ships_type, players):
    """
    Launch an attack based on the ship concerned.

    Parameters
    ----------
    orders: the attack orders of the round (list)
    info: the data structure with the portals and the asteroids (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of the ships (dictionary)
    players: the information of the players (dictionary)

    Returns
    -------
    damage: if there was any damage done (bool)

    Version
    -------
    specification: Joaquim Peremans, Thomas Blanchy (v.2 20/04/2018)
    implementation: Joaquim Peremans, Thomas Blanchy (v.2 20/04/2018)
    """

    for order in orders:
        ship_name = order['order'].split(':')[0]
        target_pos = [int(order['order'].split(':')[1].split('-')[0].replace('*', '')),
                      int(order['order'].split(':')[1].split('-')[1])]
        is_damage = False

        # Check portal damage
        for portal in info['portals']:
            if target_pos == portal['position']:
                damage = ships_type[ships_ingame[ship_name]['type']]['attack']
                portal['life'] -= damage
                is_damage = True

        # Check ship damage
        for ship in ships_ingame:
            if target_pos == ships_ingame[ship]['position']:
                damage = ships_type[ships_ingame[ship_name]['type']]['attack']
                ships_ingame[ship]['life'] -= damage
                is_damage = True

        # Remove dead ships
        for i in range(len(ships_ingame) - 1, 0, -1):
            ship = list(ships_ingame.keys())[i]
            if ships_ingame[ship]['life'] <= 0:
                print('The ship %s has been destroyed.' % ship)
                del ships_ingame[ship]

                # Delete ships from locked ships on asteroids
                for asteroid in info['asteroids']:
                    ships_locked = asteroid['ships_locked']
                    if ship in ships_locked:
                        ships_locked.remove(ship)

                # Delete ships from locked ships on portals
                for portal in info['portals']:
                    ships_locked = portal['ships_locked']
                    if ship in ships_locked:
                        ships_locked.remove(ship)

                # Delete ships from players ships
                for player in players:
                    if ship in players[player]['ships']:
                        players[player]['ships'].remove(ship)

        if is_damage:
            return False
        else:
            return True
    return True


def collect_ores(info, ships_ingame, players, ships_type):
    """
    Collect the ores from the asteroids locked by a ship and unload the ores in the portal if a ship is locked

    Parameters
    ----------
    info: the information of the game (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    players: the information of the players (dictionary)
    ships_type: the features of the ships (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.2 09/03/2018)
    implementation: Thomas Blanchy, Cyril Weber (v.1 15/04/2018)
    """

    # Collect ores from asteroids
    for asteroid in info['asteroids']:
        ships_locked = asteroid['ships_locked']

        ores_left = asteroid['ore']  # Ores left to collect in the asteroid
        ores_rate = asteroid['rate']  # The rate of giving of the asteroid
        nb_ships = len(ships_locked)  # The number of ships locked to the asteroid

        max_ores = {}  # Data structure used to compute the number of ores to give to each ship

        # The part where we compute the max number of ores to give to a ship
        for ship in ships_locked:
            capacity = ships_type[ships_ingame[ship]['type']]['tonnage'] - ships_ingame[ship]['ore']
            # If the rate is greater than the capacity of the ship ...
            if ores_rate > capacity:
                # ... we can only give the capacity of the ship
                max_ores[ship] = capacity
            else:
                # ... or we can give the rate of the asteroid because there is enough place
                max_ores[ship] = ores_rate

        # The maximum number of ores to give to all the ships
        total_ores_to_give = 0
        for o in max_ores:
            total_ores_to_give += max_ores[o]

        # If the number of ores to give is less than what's left in the asteroid ...
        if total_ores_to_give < ores_left:
            for ship in ships_locked:
                # ... we can give to each ship the max they can have
                ships_ingame[ship]['ore'] += max_ores[ship]
                asteroid['ore'] -= max_ores[ship]
        # The max number is greater than what's left in the asteroid -> we have to split
        else:
            new_ores_left = ores_left  # We save ores_left to modify it
            new_nb_ships = nb_ships  # We save nb_ships to modify it

            # While there are ores left in the asteroid
            while new_ores_left > 0.1:
                # We compute the minimum of the ores the ships can collect
                current_min = -1
                for o in max_ores:
                    if max_ores[o] < current_min or current_min == -1:
                        current_min = max_ores[o]

                # We multiply the min by the number of ships to see if we can give that min to all the ships
                if current_min * nb_ships <= ores_left:
                    for ship in max_ores:
                        ships_ingame[ship]['ore'] += current_min  # We give the min to each ships
                        asteroid['ore'] -= current_min
                        new_ores_left -= current_min  # We subtract the min to see what's left to the asteroid
                        max_ores[ship] -= current_min  # We subtract the min to see what the ship can recolt
                # If the min is greater to what the ships can recolt
                else:
                    for ship in max_ores:
                        ships_ingame[ship]['ore'] += (ores_left / new_nb_ships)
                        asteroid['ore'] -= (ores_left / new_nb_ships)
                        new_ores_left -= (ores_left / new_nb_ships)
                        max_ores[ship] -= current_min

                # We remove the full ships
                new_max_ores = {}
                for o in max_ores:
                    if max_ores[o] > 0:
                        new_max_ores[o] = max_ores[o]
                new_nb_ships -= (len(max_ores.keys()) - len(new_max_ores.keys()))
                max_ores = new_max_ores

    # Load ores to portals
    for portal in info['portals']:
        ships_locked = portal['ships_locked']
        for ship in ships_locked:
            if ships_ingame[ship]['ore'] > 0:
                for player in players:
                    if ship in players[player]['ships']:
                        players[player]['ore'] += ships_ingame[ship]['ore']
                        players[player]['total_recolted'] += ships_ingame[ship]['ore']
                        ships_ingame[ship]['ore'] = 0


def lock_ship(orders, info, ships_ingame, players):
    """
    Lock a ship to a certain position, asteroid or portal.

    Parameters
    ----------
    orders: the lock orders of the round (list)
    info: all the informatiin of the game (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    players: the information of the players (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.3 16/04/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    for order in orders:
        if order:
            ship_name = order['order'].split(':')[0]
            asteroid = get_asteroid_from_position(ships_ingame[ship_name]['position'], info)

            if asteroid:
                if ship_name not in asteroid['ships_locked']:
                    asteroid['ships_locked'].append(ship_name)
            else:
                owner = get_player_from_ship(ship_name, players)
                portal = get_portal_from_player(owner, players, info)
                if ships_ingame[ship_name]['position'] == portal['position']:
                    if ship_name not in portal['ships_locked']:
                        portal['ships_locked'].append(ship_name)


def unlock_ship(orders, info, ships_ingame, players):
    """
    Unlock a ship if it is locked to an asteroid or a portal.

    Parameters
    ----------
    orders: the unlock orders of the round (list)
    info: all the informatiin of the game (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    players: the information of the players (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.2 09/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    for order in orders:
        if order:
            ship_name = order['order'].split(':')[0]
            asteroid = get_asteroid_from_position(ships_ingame[ship_name]['position'], info)
            if asteroid:
                if ship_name in asteroid['ships_locked']:
                    asteroid['ships_locked'].remove(ship_name)
            else:
                owner = get_player_from_ship(ship_name, players)
                portal = get_portal_from_player(owner, players, info)
                if ships_ingame[ship_name]['position'] == portal['position']:
                    if ship_name in portal['ships_locked']:
                        portal['ships_locked'].remove(ship_name)


#
#   File loading
#


def load_file(config_name):
    """
    Get all the information in the game file.

    Parameters
    ----------
    config_name: the name of the config file (str)

    Returns
    -------
    info: the information of the game file (list)

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    fh = open(config_name, 'r')
    info = fh.readlines()
    for line in info:
        info[info.index(line)] = line.replace('\n', '')
    return info


def load_size(file_info):
    """
    Get the size of the board.

    Parameters
    ----------
    file_info: the information of the game file (list)

    Returns
    -------
    size: the size of the game board (list)

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    coords = file_info[1].split(' ')
    size = [int(coords[0]), int(coords[1])]
    return size


def load_portals(file_info):
    """
    Get the portals of the game.

    Parameters
    ----------
    file_info: the information of the game file (list)

    Returns
    -------
    portals: the position of each portals (list)

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    portals = file_info[file_info.index('portals:') + 1:file_info.index('asteroids:')]
    portals_pos = []
    for portal in portals:
        coords = portal.split(' ')
        portal_pos = {
            'position': [int(coords[0]), int(coords[1])],
            'life': 100,
            'ships_locked': []
        }
        portals_pos.append(portal_pos)
    return portals_pos


def load_asteroids(file_info):
    """
    Get all the asteroids in the game.

    Parameters
    ----------
    file_info: the information of the game file (list)

    Returns
    -------
    asteroids: all the asteroids (list)

    Version
    -------
    specification: Cyril Weber (v.1 03/03/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    asteroids = file_info[file_info.index('asteroids:') + 1:]
    asteroids_info = []
    for asteroid in asteroids:
        infos = asteroid.split(' ')
        aster = {
            'position': [int(infos[0]), int(infos[1])],
            'ore': int(infos[2]),
            'rate': int(infos[3]),
            'ships_locked': []
        }
        asteroids_info.append(aster)
    return asteroids_info


#
#   Orders
#


def interpret_orders(new_orders, orders, player_name, ships_type, players, ships_ingame, info):
    """
    Get all the orders written by a player and translate them.

    Parameters
    ----------
    new_orders: the orders to make this round (dictionary)
    orders: the orders written by a player (str)
    player_name: the name of the player who did the order (str)
    ships_type: the types of the ships (dictionary)
    players: the information of the players (dictionary)
    ships_ingame: the ships currently on the board (dictionary)
    info: all the information of the game (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    if len(orders) > 0:
        all_orders = orders.split(' ')
        for order in all_orders:
            order_name = order.split(':')[1]

            if order_name.startswith('@'):
                move_order = new_move_order(order, player_name, players, ships_ingame, info)

                if move_order:
                    new_orders['move_orders'].append(move_order)
            elif order_name.startswith('*'):
                attack_order = new_attack_order(order, player_name, players, ships_ingame, ships_type, info)

                if attack_order:
                    new_orders['attack_orders'].append(attack_order)
            elif order_name.startswith('release'):
                release_order = new_unlock_order(order, player_name, players, ships_ingame, info)

                if release_order:
                    new_orders['unlock_orders'].append(release_order)
            elif order_name.startswith('lock'):
                lock_order = new_lock_order(order, player_name, players, ships_ingame, info)

                if lock_order:
                    new_orders['lock_orders'].append(lock_order)
            elif (order_name[0].upper() + order_name[1:]) in ships_type.keys():
                buy_order = new_buy_order(order, player_name, ships_type, ships_ingame, players)

                if buy_order:
                    new_orders['buy_orders'].append(buy_order)
            else:
                print('Order not recognized')


def new_move_order(order, player_name, players, ships_ingame, info):
    """
    Insert a new move order.

    Parameters
    ----------
    order: the move order (str)
    player_name: the name of the player who did the order (str)
    players: the information of the players (dictionary)
    ships_ingame: the ships currently on the board (dictionary)
    info: all the information of the game (dictionary)

    Returns
    -------
    move_order: the new move order (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.2 01/04/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    # Extract the new position from the order
    ship_name = order.split(':')[0]
    new_position = order.split(':')[1].replace('@', '')
    new_position = new_position.split('-')
    new_position = [int(new_position[0]), int(new_position[1])]

    # Check if the player own the ship
    if ship_name not in players[player_name]['ships']:
        # print('%s - You do not own that ship.' % order)
        return False

    # Check if the new pos next to the old one
    current_pos = ships_ingame[ship_name]['position']
    if abs(new_position[0] - current_pos[0]) > 1 or abs(new_position[1] - current_pos[1]) > 1:
        # print('%s - Movement too far (>1)' % order)
        return False

    # Check if the new pos is in the board
    board_size = info['size']
    ship_radius = get_ship_radius(ships_ingame[ship_name]['type'])

    if new_position[0] - ship_radius <= 0 or new_position[1] - ship_radius <= 0 \
            or new_position[0] + ship_radius > board_size[0] or new_position[1] + ship_radius > board_size[1]:
        # print('%s - Movement out of the board.' % order)
        return False

    new_order = {
        'order': order,
        'player_name': player_name
    }

    return new_order


def new_attack_order(order, player_name, players, ships_ingame, ships_type, info):
    """
    Insert a new attack order.

    Parameters
    ----------
    order: the attack order (str)
    player_name: the name of the player who did the order (str)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of the ships (dictionary)
    info: the data structure with the portails and the asteroids (dictionary)

    Returns
    -------
    attack_order: the new attack order (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    # order is type : ship_name:*r-c
    ship_name = order.split(':')[0]
    target_pos = [int(order.split(':')[1].split('-')[0].replace('*', '')), int(order.split(':')[1].split('-')[1])]

    # Check in board
    if target_pos[0] < 1 or target_pos[1] < 1 or target_pos[0] > info['size'][0] or target_pos[1] > info['size'][1]:
        # print('You can not attack out of the board.')
        return False

    # Check property
    if ship_name not in players[player_name]['ships']:
        # print('You do not own that ship.')
        return False

    # Check Range
    if not check_range(ship_name, [target_pos[0], target_pos[1]], ships_ingame, ships_type):
        # print('The target is too far to be reached.')
        return False

    # Check ship type
    if ships_ingame[ship_name]['type'] not in ['Scout', 'Warship']:
        # print('You can not attack with that ship.')
        return False

    new_order = {
        'order': order,
        'player_name': player_name
    }

    return new_order


def new_buy_order(order, player_name, ships_type, ships_ingame, players):
    """
    Insert a new buy order.

    Parameters
    ----------
    order: the buy order (str)
    player_name: the name of the player who did the order (str)
    ships_type: the types of the ships (dictionary)
    ships_ingame: the ships currently on the board (dictionary)
    players: the information of the players (dictionary)

    Returns
    -------
    buy_order: the new buy order (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    ship_name = order.split(':')[0]
    ship_type = order.split(':')[1][0].upper() + order.split(':')[1][1:]

    # Check if enough money
    price = ships_type[ship_type]['cost']
    money_in_bank = players[player_name]['ore']

    if money_in_bank < price:
        # print('You do not have enough money to buy that ship.')
        return False

    if ship_name in ships_ingame.keys():
        # print('That ship name is already used.')
        return False

    new_order = {
        'order': order,
        'player_name': player_name
    }

    return new_order


def new_lock_order(order, player_name, players, ships_ingame, info):
    """
    Register a new order with the name of the ship to lock

    Parameters
    ----------
    order: the order containing the name of the ship to lock (str)
    player_name: the name of the player who did the order (str)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    info: the data structure with the asteroids and the portals (dictionary)

    Returns
    -------
    order: the new lock order (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    ship_name = order.split(':')[0]

    # Check if own the ship
    if ship_name not in players[player_name]['ships']:
        # print('You do not own that ship.')
        return False

    ship_pos = ships_ingame[ship_name]['position']

    # Check if it is an excavator
    if ships_ingame[ship_name]['type'] not in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
        # print('You can not lock that ship.')
        return False

    for asteroid in info['asteroids']:
        if asteroid['position'] == ship_pos:
            if ship_name in asteroid['ships_locked']:
                # print('That ship is already locked')
                return False

            new_order = {
                'order': order,
                'player_name': player_name
            }

            return new_order

    for portal in info['portals']:
        if portal['position'] == ship_pos:
            if ship_name in portal['ships_locked']:
                # print('That ship is already locked.')
                return False

            new_order = {
                'order': order,
                'player_name': player_name
            }

            return new_order


def new_unlock_order(order, player_name, players, ships_ingame, info):
    """
    Register a new order with the name of the ship to unlock

    Parameters
    ----------
    order: the order containing the name of the ship to unlock (str)
    player_name: the name of the player who did the order (str)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    info: the data structure of the asteroids and the portals (dictionary)

    Returns
    -------
    order: the new order (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 03/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    ship_name = order.split(':')[0]

    # Check if own the ship
    if ship_name not in players[player_name]['ships']:
        # print('You do not own that ship.')
        return False

    ship_pos = ships_ingame[ship_name]['position']

    # Check if it is an excavator
    if ships_ingame[ship_name]['type'] not in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
        # print('You can not unlock that ship.')
        return False

    for asteroid in info['asteroids']:
        if asteroid['position'] == ship_pos:
            if ship_name not in asteroid['ships_locked']:
                # print('That ship is not locked')
                return False

            new_order = {
                'order': order,
                'player_name': player_name
            }

            return new_order

    for portal in info['portals']:
        if portal['position'] == ship_pos:
            if ship_name not in portal['ships_locked']:
                # print('That ship is not locked.')
                return False

            new_order = {
                'order': order,
                'player_name': player_name
            }

            return new_order


#
#   End Game
#


def check_end_game(info, damage):
    """
    Check if a portal is destroyed or no damage has been done for 20 turns.

    Parameters
    ----------
    info: all the information of the game (dictionary)
    damage: if there was any damage on the round (bool)

    Returns
    -------
    ended: if the game is ended (bool)

    Version
    -------
    specification: Cyril Weber, Thomas Blanchy (v.2 01/04/2018)
    implementation: Cyril Weber, Thomas Blanchy (v.1 15/04/2018)
    """

    if damage:
        info['empty_round_left'] -= 1
    else:
        info['empty_round_left'] = 50
    if info['empty_round_left'] == 0:
        return False
    for portal in info['portals']:
        if portal['life'] <= 0:
            return False
    return True


def end_game(players, info):
    """
    Make the steps to end the game, write the winner.

    Parameters
    ----------
    players: the information of the players (dictionary)
    info: the data structure with the portals and the asteroids (dictionary)

    Version
    -------
    specification: Cyril Weber (v.1 04/03/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    print('%s won the game!' % get_winner(players, info))


def get_winner(players, info):
    """
    Returns the winner's name of the game according to the damage and the ore.

    Parameters
    ----------
    players: the information of the players (dictionary)
    info: the data structure with the portals and the asteroids (dictionary)

    Returns
    -------
    winner: the name of the winner (str)

    Version
    -------
    specification: Cyril Weber (v.1 04/03/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    portals_life = []
    # We save the life of all the portals
    for portal in info['portals']:
        portals_life.append(portal['life'])

    total_ores_recolted = []
    # We save the total recolted ores of all players
    for player in players:
        total_ores_recolted.append(players[player]['total_recolted'])

    current_max_portal_life = -100
    nb_max = 0

    # We check the highest value in the life of the portals
    for n in portals_life:
        if n > current_max_portal_life or current_max_portal_life == -100:
            current_max_portal_life = n
            nb_max = 1
        elif current_max_portal_life == n:
            nb_max += 1

    # If there is only one portal with the highest life value ...
    if nb_max == 1:
        for player in players:
            # ... We check for all player if their portal has the highest life value
            if get_portal_from_player(player, players, info)['life'] == current_max_portal_life:
                return player
    # If their are at least 2 portals with the same highest life ...
    else:
        current_max_ores = -100
        nb_max_ores = 0

        # ... We check the highest value in the total recolted ores
        for j in total_ores_recolted:
            if j > current_max_ores or current_max_ores == -100:
                current_max_ores = j
                nb_max_ores = 1
            elif current_max_ores == j:
                nb_max_ores += 1

        # If there is only one player with the highest value of total recolted ores ...
        if nb_max_ores == 1:
            for player in players:
                # ... We check for all players who has the highest value of total recolted ores
                if players[player]['total_recolted'] == current_max_ores:
                    return player
            else:
                return 'Nobody'


#
#   IA Functions
#

def ia(ia_name, players, ships_ingame, ships_type, info):
    """
    Basic action of the ia

    Parameters
    ----------
    ia_name: the name of the ia (str)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of the ships (dictionary)
    info: the data structure with the portals and the asteroids (dictionary)

    Returns
    -------
    order: the orders of the ia (str)

    Version
    -------
    specification: Thomas Blanchy (v.1 15/04/2018)
    implementation: Thomas Blanchy, Cyril Weber, Joaquim Peremans (v.1 15/04/2018)
    """

    orders = []

    if players[ia_name]['type'] == 'ia':
        # Random Move
        for ship_name in players[ia_name]['ships']:
            ship = ships_ingame[ship_name]
            ship_type = ship['type']
            current_pos = ship['position']

            if not is_locked(ship_name, info):
                if ship_type in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                    stock = ships_type[ship_type]['tonnage'] - ship['ore']

                    if stock > 0:
                        closest_asteroid = get_closest_asteroid(info, current_pos)

                        # Compute X move
                        x_move = 0
                        if closest_asteroid['position'][0] > current_pos[0]:
                            x_move = 1
                        elif closest_asteroid['position'][0] < current_pos[0]:
                            x_move = -1

                        # Compute Y move
                        y_move = 0
                        if closest_asteroid['position'][1] > current_pos[1]:
                            y_move = 1
                        elif closest_asteroid['position'][1] < current_pos[1]:
                            y_move = -1

                        new_pos_r = current_pos[0] + x_move
                        new_pos_c = current_pos[1] + y_move
                    else:
                        owner_name = get_player_from_ship(ship_name, players)
                        portal_pos = get_portal_from_player(owner_name, players, info)

                        # Compute X move
                        x_move = 0
                        if portal_pos['position'][0] > current_pos[0]:
                            x_move = 1
                        elif portal_pos['position'][0] < current_pos[0]:
                            x_move = -1

                        # Compute Y move
                        y_move = 0
                        if portal_pos['position'][1] > current_pos[1]:
                            y_move = 1
                        elif portal_pos['position'][1] < current_pos[1]:
                            y_move = -1

                        new_pos_r = current_pos[0] + x_move
                        new_pos_c = current_pos[1] + y_move
                else:
                    new_pos_r = current_pos[0] + random.randint(-1, 1)
                    new_pos_c = current_pos[1] + random.randint(-1, 1)
                orders.append('%s:@%d-%d' % (ship_name, new_pos_r, new_pos_c))

        # Random Buy
        money = players[ia_name]['ore']
        for ship_type in ships_type:
            if money >= ships_type[ship_type]['cost']:
                chance = random.random()
                if chance > 0.5:
                    money -= ships_type[ship_type]['cost']
                    ship_name = 'ia_ship#%s#%d' % (ship_type, random.randint(0, 999))
                    orders.append('%s:%s' % (ship_name, ship_type))

        # Lock to asteroid
        for asteroid in info['asteroids']:
            for ship in ships_ingame:
                if ships_ingame[ship]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                    if get_player_from_ship(ship, players) == ia_name:
                        stock = ships_type[ships_ingame[ship]['type']]['tonnage'] - ships_ingame[ship]['ore']
                        if asteroid['position'] == ships_ingame[ship]['position'] and stock > 0:
                            if ship not in asteroid['ships_locked']:
                                orders.append('%s:lock' % ship)

        # Lock to portal
        for portal in info['portals']:
            for ship in ships_ingame:
                if ships_ingame[ship]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                    if get_player_from_ship(ship, players) == ia_name:
                        if portal['position'] == ships_ingame[ship]['position'] and ships_ingame[ship]['ore'] > 0:
                            if ship not in portal['ships_locked']:
                                orders.append('%s:lock' % ship)

        # Unlock from asteroid
        for asteroid in info['asteroids']:
            for ship in asteroid['ships_locked']:
                if get_player_from_ship(ship, players) == ia_name:
                    if ships_ingame[ship]['ore'] == ships_type[ships_ingame[ship]['type']]['tonnage']:
                        orders.append('%s:release' % ship)

        # Unlock from portal
        for portal in info['portals']:
            for ship in portal['ships_locked']:
                if get_player_from_ship(ship, players) == ia_name:
                    if ships_ingame[ship]['ore'] == 0:
                        orders.append('%s:release' % ship)

        # Attack
        for ship in ships_ingame:
            if ships_ingame[ship]['type'] in ['Scout', 'Warship']:
                if get_player_from_ship(ship, players) == ia_name:
                    ship_range = ships_type[ships_ingame[ship]['type']]['range']
                    position = ships_ingame[ship]['position']
                    random_x = random.randint(position[0] - ship_range, position[0] + ship_range)
                    random_y = random.randint(position[1] - ship_range, position[1] + ship_range)
                    orders.append('%s:*%d-%d' % (ship, abs(random_x), abs(random_y)))

    final_ord = ' '.join(orders)
    return final_ord


#
#   Help functions
#

def get_portal_from_player(player_name, players, info):
    """
    Returns the portal of the player

    Parameters
    ----------
    player_name: the name of the player (str)
    players: the information of the players (dictionary)
    info: the data structure with the portals and the asteroids (dictionary)

    Returns
    -------
    portal: the information of the portal (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 15/04/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    # First portal goes to first player ...
    player_index = list(players.keys()).index(player_name)
    player_portal = info['portals'][player_index]
    return player_portal


def get_player_from_ship(ship_name, players):
    """
    Returns the name of the owner of a ship

    Parameters
    ----------
    ship_name: the name of the ship (str)
    players: the information of the players (dictionary)

    Returns
    -------
    player: the name of the owner of the ship (str)

    Version
    -------
    specification: Cyril Weber (v.1 15/04/2018)
    implementation: Cyril Weber (v.1 15/04/2018)
    """

    for player in players:
        if ship_name in players[player]['ships']:
            return player


def is_locked(ship_name, info):
    """
    Check if a ship is locked

    Parameters
    ----------
    ship_name: the name of the ship (str)
    info: the data structure with the portals and the asteroids (dictionary)

    Returns
    -------
    locked: if the ship is locked or not (bool)

    Version
    -------
    specification: Joaquim Peremans (v.1 15/04/2018)
    implementation: Joaquim Peremans (v.1 15/04/2018)
    """
    if ship_name in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
        for asteroid in info['asteroids']:
            if ship_name in asteroid['ships_locked']:
                return True
        return False
    else:
        return False


def get_asteroid_from_position(position, info):
    """
    Get the information of an asteroid according to its position

    Parameters
    ----------
    position: the position of the asteroid (list)
    info: the data structure with the portals and the asteroids (info)

    Returns
    -------
    asteroid: the information of the asteroid (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 15/04/2018)
    implementation: Thomas Blanchy (v.1 15/04/2018)
    """

    for asteroid in info['asteroids']:
        if position[0] == asteroid['position'][0] and position[1] == asteroid['position'][1]:
            return asteroid
    return False


def get_ship_radius(ship_type):
    """
    Get the radius of a specific type of ship

    Parameters
    ----------
    ship_type: the type of the ship (str)

    Returns
    -------
    radius: the radius of the ship (int)

    Version
    -------
    specification: Thomas Blanchy (v.1 15/03/2018)
    implementation: Thomas Blanchy (v.1 15/03/2018)
    """

    types = {
        'Scout': 1,
        'Warship': 2,
        'Excavator-S': 0,
        'Excavator-M': 1,
        'Excavator-L': 2
    }

    return types[ship_type]


def get_closest_asteroid(info, position):
    """
    Returns the closest asteroid on the board from a certain position

    Parameters
    ----------
    info: the data structure with the portals and the asteroids (dictionary)
    position: the position from where to check (list)

    Returns
    -------
    asteroid: the closest asteroid (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 12/04/2018)
    implementation: Thomas Blanchy (v.1 12/04/2018)
    """

    current_closest_asteroid = info['asteroids'][0]
    current_diff_x = -1
    current_diff_y = -1

    for asteroid in info['asteroids']:
        if asteroid['ore'] > 0.1:
            asteroid_pos = asteroid['position']
            diff_x = abs(position[0] - asteroid_pos[0])
            diff_y = abs(position[1] - asteroid_pos[1])

            close = False
            if diff_x < current_diff_x or current_diff_x == -1:
                close = True
            if diff_y < current_diff_y or current_diff_y == -1:
                close = True

            if close:
                current_closest_asteroid = asteroid
                current_diff_x = diff_x
                current_diff_y = diff_y

    return current_closest_asteroid


def check_range(attacker, target_pos, ships_ingame, ships_type):
    """
    Check if a ship is in the range of another ship.

    Parameters
    ----------
    attacker: the name of the attacker's ship (str)
    target_pos: the position of the target (list)
    ships_ingame: the ships currently on the board (dictionary)
    ships_type: the types of the ships (dictionary)

    Returns
    -------
    range: if the ships are close enough (bool)

    Version
    -------
    specification: Thomas Blanchy (v.2 01/04/2018)
    implementation: Thomas Blanchy (v.1 9/04/2018)
    """

    attacker_ship = ships_ingame[attacker]

    # |r2 - r1| + |c2 - c1|
    r_value = abs(target_pos[0] - attacker_ship['position'][0])
    c_value = abs(target_pos[1] - attacker_ship['position'][1])
    distance = r_value + c_value

    return distance <= ships_type[attacker_ship['type']]['range']


start_game('game.txt', ['ia', 'ia'])
