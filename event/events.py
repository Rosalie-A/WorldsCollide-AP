import args
from memory.space import Bank, Allocate
from event.event_reward import RewardType, Reward, choose_reward, weighted_reward_choice
import instruction.field as field

class Events():
    def __init__(self, rom, args, data):
        self.rom = rom
        self.args = args

        self.dialogs = data.dialogs
        self.characters = data.characters
        self.items = data.items
        self.maps = data.maps
        self.enemies = data.enemies
        self.espers = data.espers
        self.shops = data.shops

        self.mod()

    def mod(self):
        # generate list of events from files
        import os, importlib, inspect
        from event.event import Event
        events = []
        name_event = {}
        for event_file in sorted(os.listdir(os.path.dirname(__file__))):
            if event_file[-3:] != '.py' or event_file == 'events.py' or event_file == 'event.py':
                continue

            module_name = event_file[:-3]
            event_module = importlib.import_module('event.' + module_name)

            for event_name, event_class in inspect.getmembers(event_module, inspect.isclass):
                if event_name.lower() != module_name.replace('_', '').lower():
                    continue
                event = event_class(name_event, self.rom, self.args, self.dialogs, self.characters, self.items, self.maps, self.enemies, self.espers, self.shops)
                events.append(event)
                name_event[event.name()] = event

        # select event rewards
        if self.args.character_gating:
            self.character_gating_mod(events, name_event)
        else:
            self.open_world_mod(events)

        # initialize event bits, mod events, log rewards
        log_strings = []
        space = Allocate(Bank.CC, 400, "event/npc bit initialization", field.NOP())
        for event in events:
            event.init_event_bits(space)
            event.mod()

            if self.args.spoiler_log and (event.rewards_log or event.changes_log):
                log_strings.append(event.log_string())
        space.write(field.Return())
        #write_event_trigger_function()

        if self.args.spoiler_log:
            from log import section
            section("Events", log_strings, [])

    def init_reward_slots(self, events):
        import random
        reward_slots = []
        for event in events:
            event.init_rewards()
            for reward in event.rewards:
                if reward.id is None:
                    reward_slots.append(reward)

        random.shuffle(reward_slots)
        return reward_slots

    def choose_single_possible_type_rewards(self, reward_slots):
        for slot in reward_slots:
            if slot.single_possible_type() and RewardType.ARCHIPELAGO not in slot.possible_types:
                slot.id, slot.type = choose_reward(slot.possible_types, self.characters, self.espers, self.items)

    def choose_char_esper_possible_rewards(self, reward_slots):
        for slot in reward_slots:
            if slot.possible_types == (RewardType.CHARACTER | RewardType.ESPER):
                slot.id, slot.type = choose_reward(slot.possible_types, self.characters, self.espers, self.items)

    def choose_item_possible_rewards(self, reward_slots):
        for slot in reward_slots:
            slot.id, slot.type = choose_reward(slot.possible_types, self.characters, self.espers, self.items)

    def choose_archipelago_rewards(self, reward_slots):
        for slot in reward_slots:
            slot.id, slot.type = choose_reward(slot.possible_types, self.characters, self.espers, self.items, slot)

    def character_gating_mod(self, events, name_event):
        import random
        reward_slots = self.init_reward_slots(events)

        if args.ap_data:
            self.choose_archipelago_rewards(reward_slots)
            self.characters.available_characters = []

        # for every event with only one reward type possible, assign random rewards
        # note: this includes start, which can get up to 4 characters
        self.choose_single_possible_type_rewards(reward_slots)

        # find characters that were assigned to start
        characters_available = [reward.id for reward in name_event["Start"].rewards]

        # find all the rewards that can be a character
        character_slots = []
        for event in events:
            for reward in event.rewards:
                if reward.possible_types & RewardType.CHARACTER:
                    character_slots.append(reward)

        iteration = 0
        slot_iterations = {} # keep track of how many iterations each slot has been available
        while self.characters.get_available_count():

            # build list of which slots are available and how many iterations those slots have already had
            unlocked_slots = []
            unlocked_slot_iterations = []
            for slot in character_slots:
                slot_empty = slot.id is None
                gate_char_available = (slot.event.character_gate() in characters_available or slot.event.character_gate() is None)
                enough_chars_available = len(characters_available) >= slot.event.characters_required()
                if slot_empty and gate_char_available and enough_chars_available:
                    if slot in slot_iterations:
                        slot_iterations[slot] += 1
                    else:
                        slot_iterations[slot] = 0
                    unlocked_slots.append(slot)
                    unlocked_slot_iterations.append(slot_iterations[slot])

            # pick slot for the next character weighted by number of iterations each slot has been available
            slot_index = weighted_reward_choice(unlocked_slot_iterations, iteration)
            print(slot_index)
            slot = unlocked_slots[slot_index]
            slot.id = self.characters.get_random_available()
            slot.type = RewardType.CHARACTER
            characters_available.append(slot.id)
            self.characters.set_character_path(slot.id, slot.event.character_gate())
            iteration += 1

        # get all reward slots still available
        reward_slots = [reward for event in events for reward in event.rewards if reward.id is None]
        random.shuffle(reward_slots) # shuffle to prevent picking them in alphabetical order

        # for every event with only char/esper rewards possible, assign random rewards
        self.choose_char_esper_possible_rewards(reward_slots)

        reward_slots = [slot for slot in reward_slots if slot.id is None]

        # assign rest of rewards where item is possible
        self.choose_item_possible_rewards(reward_slots)
        return

    def open_world_mod(self, events):
        import random
        reward_slots = self.init_reward_slots(events)

        # first choose all the rewards that only have a single type possible
        # this way we don't run out of that reward type before getting to the event
        self.choose_single_possible_type_rewards(reward_slots)

        reward_slots = [slot for slot in reward_slots if not slot.single_possible_type()]

        # next choose all the rewards where only character/esper types possible
        # this way we don't run out of characters/espers before getting to these events
        self.choose_char_esper_possible_rewards(reward_slots)

        reward_slots = [slot for slot in reward_slots if slot.id is None]

        # choose the rest of the rewards, items given to events after all characters/events assigned
        self.choose_item_possible_rewards(reward_slots)

