import random
from dataclasses import dataclass
from constants import (MAP_WIDTH, MAP_HEIGHT, TILE_FLOOR, TILE_WALL,
    TILE_DOOR, TILE_STAIRS, ENEMY_PATROL, ENEMY_TRACKER, ENEMY_GUARD)


@dataclass
class Room:
    x: int; y: int; w: int; h: int
    @property
    def cx(self): return self.x + self.w // 2
    @property
    def cy(self): return self.y + self.h // 2


def _carve_room(m, r):
    for y in range(r.y, r.y + r.h):
        for x in range(r.x, r.x + r.w):
            if 0 < x < MAP_WIDTH-1 and 0 < y < MAP_HEIGHT-1: m[y][x] = TILE_FLOOR


def _carve_h(m, x1, x2, y):
    for x in range(min(x1,x2), max(x1,x2)+1):
        if 0 < x < MAP_WIDTH-1 and 0 < y < MAP_HEIGHT-1: m[y][x] = TILE_FLOOR


def _carve_v(m, y1, y2, x):
    for y in range(min(y1,y2), max(y1,y2)+1):
        if 0 < x < MAP_WIDTH-1 and 0 < y < MAP_HEIGHT-1: m[y][x] = TILE_FLOOR


def _find_door_pos(m, a, b):
    ax, ay, bx, by = a.cx, a.cy, b.cx, b.cy
    cands = []
    for x in range(min(ax,bx), max(ax,bx)+1):
        if m[ay][x] == TILE_FLOOR:
            w1 = m[ay-1][x] if ay > 0 else TILE_WALL
            w2 = m[ay+1][x] if ay < MAP_HEIGHT-1 else TILE_WALL
            if w1 == TILE_WALL and w2 == TILE_WALL:
                cands.append((x, ay))
    for y in range(min(ay,by), max(ay,by)+1):
        if m[y][ax] == TILE_FLOOR:
            w1 = m[y][ax-1] if ax > 0 else TILE_WALL
            w2 = m[y][ax+1] if ax < MAP_WIDTH-1 else TILE_WALL
            if w1 == TILE_WALL and w2 == TILE_WALL:
                cands.append((ax, y))
    for x in range(min(ax,bx), max(ax,bx)+1):
        if m[by][x] == TILE_FLOOR:
            w1 = m[by-1][x] if by > 0 else TILE_WALL
            w2 = m[by+1][x] if by < MAP_HEIGHT-1 else TILE_WALL
            if w1 == TILE_WALL and w2 == TILE_WALL:
                cands.append((x, by))
    for y in range(min(ay,by), max(ay,by)+1):
        if m[y][bx] == TILE_FLOOR:
            w1 = m[y][bx-1] if bx > 0 else TILE_WALL
            w2 = m[y][bx+1] if bx < MAP_WIDTH-1 else TILE_WALL
            if w1 == TILE_WALL and w2 == TILE_WALL:
                cands.append((bx, y))
    return random.choice(cands) if cands else None


def _room_floor(m, r, excl=None):
    fs = [(x,y) for y in range(r.y+1, r.y+r.h-1) for x in range(r.x+1, r.x+r.w-1)
          if m[y][x]==TILE_FLOOR and (not excl or (x,y) not in excl)]
    return random.choice(fs) if fs else None


def _rand_floor(m, excl=None):
    fs = [(x,y) for y in range(1,MAP_HEIGHT-1) for x in range(1,MAP_WIDTH-1)
          if m[y][x]==TILE_FLOOR and (not excl or (x,y) not in excl)]
    return random.choice(fs) if fs else (MAP_WIDTH//2, MAP_HEIGHT//2)


def generate_map(level=1):
    m = [[TILE_WALL]*MAP_WIDTH for _ in range(MAP_HEIGHT)]
    rooms = []
    target_rooms = random.randint(5, 8)
    for _ in range(target_rooms * 5):
        w, h = random.randint(4,9), random.randint(3,7)
        x, y = random.randint(1,MAP_WIDTH-w-2), random.randint(1,MAP_HEIGHT-h-2)
        nr = Room(x, y, w, h)
        if any(x-1<r2.x+r2.w and x+w+1>r2.x and y-1<r2.y+r2.h and y+h+1>r2.y for r2 in rooms):
            continue
        _carve_room(m, nr)
        if rooms:
            p = rooms[-1]
            if random.random() < 0.5:
                _carve_h(m, p.cx, nr.cx, p.cy); _carve_v(m, p.cy, nr.cy, nr.cx)
            else:
                _carve_v(m, p.cy, nr.cy, p.cx); _carve_h(m, p.cx, nr.cx, nr.cy)
        rooms.append(nr)
        if len(rooms) >= target_rooms: break

    if len(rooms) < 2:
        for y2 in range(3, MAP_HEIGHT-3):
            for x2 in range(3, MAP_WIDTH-3): m[y2][x2] = TILE_FLOOR
        rooms = [Room(3,3,5,4), Room(MAP_WIDTH-9, MAP_HEIGHT-8, 5, 4)]

    doors, keys, occ = [], [], set()
    dc = min(1 + level // 2, len(rooms) - 1, 3)
    indices = random.sample(range(1, len(rooms)), dc)
    for idx in indices:
        dp = _find_door_pos(m, rooms[idx-1], rooms[idx])
        if dp and m[dp[1]][dp[0]] == TILE_FLOOR:
            m[dp[1]][dp[0]] = TILE_DOOR; doors.append(dp); occ.add(dp)
            kr_idx = random.randint(0, max(0, idx-1))
            kp = _room_floor(m, rooms[kr_idx], occ) or _rand_floor(m, occ)
            keys.append(kp); occ.add(kp)

    if not doors and len(rooms) >= 2:
        dp = _find_door_pos(m, rooms[0], rooms[-1])
        if dp and m[dp[1]][dp[0]] == TILE_FLOOR:
            m[dp[1]][dp[0]] = TILE_DOOR; doors.append(dp)
            kp = _room_floor(m, rooms[0], occ) or _rand_floor(m, occ)
            keys.append(kp)

    ps = (rooms[0].cx, rooms[0].cy)
    sx, sy = rooms[-1].cx, rooms[-1].cy
    m[sy][sx] = TILE_STAIRS; occ.update([ps, (sx,sy)])

    enemies = []
    for _ in range(3 + level):
        p = _rand_floor(m, occ); occ.add(p)
        if level <= 2: et = ENEMY_PATROL
        elif level <= 4: et = random.choice([ENEMY_PATROL]*2+[ENEMY_TRACKER])
        else: et = random.choices([ENEMY_PATROL,ENEMY_TRACKER,ENEMY_GUARD],[3,2,1])[0]
        enemies.append((p[0], p[1], et))

    return {'map':m, 'player_spawn':ps, 'keys':keys, 'enemies':enemies, 'stairs':(sx,sy), 'doors':doors}
