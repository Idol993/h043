import pygame
from dataclasses import dataclass
from constants import (
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT,
    TILE_FLOOR, TILE_WALL, TILE_DOOR, TILE_STAIRS,
    COLOR_FLOOR, COLOR_WALL, COLOR_WALL_TOP, COLOR_DOOR,
    COLOR_KEY, COLOR_STAIRS, COLOR_PLAYER, COLOR_PLAYER_TOP,
    COLOR_HP_BG, COLOR_HP_FILL, COLOR_TEXT, COLOR_BG,
    ENEMY_PATROL, ENEMY_TRACKER, ENEMY_GUARD,
    COLOR_ENEMY_PATROL, COLOR_ENEMY_TRACKER, COLOR_ENEMY_GUARD,
    BUFF_NAMES, BUFF_COLORS, BUFF_DESCS
)


@dataclass
class Camera:
    x: int = 0; y: int = 0; view_w: int = 0; view_h: int = 0
    def update(self, tx, ty, ts):
        self.x = max(0, min(tx+ts//2-self.view_w//2, MAP_WIDTH*TILE_SIZE-self.view_w))
        self.y = max(0, min(ty+ts//2-self.view_h//2, MAP_HEIGHT*TILE_SIZE-self.view_h))


class Renderer:
    def __init__(self, screen):
        self.screen = screen; self.camera = Camera()
        try: self.font=pygame.font.SysFont("arial",20,bold=True); self.sfont=pygame.font.SysFont("arial",14)
        except: self.font=pygame.font.Font(None,24); self.sfont=pygame.font.Font(None,18)

    def resize(self, w, h): self.camera.view_w=w; self.camera.view_h=h
    def _iv(self, r): return pygame.Rect(0,0,self.camera.view_w,self.camera.view_h).colliderect(r)
    def _eye(self, r, ey):
        pygame.draw.rect(self.screen,(255,255,255),(r.x+4,ey,4,4))
        pygame.draw.rect(self.screen,(255,255,255),(r.right-8,ey,4,4))

    def draw_map(self, gm):
        vx=self.camera.x//TILE_SIZE-1; vy=self.camera.y//TILE_SIZE-1
        vw=self.camera.view_w//TILE_SIZE+2; vh=self.camera.view_h//TILE_SIZE+2
        for ty in range(vy,vy+vh):
            for tx in range(vx,vx+vw):
                if tx<0 or ty<0 or tx>=MAP_WIDTH or ty>=MAP_HEIGHT: continue
                t=gm[ty][tx]; px=tx*TILE_SIZE-self.camera.x; py=ty*TILE_SIZE-self.camera.y
                tr=pygame.Rect(px,py,TILE_SIZE,TILE_SIZE)
                if not self._iv(tr): continue
                if t==TILE_FLOOR: pygame.draw.rect(self.screen,COLOR_FLOOR,tr)
                elif t==TILE_WALL:
                    pygame.draw.rect(self.screen,COLOR_WALL,tr)
                    pygame.draw.rect(self.screen,COLOR_WALL_TOP,(px+2,py+2,TILE_SIZE-4,TILE_SIZE-8))
                elif t==TILE_DOOR:
                    pygame.draw.rect(self.screen,COLOR_FLOOR,tr)
                    pygame.draw.rect(self.screen,COLOR_DOOR,(px+4,py+2,TILE_SIZE-8,TILE_SIZE-4))
                    pygame.draw.rect(self.screen,(150,130,30),(px+TILE_SIZE//2-3,py+TILE_SIZE//2,6,6))
                elif t==TILE_STAIRS:
                    pygame.draw.rect(self.screen,COLOR_FLOOR,tr)
                    pygame.draw.rect(self.screen,COLOR_STAIRS,(px+6,py+6,TILE_SIZE-12,TILE_SIZE-12))
                    if self.sfont:
                        s=self.sfont.render("↓",True,(20,80,20)); self.screen.blit(s,s.get_rect(center=tr.center))

    def draw_keys(self, keys):
        for k in keys:
            if k.collected: continue
            kr=k.rect.move(-self.camera.x,-self.camera.y)
            if not self._iv(kr): continue
            pygame.draw.rect(self.screen,COLOR_KEY,kr)
            pygame.draw.rect(self.screen,(255,255,150),(kr.x+2,kr.y+2,kr.w-4,kr.h-8))

    def draw_enemies(self, enemies):
        cols={ENEMY_PATROL:COLOR_ENEMY_PATROL,ENEMY_TRACKER:COLOR_ENEMY_TRACKER,ENEMY_GUARD:COLOR_ENEMY_GUARD}
        hl={ENEMY_PATROL:(255,100,100),ENEMY_TRACKER:(220,120,255),ENEMY_GUARD:(255,200,100)}
        for e in enemies:
            er=e.rect.move(-self.camera.x,-self.camera.y)
            if not self._iv(er): continue
            pygame.draw.rect(self.screen,cols.get(e.etype,COLOR_ENEMY_PATROL),er)
            pygame.draw.rect(self.screen,hl.get(e.etype,(255,100,100)),(er.x+2,er.y+2,er.w-4,er.h-8))
            if e.etype==ENEMY_TRACKER: pygame.draw.rect(self.screen,(255,255,0),(er.centerx-2,er.y+2,4,4))
            elif e.etype==ENEMY_GUARD: pygame.draw.rect(self.screen,(100,80,40),(er.x+2,er.y+2,er.w-4,3))
            else: self._eye(er,er.y+6)

    def draw_player(self, player):
        pr=player.rect.move(-self.camera.x,-self.camera.y)
        if player.invincible_timer>0 and player.invincible_timer%8<4: return
        if player.door_shield_timer>0 and player.door_shield_timer%6<3: return
        pygame.draw.rect(self.screen,COLOR_PLAYER,pr)
        pygame.draw.rect(self.screen,COLOR_PLAYER_TOP,(pr.x+2,pr.y+2,pr.w-4,pr.h-8))
        self._eye(pr,pr.y+6)

    def draw_hud(self, player, level):
        bw,bh,bx,by=120,16,10,10
        pygame.draw.rect(self.screen,COLOR_HP_BG,(bx,by,bw,bh))
        pygame.draw.rect(self.screen,COLOR_HP_FILL,(bx,by,int(bw*(player.hp/player.max_hp)),bh))
        pygame.draw.rect(self.screen,(255,255,255),(bx,by,bw,bh),2)
        if self.font:
            self.screen.blit(self.font.render(f"HP:{player.hp}/{player.max_hp}",True,COLOR_TEXT),(bx+bw+10,by-2))
            self.screen.blit(self.font.render(f"x {player.keys}",True,COLOR_TEXT),(36,by+bh+8))
            lt=self.font.render(f"第 {level} 层",True,COLOR_TEXT)
            self.screen.blit(lt,lt.get_rect(topright=(self.camera.view_w-10,10)))
        y=by+bh+40
        for b in player.buffs:
            bc=BUFF_COLORS.get(b,COLOR_TEXT)
            pygame.draw.rect(self.screen,bc,(10,y,12,12))
            pygame.draw.rect(self.screen,(255,255,255),(10,y,12,12),1)
            if self.sfont:
                nm=BUFF_NAMES.get(b,"?")
                self.screen.blit(self.sfont.render(nm,True,bc),(26,y-2))
            y+=18
            if y>self.camera.view_h-20: break

    def _overlay(self, title, lines, hint=""):
        ov=pygame.Surface((self.camera.view_w,self.camera.view_h),pygame.SRCALPHA)
        ov.fill((0,0,0,180)); self.screen.blit(ov,(0,0))
        if not self.font: return
        cx,cy=self.camera.view_w//2,self.camera.view_h//2
        t=self.font.render(title,True,(255,200,100))
        self.screen.blit(t,t.get_rect(center=(cx,cy-60-len(lines)*10)))
        for i,l in enumerate(lines):
            t=self.font.render(l,True,COLOR_TEXT); self.screen.blit(t,t.get_rect(center=(cx,cy-20+i*28)))
        if hint:
            t=self.font.render(hint,True,(150,150,150)); self.screen.blit(t,t.get_rect(center=(cx,cy+20+len(lines)*28)))

    def draw_game_over(self, level): self._overlay("游戏结束",[f"到达第 {level} 层"],"按 R 键重新开始")

    def draw_pause(self, player, level):
        ls=["操作: 方向键/WASD 移动","P: 暂停  ESC: 退出",f"当前: 第 {level} 层",f"钥匙: {player.keys}"]
        for b in player.buffs: ls.append(f"强化: {BUFF_NAMES.get(b,'?')} - {BUFF_DESCS.get(b,'')}")
        self._overlay("暂停",ls,"按 P 继续")

    def draw_level_up(self, options, sel):
        ov=pygame.Surface((self.camera.view_w,self.camera.view_h),pygame.SRCALPHA)
        ov.fill((0,0,0,180)); self.screen.blit(ov,(0,0))
        if not self.font: return
        cx,cy=self.camera.view_w//2,self.camera.view_h//2
        t=self.font.render("选择强化!",True,(255,200,100))
        self.screen.blit(t,t.get_rect(center=(cx,cy-110)))
        for i,opt in enumerate(options):
            is_sel = (i==sel)
            c=(255,255,100) if is_sel else COLOR_TEXT
            bc=BUFF_COLORS.get(opt,COLOR_TEXT)
            bx,by2=cx-140,cy-60+i*60
            if is_sel: pygame.draw.rect(self.screen,(60,60,80),(bx-6,by2-4,290,52),border_radius=4)
            pygame.draw.rect(self.screen,bc,(bx,by2+4,24,24))
            pygame.draw.rect(self.screen,(255,255,255),(bx,by2+4,24,24),1)
            self.screen.blit(self.font.render(BUFF_NAMES.get(opt,"?"),True,c),(bx+32,by2))
            if self.sfont:
                self.screen.blit(self.sfont.render(BUFF_DESCS.get(opt,""),True,
                    (180,180,180) if is_sel else (120,120,120)),(bx+32,by2+24))
        if self.sfont:
            ht=self.sfont.render("↑↓选择 Enter确认",True,(150,150,150))
            self.screen.blit(ht,ht.get_rect(center=(cx,cy+140)))

    def clear(self): self.screen.fill(COLOR_BG)
