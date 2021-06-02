import random
import types

from fractions import Fraction
from collections import deque


class Stats:
    def __init__(self, bias=0, hull=0, agi=0, cpu=0):
        self.bias = bias
        self.hull = hull
        self.agi = agi
        self.cpu = cpu
    
    @classmethod
    def parse(cls, string):
        stats = cls()

        for token in string.lower().split():
            total = (
                {'-':-1, '+':+1}[token[0]] *    # sign times
                (1, m := token[1])[m.isdigit()] # magnitude
            )

            for field in 'hull', 'agi', 'cpu':
                if token.endswith(field):
                    stats.__dict__[field] += int(total)
                    break
            else:
                stats.bias += int(total)

        return stats
    
    def dotProduct(self, other):
        return sum((
            self.bias * other.bias,
            self.hull * other.hull,
            self.agi * other.agi,
            self.cpu * other.cpu,
        ))
    
    def __add__(self, other):
        return Stats(
            self.bias + other.bias,
            self.hull + other.hull,
            self.cpu + other.cpu,
            self.agi + other.agi,
        )
    
    def __repr__(self):
        return f'STATS :: {self.bias} +{self.agi}agi +{self.hull}hull +{self.cpu}cpu'



CLOSE_RANGE = 0
MID_RANGE = 1
LONG_RANGE = 2


class EffectRange:
    def __init__(self, melee=False, close=False, mid=False, long=False):
        self.melee = melee
        self.close = close
        self.mid = mid
        self.long = long

    def covers(self, distance):
        return {
            0: self.melee or self.close,
            1: self.mid,
            2: self.long,
        }[distance]


class Card:
    stats = Stats()
    scrapped = False

    def __init__(self, mech):
        self.mech = mech

    def play(self, gamestate):
        gamestate.then(
            self.discard_me,
        )
    
    def playReactively(self, gamestate):
        pass
    
    def canReactTo(self, gamestate):
        return False
    
    def discard_me(self, gamestate):
        print(self in self.mech.hand)
        self.mech.hand.remove(self)
    
    def scrap_me(self):
        self.scrapped = True
        self.play =           lambda g: None
        self.playReactively = lambda g: None
        self.canReactTo =     lambda g: False


class BattleMech:

    def __init__(self, handsize, 
        stress=0, reactorLimit=6, heat=0, heat_gauge=6,
        team=None, frontline=True, backline=True, deck=None):

        self.handsize = handsize
        self.stress = stress
        self.reactorLimit = reactorLimit
        self.heat = heat
        self.heat_gauge = heat_gauge

        self.team = team

        self.frontline = frontline
        self.backline = backline

        self.deck = deck or []
        self.hand = deque()
        self.discard = []
    

    def distanceTo(self, other):
        if sameTeam := self.team == other.team:
            samespot = any((
                    self.frontline == other.frontline,
                    self.backline == other.backline,
            ))

            if samespot:
                return CLOSE_RANGE
            else:
                return MID_RANGE
        
        if self.frontline and other.frontline:
            return CLOSE_RANGE

        elif ((self.frontline and other.backline) or
              (self.backline and other.frontline)):
            return MID_RANGE
        
        else:
            return LONG_RANGE
    
    @property
    def stats(self):
        # sum of stats for (each card in hand)
        return sum([card.stats for card in self.hand], 
            start=Stats())
    

class BattleManager:
    def __init__(self, mechs):
        assert len(set(m.team for m in mechs)) == 2
        self.mechs: types.List[BattleMech] = mechs
        self.pending = deque()  # todo: deque
        self.log = []

    def set_seed(self, seed):
        random.seed(seed)
    
    def play(self):
        while True:
            can_act = [m for m in self.mechs if m.handsize == len(m.hand)]
            if can_act:
                mech = random.choice(can_act)
                print(mech.name, 'plays standard action')
                mech.hand[-1].play(self)
            else:
                print('queueing "everyone draws" actions')
                self.then(DrawCardAction(m) for m in self.mechs)
            self.execute()
    
    def then(self, *actions):
        if isinstance(actions[0], types.GeneratorType):
            actions = tuple(actions[0])

        self.pending.extend(reversed(actions))

    def afterwards(self, *actions):
        if isinstance(actions[0], types.GeneratorType):
            actions = tuple(actions[0])

        self.pending.extendleft(actions)
    
    def execute(self):
        while self.pending:
            if possible := self.getPossibleReactions():
                print('reacting')
                random.choice(possible).playReactively(self)
            else:
                action = self.pending.pop()
                self.log.append(action)
                print('no reactions found, performing', action)
                action(self)

    def getPossibleReactions(self):
        r = []
        for mech in self.mechs:
            for card in mech.hand:
                if card.canReactTo(self):
                    r.append(card)
        return r


