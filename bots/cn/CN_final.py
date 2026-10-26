def xx(x):
    if hero.color=="blue":
        return 100-x
    else:
        return x

def xo(x):
    if hero.color=="blue":
        return -x
    else:
        return x

def cip(x, y, vx, vy, a, b, v):
    v0 = (vx**2+vy**2)**0.5
    #if v0 < 0.0000001:
        #dist = ((x-a)**2+(y-b)**2)**0.5
        #return 'dist / v', (x, y)
    t_stop = v0 / 55.0
    x_final = x + (vx * v0) / 110.0
    y_final = y + (vy * v0) / 110.0
    
    def gbp(t):
        if t >= t_stop:
            return x_final, y_final
        else:
            factor = t - 27.5 * (t ** 2) / v0
            return x + vx * factor, y + vy * factor
    
    def dd(t):
        bx, by = gbp(t)
        dpcr = v * t + 4.0
        dtb = ((bx-a)**2+(by-b)**2)**0.5
        return dtb-dpcr
    
    if dd(t_stop)<=0:
        low, high = 0.0, t_stop
        for _ in range(2):
            mid = (low + high) / 2.0
            if dd(mid) <= 0:
                high = mid
            else:
                low = mid
        #t_min = high
        target_x, target_y = gbp(high)
        return 't_min', (target_x, target_y)
    else:
        #dtf = ((x_final - a)**2+(y_final - b)**2)**0.5
        #t_min = dtf / v
        return 't_min', (x_final, y_final)

def mn(a,b):
    if a<b:
        return a
    else:
        return b

def cross(mate):
    enemymates = hero.theirMates
    enemykeeper = hero.theirKeeper
    matepos = Vector(mate.x, mate.y)
    enemy1pos = Vector(xx(enemymates[0].x), enemymates[0].y)
    enemy2pos = Vector(xx(enemymates[1].x), enemymates[1].y)
    #enemykeeperpos = Vector(xx(enemykeeper.x), enemykeeper.y)
    d1 = enemy1pos.subtract(matepos)
    d2 = enemy2pos.subtract(matepos)
    if d1.magnitude()>50:
        if mate.y>32:
            d1 = Vector(-50,-1)
        else:
            d1 = Vector(-50,1)
    if d2.magnitude()>50:
        if mate.y>32:
            d2 = Vector(-50,-1)
        else:
            d2 = Vector(-50,1)
    
    #dk = enemykeeperpos.subtract(matepos)
    theta = Math.PI/180*30
    h1 = d1.heading()
    h2 = d2.heading()
    #console.log(hero.time, d1.x,d1.y,d2.x,d2.y,h1*180/Math.PI, h2*180/Math.PI)
    #hk = dk.heading()
    if mate.distanceTo(enemykeeper)>40:
        if (h1>theta or h1<-theta) and (h2>theta or h2<-theta):
            #console.log(hero.time, "straight")
            mate.roll(xx(96), mate.y, (abs(mate.x-83)/0.0045)**0.5)
        elif h1>Math.PI/2 or h1<-Math.PI/2:
            #console.log(hero.time, "cross (type1)")
            if (h2>0 and mate.y<55) or mate.y>9:
                ans = d2.rotate(2*Math.PI-theta)
                mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
            else:
                ans = d2.rotate(theta)
                mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
        elif h2>Math.PI/2 or h2<-Math.PI/2:
            #console.log(hero.time, "cross (type2)")
            if h1>0:
                ans = d1.rotate(2*Math.PI-theta)
                mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
            else:
                ans = d1.rotate(theta)
                mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
        elif h2 - h1 > 2 * theta or h1 - h2 > 2 * theta:
            ans = d1.add(d2)
            #console.log(hero.time, "middle")#, h1*180/Math.PI, h2*180/Math.PI)
            mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
        else:
            #console.log(hero.time, "side")
            if h1 > 0:
                if h2 > 0:
                    if h1 > h2:
                        ans = d2.rotate(2*Math.PI-theta)
                        mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
                    else:
                        ans = d1.rotate(2*Math.PI-theta)
                        mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
                else:
                    if h1 > -h2:
                        ans = d2.rotate(2*Math.PI-theta)
                        mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
                    else:
                        ans = d1.rotate(theta)
                        mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
            else:
                if h2 > 0:
                    if -h1 > h2:
                        ans = d2.rotate(theta)
                        #console.log(hero.time, ans.x, ans.y)
                        mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
                    else:
                        ans = d1.rotate(2*Math.PI-theta)
                        mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
                else:
                    if -h1 > -h2:
                        ans = d2.rotate(theta)
                        #console.log(hero.time, ans.x, ans.y)
                        mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
                    else:
                        ans = d1.rotate(theta)
                        console.log(hero.time, ans.x, ans.y)
                        mate.roll(xx(mate.x+ans.x), mate.y+ans.y, 100)
    else:
        cross2(mate)

