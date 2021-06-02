import random
import math

def nop():
    pass

"""
Play a battle
Generates a series of executions.
These are saved as a "battle log"

   + attack -- +2 vs AGI for 2 damage
   execute attack
   + grazing hit -- mech5921 takes 2 damage
   + ablative armor mitigation
   execute mitigation
   execute grazing hit (0 damage)
"""

class StatBlock:
    def __init__(self, cpu=0, agi=0, hull=0):
        self.cpu = cpu
        self.agi = agi
        self.hull = hull
    
    def __add__(self, other):
        return StatBlock(self.cpu+other.cpu, self.agi+other.agi, self.hull+other.hull)
    
    def __mul__(self, other):
        return StatBlock(self.cpu*other.cpu, self.agi*other.agi, self.hull*other.hull)
    
    def __iter__(self):
        yield 'CPU', self.cpu
        yield 'AGI', self.agi
        yield 'HULL', self.hull
    
    def total(self):
        return self.cpu + self.agi + self.hull
    
    def __str__(self):
        return '\n'.join(f'{v} {k}' for k,v in self)
    

class SkillCheck:
    def __init__(self, bias=0, cpu=0, agi=0, hull=0):
        self.bias = bias
        self.ratio = StatBlock(cpu, agi, hull)
    
    def __str__(self):
        r = []
        if self.bias != 0:
            r.append(str(self.bias))

        for k, v in self.ratio:
            if v == 0:
                continue
            elif v == 1:
                r.append(k)        # AGI
            else:
                r.append(f'{v}*{k}')  # 2*AGI
        
        if not r:
            return '+0 vs AGI'
        return '+'.join(r) + ' vs AGI'


# ==========================================================
class Action:
    pass

class BasicAttackAction(Action):
    # basic attack 
    # roll to hit 
    # grazing hit | solid hit | misses
    # deals damage            | --

    def __init__(self, 
        attacker, attack_skill, 
        defender, defense_skill,
        damage
    ):
        self.attacker = attacker
        self.attack_skill = attack_skill
        self.defender = defender
        self.defense_skill = defense_skill

        self.damage = damage
        self.hit_differential = None
    
    def __call__(self, gamestate):
        offense = self.attacker.score_for(self.attack_skill)
        defense = self.defender.score_for(self.defense_skill)
        result = gamestate.perform(RollToHitAction(offense, defense))

        if result < 0:
            action = AttackMissesAction
        elif result == 0:
            action = GrazingHitAction
        else:
            action = SolidHitAction

        if damage := gamestate.perform(action(self.damage)):
            gamestate.perform(TakeDamageAction(self.defender, damage))

class RollToHitAction(Action):
    def __init__(self, offense, defense):
        self.offense = offense
        self.defense = defense

    def __call__(self, gamestate):
        return self.offense - self.defense
    
    def __str__(self):
        return f'scores {self.offense} vs {self.defense}'

class AttackMissesAction(Action):
    def __init__(self, damage):
        self.damage = damage
        self.adjusted_damage = 0

    def __call__(self, gamestate):
        return self.adjusted_damage
    
    def __str__(self):
        return 'misses the attack'

class GrazingHitAction(Action):
    def __init__(self, damage):
        self.damage = damage
        self.adjusted_damage = damage / 2

    def __call__(self, gamestate):
        return self.adjusted_damage
    
    def __str__(self):
        return f'lands a grazing hit for {self.adjusted_damage} damage'

class SolidHitAction(Action):
    def __init__(self, damage):
        self.damage = damage
        self.adjusted_damage = damage

    def __call__(self, gamestate):
        return self.adjusted_damage
    
    def __str__(self):
        return f'lands a solid hit for {self.adjusted_damage} damage'
      
class TakeDamageAction:
    def __init__(self, mech, damage):
        self.mech = mech

        tenatative = damage - mech.stats.hull/2
        self.adjusted_damage = max(0, math.ceil(tenatative))
    
    def __call__(self, gamestate):
        self.mech.reactor_stress += self.adjusted_damage
    
    def __str__(self):
        return f'deals {self.adjusted_damage} damage'

class PistolShotAction(BasicAttackAction):
    def __init__(self, attacker, defender):
        super().__init__(
            attacker, SkillCheck(bias=2), 
            defender, SkillCheck(ratio=StatBlock(agi=1)),
            damage=2
        )

def BuildAttack(attack_skill, defense_skill, damage):
    class __temp(BasicAttackAction):
        def __init__(self, attacker, defender):
            super().__init__(
                attacker, attack_skill, 
                defender, defense_skill, 
                damage
            )
    return __temp


# ==========================================================
class Card:
    def __init__(self, 
        name,
        stats=None, 
        playEffect=None, 
        reaction=None
    ):
        self.name = name
        self.stats = stats or StatBlock()
        self.playEffect = playEffect or nop
        self.reactions = reaction


deck = [
    # GMS Steel Armor
    Card('Armor Plating', 
        stats=StatBlock(hull=2)),
    Card('Heavy Plating', 
        stats=StatBlock(hull=3, agi=-1)),
    Card('Heavy Plating', 
        stats=StatBlock(hull=3, agi=-1)),
    
    # GMS Sledgehammer
    Card('Overswing',
    )


]


# ==========================================================
class BattleMech:
    def __init__(self, hand):
        self.hand = hand
        self.reactor_stress = 0
    
    def score_for(self, skill_check):
        return skill_check.bias + (self.stats*skill_check.ratio).total()

    def hand_is_full(self):
        # return len(self.hand) == self.frame.handsize
        return len(self.hand) == 3
    
    @property
    def stats(self):
        return sum([card.stats for card in self.hand],
            start=StatBlock())



   
class BattleManager:
   def __init__(self):
      self.stack = []
      self.log = []

   def play_turn(self):
      full_hands = [m for m in self.mechs if m.hand_is_full()]
      if full_hands:
         mech = random.choice(full_hands)
         mech.cards[-1].playAction(self)
         mech.cards.pop()
      else:
         # TODO -- have everyone draw 1
         NotImplemented
   
   def perform(self, action):
      self.stack.append(action)

      # maybe add a reaction
      if possible := self.get_possible_reactions():
         self.perform(random.choice(possible))

      # execute the action
      action = self.stack.pop()
      self.log.append(action)
      return action(self)
   
   def get_possible_reactions(self):
      # TODO
      return []
   

"""

Extract the last name of each person 
sort the list of last names in alphabetical order

cat input.txt | cut -d ' ' -f 2 | sort -n

names = open('input.txt')
last_names = [name.split()[1] for name in people]
last_names.sort()

open file 'input.txt' as "names"
last word of each of (first 2 names), sorted

"""
