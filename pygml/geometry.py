from dataclasses import dataclass, field


@dataclass(frozen=True)
class Geometry:
    geometry: dict

    @property
    def __geo_interface__(self):
        return self.geometry
