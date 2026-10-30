"""
The Stranger: the one soul in the Hollow we didn't write. Gemma invents them anew every game,
from nothing but the story context and a single question.
"""
import os
import threading
from copy import deepcopy

from tale import util
from tale.base import Location
from tale.llm.schemas import CharacterSchema
from tale.util import Context
from tale.web.web_utils import resource_folder, web_resources_path

import tintype
from npcs.npcs import Wanderer

# kept as small as possible, so the model's own imagination decides who turns up
STRANGER_PROMPT = "<context>{context}</context>\n[USER_START] Someone is here tonight who no one in the Hollow has ever seen before. Who are they?"
# a little hotter than usual, to keep the model away from its favourite names
STRANGER_TEMPERATURE = 1.2


class StrangerSummoner:
    """ Asks the LLM for a character in the background, and lets them step out of the fog once they exist."""

    def __init__(self, location: Location) -> None:
        self.location = location
        self.started = False
        self.character = None  # type: CharacterSchema
        self.done = threading.Event()

    def summon(self, driver, story) -> None:
        if self.started:
            return
        self.started = True
        context = f"Story context:{story.config.context.to_context()}; Story type:{story.config.type}"
        threading.Thread(target=self._generate, args=(driver.llm_util, context), daemon=True).start()
        driver.defer(5.0, self._arrive)

    def _generate(self, llm_util, context: str) -> None:
        character_building = llm_util._character
        request_body = deepcopy(character_building.default_body)
        request_body['temperature'] = STRANGER_TEMPERATURE
        try:
            self.character = character_building.io_util.structured_request(request_body, prompt=STRANGER_PROMPT,
                                                                           model=CharacterSchema, context=context)
        except Exception as exc:
            # no stranger tonight; the Hollow is just as it was written
            util._get_crash_logger().warning('Failed to generate the stranger: %s', exc)
        if self.character and self.character.name.strip() and os.environ.get("GEMINI_API_KEY"):
            self._paint_portrait()
        self.done.set()

    def _paint_portrait(self) -> None:
        """ The rest of the cast was painted in advance; the stranger sits for their portrait before arriving."""
        character = self.character
        who = f"{character.name}, {character.age}, {character.occupation}. {appearance_of(character)}"
        try:
            portrait = tintype.paint_portrait(who, attempts=2)
            portrait.save(os.path.join(web_resources_path, resource_folder, tintype.file_name(character.name)), quality=85)
        except Exception as exc:
            # they arrive without a portrait
            util._get_crash_logger().warning('Failed to paint the stranger: %s', exc)

    def _arrive(self, ctx: Context) -> None:
        if not self.done.is_set():
            ctx.driver.defer(5.0, self._arrive)
            return
        if self.character and self.character.name.strip():
            stranger = make_stranger(self.character)
            self.location.insert(stranger, None)
            # the narrator only knows who arrives if we tell it, or it invents someone else
            self.location.tell(f"Someone you have never seen before steps out of the fog. {stranger.description}",
                               extra_context=f"The stranger is {stranger.title}, {stranger.description}")


def make_stranger(character: CharacterSchema) -> Wanderer:
    gender = character.gender[:1].lower() if character.gender[:1].lower() in ('m', 'f') else 'n'
    appearance = appearance_of(character)
    stranger = Wanderer(character.name.strip(), gender, race=(character.race or "human").lower(), age=character.age,
                        descr=appearance, short_descr=appearance.split('.')[0] + '.',
                        personality=character.personality or character.description, occupation=character.occupation)
    stranger.aliases = {"stranger", character.name.split()[0].lower()}
    return stranger


def appearance_of(character: CharacterSchema) -> str:
    return character.appearance or character.description or "A stranger no one here has seen before."
