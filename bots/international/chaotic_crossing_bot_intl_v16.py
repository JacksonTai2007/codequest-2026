# Chaotic Crossing Clash - tournament bot v2
# Side-agnostic: positions are read ONLY from hero.* views (absolute for
# both colors), verbs get absolute targets, never reads mate.x / mate.y.
# Throttled brain: full evaluation every 4th frame (or instantly when the
# situation is hot) to stay far under the interpreter statement limit;
# between evaluations the cached move target is re-issued cheaply.

MGX = hero.myGoal.x
MGY = hero.myGoal.y
TGX = hero.theirGoal.x
TGY = hero.theirGoal.y
if TGX > MGX:
    ADIR = 1
else:
    ADIR = -1
MIDX = (params.field.minX + params.field.maxX) / 2.0
MOUTH_LO = 25.5
MOUTH_HI = 38.5
AIMX = TGX + ADIR * 1.5


def dst(ax, ay, bx, by):
    return ((ax - bx) * (ax - bx) + (ay - by) * (ay - by)) ** 0.5


def clamp(v, lo, hi):
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def seg_dist(px, py, ax, ay, bx, by, t0):
    # distance from point to the [t0..1] portion of segment a->b
    abx = bx - ax
    aby = by - ay
    l2 = abx * abx + aby * aby
    if l2 < 0.000001:
        return dst(px, py, ax, ay)
    t = ((px - ax) * abx + (py - ay) * aby) / l2
    if t < t0:
        t = t0
    if t > 1:
        t = 1
    return dst(px, py, ax + t * abx, ay + t * aby)


def ball_time(d, power):
    # flight time of a rolled ball over distance d (friction 55)
    v0 = (49.5 * power) ** 0.5
    m = v0 * v0 - 110.0 * d
    if m <= 0:
        return 9.9
    return (v0 - m ** 0.5) / 55.0


def my_half(x):
    if ADIR > 0:
        return x < MIDX
    return x > MIDX


def shot_clear(bx, by, aimy, enemies, keeper):
    d = dst(bx, by, AIMX, aimy)
    if d > 42:
        return False
    t = ball_time(d, 100)
    t0 = 8.0 / d
    if t0 > 1:
        t0 = 1
    i = 0
    while i < 2:
        e = enemies[i]
        if not e.isStunned:
            if seg_dist(e.x, e.y, bx, by, AIMX, aimy, t0) < 4.4:
                return False
        i += 1
    kd = seg_dist(keeper.x, keeper.y, bx, by, AIMX, aimy, 0.0)
    if kd < 3.0 + 4.0 * t + 1.4:
        return False
    return True


def pick_shot(bx, by, enemies, keeper):
    # far corner (from the keeper) first; -999 means no shot
    if keeper.y >= TGY:
        y1 = MOUTH_LO
        y2 = MOUTH_HI
    else:
        y1 = MOUTH_HI
        y2 = MOUTH_LO
    if shot_clear(bx, by, y1, enemies, keeper):
        return y1
    if shot_clear(bx, by, y2, enemies, keeper):
        return y2
    return -999


def pass_lane_clear(bx, by, tx, ty, enemies, keeper):
    d = dst(bx, by, tx, ty)
    if d < 0.001:
        return False
    t0 = 8.0 / d
    if t0 > 1:
        t0 = 1
    i = 0
    while i < 2:
        e = enemies[i]
        margin = 4.4
        if e.isStunned:
            margin = 2.6
        if seg_dist(e.x, e.y, bx, by, tx, ty, t0) < margin:
            return False
        i += 1
    if seg_dist(keeper.x, keeper.y, bx, by, tx, ty, 0.0) < 6.0:
        return False
    return True


def eta(view, tx, ty):
    t = dst(view.x, view.y, tx, ty) / 20.0
    if view.isStunned:
        t += 0.5
    return t


def nearest_threat(me, enemies):
    # a stalker on clash cooldown still counts: he outruns a carrier and
    # strikes the moment his cooldown ends
    best = None
    bestd = 999
    i = 0
    while i < 2:
        e = enemies[i]
        if not e.isStunned:
            d = dst(e.x, e.y, me.x, me.y)
            if (e.clashReady and d < 6.5) or d < 5.2:
                if d < bestd:
                    bestd = d
                    best = e
        i += 1
    return best


