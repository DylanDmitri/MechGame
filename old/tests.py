from main import *
from random import choice


stat_spread = [0]*2 + [1]*2 + [2]*5 + [3]
bias_spread = [0]*5 + [1]*2 + [2]*2 + [3]
ratio_spread = [0]*5 + [1]*3


def randomStats():
   return StatBlock(
      cpu=choice(stat_spread),
      agi=choice(stat_spread),
      hull=choice(stat_spread),
   )

def randomSkillCheck():
   return SkillCheck(
      bias=choice(bias_spread),
      ratio=StatBlock(choice(ratio_spread), choice(ratio_spread), choice(ratio_spread))
   )


def check(attacker, skill, agi=0, hull=0, damage=1):
   p1 = BattleMech([])
   p1.stats = attacker

   p2 = BattleMech([])
   p2.stats = StatBlock(cpu=0, agi=agi, hull=hull)

   gamestate = BattleManager()

   boom = GenericKinetic(p1, p2, skill, damage)
   boom(gamestate)


   return p2.reactor_stress


class GenericKinetic(BasicAttackAction):
   def __init__(self, attacker, defender, skill, damage):
      super().__init__(
         attacker, skill, 
         defender, SkillCheck(ratio=StatBlock(agi=1)),
         damage=damage
      )


def grid():
   attacker = randomStats()
   print('p1--')
   print(attacker)
   print()

   skill = randomSkillCheck()
   print(skill)
   print()

   damage = random.randint(1,6)
   print('damage', damage)

   for hull in range(8, -1, -1):
      for agi in range(0, 6, 1):
         result = check(attacker, skill, agi, hull, damage)
         print(str(result).rjust(2), end=' ')
      print()

grid()
         

# attacker = StatBlock(3, 2, 2)
# skill = SkillCheck(0, ratio=StatBlock(cpu=1, agi=1))
# r = check(attacker, skill, agi=3, hull=0)
# print(r)

