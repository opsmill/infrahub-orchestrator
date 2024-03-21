from typing import Any, List, Optional

from infrahub_sync.adapters.infrahub import InfrahubModel

# -------------------------------------------------------
# AUTO-GENERATED FILE, DO NOT MODIFY
#  This file has been generated with the command `infrahub-sync generate`
#  All modifications will be lost the next time you reexecute this command
# -------------------------------------------------------

class BuiltinTag(InfrahubModel):
    _modelname = "BuiltinTag"
    _identifiers = ("name",)
    _attributes = ("description",)
    name: str
    description: Optional[str]
    local_id: Optional[str]
    local_data: Optional[Any]

class LocationBuilding(InfrahubModel):
    _modelname = "LocationBuilding"
    _identifiers = ("shortname",)
    _attributes = ("tags", "physical_address", "name", "description")
    physical_address: Optional[str]
    name: str
    shortname: str
    description: Optional[str]
    tags: List[str] = []
    local_id: Optional[str]
    local_data: Optional[Any]