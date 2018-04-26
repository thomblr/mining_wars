from implementation import *


def ia(name, info, players, ships_ingame, ships_type):

    orders = []

    # Lock orders to an asteroid
    for asteroid in info['asteroids']:
        for ship in ships_ingame:
            if ships_ingame[ship]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                if get_player_from_ship(ship, players) == name:
                    stock = ships_type[ships_ingame[ship]['type']]['tonnage'] - ships_ingame[ship]['ore']
                    if asteroid['position'] == ships_ingame[ship]['position'] and stock > 0:
                        if asteroid['ore'] > 0.01:
                            if ship not in asteroid['ships_locked']:
                                orders.append('%s:lock' % ship)

    # Lock orders to a portal
    for portal in info['portals']:
        for ship in ships_ingame:
            if ships_ingame[ship]['type'] in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                if get_player_from_ship(ship, players) == name:
                    if portal['position'] == ships_ingame[ship]['position'] and ships_ingame[ship]['ore'] > 0:
                        if ship not in portal['ships_locked']:
                            orders.append('%s:lock' % ship)

    # Unlock orders from an asteroid
    # -> for every enemy ship : if dist(enemy, ship) <= range(enemy) + 1 -> unlock
    for asteroid in info['asteroids']:
        for ship in asteroid['ships_locked']:
            if get_player_from_ship(ship, players) == name:
                if ships_ingame[ship]['ore'] == ships_type[ships_ingame[ship]['type']]['tonnage'] \
                        or enemy_close(ship, players, ships_ingame, ships_type):
                    orders.append('%s:release' % ship)

    # Unlock orders from a portal
    for portal in info['portals']:
        for ship in portal['ships_locked']:
            if get_player_from_ship(ship, players) == name:
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

        if ore_ratio >= 0.8:
            for ship_type in types_of_ship:
                if ship_type in ['Excavator-S', 'Excavator-M', 'Excavator-L']:
                    if players[name]['ore'] >= ships_type[ship_type]['cost']:
                        if random.random() > 0.5:
                            orders.append('IAs#%d' % random.randint(999))
                            player_ore -= ships_type[ship_type]['cost']
        elif ore_ratio >= 0.3:
            for ship_type in types_of_ship:
                if players[name]['ore'] >= ships_type[ship_type]['cost']:
                    if random.random() > 0.5 or ship_type == 'Warship':
                        orders.append('IAs#%d' % random.randint(999))
                        player_ore -= ships_type[ship_type]['cost']
        else:
            for ship_type in types_of_ship:
                if ship_type in ['Scout', 'Warship']:
                    if players[name]['ore'] >= ships_type[ship_type]['cost']:
                        if random.random() > 0.5:
                            orders.append('IAs#%d' % random.randint(999))
                            player_ore -= ships_type[ship_type]['cost']

    # Move orders

    # Attack orders


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