def xc(x1, x2):
    if hero.color=="blue":
        return x1>=x2
    else:
        return x1<x2

def cross2(mate):
    enemymates = hero.theirMates
    #enemykeeper = hero.theirKeeper
    b = True
    for m in enemymates:
        if mate.x<xx(m.x) and '''xx(m.x)<mate.x+3)''' and -2<mate.y-m.y and mate.y-m.y<2:
            b = False
    if b:
        if mate.y>=32:
            mate.roll(xx(88),17,100)
        else:
            mate.roll(xx(88),47,100)
    else:
        #console.log("cross2", hero.time)
        if mate.y>=32:
            mate.roll(mate.x, mate.y-40, 100)
        else:
            mate.roll(mate.x, mate.y+40, 100)

def abs(a):
    if a<0:
        return -a
    else:
        return a

def h(a,b,c,d):
    return a*d-b*c

def s(a,b,c,d,e,f):
    return abs(a*(d-f)+c*(f-b)+e*(b-d))
    #return h(a,b,c,d)+h(c,d,e,f)+h(e,f,a,b)

def mateA(mate):
    immune = False
    immune_time = -10
    k = False
    kt = -10
    while True:
        ball = hero.ball
        enemymates = hero.theirMates
        carrier = ball.owner
        keeper = hero.myKeeper
        p = hero.myMates[0]
        enemykeeper = hero.theirKeeper
        #console.log(mate.x, mate.y, p.x, p.y, enemymates[0].x, enemymates[0].y, ball.x, ball.y, hero.time)
        if not immune and mate.immune:
            immune = True
            immune_time = hero.time
        elif immune and not mate.immune:
            immune = False
            immune_time = -10
        
        if keeper.hasBall and not k:
            k = True
            kt = hero.time
        elif not keeper.hasBall and k:
            k = False
        
        #if hero.time>60:
            #console.log(s(xx(enemymates[1].x),enemymates[1].y,mate.x,mate.y,xx(4),32),hero.time)
        
        if keeper.hasBall or hero.time<kt+2:
            mate.moveTo(xx(xx(p.x)+40),p.y)
        elif enemykeeper.hasBall:
            mate.moveTo(xx(4),32)
        elif carrier and carrier.color!=hero.color and mate.clashReady and not carrier.isImmune and mate.distanceTo(carrier)<=4:
            mate.clash()
        elif mate.hasBall and mate.x>60:
            if xx(enemymates[0].x)>=94 or xx(enemymates[1].x)>=94:
                #console.log("zero")
                if mate.y>=40:
                    mate.moveTo(xx(96),39)
                elif mate.y<=24:
                    mate.moveTo(xx(96),25)
                else:
                    mate.moveTo(xx(96),mate.y)
            elif s(xx(enemymates[0].x),enemymates[0].y,mate.x,mate.y,xx(4),32)<90 and mate.x<85 and xx(enemymates[1].x)<40:
                mate.roll(xx(mate.x),32,100)
                #console.log("one")
            elif s(xx(enemymates[1].x),enemymates[1].y,mate.x,mate.y,xx(4),32)<90 and mate.x<85 and xx(enemymates[0].x)<40:
                mate.roll(xx(mate.x),32,100)
                #console.log("two")
            else:
                #console.log("three")
                AA = s(mate.x,mate.y,xx(enemykeeper.x),enemykeeper.y,96,25)
                BB = s(mate.x,mate.y,xx(enemykeeper.x),enemykeeper.y,96,39)
                da = ((mate.x-96)**2+(mate.y-25)**2)**0.5
                db = ((mate.x-96)**2+(mate.y-39)**2)**0.5
                ha = AA/da
                hb = BB/db
                #console.log(hero.time, AA, BB, mate.x,mate.y,xx(enemykeeper.x),enemykeeper.y)
                if ha<3.5 and hb<3.5 and mate.x<80:
                    mate.roll(mate.x, 32, abs(32-mate.y)/0.45)
                elif ha>hb:
                    #console.log(hero.time, "flag")
                    mate.roll(xx(96),25.2,100)
                else:
                    mate.roll(xx(96),38.8,100)
                '''
                if enemykeeper.y<32:
                    if mate.y<24:
                        mate.roll(xx(96),25,100)
                    else:
                        mate.roll(xx(96),39,100)
                else:
                    if mate.y>40:
                        mate.roll(xx(96),39,100)
                    else:
                        mate.roll(xx(96),25,100)
                '''
        elif mate.hasBall and mate.isImmune and hero.time<immune_time+0.48:
            #mate.roll(xx(96), 32, 13)
            mate.moveTo(xx(96), 32)
        #elif mate.hasBall and (xx(enemymates[0].x)<xx(mate.x-9) and xx(enemymates[1].x)<xx(mate.x-9)):
        #    mate.moveTo(xx(96),32)
        #elif mate.hasBall and (xx(enemymates[0].x)>xx(mate.x) and xx(enemymates[1].x)>xx(mate.x)):
        #    cross(mate)
            #mate.passTo()
        elif mate.hasBall:
            cross(mate)
        elif carrier and carrier.color==hero.color:
            mate.moveTo(xx(carrier.x+10),carrier.y)
        elif mate.distanceTo(ball)>p.distanceTo(ball) and not carrier and p.distanceTo(ball)< 10 and (xx(ball.x)>23 or (ball.distanceTo(enemymates[0])/ball.distanceTo(p)<0.5 and ball.distanceTo(enemymates[1])/ball.distanceTo(p)<0.5)) and (p.y>48 or p.y<16):
            mate.moveTo(xx(xx(p.x)+40), p.y)
        else:
            if carrier and carrier.color!=hero.color:
                if not carrier.immune:
                    mate.moveTo(xx(xx(carrier.x)-2), carrier.y)
                    continue
                ep = enemymates[0]
                if ep==carrier:
                    ep = enemymates[1]
                #if False:#xc(ep.x-carrier.x-5):
                #v = Vector(xx(carrier.x)-xx(ep.x),carrier.y-ep.y).normalize().multiply(-10)
                #mate.moveTo(xx(xx(carrier.x)+v.x), carrier.y+v.y)
                #else:
                    #console.log(hero.time)
                mate.moveTo(xx(xx(ball.x)-5), ball.y)
            elif enemymates[0].distanceTo(ball)<10 and mate.distanceTo(ball)>enemymates[0].distanceTo(ball)+5:
                carrier = enemymates[0]
                ep = enemymates[1]
                #if False:#xxc(ep.x-carrier.x):
                    #v = Vector(xx(carrier.x)-xx(ep.x),carrier.y-ep.y).normalize().multiply(-10)
                    #mate.moveTo(xx(xx(carrier.x)+v.x), carrier.y+v.y)
                #else:
                mate.moveTo(xx(xx(carrier.x)-6), carrier.y)
            elif enemymates[1].distanceTo(ball)<10 and mate.distanceTo(ball)>enemymates[1].distanceTo(ball)+5:
                carrier = enemymates[1]
                ep = enemymates[0]
                #if False:#xxc(ep.x-carrier.x):
                    #v = Vector(xx(carrier.x)-xx(ep.x),carrier.y-ep.y).normalize().multiply(-10)
                    #mate.moveTo(xx(xx(carrier.x)+v.x), carrier.y+v.y)
                #else:
                mate.moveTo(xx(xx(carrier.x)-6), carrier.y)
            elif ball.vx*ball.vx+ball.vy*ball.vy>0:
                tm, tpos = cip(xx(ball.x), ball.y, xo(ball.vx), ball.vy, mate.x, mate.y, 20)
                #console.log(hero.time, ball.x, ball.y, ball.vx, ball.vy, mate.x, mate.y, tpos[0], tpos[1])
                mate.moveTo(xx(tpos[0]),tpos[1])
            else:
                mate.chaseBall()

