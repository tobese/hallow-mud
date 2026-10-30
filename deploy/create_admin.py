"""
Create the MUD's admin (wizard) account from the environment before the server starts.

Without one, the first visitor to a public server is asked to create the admin account.
Set HALLOW_ADMIN_PASSWORD (and optionally HALLOW_ADMIN_NAME); does nothing if an admin exists.
"""
import os
import pathlib
import sys

import appdirs

from tale import accounts, base, mud_context, util
from tale.story import StoryConfig

STORY_NAME = "Hallow Mud"


def main() -> None:
    password = os.environ.get("HALLOW_ADMIN_PASSWORD")
    if not password:
        print("HALLOW_ADMIN_PASSWORD not set; the first visitor will be asked to create the admin account.")
        return
    name = os.environ.get("HALLOW_ADMIN_NAME", "dungeonmaster")
    # the accounts module reports progress using the story name
    mud_context.config = StoryConfig()
    mud_context.config.name = STORY_NAME
    # the same location the driver uses for its user data
    data_dir = pathlib.Path(appdirs.user_data_dir("Tale-" + util.storyname_to_filename(STORY_NAME), "Razorvine", roaming=True))
    data_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    mud_accounts = accounts.MudAccounts(str(data_dir / "useraccounts.sqlite"))
    if mud_accounts.all_accounts(having_privilege="wizard"):
        return
    stats = base.Stats.from_race("human", gender="n")
    try:
        mud_accounts.create(name, password, f"{name}@hallow-mud.invalid", stats, privileges={"wizard"})
    except ValueError as x:
        # start the server anyway; the first visitor will be asked to create the admin account
        print(f"Admin account '{name}' not created: {x}")
        return
    print(f"Created admin account '{name}'.")


if __name__ == "__main__":
    sys.exit(main())