def write_event_trigger_function():
    from memory.space import Reserve, Bank, Write, Read, START_ADDRESS_SNES
    from instruction.event import EVENT_CODE_START
    import instruction.asm as asm
    import instruction.field as field

    trigger_addr = 0x115c  # modify at runtime to trigger events

    src = [
        field.FlashScreen(field.Flash.GREEN),
        field.PlaySoundEffect(0xCD),
        field.RecruitAndSelectParty2(0),
        field.FadeInScreen(),
        field.FinishCheck(),
        field.Return()
    ]
    space = Write(Bank.CA, src, "recruit terra")
    recruit_character = (space.start_address - EVENT_CODE_START).to_bytes(3, "little")

    src = [
        field.FlashScreen(field.Flash.BLUE),
        field.PlaySoundEffect(0xCD),
        field.AddEsper2(0),
        field.Return(),
    ]
    space = Write(Bank.CA, src, "esper trigger")
    add_esper = (space.start_address - EVENT_CODE_START).to_bytes(3, "little")

    src = [
        field.FlashScreen(field.Flash.YELLOW),
        field.PlaySoundEffect(0xCD),
        field.AddItem2(0),
        field.Return(),
    ]
    space = Write(Bank.CA, src, "item trigger")
    add_item = (space.start_address - EVENT_CODE_START).to_bytes(3, "little")

    src = [
        recruit_character,
        add_esper,
        add_item
    ]
    space = Write(Bank.C0, src, "trigger event table")
    trigger_event_table = space.start_address
    trigger_call = field.Call(EVENT_CODE_START)  # dummy call instruction for length/opcode

    # subtract the length of the trigger call to correctly return to event code start after finishing the trigger event
    return_addr = (START_ADDRESS_SNES + EVENT_CODE_START - len(trigger_call)).to_bytes(3, "little")
    src = [
        # wait until not executing any other events
        asm.LDA(0xe5, asm.DIR),
        asm.BNE("NO_TRIGGER"),
        asm.LDA(0xe6, asm.DIR),
        asm.BNE("NO_TRIGGER"),
        asm.LDA(0xca, asm.IMM8),
        asm.CMP(0xe7, asm.DIR),
        asm.BNE("NO_TRIGGER"),

        # wait for map name
        asm.LDA(0x08, asm.IMM8),
        asm.BIT(0x0745, asm.ABS),
        asm.BNE("NO_TRIGGER"),

        # check/reset trigger byte
        asm.LDA(trigger_addr, asm.ABS),
        asm.BEQ("NO_TRIGGER"),
        asm.DEC(trigger_addr, asm.ABS),
        asm.LDA(trigger_addr, asm.ABS),
        asm.ASL(),
        asm.CLC(),
        asm.ADC(trigger_addr, asm.ABS),
        asm.STZ(trigger_addr, asm.ABS),
        asm.TAX(),

        # return to ca0000 from trigger_event
        asm.LDA(return_addr[0], asm.IMM8),
        asm.STA(0xe5, asm.DIR),
        asm.LDA(return_addr[1], asm.IMM8),
        asm.STA(0xe6, asm.DIR),
        asm.LDA(return_addr[2], asm.IMM8),
        asm.STA(0xe7, asm.DIR),

        # call trigger_event
        asm.LDA(trigger_event_table + 2, asm.ABS_X),
        asm.STA(0xed, asm.DIR),
        asm.LDA(trigger_event_table + 1, asm.ABS_X),
        asm.STA(0xec, asm.DIR),
        asm.LDA(trigger_event_table + 0, asm.ABS_X),
        asm.STA(0xeb, asm.DIR),
        asm.LDA(trigger_call.opcode, asm.IMM8),
        asm.STA(0xea, asm.DIR),
        asm.RTS(),

        "NO_TRIGGER",
        Read(0x009b37, 0x009b3a),
        asm.RTS(),
    ]
    space = Write(Bank.C0, src, "check trigger event byte and inject if set")
    trigger_event_check = space.start_address

    space = Reserve(0x009b37, 0x009b3a, "call trigger event check", asm.NOP())
    space.write(
        asm.JSR(trigger_event_check, asm.ABS),
    )