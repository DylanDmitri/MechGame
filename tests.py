from main import *
import random
import unittest



class IntegrationTests(unittest.TestCase):
    def setup(self):
        BigTumpo = GMS_Everest(
            name='BigTumpo'
        )
        BigTumpo.equip(
            AblativeArmor,
            GMSCore,
            FragGrenade,

            ArmorPlating,
            HeavyPlating,
            HeavyPlating,

            Overswing,
            Overswing,
            Bonk,
            Bonk,
            Bonk,
            ReinforcedActuators
        )

        LilUzi = GMS_Everest(
            name='LilUzi'
        )
        LilUzi.equip(
            GMSCore,
            FuelInjectors,
            AblativeArmor,

            ShootPistol,
            ShootPistol,
            Reload,

            Snipe,
            Snipe,
            BurstFire,
            BurstFire,
            BurstFire,
            Reload,
        )

        LilUzi.team = 'red'
        BigTumpo.team = 'blue'

        self.game = BattleManager([LilUzi, BigTumpo])

    def test_1(self):
        self.setup()
        self.game.set_seed(1)
        self.game.play()

if __name__ == '__main__':
    unittest.main()