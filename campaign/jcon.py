
from enum import Enum


TEXT_MESSAGE = "text_message"
SENDER = "sender"
METEOR_SHOWER = "meteor_shower"
ENEMY_TYPE = "enemy_type"


class Sender(str, Enum):
    PLAYER = "player"
    ALIEN = "alien"
    AI = "ai"

class Meteor(str, Enum):
    START = "start"
    STOP = "stop"

class EnemyType(str,Enum):
       ENEMY_BATTLESHIP      = "enemy_battleship",
       ENEMY_GUNSHIP         = "enemy_gunship",
       ENEMY_METEOR          = "enemy_meteor",
       ENEMY_PROXIMITY_MINE  = "enemy_proximity_mine",
       ENEMY_CLUSTER_BOMB    = "enemy_cluster_bomb",
       ENEMY_SUICIDE_DRONE   = "enemy_suicide_drone"


# class Key(str, Enum):
#     TRIGGER = "trigger"
#     MESSAGE = "message"
#     SPAWN = "spawn"