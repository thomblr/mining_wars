import implementation
import random


def ia_func(name, targets, info, players, ships_ingame, ships_type):

    orders = []

    # Lock orders to an asteroid
    for asteroid in info['asteroids']:
        for ship in ships_ingame:
            if ships_ingame[ship]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                if implementation.get_player_from_ship(ship, players) == name:
                    stock = ships_type[ships_ingame[ship]['type']]['tonnage'] - ships_ingame[ship]['ore']
                    if asteroid['position'] == ships_ingame[ship]['position'] and stock > 0:
                        if asteroid['ore'] > 0.01:
                            if ship not in asteroid['ships_locked']:
                                orders.append('%s:lock' % ship)

    # Lock orders to a portal
    for portal in info['portals']:
        for ship in ships_ingame:
            if ships_ingame[ship]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                if implementation.get_player_from_ship(ship, players) == name:
                    if portal['position'] == ships_ingame[ship]['position'] and ships_ingame[ship]['ore'] > 0:
                        if ship not in portal['ships_locked']:
                            orders.append('%s:lock' % ship)

    # Unlock orders from an asteroid
    # -> for every enemy ship : if dist(enemy, ship) <= range(enemy) + 1 -> unlock
    for asteroid in info['asteroids']:
        for ship in asteroid['ships_locked']:
            if implementation.get_player_from_ship(ship, players) == name:
                if ships_ingame[ship]['ore'] == ships_type[ships_ingame[ship]['type']]['tonnage'] \
                        or enemy_close(ship, players, ships_ingame, ships_type):
                    orders.append('%s:release' % ship)

    # Unlock orders from a portal
    for portal in info['portals']:
        for ship in portal['ships_locked']:
            if implementation.get_player_from_ship(ship, players) == name:
                if ships_ingame[ship]['ore'] == 0:
                    orders.append('%s:release' % ship)

    # Buy orders
    player_ore = int(players[name]['ore'])
    if not players[name]['ships'] and player_ore == 4:
        orders.append('IAs%d:Excavator-M' % random.randint(999))
        orders.append('IAs%d:Excavator-M' % random.randint(999))
    else:
        types_of_ship = list(ships_type.keys())
        random.shuffle(types_of_ship)
        ore_started = info['total_ore_on_board']
        current_ore = 0
        for asteroid in info['asteroids']:
            current_ore += asteroid['ore']
        ore_ratio = current_ore / ore_started

        ship_type_to_buy = []

        if ore_ratio >= 0.8:
            for ship_type in types_of_ship:
                if ship_type in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                    if players[name]['ore'] >= ships_type[ship_type]['cost']:
                        if random.random() > 0.5:
                            orders.append('IAs#%d' % random.randint(999))
                            ship_type_to_buy.append(ship_type)
                            player_ore -= ships_type[ship_type]['cost']
        elif ore_ratio >= 0.3:
            for ship_type in types_of_ship:
                if players[name]['ore'] >= ships_type[ship_type]['cost']:
                    if random.random() > 0.5 or ship_type == 'Warship':
                        orders.append('IAs#%d' % random.randint(999))
                        ship_type_to_buy.append(ship_type)
                        player_ore -= ships_type[ship_type]['cost']
        else:
            for ship_type in types_of_ship:
                if ship_type in ['Scout', 'Warship']:
                    if players[name]['ore'] >= ships_type[ship_type]['cost']:
                        if random.random() > 0.5:
                            orders.append('IAs#%d' % random.randint(999))
                            ship_type_to_buy.append(ship_type)
                            player_ore -= ships_type[ship_type]['cost']

        for ship_type in ship_type_to_buy:
            if ship_type == 'Scout':
                # Find best asteroid to attack
                best_asteroid = dict(find_best_asteroid_to_attack(info))
                targets[name] = [best_asteroid['position'][0], best_asteroid['position'][1]]

    # Move orders
    space_left = ships_type[ships_ingame[name]['type']]['tonnage'] - ships_ingame[name]['ore']
    current_pos = ships_ingame[name]['position']

    if ships_ingame[name]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
        if space_left > 0.01:
            closest_asteroid = implementation.get_closest_asteroid(info, current_pos)

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
            orders.append('%s:@%d-%d' % (name, new_pos_r, new_pos_c))
        else:
            owner_name = implementation.get_player_from_ship(name, players)
            portal_pos = implementation.get_portal_from_player(owner_name, players, info)

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
            orders.append('%s:@%d-%d' % (name, new_pos_r, new_pos_c))
    else:
        # Handle Attack ships
        if ships_ingame[name]['type'] == 'Warship':
            for player in players:
                if name not in players[player]['ships']:
                    portal = implementation.get_portal_from_player(player, players, info)
                    r_diff = abs(portal['position'][0] - ships_ingame[name]['position'][0])
                    c_diff = abs(portal['position'][1] - ships_ingame[name]['position'][1])

                    if r_diff + c_diff > 5:
                        # Compute X move
                        x_move = 0
                        if portal['position'][0] > current_pos[0]:
                            x_move = 1
                        elif portal['position'][0] < current_pos[0]:
                            x_move = -1

                        # Compute Y move
                        y_move = 0
                        if portal['position'][1] > current_pos[1]:
                            y_move = 1
                        elif portal['position'][1] < current_pos[1]:
                            y_move = -1

                        new_pos_r = current_pos[0] + x_move
                        new_pos_c = current_pos[1] + y_move
                        orders.append('%s:@%d-%d' % (name, new_pos_r, new_pos_c))
        else:
            if name in targets:
                r_diff = abs(targets[name][0] - ships_ingame[name]['position'][0])
                c_diff = abs(targets[name][0] - ships_ingame[name]['position'][1])

                if r_diff + c_diff > 3:
                    # Compute X move
                    x_move = 0
                    if targets[name][0] > current_pos[0]:
                        x_move = 1
                    elif targets[name][0] < current_pos[0]:
                        x_move = -1

                    # Compute Y move
                    y_move = 0
                    if targets[name][1] > current_pos[1]:
                        y_move = 1
                    elif targets[name][1] < current_pos[1]:
                        y_move = -1

                    new_pos_r = current_pos[0] + x_move
                    new_pos_c = current_pos[1] + y_move
                    orders.append('%s:@%d-%d' % (name, new_pos_r, new_pos_c))

    # Attack orders
    return orders


def find_best_asteroid_to_attack(info):
    current_max = -1
    best_asteroid = ''
    for asteroid in info['asteroids']:
        if asteroid['ore'] > current_max or asteroid['ore'] == -1:
            current_max = asteroid['ore']
            best_asteroid = asteroid
    return best_asteroid


def enemy_close(ship_name, players, ships_ingame, ships_type):
    for player in players:
        if ship_name not in players[player]['ships']:
            enemy_player = players[player]
            ship_pos = ships_ingame[ship_name]['position']

            for enemy_ship_name in enemy_player['ships']:
                enemy_ship_type = ships_ingame[enemy_ship_name]['type']

                if enemy_ship_type in ['Scout', 'Warship']:
                    enemy_ship_pos = ships_ingame[enemy_ship_name]['position']

                    r_delta = abs(enemy_ship_pos[0] - ship_pos[0])
                    c_delta = abs(enemy_ship_pos[1] - ship_pos[0])

                    if r_delta + c_delta < ships_type[ships_ingame[enemy_ship_name]['type']]['range'] + 1:
                        return True
    return False
