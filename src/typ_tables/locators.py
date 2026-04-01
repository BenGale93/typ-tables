"""Module defining styling locators."""

from dataclasses import dataclass


@dataclass
class Loc:
    """Base marker for table style locator targets.

    This class is used as a common type for location-specific style selectors.
    Subclasses identify concrete table regions (for example, header cells).
    """


@dataclass
class LocHeader(Loc):
    """Marker locator selecting the table header region.

    Instances of this locator are used when applying styles intended for
    header cells.
    """
