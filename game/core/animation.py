# Enums for defining frames and animations
from enum import Enum


class PetFrame(Enum):
    IDLE1, IDLE2, HAPPY, ANGRY = range(4)
    TRAIN1, TRAIN2, ATK1, ATK2 = range(4, 8)
    EAT1, EAT2, NOPE, EXTRA = range(8, 12)
    NAP1, NAP2, SICK, LOSE = range(11, 15)

class EggFrame(Enum):
    IDLE1, IDLE2, HATCH, DEAD = range(4)

class Animation:
    HATCH = [PetFrame.HAPPY]
    IDLE = [PetFrame.IDLE1, PetFrame.IDLE2]
    MOVING = [PetFrame.IDLE1, PetFrame.IDLE2]
    HAPPY = [PetFrame.HAPPY, PetFrame.IDLE1]
    HAPPY2 = [PetFrame.HAPPY, PetFrame.IDLE1]
    HAPPY3 = [PetFrame.HAPPY, PetFrame.IDLE1]
    NOPE = [PetFrame.NOPE, PetFrame.NOPE]
    ANGRY = [PetFrame.ANGRY, PetFrame.IDLE1]
    TRAIN = [PetFrame.TRAIN1, PetFrame.TRAIN2]
    ATTACK = [PetFrame.ATK1, PetFrame.ATK2]
    EAT = [PetFrame.EAT1, PetFrame.EAT2]
    NAP = [PetFrame.NAP1, PetFrame.NAP2]
    TIRED = [PetFrame.NAP1, PetFrame.NAP2]
    SICK = [PetFrame.SICK, PetFrame.ANGRY]
    POOPING = [PetFrame.SICK, PetFrame.SICK]
    LOSE = [PetFrame.LOSE, PetFrame.ANGRY]