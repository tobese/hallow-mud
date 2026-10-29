"""
The restless dead (and a few of the living) of Swede Hollow, All Hallows' Eve 1870
"""
import random

from tale.base import Living, ParseResult, Weapon
from tale.llm.LivingNpc import LivingNpc
from tale.quest import Quest, QuestType
from tale.resources_utils import pad_text_for_avatar
from tale.util import call_periodically, Context

from tale.skills.weapon_type import WeaponType


class HollowDweller(LivingNpc):
    """ A (former) inhabitant of the Hollow who idles when a player is nearby."""

    @call_periodically(75, 180)
    def do_idle_action(self, ctx: Context) -> None:
        player_names = ctx.driver.all_players.keys()
        player_in_location = any(name == living.name for name in player_names for living in self.location.livings)
        if player_in_location:
            self.idle_action()


class Wanderer(HollowDweller):
    """ Drifts between the locations of the Hollow."""

    @call_periodically(60, 120)
    def do_random_move(self, ctx: Context) -> None:
        direction = self.select_random_move()
        if direction:
            self.move(direction.target, self, direction_names=direction.names)


class Werewolf(HollowDweller):

    def init(self) -> None:
        self.stats.weapon_skills.set(weapon_type=WeaponType.UNARMED, value=70)


class Nacken(HollowDweller):
    """ The water spirit, who fights with (and never stops playing) his fiddle."""

    def init(self) -> None:
        self.stats.weapon_skills.set(weapon_type=WeaponType.ONE_HANDED, value=60)

    @call_periodically(30, 60)
    def do_play_fiddle(self, ctx: Context) -> None:
        fiddle = self.search_item("fiddle", include_location=False)
        if not fiddle:
            return
        if self.wielding is not fiddle:
            # wielding announces itself to the room, so it can't be done while the zone loads
            self.wielding = fiddle
            return
        action = "{Actor} " + random.choice(["plays a haunting polska on his fiddle", "draws a long, weeping note from his fiddle",
                                             "plays faster, and your feet take a step towards the water", "hums an old ballad over the strings"])
        if self.avatar:
            action = pad_text_for_avatar(action, self.name)
        self.tell_others(action, evoke=False, short_len=True)


class Gengangare(Living):
    """ A mindless revenant (gengångare) shambling in the cellars."""

    def init(self) -> None:
        super().init()
        self.aggressive = False
        self.stats.strength = 4
        self.stats.agility = 2
        self.title = "gengångare"
        self.stats.weapon_skills.set(weapon_type=WeaponType.UNARMED, value=30)
        self.target = None

    @call_periodically(10, 25)
    def do_idle_action(self, ctx: Context) -> None:
        if self.aggressive and self.target:
            self.start_attack(self.target)
        action = "{Actor} " + random.choice(["moans", "shuffles in the dirt", "gnaws on a rotten potato", "stares with milky eyes"])
        if self.avatar:
            action = pad_text_for_avatar(action, self.name)
        self.tell_others(action, evoke=False, short_len=True)

    def handle_verb(self, parsed: ParseResult, actor: Living) -> bool:
        if parsed.verb == "attack":
            self.aggressive = True
            self.target = actor
            return True
        return False


brita = HollowDweller("Brita Lindqvist", "f", race="wraith", age=29, descr="A pale, translucent young woman in a faded blue folkdräkt and a white linen headscarf. Her bare feet never quite touch the ground, and her cheeks are hollow from fever.", personality="Mor Brita came from Småland in 1853 and died with her little son Nils in the cholera summer of 1854. She has forgotten where Nils was buried and drifts between the graves calling his name. She is gentle and sorrowful, mixes Swedish words into her English, and begs anyone who will listen to find the painted wooden horse Nils always slept with, so she can lay it on his grave.", short_descr="A pale woman in a faded folkdräkt drifting between the headstones.")
brita.aliases = {"brita", "mor brita", "ghost", "pale woman"}
brita.quest = Quest(name="Nils' wooden horse", reason="lay the dalahorse on little Nils' grave so Brita can rest", giver=brita.name, type=QuestType.GIVE, target="dalahorse")