# ------------ Actions ---------------

class DrawCardAction:
    def __init__(self, mech):
        self.mech: BattleMech = mech
    
    def __call__(self, gamestate):
        card = self.mech.deck.pop()
        self.mech.hand.appendleft(card)

class CardPlayedAction:
    def __init__(self, card):
        self.card = card

    def __call__(self, gamestate):
        name = self.card.__class__.__name__
        gamestate.log.append(
            f'{self.card.mech} plays {name}')
    
    def __str__(self):
        name = self.card.__class__.__name__
        return f'play card {name}'


PHASE_CHOOSE_TARGET = 0
PHASE_ROLL_ACCURACY = 1
PHASE_SOLID_HIT = 2
PHASE_GRAZING_HIT = 3
PHASE_MISSED_ATTACK = 4
PHASE_APPLY_ARMOR_REDUCTION = 5
PHASE_DEAL_REACTOR_STRESS = 6

class AttackAction:
    def __init__(self, 
        phase, source, target=None, offense=0, defense=0,
        attack_skill=Stats(), defense_skill=Stats(), 
        range=None, piercing=False, 
        initial_damage=0, hit_damage=0, reactor_damage=0):
        self.phase = phase
        self.source = source
        self.target = target
        self.offense = offense
        self.defense = defense
        self.attack_skill = attack_skill
        self.defense_skill = defense_skill
        self.range = range
        self.piercing = piercing
        self.initial_damage = initial_damage
        self.hit_damage = hit_damage
        self.reactor_damage = reactor_damage
        
    def __call__(self, gamestate):
        {
            PHASE_CHOOSE_TARGET: self.choose_target,
            PHASE_ROLL_ACCURACY: self.roll_accuracy,
            PHASE_SOLID_HIT: self.solid_hit,
            PHASE_GRAZING_HIT: self.grazing_hit,
            PHASE_MISSED_ATTACK: self.missed_attack,
            PHASE_APPLY_ARMOR_REDUCTION: self.apply_armor_reduction,
            PHASE_DEAL_REACTOR_STRESS: self.deal_reactor_stress,
        }[self.phase](gamestate)
    
    def choose_target(self, gamestate):
        valid = [m for m in gamestate.mechs if
            m.team != self.source.team and 
            self.range.covers(self.source.distanceTo(m))]
        
        self.target = random.choice(valid)
        self.phase = PHASE_ROLL_ACCURACY
        gamestate.then(self)

    def roll_accuracy(self, gamestate):
        self.offense = self.attack_skill.dotProduct(self.source.stats)
        self.defense = self.defense_skill.dotProduct(self.target.stats)

        if self.offense > self.defense:
            self.phase = PHASE_SOLID_HIT
        elif self.offense < self.defense:
            self.phase = PHASE_MISSED_ATTACK
        else:
            self.phase = PHASE_GRAZING_HIT
        
        gamestate.then(self)
    
    def solid_hit(self, gamestate):
        self.hit_damage = Fraction(1, 1) * self.initial_damage
        self.phase = PHASE_APPLY_ARMOR_REDUCTION
        gamestate.then(self)
    
    def grazing_hit(self, gamestate):
        self.hit_damage = Fraction(1, 2) * self.initial_damage
        self.phase = PHASE_APPLY_ARMOR_REDUCTION
        gamestate.then(self)

    def missed_attack(self, gamestate):
        self.hit_damage = 0
    
    def apply_armor_reduction(self, gamestate):
        if not self.piercing:
            reduction = Fraction(self.target.stats.hull, 2)
            self.reactor_damage = self.hit_damage - reduction
            if self.reactor_damage == 0:
                return  # everything block
        
        Phase = PHASE_DEAL_REACTOR_STRESS
        gamestate.then(self)

    def deal_reactor_stress(self, gamestate):
        self.target.stress += self.reactor_damage
        if self.target.stress > self.target.reactorLimit:
            print('kaBOOM!')
    
    def __str__(self):
        return {
            PHASE_CHOOSE_TARGET: 'Choosing Target',
            PHASE_ROLL_ACCURACY: 'Rolling Accuracy',
            PHASE_SOLID_HIT: "Solid Hit",
            PHASE_GRAZING_HIT: "Grazing Hit",
            PHASE_MISSED_ATTACK: "Missed Attack",
            PHASE_APPLY_ARMOR_REDUCTION: 'Applying Armor Reduction',
            PHASE_DEAL_REACTOR_STRESS: 'Dealing Reactor Stress'
        }[self.phase]

