import random, sys
sys.path.insert(0, ".")
from map_gen import generate_map
from player import Player
from constants import (ENEMY_PATROL, ENEMY_TRACKER, ENEMY_GUARD, ENEMY_ELITE,
    BUFF_DOOR_SHIELD, BUFF_HURT_KNOCK, BUFF_KEY_KEEP, BUFF_KEY_MAGNET,
    BUFF_LOW_HP_SPEED, BUFF_INVINCIBLE)

def test_map_paths(N=300):
    fail=0
    from collections import deque
    def bfs(m, s, e, door_pass=True):
        if s==e: return True
        v={s}; q=deque([s])
        while q:
            x,y=q.popleft()
            for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx,ny=x+dx,y+dy
                if nx<0 or ny<0 or nx>=len(m[0]) or ny>=len(m): continue
                if (nx,ny) in v: continue
                t=m[ny][nx]
                if t==1 or (t==2 and not door_pass): continue
                if (nx,ny)==e: return True
                v.add((nx,ny)); q.append((nx,ny))
        return False
    for i in range(N):
        d=generate_map(level=(i%15)+1)
        m, ps, ks, stairs = d['map'], d['player_spawn'], d['keys'], d['stairs']
        for k in ks[:len(d['doors'])]:
            if not bfs(m,ps,k,False):
                print(f"FAIL lv{(i%15)+1}: 出生点不能无门到达钥匙 {k}  spawn={ps}")
                fail+=1; break
            if not bfs(m,ps,stairs,True):
                print(f"FAIL lv{(i%15)+1}: 开门后不能到达楼梯  spawn={ps} stairs={stairs}")
                fail+=1; break
    return fail

def test_safe_spawn(N=300):
    fail=0
    for i in range(N):
        d=generate_map(level=(i%15)+1)
        ps, enemies = d['player_spawn'], d['enemies']
        for ex, ey, et in enemies:
            dist = abs(ex-ps[0])+abs(ey-ps[1])
            if dist < 4 and len(enemies) > 2:
                print(f"FAIL lv{(i%15)+1}: 敌人离出生点太近 dist={dist} pos=({ex},{ey})")
                fail+=1; break
    return fail

def test_monster_layers():
    for lvl in [1,3,5,7,10,15]:
        d=generate_map(level=lvl)
        counts={ENEMY_PATROL:0,ENEMY_TRACKER:0,ENEMY_GUARD:0,ENEMY_ELITE:0}
        for _,_,et in d['enemies']: counts[et]=counts.get(et,0)+1
        print(f"Lv{lvl}: 总数{len(d['enemies'])}", 
              f"巡逻{counts[ENEMY_PATROL]} 追踪{counts[ENEMY_TRACKER]} 守卫{counts[ENEMY_GUARD]} 精英{counts[ENEMY_ELITE]}")

def test_buff_combos():
    p=Player()
    print("\n无buff组合:", p.get_combos())
    p.apply_buff(BUFF_DOOR_SHIELD); p.apply_buff(BUFF_HURT_KNOCK)
    print("破门护盾+受伤反击:", p.get_combos(), p.get_combo_info())
    p.apply_buff(BUFF_LOW_HP_SPEED)
    print("再加绝境加速:", p.get_combos())
    p.apply_buff(BUFF_KEY_KEEP); p.apply_buff(BUFF_KEY_MAGNET)
    p.apply_buff(BUFF_INVINCIBLE)
    print("全buff组合:", p.get_combos(), p.get_combo_info())
    print("磁铁加成:", p.get_magnet_bonus())
    print("击退加成(满血):", p.get_knockback_bonus())
    p.hp=1
    print("击退加成(残血):", p.get_knockback_bonus())
    p.door_shield_timer=60
    print("击退加成(护盾期):", p.get_knockback_bonus())

if __name__=="__main__":
    print("=== 测试1: 地图路径连通性(300次) ===")
    f=test_map_paths(300)
    print(f"  路径失败: {f}")
    print("\n=== 测试2: 出生点安全区(300次) ===")
    f=test_safe_spawn(300)
    print(f"  安全区失败: {f}")
    print("\n=== 测试3: 怪物层次分布 ===")
    test_monster_layers()
    print("\n=== 测试4: 能力组合检测 ===")
    test_buff_combos()
    print("\n=== 完成 ===")