gustaf = HollowDweller("Gustaf Nilsson", "m", race="ghoul", age=41, descr="A hulking, grey-skinned man in a leather brewer's apron stiff with old blood. One side of his skull is caved in, and frost still clings to his beard.", personality="Järn-Gustaf hauled ice and barrels in the caves of the Hamm brewery at the top of the Hollow until a stack of ice blocks crushed him in 1866. He still believes he is on shift. He is slow, stubborn and literal, guards the cellar stairs for 'Herr Hamm', and only lets people pass if they convince him they work for the brewery or bring him something to drink.", short_descr="A hulking dead man in a brewer's apron, blocking the cellar stairs.")
gustaf.aliases = {"gustaf", "järn-gustaf", "brewer", "dead man"}

sigrid = HollowDweller("Sigrid Ahlgren", "f", race="human", age=212, descr="A tall woman in an immaculate black silk mourning dress decades out of fashion. Her skin is porcelain white, her lips are dark, and her eyes catch the candle light like a cat's.", personality="Fru Sigrid claims to be a widow of a Stockholm merchant house who came to Saint Paul for her health. In truth she is a vampire who sleeps in the Hollow's cellars because no one looks for the missing poor. She is exquisitely polite, condescending about the 'peasants' of the Hollow, hungry for news of the world above, and always tries to persuade guests to stay a little longer, or to invite her into their homes.", short_descr="A pale lady in black silk sitting very still on an upturned barrel.")
sigrid.aliases = {"sigrid", "fru sigrid", "lady", "vampire"}

anders = Werewolf("Anders Holm", "m", race="human", age=34, descr="A gaunt, unshaven trapper in a torn wolfskin coat. His fingernails are long and black, coarse grey hair sprouts on the backs of his hands, and his eyes are a little too yellow.", personality="Varg-Anders was a trapper from Värmland who was bitten by something in the woods along Phalen Creek three winters ago. He is tormented and ashamed, wants desperately to be cured, and gruffly warns strangers to leave the creek before the full moon rises over the bluff. When provoked his speech becomes a snarl.", short_descr="A gaunt trapper in a wolfskin coat crouching by the water.")
anders.aliases = {"anders", "varg-anders", "trapper", "werewolf"}

nacken = Nacken("Näcken", "m", race="fae", age=1000, descr="A beautiful, naked young man sitting waist-deep in the black water, playing a fiddle. Water lilies are tangled in his long hair, and the music makes your feet want to walk into the creek.", personality="Näcken is the water spirit of Swedish folklore who followed the immigrants across the ocean. He is charming, playful and utterly without mercy, speaks in riddles and old ballads, and tries to lure listeners into the water to drown. He can be bargained with: he will teach his music, or reveal a secret of the Hollow, in exchange for a gift of meat or a promise.", short_descr="A beautiful young man playing a fiddle in the creek.")
nacken.aliases = {"näcken", "nacken", "fiddler", "water spirit"}

fiddle = Weapon(name="fiddle", short_descr="a black fiddle", descr="A fiddle of wood gone black from the creek, strung with what looks like human hair. It is always slightly wet, and it hums faintly even when no one plays it.", wc=WeaponType.ONE_HANDED, base_damage=4, weight=1.0, value=100)
fiddle.aliases = {"violin", "fiol", "black fiddle"}
nacken.init_inventory([fiddle])

lars = Wanderer("Lars Öberg", "m", race="human", age=67, descr="A stooped old man in a patched wool coat and a flat cap, carrying a long pole with a hook for the street lanterns. He is very much alive, and very much frightened.", personality="Gamle Lars is the Hollow's lamplighter and the last living soul who refused to flee tonight. He is superstitious, talkative and drinks brännvin for courage. He knows everyone in the cemetery by name and how they died, and gladly gossips about Brita, Järn-Gustaf, the strange lady in the cellar and the trapper by the creek, but he will not go near the water.", short_descr="An old lamplighter with a hooked pole, muttering a prayer.")
lars.aliases = {"lars", "lamplighter", "old man"}