def block_line(bx, by):
    # sweeper, league-searched config (no losses vs the whole battery):
    # - threat inside 30: stand in the door they are driving toward
    #   (only a clash stops a carried ball - body position wins)
    # - threat beyond 30: park at depth 9 on the corner our keeper does
    #   NOT cover (keeper tracks ball.y and seals the near corner); on a
    #   launch the urgency path steps onto the exact crossing point
    dd = dst(bx, by, MGX, MGY)
    if dd < 30:
        return (MGX + ADIR * 9, clamp(by, 27.5, 36.5))
    if hero.myKeeper.y >= 32:
        return (MGX + ADIR * 9, 28.0)
    return (MGX + ADIR * 9, 36.0)


def try_escape(mate, me, pn, enemies, tk, mk):
    in_my_half = my_half(me.x)
    # forward pass to the partner
    if not pn.isStunned:
        pd = dst(me.x, me.y, pn.x, pn.y)
        if pd >= 10 and pd <= 40 and dst(pn.x, pn.y, MGX, MGY) > 18:
            ptx = pn.x + ADIR * 2.5
            pty = pn.y
            if pass_lane_clear(me.x, me.y, ptx, pty, enemies, tk):
                power = (pd + 9) / 0.45
                if power > 100:
                    power = 100
                mate.roll(ptx, pty, power)
                return True
    # in OUR half: long clearance up the wall, far from our mouth
    if in_my_half:
        if me.y >= 32:
            fy = 60
        else:
            fy = 4
        mate.roll(me.x + ADIR * 40, fy, 100)
        return True
    # knock ahead past the presser - only in THEIR half
    if not in_my_half:
        kx = me.x + ADIR * 13
        besty = -999
        bestscore = -999
        j = 0
        while j < 3:
            if j == 0:
                ty = me.y
            elif j == 1:
                ty = me.y + 10
            else:
                ty = me.y - 10
            tyy = clamp(ty, 4, 60)
            if kx > 4 and kx < 96:
                score = 999.0
                i = 0
                while i < 2:
                    e = enemies[i]
                    d = seg_dist(e.x, e.y, me.x, me.y, kx, tyy, 0.3)
                    if d < score:
                        score = d
                    i += 1
                if dst(kx, tyy, tk.x, tk.y) < 9:
                    score = -1
                if score > bestscore:
                    bestscore = score
                    besty = tyy
            j += 1
        if besty > -999 and bestscore > 4.5:
            mate.roll(kx, besty, 30)
            return True
    # deep cross toward the far post in THEIR half - away from our goal
    if pn.y < 32:
        fy = 25.5
    else:
        fy = 38.5
    mate.roll(TGX - ADIR * 8, fy, 100)
    return True


def escape_deep(mate, me, pn, enemies, tk, mk):
    # in our defensive zone with the ball: get it OUT, never dribble
    # across our own mouth (a carried ball can score an own goal)
    if not pn.isStunned:
        pd = dst(me.x, me.y, pn.x, pn.y)
        if pd >= 9 and dst(pn.x, pn.y, MGX, MGY) > \
                dst(me.x, me.y, MGX, MGY) - 2:
            ptx = pn.x + ADIR * 2.5
            pty = pn.y
            if pass_lane_clear(me.x, me.y, ptx, pty, enemies, tk):
                power = (pd + 9) / 0.45
                if power > 100:
                    power = 100
                mate.roll(ptx, pty, power)
                return None
    # long clearance down the wall, out of the danger zone
    if me.y >= 32:
        fy = 60
    else:
        fy = 4
    mate.roll(me.x + ADIR * 40, fy, 100)
    return None


