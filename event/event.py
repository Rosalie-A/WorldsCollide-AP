import json
import os

import worlds.ff6wc.WorldsCollide.args as args
from worlds.ff6wc.WorldsCollide.memory.space import Bank, Space, Reserve, Allocate, Free, Write, Read
import worlds.ff6wc.WorldsCollide.data.direction as direction

import worlds.ff6wc.WorldsCollide.data.event_bit as event_bit
import worlds.ff6wc.WorldsCollide.data.event_word as event_word
import worlds.ff6wc.WorldsCollide.data.npc_bit as npc_bit
import worlds.ff6wc.WorldsCollide.data.battle_bit as battle_bit

import worlds.ff6wc.WorldsCollide.instruction.asm as asm
import worlds.ff6wc.WorldsCollide.instruction.field as field
import worlds.ff6wc.WorldsCollide.instruction.field.entity as field_entity
import worlds.ff6wc.WorldsCollide.instruction.world as world
import worlds.ff6wc.WorldsCollide.instruction.vehicle as vehicle

from worlds.ff6wc.WorldsCollide.instruction.event import EVENT_CODE_START
from worlds.ff6wc.WorldsCollide.event.event_reward import RewardType, Reward

class Event():
    if args.ap_data:
        with open(os.path.dirname(os.path.abspath(__file__)) + "/../../location_equivalences.json") as file:
            location_equivalencies = json.load(file)

    def __init__(self, events, rom, args, dialogs, characters, items, maps, enemies, espers, shops):
        self.events = events
        self.rom = rom
        self.args = args
        self.dialogs = dialogs
        self.characters = characters
        self.items = items
        self.maps = maps
        self.enemies = enemies
        self.espers = espers
        self.shops = shops
        self.rewards = []

        self.rewards_log = []
        self.changes_log = []
        self.aliases = []
        self.planned_reward_index = 0

    def name(self):
        raise NotImplementedError(self.__class__.__name__ + " event name")

    def character_gate(self):
        return None

    def characters_required(self):
        return 1

    def add_reward(self, possible_types):
        if args.ap_data and self.name() in Event.location_equivalencies.keys():
            ap_name = Event.location_equivalencies[self.name()][self.planned_reward_index]
            ap_index = self.planned_reward_index
            self.planned_reward_index += 1
            new_reward = Reward(self, RewardType.ARCHIPELAGO, ap_name, ap_index)
        else:
            new_reward = Reward(self, possible_types)
        self.rewards.append(new_reward)
        return new_reward

    def init_rewards(self):
        pass

    def init_event_bits(self, space):
        pass

    def get_boss(self, original_boss_name, log_change = True):
        pack_id = self.enemies.get_event_boss(original_boss_name)

        if (self.args.boss_battles_shuffle or self.args.boss_battles_random) and log_change:
            boss_name = self.enemies.packs.get_name(pack_id)
            self.log_change(original_boss_name, boss_name)
        return pack_id

    def log_reward(self, reward, prefix = "", suffix = ""):
        reward_string = prefix
        if reward.type == RewardType.CHARACTER:
            reward_string += self.characters.get_name(reward.id)
        elif reward.type == RewardType.ESPER:
            reward_string += self.espers.get_name(reward.id)
        elif reward.type == RewardType.ITEM:
            reward_string += self.items.get_name(reward.id)
        self.rewards_log.append(reward_string + suffix)

    def log_change(self, original, new):
        self.changes_log.append(f"    {original:<14} -> {new}")

    def log_string(self):
        log_string = f"{self.name():<30}"
        if self.rewards_log:
            log_string += f" {', '.join(self.rewards_log)}"
        if self.changes_log:
            log_string += '\n' + '\n'.join(self.changes_log)
        return log_string

    def mod(self):
        raise NotImplementedError(self.__class__.__name__ + " event must implement mod")
