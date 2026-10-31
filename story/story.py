"""
Hallow Mud - A Halloween-themed LLM MUD set in Swede Hollow, Saint Paul

'Tale' mud driver, mudlib and interactive fiction framework
"""
import os
import pathlib
import sys
import threading
import types
from typing import Optional, Generator

import tale
from tale import lang, util
from tale.base import Location, Weapon, Wearable
from tale.cmds import spells
from tale.driver import Driver
from tale.dungeon.dungeon_config import DungeonConfig
from tale.items.basic import Food, Health
from tale.llm.dynamic_story import DynamicStory
from tale.skills.magic import MagicType
from tale.main import run_from_cmdline
from tale.player import Player, PlayerConnection
from tale.charbuilder import PlayerNaming
from tale.skills.skills import SkillType
from tale.story import *
from tale.skills.weapon_type import WeaponSkills, WeaponType
from tale.story_context import StoryContext
from tale.util import Context
from tale.wearable import WearLocation
from tale.zone import Zone


# what a player can take before falling; also what they wake with
PLAYER_HP = 10


class Story(DynamicStory):

    config = StoryConfig()
    config.name = "Hallow Mud"
    config.author = "the Dungeon Master and the ghost in the machine"
    config.author_address = ""
    config.version = tale.__version__
    config.supported_modes = {GameMode.IF, GameMode.MUD}
    config.player_money = 15.0
    config.playable_races = {"human"}
    config.money_type = MoneyType.FANTASY
    config.server_tick_method = TickMethod.TIMER
    config.server_tick_time = 0.5
    config.gametime_to_realtime = 5
    config.display_gametime = True
    # hosting platforms such as Render set PORT; empty values fall back to localhost:8180
    config.mud_host = os.environ.get("MUD_HOST", "")
    config.mud_port = int(os.environ.get("PORT", 0))
    config.startlocation_player = "hallow_mud.swede_hollow"
    config.startlocation_wizard = "hallow_mud.swede_hollow"
    config.zones = ["hallow_mud"]
    config.context = StoryContext(
        base_story="Swede Hollow, Saint Paul, Minnesota - 1800s Swedish immigrant neighborhood. "
                   "On All Hallows' Eve, the veil between worlds grows thin. "
                   "The spirits of long-dead Swedish immigrants have returned as ghosts, "
                   "zombies, werewolves, and vampires. A misty, autumnal Halloween atmosphere."
    )
    config.type = "A dark Halloween adventure set in 19th century Swedish immigrant Saint Paul."
    config.custom_resources = True

    def init(self, driver: Driver) -> None:
        """Called by the game driver when it is done with its initial initialization."""
        self.driver = driver
        # runs once the game loop has started and the LLM knows the story
        driver.defer(1.0, self._warm_up_rooms)
        self._zones = dict()

        hallow_zone = Zone(
            "Swede Hollow",
            description="A misty autumn night in 1800s Swede Hollow, Saint Paul. "
                        "The air is thick with fog and the smell of rotting leaves. "
                        "Lantern light flickers weakly, unable to pierce the gloom. "
                        "Something unnatural lurks in the shadows."
        )
        hallow_zone.dungeon_config = DungeonConfig(
            name="The Forgotten Cellars",
            description="Crumbling root cellars beneath the old Swedish homes, "
                        "now infested with restless undead.",
            races=["zombie", "skeleton", "vampire", "werewolf"],
            items=["swedish axe", "rusty sickle", "folkdräkt", "lantern", "food rations"],
            max_depth=4
        )
        self._zones["Swede Hollow"] = hallow_zone

        import zones.hallow_mud
        for location in zones.hallow_mud.all_locations:
            self._zones["Swede Hollow"].add_location(location)

        import tale.races as races
        race_names = ["human", "zombie", "vampire", "werewolf", "skeleton"]
        self._catalogue._creatures = [dict(races._races.get(name, {"name": name})) for name in race_names]

        folkdrakt = Wearable(
            name='folkdräkt',
            short_descr='a traditional Swedish folk costume',
            descr='A well-worn traditional Swedish folkdräkt from the 1800s. '
                 'Despite its age, it provides decent protection.',
            wear_location=WearLocation.TORSO,
            weight=2.0,
            value=40
        )
        lie = Weapon(
            name='lie',
            short_descr='a long-handled scythe',
            descr='A long-handled Swedish scythe (lie), used for harvesting but deadly in combat.',
            weapon_type=WeaponType.TWO_HANDED,
            base_damage=6,
            weight=4.0,
            value=30
        )
        sledgehammer = Weapon(
            name='sledgehammer',
            short_descr='a heavy sledgehammer',
            descr='A heavy iron sledgehammer, a common tool in 1800s workshops.',
            weapon_type=WeaponType.TWO_HANDED,
            base_damage=7,
            weight=8.0,
            value=25
        )
        food_ration = Food(
            name='food rations',
            short_descr='a pack of food rations',
            descr='Hard tack and dried meat, common fare for Swedish immigrants.',
            value=5
        )
        lantern = Wearable(
            name='lantern',
            short_descr='a flickering oil lantern',
            descr='An oil lantern that casts a weak, flickering light against the fog.',
            wear_location=WearLocation.HANDS,
            weight=1.0,
            value=15
        )
        self._catalogue._items = [folkdrakt.to_dict(), lie.to_dict(), sledgehammer.to_dict(),
                                  food_ration.to_dict(), lantern.to_dict()]

    def _warm_up_rooms(self, ctx: Context) -> None:
        """ Have the LLM rewrite every room in the background, so no player waits for a room description."""
        import zones.hallow_mud
        for location in zones.hallow_mud.all_locations:
            threading.Thread(target=self._rewrite_room, args=(ctx.driver.llm_util, location), daemon=True).start()

    @staticmethod
    def _rewrite_room(llm_util, location: Location) -> None:
        try:
            # the same text Player.look evokes, so the rewrite lands in the cache it reads from
            llm_util.evoke('\n'.join(location.look_room()))
        except Exception as exc:
            util._get_crash_logger().warning('Failed to rewrite %s: %s', location.name, exc)

    def init_player(self, player: Player) -> None:
        """
        Called by the game driver when it has created the player object (after successful login).
        """
        import zones.hallow_mud
        zones.hallow_mud.stranger_summoner.summon(self.driver, self)
        # players start with no skill in any weapon and could never land a blow; with these
        # they beat the gengångare most of the time, and the werewolf rarely.
        # A mud account loads its skills back from JSON as a plain dict keyed "1".."7", so rebuild them.
        skills = WeaponSkills()
        for weapon, value in player.stats.weapon_skills.items():
            skills[WeaponType(int(weapon))] = value
        skills[WeaponType.UNARMED] = 30
        skills[WeaponType.ONE_HANDED] = 40
        skills[WeaponType.TWO_HANDED] = 40
        player.stats.weapon_skills = skills
        player.stats.hp = player.stats.max_hp = PLAYER_HP
        # combat defers the death by name on its owner, so it has to stay player.do_on_death
        player.do_on_death = types.MethodType(do_on_death, player)

    def create_account_dialog(self, playerconnection: PlayerConnection, playernaming: PlayerNaming) -> Generator:
        """
        Override to add extra dialog options to the character creation process.
        """
        return True
        yield

    def welcome(self, player: Player) -> str:
        player.tell("<bright>Welcome to Hallow Mud - Swede Hollow, Saint Paul, All Hallows' Eve 1870</>", end=True)
        player.tell("\nThe fog rolls between the crooked wooden houses. The veil is thin tonight...")
        player.tell("\n")
        return "<bright>Press enter to begin.</>"


def do_on_death(player: Player) -> None:
    """ No one stays dead in the Hollow tonight: a fallen player wakes in the cemetery, whole again."""
    import zones.hallow_mud
    player.tell("You die.", end=True)
    player.location.tell("%s falls, and the fog closes over the body." % lang.capital(player.title), exclude_living=player)
    player.stats.hp = player.stats.max_hp
    player.move(zones.hallow_mud.cemetery, silent=True)
    player.tell("...and you wake, cold as the earth, among the graves. The veil is thin tonight, and it will not let you go.", end=True)
    player.look()


if __name__ == "__main__":
    from tale.main import run_from_cmdline
    run_from_cmdline(["--game", sys.path[0], "--mode", "mud"])