def do_carry(mate, me, pn, enemies, tk, mk, flip):
    # hot path: cache every view read once (each property read crosses
    # the API layer and costs several interpreter ops)
    mex = me.x
    mey = me.y
    e0 = enemies[0]
    e1 = enemies[1]
    e0x = e0.x
    e0y = e0.y
    e1x = e1.x
    e1y = e1.y
    e0s = e0.isStunned
    e1s = e1.isStunned
    dx = e0x - mex
    dy = e0y - mey
    d0 = (dx * dx + dy * dy) ** 0.5
    dx = e1x - mex
    dy = e1y - mey
    d1 = (dx * dx + dy * dy) ** 0.5

    # 1. own-goal guard zone: clear it, never dribble near our mouth
    dx = mex - MGX
    dy = mey - MGY
    if dx * dx + dy * dy < 400:
        return escape_deep(mate, me, pn, enemies, tk, mk)

    # 2. walk-in: carry the ball over the line if nobody can stop us
    #    (the keeper cannot take a carried ball - only a clash stops it)
    wy = clamp(mey, 27, 37)
    carry_d = dst(mex, mey, TGX, wy)
    if carry_d < 34:
        need = (carry_d - 2.5) / 15.0
        if need < 0:
            need = 0
        t = (d0 - 4.0) / 20.0
        if t < 0:
            t = 0
        if e0s:
            t += 0.5
        elif not e0.clashReady:
            t += 0.8
        safe = t >= need + 0.12
        if safe:
            t = (d1 - 4.0) / 20.0
            if t < 0:
                t = 0
            if e1s:
                t += 0.5
            elif not e1.clashReady:
                t += 0.8
            if t < need + 0.12:
                safe = False
        if safe:
            return (TGX, wy)

    # 3. clean far-corner shot (carry_d ~ distance to goal: beyond max
    #    range the evaluation is waste; inside it, every 2nd frame is
    #    plenty - the keeper moves 0.16 units per frame)
    if carry_d < 45 and flip:
        aimy = pick_shot(mex, mey, enemies, tk)
        if aimy > -999:
            mate.roll(AIMX, aimy, 100)
            return None

    in_their_half = not my_half(mex)
    if in_their_half and not pn.isStunned:
        pnx = pn.x
        pny = pn.y
        # 3a. deliberate cross to the far-post runner: beats ball-side
        #     sweepers whose y is clamped short of the posts
        if (pny - 32) * (mey - 32) < 0 and \
                dst(pnx, pny, TGX, TGY) < 24:
            if pny > 32:
                cfy = 38.5
            else:
                cfy = 25.5
            ctx = TGX - ADIR * 8
            if pass_lane_clear(mex, mey, ctx, cfy, enemies, tk):
                mate.roll(ctx, cfy, 100)
                return None
        # 3c. open forward pass: +1 fan support and the ball travels
        #     much faster than a carrier dribbles
        if dst(pnx, pny, TGX, TGY) < carry_d - 6:
            pd = dst(mex, mey, pnx, pny)
            if pd >= 12 and pd <= 35:
                ptx = pnx + ADIR * 2.5
                if pass_lane_clear(mex, mey, ptx, pny, enemies, tk):
                    power = (pd + 9) / 0.45
                    if power > 100:
                        power = 100
                    mate.roll(ptx, pny, power)
                    return None

    # 3b. endgame: tied or behind late in the second half - force shots
    #     (a shot on target scores fan support even when caught, and fan
    #     support is the tiebreaker)
    if in_their_half and carry_d < 44 and hero.round == 1 and \
            hero.roundTime > 46 and hero.score <= hero.opponentScore:
        if tk.y >= TGY:
            mate.roll(AIMX, MOUTH_LO, 100)
        else:
            mate.roll(AIMX, MOUTH_HI, 100)
        return None

    # 4. under threat: release before the stalker strikes. Inside 4.6 we
    #    release even while immune - his clash lands the frame it ends.
    threat = None
    td = 999
    if not e0s and d0 < td and ((d0 < 6.5 and e0.clashReady) or d0 < 5.2):
        threat = e0
        td = d0
    if not e1s and d1 < td and ((d1 < 6.5 and e1.clashReady) or d1 < 5.2):
        threat = e1
        td = d1
    if threat:
        if td < 4.6 or not me.isImmune:
            if try_escape(mate, me, pn, enemies, tk, mk):
                return None

    # 5. dribble drive along a mouth edge (drags the keeper wide, keeps
    #    the walk-in threat alive)
    if mey <= 32:
        ey = 25.5
    else:
        ey = 38.5
    bex_y = -999
    fx = mex + ADIR * 11
    if not e0s and seg_dist(e0x, e0y, mex, mey, fx, mey, 0.0) < 5.5:
        bex_y = e0y
    if not e1s and seg_dist(e1x, e1y, mex, mey, fx, mey, 0.0) < 5.5:
        bex_y = e1y
    if bex_y > -999:
        if bex_y >= mey:
            dy = -9
        else:
            dy = 9
        return (mex + ADIR * 7, clamp(mey + dy, 4, 60))
    return (TGX - ADIR * 13, ey)


