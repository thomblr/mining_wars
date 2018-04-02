def load_file():
    fh = open('game.txt', 'r')
    lines = fh.readlines()
    for line in lines:
        lines[lines.index(line)] = line.replace('\n', '')
    return lines


def load_size(info):
    coords = info[1].split(' ')
    size = [int(coords[0]), int(coords[1])]
    return size


def load_portals(info):
    portals = info[info.index('portals:') + 1:info.index('asteroids:')]
    portals_pos = []
    for portal in portals:
        coords = portal.split(' ')
        pos = [int(coords[0]), int(coords[1])]
        portals_pos.append(pos)
    return portals_pos


def load_asteroids(info):
    asteroids = info[info.index('asteroids:') + 1:]
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


info = load_file()
print(load_size(info))
print(load_portals(info))
print(load_asteroids(info))