# ------------- Cards ----------------

class GMSCore(Card):
    stats = Stats.parse("+HULL +AGI +CPU")

class GMSProcessor(Card):
    """
    Grants an additional point of CPU when used defensively.
    """
    stats = Stats.parse("+2CPU")

    def canReactTo(self, gamestate):
        pending = gamestate.pending[-1]
        return (pending.target is self
            and hasattr(pending, 'defense_skill')
            and pending.defense_skill.cpu
        )
    
    def reaction(self, gamestate):
        pending = gamestate.pending[-1]
        pending.bias += pending.cpu


class FuelInjectors(Card):
    """
    Discard me, then draw a card.
    """
    stats = Stats.parse("+AGI")

    def play(self, gamestate):
        gamestate.then(
            CardPlayedAction(self),
            self.discard_me,
            DrawCardAction(self.mech))


class FragGrenade(Card):
    """
    Hits all enemies at close range for 1 damage.
    This damage can still be reduced by armor.
    """
    def play(self, gamestate):
        targets = [
            m for m in gamestate.mechs if
            m.team != self.mech.team and
            EffectRange(close=True).covers(
                self.mech.distanceTo(m)
            )
        ]
        random.shuffle(targets)

        gamestate.then(
            CardPlayedAction(self),
            *(AttackAction(
                phase=PHASE_SOLID_HIT,
                initial_damage=1,
                source=self.mech,
                target=target,
            )
            for target in targets),
            self.discard_me
        )


class EmergencyCoolant(Card):
    """
    If your heat gauge is full, clear it, then scrap me.
    """

    def clear_heat_action(self):
        if self.procs():
            self.mech.heat -= self.mech.heat_gauge
    
    def procs(self):
        return self.mech.heat >= self.mech.heat_gauge

    def play(self, gamestate):
        if self.procs():
            gamestate.then(
                CardPlayedAction(self),
                self.clear_heat_action,
                self.discard_me
            )
        else:
            gamestate.then(
                self.discard_me
            )


class AblativeArmor(Card):
    """
    Reaction -- when you would take damage, 
    reduce that damage by 2 to a minimum of 0,
    then scrap me.
    """
    stats = Stats.parse("+HULL")

    def canReactTo(self, gamestate) -> bool:
        pending = gamestate.pending[-1]
        return all((
            type(pending) is AttackAction,
            pending.phase is PHASE_DEAL_REACTOR_STRESS,
            pending.target is self.mech,
        ))

    def reaction(self, gamestate):
        pending = gamestate.pending[-1]
        pending.reactor_damage = max(0, pending.reactor_damage-2)
        gamestate.then(self.scrap_me)

class ArmorPlating(Card):
    stats = Stats.parse("+2HULL")

class HeavyPlating(Card):
    stats = Stats.parse("+3HULL -AGI")

class JetBoost(Card):
    """
    Reaction -- if my agility lets you dodge an attack, take 2 heat.
    """
    stats = Stats.parse("+3AGI")

    def canReactTo(self, gamestate):
        pending = gamestate.pending[-1]
        if type(pending) is not AttackAction:
            return False
        
        margin = pending.offense - pending.defense
        return all((
            pending.phase is PHASE_MISSED_ATTACK,
            (agi_mult := pending.defense_skill.agi),
            margin <= 3*agi_mult,
        ))
    
    def reaction(self, gamestate):
        self.mech.heat += 2

class Sidestep(Card):
    stats = Stats.parse("+AGI")

class ShootPistol(Card):
    """
    Close/Mid-range attack, +2 vs AGI, onhit deal 2 damage
    """
    def play(self, gamestate):
        attack = AttackAction(
            phase=PHASE_CHOOSE_TARGET, 
            source=self.mech,
            attack_skill=Stats.parse("+2"),
            defense_skill=Stats.parse("+AGI"),
            range=EffectRange(close=True, mid=True),
            initial_damage=2,
        )
        gamestate.then(
            CardPlayedAction(self),
            attack, self.discard_me
        )


class Reload(Card):
    """
    Passes your turn.
    """
    pass