def do_support(me, pn):
    # partner carries: give him targets
    if my_half(pn.x) and dst(pn.x, pn.y, TGX, TGY) > 55:
        # deep build-up: forward outlet at a passing angle
        if pn.y > 32:
            oy = pn.y - 16
        else:
            oy = pn.y + 16
        return (pn.x + ADIR * 18, clamp(oy, 8, 56))
    # attacking phase: far-post runner for crosses and rebounds
    if pn.y < 32:
        fy = 38.5
    else:
        fy = 25.5
    fx = TGX - ADIR * 11
    if dst(fx, fy, pn.x, pn.y) < 10:
        fy = 32
    return (fx, fy)


def press_carrier(mate, me, carrier):
    d = dst(me.x, me.y, carrier.x, carrier.y)
    near_mouth = dst(me.x, me.y, MGX, MGY) < 12
    goal_side = dst(carrier.x, carrier.y, MGX, MGY) < \
        dst(me.x, me.y, MGX, MGY) - 1
    if near_mouth and goal_side:
        # clashing while facing our own mouth can carry the ball in:
        # get goal-side first so the clash faces outward
        return (MGX + ADIR * 4, clamp(carrier.y, MOUTH_LO, MOUTH_HI))
    if d <= 3.7 and not carrier.isImmune and \
            mate.clashReady and not me.isStunned:
        mate.clash()
        return None
    # close in with a slight goal-side bias
    bx = MGX - carrier.x
    by = MGY - carrier.y
    bd = (bx * bx + by * by) ** 0.5
    if bd > 0.001:
        return (carrier.x + bx / bd * 1.2, carrier.y + by / bd * 1.2)
    return (carrier.x, carrier.y)


def do_defend(mate, me, pn, enemies, ball):
    carrier = ball.owner
    my_d = dst(me.x, me.y, carrier.x, carrier.y)
    pn_d = dst(pn.x, pn.y, carrier.x, carrier.y)
    if pn.isStunned:
        presser = True
    elif me.isStunned:
        presser = False
    elif my_d - pn_d < 0.6 and pn_d - my_d < 0.6:
        presser = (mate.mateId == 0)
    else:
        presser = my_d < pn_d
    # presser hunts the carrier; the sweeper NEVER joins the press -
    # pulling the last line off the mouth is how walk-ins get in
    if presser:
        return press_carrier(mate, me, carrier)
    return block_line(carrier.x, carrier.y)


def do_keeper_held(mate, me, pn, enemies, ball, tk, mk):
    if tk.hasBall:
        # their clearance goes to their nearest non-stunned mate:
        # contest that receiver, other man covers our goal line
        rec = None
        recd = 9999
        i = 0
        while i < 2:
            e = enemies[i]
            if not e.isStunned:
                d = dst(e.x, e.y, tk.x, tk.y)
                if d < recd:
                    recd = d
                    rec = e
            i += 1
        if not rec:
            rec = enemies[0]
        my_d = dst(me.x, me.y, rec.x, rec.y)
        pn_d = dst(pn.x, pn.y, rec.x, rec.y)
        if my_d < pn_d or (my_d == pn_d and mate.mateId == 0):
            return (rec.x, rec.y)
        # the shot will come from the RECEIVER, not the keeper:
        # pre-position on the receiver's shot cone during the hold
        return block_line(rec.x, rec.y)
    # our keeper clears to OUR nearest mate: the likely receiver drifts
    # upfield, the other sprints deep as the next outlet
    my_d = dst(me.x, me.y, mk.x, mk.y)
    pn_d = dst(pn.x, pn.y, mk.x, mk.y)
    if my_d < pn_d or (my_d == pn_d and mate.mateId == 0):
        return (me.x + ADIR * 6, clamp(me.y, 14, 50))
    if me.y >= 32:
        oy = 44
    else:
        oy = 20
    return (MIDX + ADIR * 18, oy)


