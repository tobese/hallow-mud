"""
Swede Hollow zone locations
"""
from tale.base import Location, Exit, Item, Weapon
from tale.skills.weapon_type import WeaponType
from npcs.npcs import *
from npcs.stranger import StrangerSummoner


swede_hollow = Location("The heart of Swede Hollow", descr="""You stand in the muddy street of Swede Hollow on All Hallows' Eve, 1870.
Thick fog rolls between the crude log and plank houses built into the steep hillside.
The windows of the houses are dark and boarded, as if the inhabitants fled in terror.
A crooked wooden fence casts twisted shadows in the moonlight. Strange whispers
echo from somewhere in the darkness. The smell of damp earth and decay fills the air.""")
cemetery = Location("The old Swedish cemetery", descr="""A small, overgrown cemetery sits on the edge of Swede Hollow.
Rusted iron crosses and crumbling headstones mark the graves of early Swedish settlers.
Many of the headstones are written in Swedish and date back to the 1850s.
On this night, the graves appear disturbed - fresh earth has been turned up.
Ghostly figures drift between the tombstones, wailing in a mixture of Swedish and English.""")
cellar_entrance = Location("A crumbling cellar entrance", descr="""An old wooden door hangs ajar, leading down into the dark earth.
Steps descend into a root cellar that must be centuries old.
A foul stench of rot and corruption wafts up from the depths.
Shadows move in the darkness below. You can hear moaning and shuffling sounds.""")
cellar = Location("A dark, damp root cellar", descr="""You find yourself in a long-abandoned root cellar beneath one of the old houses.
Sacks of rotted potatoes lie scattered on the dirt floor. Broken barrels line the walls.
The air is thick with the stench of decay. Candles flicker on their own.
Tattered remains of 1800s clothing hang from rusted hooks. The undead shamble in the gloom.""")
creek_bank = Location("The muddy bank of Phalen Creek", descr="""The murky waters of Phalen Creek flow sluggishly beside you.
On a normal night, this would be a peaceful spot, but tonight the water
is unnaturally black and mist rises from its surface. 
Old broken buckets and fishing nets lie abandoned on the muddy bank.
Something large and hairy prowls in the woods nearby, growling hungrily.""")

swede_hollow.add_exits([Exit(["north", "n"], "hallow_mud.cemetery", "The cemetery lies to the north."),
                        Exit(["east", "e"], "hallow_mud.cellar_entrance", "A cellar entrance lies to the east."),
                        Exit(["south", "s"], "hallow_mud.creek_bank", "The creek bank lies to the south.")])
cemetery.add_exits([Exit(["south", "s"], "hallow_mud.swede_hollow", "Swede Hollow lies to the south.")])
cellar_entrance.add_exits([Exit(["west", "w"], "hallow_mud.swede_hollow", "Swede Hollow lies to the west."),
                           Exit(["down", "d"], "hallow_mud.cellar", "A dark cellar descends below.")])
cellar.add_exits([Exit(["up", "u"], "hallow_mud.cellar_entrance", "The cellar entrance lies above.")])
creek_bank.add_exits([Exit(["north", "n"], "hallow_mud.swede_hollow", "Swede Hollow lies to the north.")])

dalahorse = Item("dalahorse", "small painted wooden horse", descr="A child's dalahäst, carved from pine and painted red with white and blue flowers. Tiny teeth marks are worn into its ears.")
dalahorse.aliases = {"horse", "wooden horse", "dalahäst"}

# the gravedigger's scythe and the brewery's hammer, for whoever means to fight the dead
lie = Weapon("lie", title="long-handled scythe", descr="A long-handled Swedish scythe (lie), left among the graves by a gravedigger who didn't stay to finish. The blade is freshly honed.", weapon_type=WeaponType.TWO_HANDED, base_damage=6, weight=4.0, value=30)
lie.aliases = {"scythe"}
sledgehammer = Weapon("sledgehammer", title="heavy sledgehammer", descr="A heavy iron sledgehammer from the Hamm brewery, used for knocking the ice loose in the caves. HAMM is burned into the handle.", weapon_type=WeaponType.TWO_HANDED, base_damage=7, weight=8.0, value=25)
sledgehammer.aliases = {"hammer"}

gengangare = new_gengangare()

swede_hollow.init_inventory([lars])
cemetery.init_inventory([brita, lie])
cellar_entrance.init_inventory([gustaf, sledgehammer])
cellar.init_inventory([sigrid, gengangare, dalahorse])
creek_bank.init_inventory([anders, nacken])

# the stranger isn't written here; Gemma invents them each game
stranger_summoner = StrangerSummoner(swede_hollow)

all_locations = [swede_hollow, cemetery, cellar_entrance, cellar, creek_bank]
