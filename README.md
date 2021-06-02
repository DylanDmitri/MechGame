# MechGame

Test to make a rougelite autobattler deckbuilder.

Inspired by Lancer RPG, Dota AutoChess, Into the Breach, Slay the Spire, and Cardhunter.  

## Core game loop

  - You have some spare parts, pilots, and mech frames.
  - You have some info on the next challenge.
  - You build a party that counters the enemy composition.
  - Pilots automatically fight for you.

## Map and Range

Two teams, mechs are either backline or frontline.

     team a     team a    team b    team b 
    backline  frontline  frontline backline

Close range weapons are frontline-frontline only. Mid-range weapons can skip 1 zone, long range can run anywhere.

If only one mech remains on any side, it counts as both frontline and backline.

## Cards and Stats

Cards can have any combination of: 
  - "playEffect" or what happens when you play them normallly
  - "reaction" can cast themselves from hand when conditions are pmet
  - "passive" continual effect while in hand (see reinforced actuators card)

Many cards grant passive stats. These are:
  - 'HULL' flat reduction against most damage
  - 'AGI' agility, lets you dodge some attacks entirely
  - 'CPU' used for hacking, targetting, resisting hacks
  
## Factions and Color Wheel

    :            Jita
    :      Weyland   Rendersoft
    :           Spacers

Weyland prioritizes heavy armor as defense, with slow heavy weapons to break through.
Rendersoft prioritizes high agility as defense, with big CPU to target and hit them.
The Jita Group combines both offenses, Spacer Collective combines both defenses.

HULL - Weyland / Spacers
AGI - Rendersoft / Spacers
CPU - Rendersoft / Jita
HEAT - Weyland / Jita

## Heat 

Mechs have a heat gauge. Take too much, and it rolls over to damage.
Many high damage weapons (giga lasers) can be heat boosted.
There's gear availible to manipulate, and mitigate heat.

## Pilot Skill

Randomness doesn't need to affect card draw etc. Both teams have an aggregate skill level. Sigmoid the difference to get a percentile.

Simulate ~100 games, choose the outcome at that percentile, that's what happens.

High average skill you simulate more games (lower variance).


# Testing Reveals

It's not actually that fun.

The mechanics are satisfying and fit together well, the balance and gamespace are good, but there's no visceral excitement of being there and doing well. 
I think there's something that autobattlers do well (constant clicking to upgrade units) which is missing from a more deliberative design.
Going to recycle much of this material for a multiplayer game (one person per mech) with physical cards. 