def path_y_at_x(bx, by, sx, sy, px):
    dx = sx - bx
    if dx < 0.001 and dx > -0.001:
        return sy
    t = clamp((px - bx) / dx, 0.0, 1.0)
    return by + (sy - by) * t


def chase_free(mate, me, pn, enemies, ball, sx, sy, sp):
    my_t = eta(me, sx, sy)
    pn_t = eta(pn, sx, sy)
    their_t = 999
    i = 0
    while i < 2:
        t = eta(enemies[i], sx, sy)
        if t < their_t:
            their_t = t
        i += 1
    if my_t < pn_t or (my_t == pn_t and mate.mateId == 0):
        if sp > 1:
            # meet the roll on its path if we can get there early
            mid_x = (ball.x + sx) / 2.0
            mid_y = (ball.y + sy) / 2.0
            t_ball = ball_time(dst(ball.x, ball.y, mid_x, mid_y),
                               sp * sp / 49.5)
            if eta(me, mid_x, mid_y) + 0.1 < t_ball:
                return (mid_x, mid_y)
            return (sx, sy)
        return (ball.x, ball.y)
    deep_theirs = dst(sx, sy, TGX, TGY) < 40
    we_win = my_t < their_t - 0.05 or pn_t < their_t - 0.05
    if we_win and deep_theirs:
        # secure enough upfield: far-post support spot
        if sy < 32:
            fy = 38.5
        else:
            fy = 25.5
        fx = TGX - ADIR * 11
        if dst(fx, fy, sx, sy) < 10:
            fy = 32
        return (fx, fy)
    # contested ball: last man covers the shot cone
    return block_line(sx, sy)


def do_free_ball(mate, me, pn, enemies, ball):
    sp = (ball.vx * ball.vx + ball.vy * ball.vy) ** 0.5
    if sp > 1:
        sd = sp * sp / 110.0
        sx = ball.x + ball.vx / sp * sd
        sy = ball.y + ball.vy / sp * sd
        # a roll heading for our mouth is a shot: get a body on its line
        toward_goal = (MGX - ball.x) * ball.vx + (MGY - ball.y) * ball.vy
        if toward_goal > 0 and \
                seg_dist(MGX, MGY, ball.x, ball.y, sx, sy, 0.0) < 11:
            px = MGX + ADIR * 7
            py = path_y_at_x(ball.x, ball.y, sx, sy, px)
            return (px, clamp(py, MOUTH_LO - 2, MOUTH_HI + 2))
        return chase_free(mate, me, pn, enemies, ball, sx, sy, sp)
    return chase_free(mate, me, pn, enemies, ball, ball.x, ball.y, 0.0)


def brain(mate, me, pn, enemies, ball, tk, mk, flip):
    # returns a move target (tx, ty), or None when a verb was issued
    if me.hasBall:
        return do_carry(mate, me, pn, enemies, tk, mk, flip)
    if ball.heldByKeeper:
        return do_keeper_held(mate, me, pn, enemies, ball, tk, mk)
    if ball.owner:
        if ball.owner.color == me.color:
            return do_support(me, pn)
        return do_defend(mate, me, pn, enemies, ball)
    return do_free_ball(mate, me, pn, enemies, ball)


