import random
from dataclasses import dataclass
from constants import MAP_WIDTH, MAP_HEIGHT, TILE_FLOOR, TILE_WALL, TILE_DOOR, TILE_STAIRS


@dataclass
class Room:
    x: int
    y: int
    w: int
    h: int


def create_empty_map():
    return [[TILE_WALL for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]


def carve_room(game_map, room):
    for y in range(room.y, room.y + room.h):
        for x in range(room.x, room.x + room.w):
            if 0 < x < MAP_WIDTH - 1 and 0 < y < MAP_HEIGHT - 1:
                game_map[y][x] = TILE_FLOOR


def carve_h_tunnel(game_map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        if 0 < x < MAP_WIDTH - 1 and 0 < y < MAP_HEIGHT - 1:
            game_map[y][x] = TILE_FLOOR


def carve_v_tunnel(game_map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if 0 < x < MAP_WIDTH - 1 and 0 < y < MAP_HEIGHT - 1:
            game_map[y][x] = TILE_FLOOR


def place_doors(game_map, rooms):
    doors = []
    for i in range(1, len(rooms)):
        prev = rooms[i - 1]
        curr = rooms[i]
        px = prev.x + prev.w // 2
        py = prev.y + prev.h // 2
        cx = curr.x + curr.w // 2
        cy = curr.y + curr.h // 2
        if random.random() < 0.3:
            if py == cy:
                door_x = random.randint(min(px, cx) + 1, max(px, cx) - 1)
                if game_map[py][door_x] == TILE_FLOOR:
                    game_map[py][door_x] = TILE_DOOR
                    doors.append((door_x, py))
            elif px == cx:
                door_y = random.randint(min(py, cy) + 1, max(py, cy) - 1)
                if game_map[door_y][px] == TILE_FLOOR:
                    game_map[door_y][px] = TILE_DOOR
                    doors.append((px, door_y))
    return doors


def get_random_floor_pos(game_map):
    floors = []
    for y in range(1, MAP_HEIGHT - 1):
        for x in range(1, MAP_WIDTH - 1):
            if game_map[y][x] == TILE_FLOOR:
                floors.append((x, y))
    if floors:
        return random.choice(floors)
    return (MAP_WIDTH // 2, MAP_HEIGHT // 2)


def generate_map(level=1):
    game_map = create_empty_map()
    rooms = []
    num_rooms = random.randint(4, 7)

    for _ in range(num_rooms * 3):
        w = random.randint(4, 9)
        h = random.randint(3, 7)
        x = random.randint(1, MAP_WIDTH - w - 2)
        y = random.randint(1, MAP_HEIGHT - h - 2)
        new_room = Room(x, y, w, h)

        overlaps = False
        for r in rooms:
            if (x - 1 < r.x + r.w and x + w + 1 > r.x and
                y - 1 < r.y + r.h and y + h + 1 > r.y):
                overlaps = True
                break

        if not overlaps:
            carve_room(game_map, new_room)
            if rooms:
                prev = rooms[-1]
                px = prev.x + prev.w // 2
                py = prev.y + prev.h // 2
                cx = new_room.x + new_room.w // 2
                cy = new_room.y + new_room.h // 2
                if random.random() < 0.5:
                    carve_h_tunnel(game_map, px, cx, py)
                    carve_v_tunnel(game_map, py, cy, cx)
                else:
                    carve_v_tunnel(game_map, py, cy, px)
                    carve_h_tunnel(game_map, px, cx, cy)
            rooms.append(new_room)
            if len(rooms) >= num_rooms:
                break

    doors = place_doors(game_map, rooms)

    key_count = max(1, len(doors))
    keys = []
    for _ in range(key_count):
        kx, ky = get_random_floor_pos(game_map)
        keys.append((kx, ky))

    enemy_count = min(3 + level, 10)
    enemies = []
    for _ in range(enemy_count):
        ex, ey = get_random_floor_pos(game_map)
        enemies.append((ex, ey))

    if rooms:
        start_room = rooms[0]
        player_spawn = (start_room.x + start_room.w // 2, start_room.y + start_room.h // 2)
        end_room = rooms[-1]
        stairs_pos = (end_room.x + end_room.w // 2, end_room.y + end_room.h // 2)
        game_map[stairs_pos[1]][stairs_pos[0]] = TILE_STAIRS
    else:
        player_spawn = (MAP_WIDTH // 2, MAP_HEIGHT // 2)
        stairs_pos = (MAP_WIDTH - 3, MAP_HEIGHT - 3)
        game_map[stairs_pos[1]][stairs_pos[0]] = TILE_STAIRS

    return {
        'map': game_map,
        'player_spawn': player_spawn,
        'keys': keys,
        'enemies': enemies,
        'stairs': stairs_pos,
        'doors': doors
    }
