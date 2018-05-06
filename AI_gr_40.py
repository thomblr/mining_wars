import random


#
# IA Functions
#


def ia(name, targets, info, players, ships_ingame, ships_type, ships_structure):
    """
    The main function of the AI which compute which orders to sent.

    Parameters
    ----------
    name: the name of the player who plays (str)
    targets: the current targets of the ships (dictionary)
    info: the information of the asteroids and the portals (dictionary)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of the ships (dictionary)
    ships_structure: the structure of the ships (dictionary)

    Returns
    -------
    orders: the orders of the AI (str)

    Version
    -------
    specification: Thomas Blanchy (v.1 29/04/2018)
    implementation: Thomas Blanchy, Cyril Weber, Joaquim Peremans (v.5 06/05/2018)
    """

    orders = []

    # Lock orders to an asteroid
    for asteroid in info['asteroids']:
        for ship in players[name]['ships']:
            if ships_ingame[ship]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                stock = ships_type[ships_ingame[ship]['type']]['tonnage'] - ships_ingame[ship]['ore']
                if asteroid['position'] == ships_ingame[ship]['position'] and stock > 0:
                    if asteroid['ore'] > 0.01:
                        if ship not in asteroid['ships_locked']:
                            orders.append('%s:lock' % ship)

    # Lock orders to a portal
    for portal in info['portals']:
        for ship in players[name]['ships']:
            if ships_ingame[ship]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                if portal['position'] == ships_ingame[ship]['position'] and ships_ingame[ship]['ore'] > 0:
                    if ship not in portal['ships_locked']:
                        orders.append('%s:lock' % ship)

    # Unlock orders from an asteroid
    # -> for every enemy ship : if dist(enemy, ship) <= range(enemy) + 1 -> unlock
    for asteroid in info['asteroids']:
        for ship in asteroid['ships_locked']:
            if ship in players[name]['ships']:
                if ships_ingame[ship]['ore'] == ships_type[ships_ingame[ship]['type']]['tonnage'] \
                        or enemy_close(ship, players, ships_ingame, ships_type) or asteroid['ore'] < 0.1:
                    orders.append('%s:release' % ship)

    # Unlock orders from a portal
    for portal in info['portals']:
        for ship in portal['ships_locked']:
            if ship in players[name]['ships']:
                if ships_ingame[ship]['ore'] == 0:
                    orders.append('%s:release' % ship)

    # Buy orders
    player_ore = int(players[name]['ore'])
    if not players[name]['ships'] and player_ore == 4:
        orders.append('%s#%d:Excavator-M' % (name[:3], random.randint(0, 999)))
        orders.append('%s#%d:Excavator-M' % (name[:3], random.randint(0, 999)))
    else:
        types_of_ship = list(ships_type.keys())
        random.shuffle(types_of_ship)
        ore_started = info['total_ore_on_board']
        current_ore = 0
        for asteroid in info['asteroids']:
            current_ore += asteroid['ore']
        ore_ratio = current_ore / ore_started

        ships_to_buy = []

        if ore_ratio >= 0.8:
            type_to_buy = random.choice(['Excavator-S', 'Excavator-M', 'Excavator-L'])
            if player_ore >= ships_type[type_to_buy]['cost']:
                if random.random() > 0.5:
                    orders.append('%s#%d:%s' % (name[:3], random.randint(0, 999), type_to_buy))
                    player_ore -= ships_type[type_to_buy]['cost']
        elif ore_ratio >= 0.5:
            type_to_buy = random.choice(['Warship', 'Scout', 'Excavator-L'])
            if player_ore >= ships_type[type_to_buy]['cost']:
                if random.random() > 0.5 or type_to_buy == 'Warship':
                    ship_name = '%s#%d' % (name[:3], random.randint(0, 999))
                    orders.append('%s:%s' % (ship_name, type_to_buy))
                    ships_to_buy.append((ship_name, type_to_buy))
                    player_ore -= ships_type[type_to_buy]['cost']
        else:
            type_to_buy = random.choice(['Warship', 'Scout'])
            if player_ore >= ships_type[type_to_buy]['cost']:
                if random.random() > 0.5:
                    ship_name = '%s#%d' % (name[:3], random.randint(0, 999))
                    orders.append('%s:%s' % (ship_name, type_to_buy))
                    ships_to_buy.append((ship_name, type_to_buy))
                    player_ore -= ships_type[type_to_buy]['cost']

    # Update all ships target to know where to move and where to attack
    for player_ship in players[name]['ships']:
        set_ship_target(name, [player_ship, ships_ingame[player_ship]['type']],
                        targets, info, players, ships_ingame, ships_type)

    attack_this_round = []
    # Attack orders
    for ship in players[name]['ships']:
        if ships_ingame[ship]['type'] in ['Scout', 'Warship']:
            player_index = list(players.keys()).index(name)
            enemy_player = list(players.keys())[abs(player_index - 1)]

            # Handle attack other ships
            pos_to_attack = []
            for enemy_ship in players[enemy_player]['ships']:
                ship_structure = []
                for enemy_ship_structure in ships_structure[ships_ingame[enemy_ship]['type']]:
                    ship_structure.append([ships_ingame[enemy_ship]['position'][0] + enemy_ship_structure[0],
                                           ships_ingame[enemy_ship]['position'][1] + enemy_ship_structure[1]])

                for enemy_ship_structure in ship_structure:
                    if check_range(ship, enemy_ship_structure, ships_ingame, ships_type):
                        pos_to_attack.append([enemy_ship_structure[0], enemy_ship_structure[1]])

            # Handle attack enemy portal
            enemy_portal = get_portal_from_player(enemy_player, players, info)
            portal_structure = [(-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
                                (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
                                (0, -2), (0, -1), (0, 0), (0, 1), (0, 2),
                                (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
                                (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)]

            portal_pos_to_attack = []
            for portal_element in portal_structure:
                r_pos = enemy_portal['position'][0] + portal_element[0]
                c_pos = enemy_portal['position'][1] + portal_element[1]

                if check_range(ship, [r_pos, c_pos], ships_ingame, ships_type):
                    portal_pos_to_attack.append([r_pos, c_pos])

            all_pos = pos_to_attack.copy()
            all_pos.extend(portal_pos_to_attack)
            attacked = False

            for attack_pos in all_pos:
                if attack_pos in portal_pos_to_attack and attack_pos in pos_to_attack:
                    if not attacked:
                        orders.append('%s:*%d-%d' % (ship, attack_pos[0], attack_pos[1]))
                        attacked = True
                        attack_this_round.append(ship)

            if not attacked:
                for attack_pos in all_pos:
                    if attack_pos in portal_pos_to_attack:
                        if not attacked:
                            orders.append('%s:*%d-%d' % (ship, attack_pos[0], attack_pos[1]))
                            attacked = True
                            attack_this_round.append(ship)

            if not attacked:
                for attack_pos in all_pos:
                    if attack_pos in pos_to_attack:
                        if not attacked:
                            orders.append('%s:*%d-%d' % (ship, attack_pos[0], attack_pos[1]))
                            attacked = True
                            attack_this_round.append(ship)

    # Move orders
    current_ore = 0
    for asteroid in info['asteroids']:
        current_ore += asteroid['ore']

    for ship in players[name]['ships']:
        if ship not in attack_this_round:
            current_pos = ships_ingame[ship]['position']
            target_position = targets[ship]
            current_ore = 0
            for asteroid in info['asteroids']:
                current_ore += asteroid['ore']

            ship_type = ships_ingame[ship]['type']
            r_delta = target_position[0] - ships_ingame[ship]['position'][0]
            c_delta = target_position[1] - ships_ingame[ship]['position'][1]

            # --- Apply movement to the target
            if not check_range(ship, target_position, ships_ingame, ships_type) \
                    or ship_type in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                r_move = 0 if target_position[0] == current_pos[0] else r_delta / abs(r_delta)
                c_move = 0 if target_position[1] == current_pos[1] else c_delta / abs(c_delta)

                new_pos_r = current_pos[0] + r_move
                new_pos_c = current_pos[1] + c_move
                orders.append('%s:@%d-%d' % (ship, new_pos_r, new_pos_c))

    return ' '.join(orders)


def set_ship_target(owner_name, ship, targets, info, players, ships_ingame, ships_type):
    """
    Set target of a scout according to the best asteroids

    Parameters
    ----------
    owner_name: the name of the player who own the scout (str)
    ship: the name and the type of the ship (tuple)
    targets: the current targets of the scout on the board (dictionary)
    info: the information of the asteroids on the board (dictionary)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of all the types of ship (dictionary)

    Returns
    -------
    None

    Version
    -------
    specification: Thomas Blanchy (v.1 29/04/2018)
    implementation: Thomas Blanchy, Cyril Weber (v.2 01/05/2018)
    """

    ore_started = info['total_ore_on_board']
    current_ore = 0
    for asteroid in info['asteroids']:
        current_ore += asteroid['ore']
    ore_ratio = current_ore / ore_started

    if ships_ingame[ship[0]]['type'] == 'Scout':
        # Check if enemy extractor left to avoid targeting asteroids if nobody comes to recolt
        extractor_left = False
        player_index = list(players.keys()).index(owner_name)
        enemy_player = list(players.keys())[abs(player_index - 1)]
        for enemy_ship in players[enemy_player]['ships']:
            if ships_ingame[enemy_ship]['type'].startswith('Excavator'):
                extractor_left = True

        if ore_ratio > 0.1 and extractor_left:  # Still some ore left -> Target ships on asteroids
            if ship[0] in targets:
                for asteroid in info['asteroids']:
                    if asteroid['position'][0] == targets[ship[0]][0] \
                            and asteroid['position'][1] == targets[ship[0]][1]:
                        if asteroid['ore'] < 0.1:
                            # Find best asteroid to attack
                            best_asteroid = dict(find_best_asteroid_to_attack(owner_name, info, targets, players))
                            targets[ship[0]] = [best_asteroid['position'][0], best_asteroid['position'][1]]
            else:
                # Find best asteroid to attack
                best_asteroid = dict(find_best_asteroid_to_attack(owner_name, info, targets, players))
                targets[ship[0]] = [best_asteroid['position'][0], best_asteroid['position'][1]]
        else:  # -> Target enemy portal as there is not any ore left
            player_index = list(players.keys()).index(owner_name)
            enemy_portal = info['portals'][abs(player_index - 1)]
            targets[ship[0]] = [enemy_portal['position'][0], enemy_portal['position'][1]]
    elif ships_ingame[ship[0]]['type'] == 'Warship':
        # Always target enemy portal
        for player in players:
            if ship[0] not in players[player]['ships']:
                portal = get_portal_from_player(player, players, info)
                targets[ship[0]] = [portal['position'][0], portal['position'][1]]
    else:
        # Excavator : target closest asteroid
        space_left = ships_type[ships_ingame[ship[0]]['type']]['tonnage'] - ships_ingame[ship[0]]['ore']
        if space_left > 0.01 and current_ore > 0.01:
            closest_asteroid = get_closest_asteroid(info, ships_ingame[ship[0]]['position'])
            targets[ship[0]] = [closest_asteroid['position'][0], closest_asteroid['position'][1]]
        else:
            owner_name = get_player_from_ship(ship[0], players)
            portal_pos = get_portal_from_player(owner_name, players, info)
            targets[ship[0]] = [portal_pos['position'][0], portal_pos['position'][1]]


def find_best_asteroid_to_attack(player, info, targets, players):
    """
    Find the best asteroid with the max ores and who's not targeted yet.

    Parameters
    ----------
    player: the name of the attacker (str)
    info: the information of the elements on the board (dictionary)
    targets: the current targets of the ships (dictionary)
    players: the information of the players (dictionary)

    Returns
    -------
    asteroid: the best asteroid (dictionary)

    Version
    -------
    specification: Thomas Blanchy (v.1 29/04/2018)
    implementation: Thomas Blanchy, Joaquim Peremans (01/05/2018)
    """

    current_max = -1
    best_asteroid = ''

    new_list_asteroids = []
    if len(targets) > 0:
        for asteroid in info['asteroids']:
            a_pos = asteroid['position']
            can_be_targeted = True
            for target in targets:
                t_pos = targets[target]
                if t_pos[0] == a_pos[0] and t_pos[1] == a_pos[1] and target in players[player]['ships']:
                    can_be_targeted = False
            if can_be_targeted:
                new_list_asteroids.append(asteroid)
    else:
        new_list_asteroids = info['asteroids']

    for asteroid in new_list_asteroids:
        if asteroid['ore'] > current_max or asteroid['ore'] == -1:
            current_max = asteroid['ore']
            best_asteroid = asteroid
    return best_asteroid


def enemy_close(ship_name, players, ships_ingame, ships_type):
    """
    Check if there is any enemy attack ship close to a certain ship.

    Parameters
    ----------
    ship_name: the name of the ship (str)
    players: the information of the players (dictionary)
    ships_ingame: the information of the ships on the board (dictionary)
    ships_type: the features of the different ships (dictionary)

    Returns
    -------
    enemy: if there is any enemy or not (bool)

    Version
    -------
    specification: Thomas Blanchy (v.1 29/04/2018)
    implementation: Thomas Blanchy, Joaquim Peremans (v.2 01/05/2018)
    """

    ship_pos = ships_ingame[ship_name]['position']
    player = get_player_from_ship(ship_name, players)
    player_index = list(players.keys()).index(player)
    enemy_player = list(players.keys())[abs(player_index - 1)]

    for enemy_ship in players[enemy_player]['ships']:
        enemy_ship_type = ships_ingame[enemy_ship]['type']

        if enemy_ship_type in ['Scout', 'Warship']:
            enemy_ship_pos = ships_ingame[enemy_ship]['position']

            r_delta = abs(enemy_ship_pos[0] - ship_pos[0])
            c_delta = abs(enemy_ship_pos[1] - ship_pos[1])

            if r_delta + c_delta < ships_type[ships_ingame[enemy_ship]['type']]['range'] + 1:
                return ships_ingame[enemy_ship]
    return False


#
# Help Functions
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
    current_distance = -1

    for asteroid in info['asteroids']:
        if asteroid['ore'] > 0.1:
            asteroid_pos = asteroid['position']
            distance = abs(position[0] - asteroid_pos[0]) + abs(position[1] - asteroid_pos[1])

            close = False
            if distance < current_distance or current_distance == -1:
                close = True

            if close:
                current_closest_asteroid = asteroid
                current_distance = distance

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

    if attacker_ship['type'] in ['Warship', 'Scout']:
        return distance <= ships_type[attacker_ship['type']]['range']
    else:
        return True
