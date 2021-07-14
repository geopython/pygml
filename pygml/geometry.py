from dataclasses import dataclass


@dataclass(frozen=True)
class Geometry:
    """ Simple container class to hold a geometry and expose it via the
        `__geo_interface__`
    """
    geometry: dict

    @property
    def __geo_interface__(self):
        return self.geometry
