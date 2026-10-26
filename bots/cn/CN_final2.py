# CQ2026 dual-role engine v5 (f-lineage final)
# strikerRole swaps by 2x ball-distance rule; keeperFeedLock gates the feed cycle
# aim tuned 38/26, clearance lanes 62/2
hero.on("spawn-mate", onMateBrain)
def onMateBrain(mate):
    strikerRole=0
    keeperFeedLock=0
    while True:
        if strikerRole == 1:
            if hero.myMates[1].distanceTo(hero.ball) >= hero.myMates[0].distanceTo(hero.ball)*2:
                strikerRole=0
        else:
            if hero.myMates[0].distanceTo(hero.ball) >= hero.myMates[1].distanceTo(hero.ball)*2:
                strikerRole=1
        if strikerRole == 1:
            if hero.abilityReady("inspire"):
                if hero.myMates[1].distanceTo(hero.ball) <= hero.myMates[0].distanceTo(hero.ball):
                    hero.inspire(hero.myMates[1])
                else:
                    hero.inspire(hero.myMates[0])
        else:
            if hero.abilityReady("inspire"):
                if hero.myMates[0].distanceTo(hero.ball) <= hero.myMates[1].distanceTo(hero.ball):
                    hero.inspire(hero.myMates[0])
                else:
                    hero.inspire(hero.myMates[1])
        if min(hero.myMates[0].distanceTo(hero.myKeeper),hero.myMates[0].distanceTo(hero.myKeeper))*2<max(hero.myMates[0].distanceTo(hero.theirKeeper),hero.myMates[0].distanceTo(hero.theirKeeper)):
            if strikerRole == 1:
                if hero.myMates[1].isStunned and hero.abilityReady("whistle"):
                    hero.whistle(hero.myMates[1])
                elif hero.myMates[0].isStunned and hero.abilityReady("whistle"):
                    hero.whistle(hero.myMates[0])
            else:
                if hero.myMates[0].isStunned and hero.abilityReady("whistle"):
                    hero.whistle(hero.myMates[0])
                elif hero.myMates[1].isStunned and hero.abilityReady("whistle"):
                    hero.whistle(hero.myMates[1])
        if hero.abilityReady("press"):
            if hero.theirMates[0].distanceTo(hero.ball)<hero.theirMates[1].distanceTo(hero.ball):
                hero.press(hero.theirMates[0])
            else:
                hero.press(hero.theirMates[1])
        carrier=hero.ball.owner
        if mate.mateId:
            if mate.hasBall:
                if mate.distanceTo(hero.myKeeper)*2 <= mate.distanceTo(hero.theirKeeper)  and mate.distanceTo(hero.myKeeper) <= hero.theirMates[0].distanceTo(hero.myKeeper) and mate.distanceTo(hero.myKeeper) <= hero.theirMates[1].distanceTo(hero.myKeeper):
                    mate.roll(hero.myKeeper.x, hero.myKeeper.y, 100)
                elif min(mate.distanceTo(hero.theirMates[0]),mate.distanceTo(hero.theirMates[1]))>params.clashRange+1:
                    if hero.abilityReady("distract"):
                        hero.distract()
                    if mate.y >= 32:
                        mate.moveTo(hero.theirGoal.x, 39)
                    else:
                        mate.moveTo(hero.theirGoal.x, 25)
                elif abs(hero.ball.x-hero.theirKeeper.x) <= 8 and (64-hero.ball.y <= 8 or hero.ball.y <= 8):
                    if mate.y >= 32:
                        mate.roll(hero.theirGoal.x, 38, 100)
                    else:
                        mate.roll(hero.theirGoal.x, 26, 100)
                elif mate.distanceTo(hero.theirGoal) <= 15:
                    if hero.abilityReady("distract"):
                        hero.distract()
                    if mate.y >= 32:
                        mate.roll(hero.theirGoal.x, 38, 100)
                    else:
                        mate.roll(hero.theirGoal.x, 26, 100)
                elif mate.distanceTo(hero.theirGoal) <= 40:
                    if hero.abilityReady("distract"):
                        hero.distract()
                    if hero.theirKeeper.y<32:
                        mate.roll(hero.theirGoal.x, 38, 100)
                    else:
                        mate.roll(hero.theirGoal.x, 26, 100)
                elif hero.myMates[0].distanceTo(hero.theirGoal)<mate.distanceTo(hero.theirGoal) and min(hero.myMates[0].distanceTo(hero.theirMates[0]),hero.myMates[0].distanceTo(hero.theirMates[1])) >= 5:
                    mate.roll(hero.myMates[0].x, hero.myMates[0].y, 100)
                    strikerRole=0
                else:
                    if mate.y >= 32:
                        mate.roll(hero.theirKeeper.x, 62, 100)
                    else:
                        mate.roll(hero.theirKeeper.x, 2, 100)
            elif carrier and carrier.color!=hero.color and mate.clashReady and not carrier.isImmune and mate.distanceTo(carrier) <= params.clashRange:
                mate.clash()
            elif hero.theirKeeper.hasBall:
                if hero.theirMates[0].distanceTo(hero.myGoal) <= hero.theirMates[1].distanceTo(hero.myGoal):
                    m1=hero.theirMates[0]
                    m2=hero.theirMates[1]
                else:
                    m1=hero.theirMates[1]
                    m2=hero.theirMates[0]
                if strikerRole == 0:
                    mate.moveTo(hero.myKeeper.x-(hero.myKeeper.x-m2.x)/2, hero.myKeeper.y-(hero.myKeeper.y-m2.y)/2)
                else:
                    mate.moveTo(m1.x-(m1.x-hero.theirKeeper.x)/2, m1.y-(m1.y-hero.theirKeeper.y)/2)
            elif carrier and carrier.color!=hero.color:
                if mate.distanceTo(hero.ball) <= hero.myMates[0].distanceTo(hero.ball):
                    mate.moveTo(hero.ball.x, hero.ball.y)
                    strikerRole=1
                else:
                    mate.moveTo(hero.myGoal.x-(hero.myGoal.x-hero.ball.x)/2,hero.myGoal.y-(hero.myGoal.y-hero.ball.y)/2)
            elif hero.myMates[0].hasBall:
                if mate.y >= 32:
                    mate.moveTo(hero.theirGoal.x,hero.theirGoal.y+15)
                else:
                    mate.moveTo(hero.theirGoal.x,hero.theirGoal.y-15)
            elif hero.myKeeper.hasBall:
                d1=abs(hero.myMates[0].x-hero.theirGoal.x)
                d2=abs(hero.myMates[1].x-hero.theirGoal.x)
                if (min(d1,d2) <= 45 or keeperFeedLock == 1) and mate.clashReady and hero.myMates[1].clashReady:
                    if d1<d2 and keeperFeedLock == 0:
                        keeperFeedLock=1
                        mate.clash()
                    else:
                        if mate.x<hero.myMates[0].x:
                            mate.moveTo(mate.x, mate.y)
                        else:
                            if mate.y >= 25 and mate.y <= 39:
                                mate.moveTo(hero.theirGoal.x, mate.y)
                            else:
                                if mate.y >= 32:
                                    mate.moveTo(hero.theirGoal.x, 39)
                                else:
                                    mate.moveTo(hero.theirGoal.x, 25)
                else:
                    if mate.y >= hero.myMates[0].y:
                        mate.moveTo(hero.theirGoal.x,hero.theirGoal.y+15)
                    else:
                        mate.moveTo(hero.theirGoal.x,hero.theirGoal.y-15)
            else:
                keeperFeedLock=0
                if strikerRole == 1:
                    mate.moveTo(hero.ball.x, hero.ball.y)
                else:
                    mate.moveTo(hero.myGoal.x-(hero.myGoal.x-hero.ball.x)/4*3,hero.myGoal.y-(hero.myGoal.y-hero.ball.y)/5*3)
        else:
            if mate.hasBall:
                if mate.distanceTo(hero.myKeeper)*2 <= mate.distanceTo(hero.theirKeeper)  and mate.distanceTo(hero.myKeeper) <= hero.theirMates[0].distanceTo(hero.myKeeper) and mate.distanceTo(hero.myKeeper) <= hero.theirMates[1].distanceTo(hero.myKeeper):
                    mate.roll(hero.myKeeper.x, hero.myKeeper.y, 100)
                elif min(mate.distanceTo(hero.theirMates[0]),mate.distanceTo(hero.theirMates[1]))>params.clashRange+1:
                    if hero.abilityReady("distract"):
                        hero.distract()
                    if mate.y >= 32:
                        mate.moveTo(hero.theirGoal.x, 39)
                    else:
                        mate.moveTo(hero.theirGoal.x, 25)
                elif abs(hero.ball.x-hero.theirKeeper.x) <= 8 and (64-hero.ball.y <= 8 or hero.ball.y <= 8):
                    if mate.y >= 32:
                        mate.roll(hero.theirGoal.x, 38, 100)
                    else:
                        mate.roll(hero.theirGoal.x, 26, 100)
                elif mate.distanceTo(hero.theirGoal) <= 15:
                    if hero.abilityReady("distract"):
                        hero.distract()
                    if mate.y >= 32:
                        mate.roll(hero.theirGoal.x, 38, 100)
                    else:
                        mate.roll(hero.theirGoal.x, 26, 100)
                elif mate.distanceTo(hero.theirGoal) <= 40:
                    if hero.abilityReady("distract"):
                        hero.distract()
                    if hero.theirKeeper.y<32:
                        mate.roll(hero.theirGoal.x, 38, 100)
                    else:
                        mate.roll(hero.theirGoal.x, 26, 100)
                elif hero.myMates[1].distanceTo(hero.theirGoal)<mate.distanceTo(hero.theirGoal) and min(hero.myMates[1].distanceTo(hero.theirMates[0]),hero.myMates[0].distanceTo(hero.theirMates[1])) >= 5:
                    mate.roll(hero.myMates[1].x, hero.myMates[1].y, 100)
                    strikerRole=1
                else:
                    if mate.y >= 32:
                        mate.roll(hero.theirKeeper.x, 62, 100)
                    else:
                        mate.roll(hero.theirKeeper.x, 2, 100)
            elif carrier and carrier.color!=hero.color and mate.clashReady and not carrier.isImmune and mate.distanceTo(carrier) <= params.clashRange:
                mate.clash()
            elif hero.theirKeeper.hasBall:
                if hero.theirMates[0].distanceTo(hero.myGoal) <= hero.theirMates[1].distanceTo(hero.myGoal):
                    m1=hero.theirMates[0]
                    m2=hero.theirMates[1]
                else:
                    m1=hero.theirMates[1]
                    m2=hero.theirMates[0]
                if strikerRole == 1:
                    mate.moveTo(hero.myKeeper.x-(hero.myKeeper.x-m2.x)/2, hero.myKeeper.y-(hero.myKeeper.y-m2.y)/2)
                else:
                    mate.moveTo(m1.x-(m1.x-hero.theirKeeper.x)/2, m1.y-(m1.y-hero.theirKeeper.y)/2)
            elif carrier and carrier.color!=hero.color:
                if mate.distanceTo(hero.ball) <= hero.myMates[1].distanceTo(hero.ball):
                    mate.moveTo(hero.ball.x, hero.ball.y)
                    strikerRole=0
                else:
                    mate.moveTo(hero.myGoal.x-(hero.myGoal.x-hero.ball.x)/2,hero.myGoal.y-(hero.myGoal.y-hero.ball.y)/2)
            elif hero.myMates[1].hasBall:
                if mate.y >= 32:
                    mate.moveTo(hero.theirGoal.x,hero.theirGoal.y+15)
                else:
                    mate.moveTo(hero.theirGoal.x,hero.theirGoal.y-15)
            elif hero.myKeeper.hasBall:
                d1=abs(hero.myMates[0].x-hero.theirGoal.x)
                d2=abs(hero.myMates[1].x-hero.theirGoal.x)
                if (min(d1,d2) <= 45 or keeperFeedLock == 1) and mate.clashReady and hero.myMates[1].clashReady:
                    if d2 <= d1 and keeperFeedLock == 0:
                        keeperFeedLock=1
                        mate.clash()
                    else:
                        if mate.x <= hero.myMates[1].x:
                            mate.moveTo(mate.x, mate.y)
                        else:
                            if mate.y >= 25 and mate.y <= 39:
                                mate.moveTo(hero.theirGoal.x, mate.y)
                            else:
                                if mate.y >= 32:
                                    mate.moveTo(hero.theirGoal.x, 39)
                                else:
                                    mate.moveTo(hero.theirGoal.x, 25)
                else:
                    if mate.y>hero.myMates[1].y:
                        mate.moveTo(hero.theirGoal.x,hero.theirGoal.y+15)
                    else:
                        mate.moveTo(hero.theirGoal.x,hero.theirGoal.y-15)
            else:
                keeperFeedLock=0
                if strikerRole == 0: 
                    mate.moveTo(hero.ball.x, hero.ball.y)
                else:
                    mate.moveTo(hero.myGoal.x-(hero.myGoal.x-hero.ball.x)/4*3,hero.myGoal.y-(hero.myGoal.y-hero.ball.y)/5*3)
