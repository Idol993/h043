import random
from collections import deque
from dataclasses import dataclass
from constants import (MAP_WIDTH, MAP_HEIGHT, TILE_FLOOR, TILE_WALL,
    TILE_DOOR, TILE_STAIRS, ENEMY_PATROL, ENEMY_TRACKER, ENEMY_GUARD, ENEMY_ELITE)

@dataclass
class Room:
    x:int; y:int; w:int; h:int
    @property
    def cx(self): return self.x+self.w//2
    @property
    def cy(self): return self.y+self.h//2

def _bfs(m, s, e, door_pass=True):
    if s==e: return True
    v={s}; q=deque([s])
    while q:
        x,y=q.popleft()
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx,ny=x+dx,y+dy
            if nx<0 or ny<0 or nx>=MAP_WIDTH or ny>=MAP_HEIGHT or (nx,ny) in v: continue
            t=m[ny][nx]
            if t==TILE_WALL or (t==TILE_DOOR and not door_pass): continue
            if (nx,ny)==e: return True
            v.add((nx,ny)); q.append((nx,ny))
    return False

def _carve(m,x1,x2,y1,y2):
    for y in range(min(y1,y2),max(y1,y2)+1):
        for x in range(min(x1,x2),max(x1,x2)+1):
            if 0<x<MAP_WIDTH-1 and 0<y<MAP_HEIGHT-1: m[y][x]=TILE_FLOOR

def _carve_h(m,x1,x2,y): _carve(m,min(x1,x2),max(x1,x2),y,y)
def _carve_v(m,y1,y2,x): _carve(m,x,x,min(y1,y2),max(y1,y2))

def _door_pos(m,a,b):
    ax,ay,bx,by=a.cx,a.cy,b.cx,b.cy; c=[]
    for x in range(min(ax,bx),max(ax,bx)+1):
        if m[ay][x]==TILE_FLOOR and 0<ay<MAP_HEIGHT-1 and m[ay-1][x]==TILE_WALL and m[ay+1][x]==TILE_WALL: c.append((x,ay))
    for y in range(min(ay,by),max(ay,by)+1):
        if m[y][ax]==TILE_FLOOR and 0<ax<MAP_WIDTH-1 and m[y][ax-1]==TILE_WALL and m[y][ax+1]==TILE_WALL: c.append((ax,y))
    for x in range(min(ax,bx),max(ax,bx)+1):
        if m[by][x]==TILE_FLOOR and 0<by<MAP_HEIGHT-1 and m[by-1][x]==TILE_WALL and m[by+1][x]==TILE_WALL: c.append((x,by))
    for y in range(min(ay,by),max(ay,by)+1):
        if m[y][bx]==TILE_FLOOR and 0<bx<MAP_WIDTH-1 and m[y][bx-1]==TILE_WALL and m[y][bx+1]==TILE_WALL: c.append((bx,y))
    return random.choice(c) if c else None

def _rand(m,r=None,ex=None):
    if r:
        fs=[(x,y) for y in range(r.y+1,r.y+r.h-1) for x in range(r.x+1,r.x+r.w-1) if m[y][x]==TILE_FLOOR and (not ex or (x,y) not in ex)]
    else:
        fs=[(x,y) for y in range(1,MAP_HEIGHT-1) for x in range(1,MAP_WIDTH-1) if m[y][x]==TILE_FLOOR and (not ex or (x,y) not in ex)]
    return random.choice(fs) if fs else None

def _force_route(m,sr,er):
    sx,sy,ex,ey=sr.cx,sr.cy,er.cx,er.cy
    dx,dy=min(er.cx-3,sr.cx+6),(sr.cy+er.cy)//2
    if dx>=MAP_WIDTH-2: dx=MAP_WIDTH//2
    dy=max(4,min(dy,MAP_HEIGHT-5))
    _carve_h(m,sx,dx,sy); _carve_v(m,sy,dy,dx); _carve_h(m,dx,ex,dy); _carve_v(m,dy,ey,ex)
    for y in range(2,MAP_HEIGHT-2):
        if 0<dx-1<MAP_WIDTH-1 and y!=sy and y!=dy: m[y][dx-1]=TILE_WALL
        if 0<dx+1<MAP_WIDTH-1 and y!=sy and y!=dy: m[y][dx+1]=TILE_WALL
    m[dy][dx]=TILE_DOOR
    kx,ky=random.randint(sr.x+1,sr.x+sr.w-2),random.randint(sr.y+1,sr.y+sr.h-2)
    m[ky][kx]=TILE_FLOOR; m[sy][sx]=TILE_FLOOR; m[ey][ex]=TILE_FLOOR
    return (dx,dy),(kx,ky)