def onSpawnMate(mate):
    myid = mate.mateId
    cx = 0.0
    cy = 0.0
    have = False
    cool = 0
    flip = False
    # views are LIVE proxies into the referee state - fetch them once;
    # refetching every frame rebuilds arrays inside the interpreter and
    # burns the 3M-op statement budget
    mates = hero.myMates
    me = mates[myid]
    pn = mates[1 - myid]
    enemies = hero.theirMates
    ball = hero.ball
    tk = hero.theirKeeper
    mk = hero.myKeeper
    while True:
        if not hero.gameActive:
            have = False
            mate.moveTo(me.x, me.y)
            continue
        # hot situations get a fresh decision every frame; a carrier is
        # hot inside the attack zone (shot/walk-in timing) or with an
        # enemy close (escape timing) - open-field ferrying at full rate
        # just burns the interpreter budget
        urgent = False
        if me.hasBall:
            dx = TGX - me.x
            dy = TGY - me.y
            if dx * dx + dy * dy < 2116:
                urgent = True
            else:
                dx = enemies[0].x - me.x
                dy = enemies[0].y - me.y
                if dx * dx + dy * dy < 100:
                    urgent = True
                else:
                    dx = enemies[1].x - me.x
                    dy = enemies[1].y - me.y
                    if dx * dx + dy * dy < 100:
                        urgent = True
        if not urgent:
            own = ball.owner
            if own:
                if own.color != me.color:
                    # only the actual presser (closer of our two mates)
                    # needs frame-rate decisions; the covering mate at
                    # full rate doubles the statement burn for nothing
                    dx = own.x - me.x
                    dy = own.y - me.y
                    d2 = dx * dx + dy * dy
                    if d2 < 64:
                        dx = own.x - pn.x
                        dy = own.y - pn.y
                        if d2 <= dx * dx + dy * dy:
                            urgent = True
            elif not ball.heldByKeeper:
                dx = ball.x - me.x
                dy = ball.y - me.y
                if dx * dx + dy * dy < 400:
                    urgent = True
                elif (MGX - ball.x) * ball.vx + \
                        (MGY - ball.y) * ball.vy > 0 and \
                        ball.vx * ball.vx + ball.vy * ball.vy > 400:
                    # a fast roll heading our way: track it every frame
                    urgent = True
        if have and cool > 0 and not urgent:
            cool -= 1
            mate.moveTo(cx, cy)
            continue
        flip = not flip
        res = brain(mate, me, pn, enemies, ball, tk, mk, flip)
        if res:
            cx = res[0]
            cy = res[1]
            have = True
            if me.hasBall:
                cool = 1
            else:
                cool = 3
            mate.moveTo(cx, cy)
        else:
            have = False


hero.on("spawn-mate", onSpawnMate)


# ---------------- coach ----------------

# live view proxies, fetched once (see the note in onSpawnMate)
mm = hero.myMates
tm = hero.theirMates
cball = hero.ball

while True:
    acted = False

    # free a stunned mate when the play is near him or in our half
    ci = 0
    while ci < 2 and not acted:
        cm = mm[ci]
        if cm.isStunned and hero.abilityReady("whistle"):
            if dst(cball.x, cball.y, cm.x, cm.y) < 30 or my_half(cball.x):
                hero.whistle(cm)
                acted = True
        ci += 1

    ccarrier = cball.owner
    if not acted and ccarrier:
        if ccarrier.color == hero.color:
            cgd = dst(ccarrier.x, ccarrier.y, TGX, TGY)
            cde = 999
            cen = None
            ci = 0
            while ci < 2:
                ce = tm[ci]
                if not ce.isStunned:
                    cd = dst(ce.x, ce.y, ccarrier.x, ccarrier.y)
                    if cd < cde:
                        cde = cd
                        cen = ce
                ci += 1
            if cde < 12 and cen and hero.abilityReady("press"):
                hero.press(cen)
                acted = True
            elif cgd < 28 and hero.abilityReady("distract"):
                hero.distract()
                acted = True
            elif cde > 9 and cgd < 50 and hero.abilityReady("inspire"):
                hero.inspire(ccarrier)
                acted = True
        else:
            if (my_half(cball.x) or
                    dst(ccarrier.x, ccarrier.y, MGX, MGY) < 50) and \
                    hero.abilityReady("press"):
                hero.press(ccarrier)
                acted = True
    elif not acted and not cball.heldByKeeper:
        # free-ball race: assume the enemy coach inspires HIS chaser
        # (x1.5 speed), so inspire ours whenever an inspired enemy could
        # snatch a ball we would otherwise reach first
        cmy_t = 999
        cbest = None
        ci = 0
        while ci < 2:
            ct = eta(mm[ci], cball.x, cball.y)
            if ct < cmy_t:
                cmy_t = ct
                cbest = mm[ci]
            ci += 1
        cth_t = 999
        ci = 0
        while ci < 2:
            ct = eta(tm[ci], cball.x, cball.y)
            if ct < cth_t:
                cth_t = ct
            ci += 1
        if cbest and hero.abilityReady("inspire"):
            their_boosted = cth_t / 1.5
            our_boosted = cmy_t / 1.5
            if their_boosted < cmy_t + 0.2 and \
                    our_boosted < their_boosted + 0.05:
                hero.inspire(cbest)
                acted = True

    hero.wait(0.1)
