import main


def check_range(attacker, target):
    # Attacker
    attacker_type = attacker['type']
    attacker_pos = attacker['position']
    # attacker_radius = main.get_ship_radius(attacker_type)
    # attacker_range = main.get_ship_range(attacker_type)

    # Target
    target_type = target['type']
    target_pos = target['position']
    # target_radius = main.get_ship_radius(target_type)
    # target_range = main.get_ship_range(target_type)

    # |r2 - r1| + |c2 - c1|
    dist = abs(target_pos[1] - attacker_pos[1]) + abs(target_pos[0] - attacker_pos[1])
    print(dist)


check_range(main.ships_ingame['thom'], main.ships_ingame['two'])