def generate_map(level=1):
    m=[[TILE_WALL]*MAP_WIDTH for _ in range(MAP_HEIGHT)]
    rooms=[]; tr=random.randint(5,8)
    for _ in range(tr*6):
        w,h=random.randint(4,9),random.randint(3,7)
        x,y=random.randint(1,MAP_WIDTH-w-2),random.randint(1,MAP_HEIGHT-h-2)
        nr=Room(x,y,w,h)
        if any(x-1<r2.x+r2.w and x+w+1>r2.x and y-1<r2.y+r2.h and y+h+1>r2.y for r2 in rooms): continue
        _carve(m,nr.x,nr.x+nr.w-1,nr.y,nr.y+nr.h-1)
        if rooms:
            p=rooms[-1]
            if random.random()<0.5: _carve_h(m,p.cx,nr.cx,p.cy); _carve_v(m,p.cy,nr.cy,nr.cx)
            else: _carve_v(m,p.cy,nr.cy,p.cx); _carve_h(m,p.cx,nr.cx,nr.cy)
        rooms.append(nr)
        if len(rooms)>=tr: break
    if len(rooms)<2:
        sr=Room(3,3,6,5); er=Room(MAP_WIDTH-10,MAP_HEIGHT-9,6,5)
        rooms=[sr,er]; _carve(m,sr.x,sr.x+sr.w-1,sr.y,sr.y+sr.h-1); _carve(m,er.x,er.x+er.w-1,er.y,er.y+er.h-1)
    rooms.sort(key=lambda r:r.x+r.y)
    sr,er=rooms[0],rooms[-1]
    doors,keys,occ=[],[],set()
    dc=min(1+level//2,len(rooms)-1,3)
    for idx in sorted(random.sample(range(1,len(rooms)),dc)):
        dp=_door_pos(m,rooms[idx-1],rooms[idx])
        if dp and m[dp[1]][dp[0]]==TILE_FLOOR:
            m[dp[1]][dp[0]]=TILE_DOOR; doors.append(dp); occ.add(dp)
            kp=_rand(m,rooms[random.randint(0,max(0,idx-1))],occ) or _rand(m,None,occ) or (MAP_WIDTH//2,MAP_HEIGHT//2)
            if not _bfs(m,(sr.cx,sr.cy),kp,False): kp=_rand(m,sr,occ) or _rand(m,None,occ) or (MAP_WIDTH//2,MAP_HEIGHT//2)
            keys.append(kp); occ.add(kp)
    ps=(sr.cx,sr.cy); sx,sy=er.cx,er.cy; m[sy][sx]=TILE_STAIRS
    ok=len(doors)>0 and all(_bfs(m,ps,k,False) and _bfs(m,ps,(sx,sy),True) for k in keys[:len(doors)])
    if not ok:
        for y2 in range(3,MAP_HEIGHT-3):
            for x2 in range(3,MAP_WIDTH-3): m[y2][x2]=TILE_WALL
        sr=Room(3,3,6,5); er=Room(MAP_WIDTH-10,MAP_HEIGHT-9,6,5)
        _carve(m,sr.x,sr.x+sr.w-1,sr.y,sr.y+sr.h-1); _carve(m,er.x,er.x+er.w-1,er.y,er.y+er.h-1)
        dp,kp=_force_route(m,sr,er)
        doors=[dp]; keys=[kp]; occ={dp,kp}
        ps=(sr.cx,sr.cy); sx,sy=er.cx,er.cy; m[sy][sx]=TILE_STAIRS
    occ.update([ps,(sx,sy)])
    safe=4; guards=[]
    for dp in doors:
        for ddx,ddy in [(-1,0),(1,0),(0,-1),(0,1)]:
            gx,gy=dp[0]+ddx,dp[1]+ddy
            if 0<gx<MAP_WIDTH-1 and 0<gy<MAP_HEIGHT-1 and m[gy][gx]==TILE_FLOOR and (gx,gy) not in occ and abs(gx-ps[0])+abs(gy-ps[1])>=safe:
                guards.append((gx,gy)); break
    enemies=[]; total=3+level; elite=max(0,(level-4)//2)
    for _ in range(min(len(guards),1+level//3)):
        p=guards.pop(0); occ.add(p); enemies.append((p[0],p[1],ENEMY_GUARD))
    safe_fs=[(x,y) for y in range(1,MAP_HEIGHT-1) for x in range(1,MAP_WIDTH-1)
             if m[y][x]==TILE_FLOOR and (x,y) not in occ and abs(x-ps[0])+abs(y-ps[1])>=safe]
    unsafe_fs=[(x,y) for y in range(1,MAP_HEIGHT-1) for x in range(1,MAP_WIDTH-1)
               if m[y][x]==TILE_FLOOR and (x,y) not in occ and abs(x-ps[0])+abs(y-ps[1])<safe]
    random.shuffle(safe_fs); random.shuffle(unsafe_fs)
    for _ in range(elite):
        if safe_fs: p=safe_fs.pop(); occ.add(p); enemies.append((p[0],p[1],ENEMY_ELITE))
    while len(enemies)<total:
        if safe_fs: p=safe_fs.pop()
        elif unsafe_fs and len(enemies)>=max(1,total-1): p=unsafe_fs.pop()
        elif unsafe_fs: break
        else: break
        occ.add(p)
        if level<=2: et=ENEMY_PATROL
        elif level<=4: et=random.choice([ENEMY_PATROL]*2+[ENEMY_TRACKER])
        else: et=random.choices([ENEMY_PATROL,ENEMY_TRACKER,ENEMY_GUARD],[3,2,1])[0]
        enemies.append((p[0],p[1],et))
    return {'map':m,'player_spawn':ps,'keys':keys,'enemies':enemies,'stairs':(sx,sy),'doors':doors}
