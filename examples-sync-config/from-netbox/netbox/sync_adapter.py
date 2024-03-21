from infrahub_sync.adapters.netbox import NetboxAdapter

from .sync_models import (
    BuiltinTag,
    LocationBuilding,
)


# -------------------------------------------------------
# AUTO-GENERATED FILE, DO NOT MODIFY
#  This file has been generated with the command `infrahub-sync generate`
#  All modifications will be lost the next time you reexecute this command
# -------------------------------------------------------
class NetboxSync(NetboxAdapter):
    BuiltinTag = BuiltinTag
    LocationBuilding = LocationBuilding