class StabNSlice(Card):
    """
    Make two close-range attacks, both AGI vs AGI to hit.
    First attack is a stab, dealing 1 piercing damage.
    The second is a slash, dealing 1 regular damage.
    """

    def play(self, gamestate):
        target = random.choice(
            m for m in gamestate.mechs if
            m.team != self.mech.team and
            EffectRange(close=True).covers(
                self.mech.distanceTo(m)
            )
        )

        Stab = AttackAction(
            phase=PHASE_ROLL_ACCURACY,
            target=target, source=self.mech,
            attack_skill=Stats.parse("+AGI"),
            defense_skill=Stats.parse("+AGI"),
            initial_damage=1,
            piercing=True
        )

        Slice = AttackAction(
            phase=PHASE_ROLL_ACCURACY,
            target=target, source=self.mech,
            attack_skill=Stats.parse("+AGI"),
            defense_skill=Stats.parse("+AGI"),
            initial_damage=1,
            piercing=False
        )

        gamestate.then(
            CardPlayedAction(self),
            Stab, Slice,
            self.discard_me,
        )

class Overswing(Card):
    """
    Melee attack, +0 vs AGI, onhit deal 6 damage.
    """
    def play(self, gamestate):
        attack = AttackAction(
            phase=PHASE_CHOOSE_TARGET,
            source=self.mech,
            range=EffectRange(melee=True),
            attack_skill=Stats.parse("+0"),
            defense_skill=Stats.parse("+AGI"),
            initial_damage=6,
        )
        gamestate.then(
            CardPlayedAction(self),
            attack, self.discard_me
        )

class Bonk(Card):
    """
    Melee attack, +1 vs AGI, onhit deal 3 damage.
    """
    def play(self, gamestate):
        attack = AttackAction(
            phase=PHASE_CHOOSE_TARGET,
            source=self.mech,
            range=EffectRange(melee=True),
            attack_skill=Stats.parse("+1"),
            defense_skill=Stats.parse("+AGI"),
            initial_damage=3,
        )
        gamestate.then(
            CardPlayedAction(self),
            attack, self.discard_me
        )

class ReinforcedActuators(Card):
    """
    Passive -- Landing a solid hit with a melee weapon grants +1 damage.
    """
    stats = Stats.parse("+HULL")

    def canReact(self, gamestate):
        pending = gamestate.pending[-1]
        return (
            (type(pending) is AttackAction) and
            (pending.source is self.mech) and
            (pending.range.melee is True) and 
            (pending.phase is PHASE_SOLID_HIT))

    def playReactively(self, gamestate):
        pending = gamestate.pending[-1]
        pending.initial_damage += 1

class Snipe(Card):
    """
    Mid/Long-ranged attack, CPU vs AGI, onhit deal 2 damage.
    """
    stats = Stats.parse("+CPU")

    def play(self, gamestate):
        attack = AttackAction(
            phase=PHASE_CHOOSE_TARGET,
            source=self.mech,
            range=EffectRange(mid=True, long=True),
            attack_skill=Stats.parse("+CPU"),
            defense_skill=Stats.parse("+AGI"),
            initial_damage=2,
        )

        gamestate.then(
            CardPlayedAction(self),
            attack,
            self.discard_me,
        )



class BurstFire(Card):
    """
    Close/Mid-ranged attack, +2 vs AGI, onhit deal 2 damage.
    Close/Mid-ranged attack, +3 vs AGI, onhit deal 1 damage.
    """
    def play(self, gamestate):
        target = random.choice([
            m for m in gamestate.mechs if
            m.team != self.mech.team and
            EffectRange(close=True).covers(
                self.mech.distanceTo(m)
            )
        ])

        Shot1 = AttackAction(
            phase=PHASE_ROLL_ACCURACY,
            target=target, source=self.mech,
            attack_skill=Stats.parse("+2"),
            defense_skill=Stats.parse("+AGI"),
            initial_damage=2,
        )

        Shot2 = AttackAction(
            phase=PHASE_ROLL_ACCURACY,
            target=target, source=self.mech,
            attack_skill=Stats.parse("+3"),
            defense_skill=Stats.parse("+AGI"),
            initial_damage=1,
        )

        gamestate.then(
            CardPlayedAction(self),
            Shot1, Shot2,
            self.discard_me,
        )


# ------------- Mechs ----------------

class GMS_Everest(BattleMech):
    def __init__(self, name):
        self.name = name

        super().__init__(
            handsize=3,
            stress=0,
            reactorLimit=5,
            heat=0,
            heat_gauge=4,
        )

    def __repr__(self):
        return f'{self.name} {len(self.hand)}/3'

    def equip(self, *cards):
        for card in cards:
            self.deck.append(card(self))