def f(l, k):
    if xx(l) > 20 or k > 50 or k < 14:
        return (k*2+32*3)/5
    if k>=40:
        return 40
    elif k<=24:
        return 24
    else:
        return k

def mateB(mate):
    k = False
    kt = -10
    while True:
        ball = hero.ball
        enemymates = hero.theirMates
        carrier = ball.owner
        keeper = hero.myKeeper
        enemykeeper = hero.theirKeeper
        
        if keeper.hasBall and not k:
            k = True
            kt = hero.time
            #console.log(hero.time, 0)
        elif not keeper.hasBall and k:
            k = False
            #console.log(hero.time, -1)
        
        if keeper.hasBall:# or hero.time<kt+2:
            if hero.time<kt+0.5:
                mate.moveTo(xx(20),32)
            else:
                mate.clash()
            #mate.moveTo(xx(20),32)
        elif enemykeeper.hasBall:
            mate.moveTo(xx(4), 32)
        elif carrier and carrier.color!=hero.color and mate.clashReady and not carrier.isImmune and mate.distanceTo(carrier)<=4:
            mate.clash()
        elif mate.hasBall and mate.x>60:
            mate.roll(xx(96),25,100)
        #elif mate.hasBall and mate.isImmune:
            #mate.roll(xx(96), 32, 13)
            #mate.moveTo(xx(96),32)
        #elif mate.hasBall and (xx(enemymates[0].x)<xx(mate.x-9) and xx(enemymates[1].x)<xx(mate.x-9)):
        #    mate.moveTo(xx(96),32)
        elif mate.hasBall:
            if mate.y<10 and (enemymates[0].y<10 or enemymates[1].y<10):
                mate.roll(keeper.x,keeper.y,100)
            elif mate.y>54 and (enemymates[0].y>54 or enemymates[1].y>54):
                mate.roll(keeper.x,keeper.y,100)
            else:
                cross(mate)
            #mate.passTo()
        #elif carrier and carrier.color==hero.color:
        #    mate.moveTo(xx(carrier.x-13),carrier.y)
        elif xx(enemymates[0].x)<mate.x:# and enemymates[0].hasBall:
            mate.moveTo(xx((xx(enemymates[0].x)+4)//2),(enemymates[0].y+32)//2)
        elif xx(enemymates[1].x)<mate.x:# and enemymates[1].hasBall:
            mate.moveTo(xx((xx(enemymates[1].x)+4)//2),(enemymates[1].y+32)//2)
        elif not carrier and not enemykeeper.hasBall:# and mate.distanceTo(ball)>mate.distanceTo(keeper):
            if ball.vx*ball.vx+ball.vy*ball.vy>0:
                tm, tpos = cip(xx(ball.x), ball.y, xo(ball.vx), ball.vy, mate.x, mate.y, 20)
                #console.log(ball.x, ball.y, mate.x, mate.y, enemymates[0].x, enemymates[0].y, enemymates[1].x, enemymates[1].y, hero.time)
                if Vector(mate.x,mate.y).distance(Vector(xx(ball.x),ball.y))<Vector(xx(enemymates[0].x),enemymates[0].y).distance(Vector(xx(ball.x),ball.y)) and Vector(mate.x,mate.y).distance(Vector(xx(ball.x),ball.y))<Vector(xx(enemymates[1].x),enemymates[1].y).distance(Vector(xx(ball.x),ball.y)):
                    if tpos[0]<5:
                        if ball.y>40:
                            mate.moveTo(xx(7), 39)
                        elif ball.y<24:
                            mate.moveTo(xx(7), 25)
                        else:
                            mate.moveTo(xx((xx(ball.x)*2+4*3)/5),f(ball.x, ball.y))
                            #mate.moveTo(xx((xx(ball.x)+4)//2),f(ball.x, ball.y))
                    else:
                        while (not ball.owner) and (not mate.hasBall) and (not keeper.hasBall) and (not (mate.x-tpos[0])**2+(mate.y-tpos[1])**2<10):
                            mate.moveTo(xx(tpos[0]),tpos[1])
                            ball = hero.ball
                else:
                    mate.moveTo(xx((xx(ball.x)*2+4*3)/5),f(ball.x, ball.y))
                    #mate.moveTo(xx((xx(ball.x)+4)//2),f(ball.x, ball.y))
            else:
                if ball.distanceTo(keeper)>40:
                    mate.chaseBall()
                else:
                    mate.moveTo(xx((xx(ball.x)*2+4*3)/5),f(ball.x, ball.y))
                    #mate.moveTo(xx((xx(ball.x)+4)//2),f(ball.x, ball.y))
        else:
            if carrier.immune:
                mate.moveTo(xx((xx(ball.x)*2+4*3)/5),f(ball.x, ball.y))
                #mate.moveTo(xx((xx(ball.x)+4)//2),f(ball.x, ball.y))
            else:
                mate.moveTo(carrier.x,carrier.y)

def onSpawnMate(mate):
    if mate.mateId==1:
        mateA(mate)
    else:
        mateB(mate)
hero.on("spawn-mate", onSpawnMate)

while True:
    mate0 = hero.myMates[0]
    mate1 = hero.myMates[1]
    enemymate0 = hero.theirMates[0]
    enemymate1 = hero.theirMates[1]
    keeper = hero.myKeeper
    #if hero.time>60:
        #console.log((hero.ball.vx**2+hero.ball.vy**2)**0.5,hero.time)
    #if hero.time>60:
    #    console.log(hero.time, mate0.x, mate0.y, mate1.x, mate1.y, enemymate0.x,enemymate0.y,enemymate1.x,enemymate1.y)
    if hero.abilityReady("inspire"):
        if xx(mate0.x)>xx(mate1.x):
            hero.inspire(mate0)
        else:
            hero.inspire(mate1)
    if hero.abilityReady("whistle"):
        #if mate0.isStunned and not keeper.hasBall:
            #hero.whistle(mate0)
        if mate1.isStunned and not keeper.hasBall:
            hero.whistle(mate1)
    if hero.abilityReady("press"):
        if enemymate0.x>enemymate1.x:
            hero.press(enemymate0)
        else:
            hero.press(enemymate1)
    #if hero.abilityReady("distract"):
    #    hero.distract()
    hero.wait(0.01)
 