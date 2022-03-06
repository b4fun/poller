import abc
import dataclasses


class Entity(metaclass=abc.ABCMeta):
    """Entity describes the entity for polling."""

    @property
    @abc.abstractmethod
    def id(self) -> str:
        """Unique ID of the entity."""

    @abc.abstractmethod
    def to_json(self) -> str:
        """Convert the entity instance to JSON."""


@dataclasses.dataclass
class EntityStorageSettings:
    """Base settings for the entity storage."""

    # table to store the entity.
    table: str


class EntityStorage(metaclass=abc.ABCMeta):
    """EntityStorage defines the base interface for the entity storage."""
    
    def save_entity(self, entity: Entity):
        """Save an entity."""

    def has_entity(self, entity: Entity) -> bool:
        """Check if an entity is already stored."""