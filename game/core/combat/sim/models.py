from dataclasses import dataclass
from enum import Enum, auto
from typing import List

@dataclass
class Digimon:
    name: str                  # Name of the Digimon
    order: int                 # Order in the team (0 for single battles)
    traited: int               # Whether the Digimon has a trait applied (0 or 1)
    egg_shake: int             # Egg shake count (if applicable)
    index: int                 # Index of the Digimon
    hp: int                    # Current HP of the Digimon
    attribute: int             # Attribute (0=Vaccine, 1=Data, 2=Virus, 3=Free)
    power: int                 # Power level of the Digimon
    handicap: int              # Handicap applied to the Digimon
    buff: int                  # Buff applied to the Digimon
    mini_game: int             # Mini-game score or multiplier
    level: int                 # Level of the Digimon
    stage: int                 # Evolution stage
    sick: int                  # Whether the Digimon is sick (0=healthy, 1=sick)
    shot1: int                 # ID of the first attack sprite
    shot2: int 
    tag_meter: int


@dataclass
class DigimonStatus:
    name: str
    hp: int
    alive: bool

@dataclass
class AttackLog:
    turn: int
    device: str  # "device1" or "device2"
    attacker: int  # Index of the attacker
    defender: int  # Index of the defender (-1 if no defender)
    hit: bool
    damage: int

@dataclass
class TurnLog:
    turn: int
    device1_status: List[DigimonStatus]
    device2_status: List[DigimonStatus]
    attacks: List[AttackLog]

@dataclass
class BattleResult:
    winner: str  # "device1", "device2", or "draw"
    device1_final: List[DigimonStatus]
    device2_final: List[DigimonStatus]
    battle_log: List[TurnLog]
    device1_packets: List[List[bytes]]
    device2_packets: List[List[bytes]]

class AttributeEnum(Enum):
    FREE = 0
    VIRUS = 1
    DATA = 2
    VACCINE = 3

class BattleProtocol(Enum):
    DM20_BS = auto()
    DMC_BS = auto()
    DMX_BS = auto()
    PEN20_BS = auto()