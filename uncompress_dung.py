import struct

class BufferReader:
    def __init__(self, buffer):
        self.buffer = buffer
        self.position = 0

    def read_data(self, size):
        # Check if the request exceeds the buffer's bounds
        if self.position + size > len(self.buffer):
            raise ValueError("Attempt to read beyond buffer length")
        
        # Read `size` bytes from the current position
        data = self.buffer[self.position:self.position + size]
        
        # Update the position
        self.position += size
        return data

#
# Class LoadDungeon to load and extract the Data of a Dungeon Master (Amiga, Atari,...) (Big Endian) Data File
#

class LoadDungeon:
    def decompress_dungeon(self, compressed_buffer, decompressed_byte_count):
        # Initialize variables
        byte_count = 0
        bit_buffer = 0
        bits_in_buffer_count = 0
        
        # Extract the most and less common bytes from the beginning of the compressed buffer
        most_common_bytes = compressed_buffer[:4]
        less_common_bytes = compressed_buffer[4:20]
        
        # Adjust the compressed buffer to skip the extracted part
        compressed_buffer = compressed_buffer[20:]
        
        # Prepare the decompressed buffer
        decompressed_buffer = bytearray(decompressed_byte_count)
        
        # Iterator for the compressed buffer
        buffer_iterator = iter(compressed_buffer)
        
        def get_next_byte():
            """Fetch the next byte from the compressed buffer."""
            try:
                return next(buffer_iterator)
            except StopIteration:
                print("No more bytes filling with 0")
                return 0
        
        while byte_count < decompressed_byte_count:
            # Ensure the bit buffer has at least 24 bits
            while bits_in_buffer_count <= 24:
                bit_buffer = (bit_buffer << 8) | get_next_byte()
                bits_in_buffer_count += 8
            
            # Decode based on the leading 2 bits
            leading_bits = (bit_buffer >> (bits_in_buffer_count - 2)) & 3
            if leading_bits in (0, 1):
                # Decode one of the most common bytes
                index = (bit_buffer >> (bits_in_buffer_count - 3)) & 3
                decompressed_buffer[byte_count] = most_common_bytes[index]
                bits_in_buffer_count -= 3
            elif leading_bits == 2:
                # Decode one of the less common bytes
                index = (bit_buffer >> (bits_in_buffer_count - 6)) & 15
                decompressed_buffer[byte_count] = less_common_bytes[index]
                bits_in_buffer_count -= 6
            elif leading_bits == 3:
                # Decode a byte directly
                decompressed_buffer[byte_count] = (bit_buffer >> (bits_in_buffer_count - 10)) & 255
                bits_in_buffer_count -= 10
            
            byte_count += 1
        
        return decompressed_buffer
    
    def _unpack_dungeon_header(self,data):
        format_string = '>HHBxHHH' + ('H' * 16)
        expected_size = struct.calcsize(format_string)
        if len(data) < expected_size:
            print((f"Data is too short, expected at least {expected_size} bytes, got {len(data)}"))
            raise ValueError(f"Data is too short, expected at least {expected_size} bytes, got {len(data)}")
    
        # Unpack the data
        unpacked_data = struct.unpack(format_string, data)
        
        # Extract fields from the unpacked data
        header = {
            'OrnamentRandomSeed': unpacked_data[0],
            'RawMapDataByteCount': unpacked_data[1],
            'MapCount': unpacked_data[2],
            # Skip the Unreferenced byte since it's padding and not explicitly unpacked
            'TextDataWordCount': unpacked_data[3],
            'InitialPartyLocation': unpacked_data[4],
            'SquareFirstThingCount': unpacked_data[5],
            'ThingCount': unpacked_data[6:]  # This extracts all 16 ThingCount values
        }
    
        return header
    
    def decode_doorlist(self, bytestream):
        doors = []
        # Assuming each DOOR is 4 bytes in total: 2 bytes for THING and 2 for the bit fields
        door_size = 4  # Adjust if THING Next size differs

        # Calculate how many DOOR structures are in the bytestream
        num_doors = len(bytestream) // door_size

        for i in range(num_doors):
            # Extract 4 bytes for each DOOR
            door_data = bytestream[i * door_size:(i + 1) * door_size]
            # Unpack THING Next (2 bytes) and the next 2 bytes containing the bit fields
            next_thing, bit_fields = struct.unpack('>HH', door_data)  # Adjust '>' for byte order
            
            # Manually decode bit fields from the second 2 bytes
            unreferenced = (bit_fields >> 9) & 0x7F
            melee_destructible = (bit_fields >> 8) & 0x1
            magic_destructible = (bit_fields >> 7) & 0x1
            button = (bit_fields >> 6) & 0x1
            vertical = (bit_fields >> 5) & 0x1
            ornament_ordinal = (bit_fields >> 1) & 0xF
            type_ = bit_fields & 0x1

            # Create a dictionary for each DOOR and append to the list
            door_info = {
                'Next': next_thing,
                'Unreferenced': unreferenced,
                'MeleeDestructible': melee_destructible,
                'MagicDestructible': magic_destructible,
                'Button': button,
                'Vertical': vertical,
                'OrnamentOrdinal': ornament_ordinal,
                'Type': type_,
            }
            doors.append(door_info)
        return doors

    def decode_teleporterlist(self, data):
        teleporters = []
        teleporter_size = 6  # Total bytes per TELEPORTER instance
        
        num_teleporters = len(data) // teleporter_size
        
        for i in range(num_teleporters):
            # Extract bytes for each TELEPORTER
            teleporter_data = data[i * teleporter_size:(i + 1) * teleporter_size]
            # Unpack THING Next and the next 2 bytes containing the first set of bit fields
            next_thing, bit_fields, target_map_index, unreferenced = struct.unpack('>HHBB', teleporter_data)
            
            # Decode bit fields
            audible = (bit_fields >> 15) & 0x1
            scope = (bit_fields >> 13) & 0x3
            absolute_rotation = (bit_fields >> 12) & 0x1
            rotation = (bit_fields >> 10) & 0x3
            target_map_y = (bit_fields >> 5) & 0x1F
            target_map_x = bit_fields & 0x1F
            
            # Create a dictionary for each TELEPORTER and append to the list
            teleporter_info = {
                'Next': next_thing,
                'Audible': audible,
                'Scope': scope,
                'AbsoluteRotation': absolute_rotation,
                'Rotation': rotation,
                'TargetMapY': target_map_y,
                'TargetMapX': target_map_x,
                'TargetMapIndex': target_map_index,
                'Unreferenced': unreferenced,
            }
            teleporters.append(teleporter_info)
        return teleporters

    def decode_textstringlist(self, data):
        textstrings = []
        textstring_size = 4  # 2 bytes for THING Next + 2 bytes for the bitfield

        num_textstrings = len(data) // textstring_size
        
        for i in range(num_textstrings):
            # Extract bytes for each TEXTSTRING
            textstring_data = data[i * textstring_size:(i + 1) * textstring_size]
            # Unpack THING Next and the next 2 bytes containing the bit fields
            next_thing, bit_fields = struct.unpack('>HH', textstring_data)
            
            # Decode bit fields
            text_data_word_offset = (bit_fields >> 3) & 0x1FFF  # 13 bits for TextDataWordOffset
            unreferenced = (bit_fields >> 1) & 0x3  # 2 bits for Unreferenced
            visible = bit_fields & 0x1  # 1 bit for Visible
            
            # Create a dictionary for each TEXTSTRING and append to the list
            textstring_info = {
                'Next': next_thing,
                'TextDataWordOffset': text_data_word_offset,
                'Unreferenced': unreferenced,
                'Visible': visible,
            }
            textstrings.append(textstring_info)
        
        return textstrings
    
    def decode_sensorlist(self, data):
        sensors = []
        sensor_size = 8  # Assuming the size is 8 bytes for both Remote and Local
        
        for i in range(0, len(data), sensor_size):
            sensor_data = data[i:i + sensor_size]
            # Unpack the shared initial part
            next_thing, type_data, bit_fields1 = struct.unpack_from('>HHH', sensor_data, 0)
            
            # Extract common fields
            ornament_ordinal = (bit_fields1 >> 12) & 0xF
            local_effect = (bit_fields1 >> 11) & 0x1
            value = (bit_fields1 >> 7) & 0xF
            audible = (bit_fields1 >> 6) & 0x1
            revert_effect = (bit_fields1 >> 5) & 0x1
            effect = (bit_fields1 >> 3) & 0x3
            once_only = (bit_fields1 >> 2) & 0x1
            a_unreferenced = bit_fields1 & 0x3
            
            # Now, decide if it's Remote or Local based on the LocalEffect bit or other logic
            if local_effect:
                # Decode as Local
                # Unpack fields specific to Local
                bit_fields2 = struct.unpack_from('>H', sensor_data, 6)[0]
                multiple = bit_fields2 >> 4
                b_unreferenced = bit_fields2 & 0xF
                
                sensor_info = {
                    'Next': next_thing,
                    'Type_Data': type_data,
                    'OrnamentOrdinal': ornament_ordinal,
                    'LocalEffect': local_effect,
                    'Value': value,
                    'Audible': audible,
                    'RevertEffect': revert_effect,
                    'Effect': effect,
                    'OnceOnly': once_only,
                    'aUnreferenced': a_unreferenced,
                    'Multiple': multiple,
                    'bUnreferenced': b_unreferenced,
                }
            else:
                # Decode as Remote
                # Assuming Remote has additional fields after the shared ones
                bit_fields2, bit_fields3 = struct.unpack_from('>HH', sensor_data, 4)
                target_map_y = (bit_fields2 >> 11) & 0x1F
                target_map_x = (bit_fields2 >> 6) & 0x1F
                target_cell = bit_fields2 & 0x3
                b_unreferenced = bit_fields3 & 0xF
                
                sensor_info = {
                    'Next': next_thing,
                    'Type_Data': type_data,
                    'OrnamentOrdinal': ornament_ordinal,
                    'LocalEffect': local_effect,
                    'Value': value,
                    'Audible': audible,
                    'RevertEffect': revert_effect,
                    'Effect': effect,
                    'OnceOnly': once_only,
                    'aUnreferenced': a_unreferenced,
                    'TargetMapY': target_map_y,
                    'TargetMapX': target_map_x,
                    'TargetCell': target_cell,
                    'bUnreferenced': b_unreferenced,
                }
                
            sensors.append(sensor_info)

        return sensors
    
    def decode_creaturelist(self, data):
        groups = []
        # Calculate group size: THING Next (2 bytes) + THING Slot (2 bytes) + Type (1 byte) +
        # Cells (1 byte) + Health[4] (4 * 2 bytes) + bit field (2 bytes)
        group_size = 2 + 2 + 1 + 1 + (4 * 2) + 2  # Adjust based on actual struct size
        
        num_groups = len(data) // group_size
        
        for i in range(num_groups):
            # Extract bytes for each GROUP
            group_data = data[i * group_size:(i + 1) * group_size]
            # Unpack THING Next, Slot, Type, Cells, Health, and then the bit field
            unpacked_data = struct.unpack('>HHBBHHHHH', group_data)
            next_thing, slot, type_, cells, health1, health2, health3, health4, bit_fields = unpacked_data
            
            # Decode bit fields
            c_unreferenced = (bit_fields >> 11) & 0x1F
            do_not_discard = (bit_fields >> 10) & 0x1
            direction = (bit_fields >> 8) & 0x3
            b_unreferenced = (bit_fields >> 7) & 0x1
            count = (bit_fields >> 5) & 0x3
            a_unreferenced = (bit_fields >> 4) & 0x1
            behavior = bit_fields & 0xF
            
            # Create a dictionary for each GROUP and append to the list
            group_info = {
                'Next': next_thing,
                'Slot': slot,
                'Type': type_,
                'Cells': cells,
                'Health': [health1, health2, health3, health4],
                'cUnreferenced': c_unreferenced,
                'DoNotDiscard': do_not_discard,
                'Direction': direction,
                'bUnreferenced': b_unreferenced,
                'Count': count,
                'aUnreferenced': a_unreferenced,
                'Behavior': behavior,
            }
            groups.append(group_info)            
        return groups

    def decode_weaponlist(self, data):
        weapons = []
        weapon_size = 4  # 2 bytes for THING Next + 2 bytes for the bitfield
        
        for i in range(0, len(data), weapon_size):
            weapon_data = data[i:i + weapon_size]
            next_thing, bit_fields = struct.unpack('>HH', weapon_data)
            
            weapon_info = {
                'Next': next_thing,
                'Lit': (bit_fields >> 15) & 0x1,
                'Broken': (bit_fields >> 14) & 0x1,
                'ChargeCount': (bit_fields >> 10) & 0xF,
                'Poisoned': (bit_fields >> 9) & 0x1,
                'Cursed': (bit_fields >> 8) & 0x1,
                'DoNotDiscard': (bit_fields >> 7) & 0x1,
                'Type': bit_fields & 0x7F,
            }
            weapons.append(weapon_info)
        
        return weapons

    def decode_armorlist(self, data):
        armors = []
        armor_size = 4  # 2 bytes for THING Next + 2 bytes for the bitfield
        
        for i in range(0, len(data), armor_size):
            armor_data = data[i:i + armor_size]
            next_thing, bit_fields = struct.unpack('>HH', armor_data)
            
            armor_info = {
                'Next': next_thing,
                'Unreferenced': (bit_fields >> 14) & 0x3,
                'Broken': (bit_fields >> 13) & 0x1,
                'ChargeCount': (bit_fields >> 9) & 0xF,
                'Cursed': (bit_fields >> 8) & 0x1,
                'DoNotDiscard': (bit_fields >> 7) & 0x1,
                'Type': bit_fields & 0x7F,
            }
            armors.append(armor_info)
        
        return armors

    def decode_scrolllist(self, data):
        scrolls = []
        scroll_size = 4  # 2 bytes for THING Next + 2 bytes for the bitfield

        for i in range(0, len(data), scroll_size):
            scroll_data = data[i:i + scroll_size]
            next_thing, bit_fields = struct.unpack('>HH', scroll_data)

            scroll_info = {
                'Next': next_thing,
                'Closed': (bit_fields >> 10) & 0x3F,  # 6 bits for Closed
                'TextStringThingIndex': bit_fields & 0x3FF,  # 10 bits for TextStringThingIndex
            }
            scrolls.append(scroll_info)

        return scrolls

    def decode_potionlist(self, data):
        potions = []
        potion_size = 4  # 2 bytes for THING Next + 2 bytes for the bitfield

        for i in range(0, len(data), potion_size):
            potion_data = data[i:i + potion_size]
            next_thing, bit_fields = struct.unpack('>HH', potion_data)

            potion_info = {
                'Next': next_thing,
                'DoNotDiscard': (bit_fields >> 15) & 0x1,  # 1 bit for DoNotDiscard
                'Type': (bit_fields >> 8) & 0x7F,  # 7 bits for Type
                'Power': bit_fields & 0xFF,  # 8 bits for Power
            }
            potions.append(potion_info)

        return potions

    def decode_containerlist(self, data):
        containers = []
        container_size = 8  # 2 bytes for THING Next + 2 bytes for THING Slot + 2 bytes for bitfields + 2 bytes for cUnreferenced

        for i in range(0, len(data), container_size):
            container_data = data[i:i + container_size]
            next_thing, slot, bit_fields, c_unreferenced = struct.unpack('>HHHH', container_data)

            container_info = {
                'Next': next_thing,
                'Slot': slot,
                'Type': (bit_fields >> 1) & 0x3,  # 2 bits for Type
                'aUnreferenced': (bit_fields >> 15) & 0x1,  # 1 bit for aUnreferenced
                'bUnreferenced': bit_fields & 0x1FFF,  # 13 bits for bUnreferenced, masked out Type and aUnreferenced
                'cUnreferenced': c_unreferenced,  # Directly taken from the last 2 bytes
            }
            containers.append(container_info)

        return containers

    def decode_junklist(self, data):
        junk_items = []
        junk_size = 4  # 2 bytes for THING Next + 2 bytes for the bitfield

        for i in range(0, len(data), junk_size):
            junk_data = data[i:i + junk_size]
            next_thing, bit_fields = struct.unpack('>HH', junk_data)

            junk_info = {
                'Next': next_thing,
                'ChargeCount': (bit_fields >> 14) & 0x3,
                'Unreferenced': (bit_fields >> 9) & 0x1F,
                'Cursed': (bit_fields >> 8) & 0x1,
                'DoNotDiscard': (bit_fields >> 7) & 0x1,
                'Type': bit_fields & 0x7F,
            }
            junk_items.append(junk_info)

        return junk_items

    def decode_projectilelist(self, data):
        projectiles = []
        projectile_size = 8  # 2 bytes for THING Next + 2 bytes for THING Slot + 1 byte for KineticEnergy + 1 byte for Attack + 2 bytes for EventIndex

        for i in range(0, len(data), projectile_size):
            projectile_data = data[i:i + projectile_size]
            next_thing, slot, kinetic_energy, attack, event_index = struct.unpack('>HHBBH', projectile_data)

            projectile_info = {
                'Next': next_thing,
                'Slot': slot,
                'KineticEnergy': kinetic_energy,
                'Attack': attack,
                'EventIndex': event_index,
            }
            projectiles.append(projectile_info)

        return projectiles

    def decode_explosionlist(self, data):
        explosions = []
        explosion_size = 4  # 2 bytes for THING Next + 2 bytes for the bitfield

        for i in range(0, len(data), explosion_size):
            explosion_data = data[i:i + explosion_size]
            next_thing, bit_fields = struct.unpack('>HH', explosion_data)

            explosion_info = {
                'Next': next_thing,
                'Attack': bit_fields >> 8,
                'Centered': (bit_fields >> 7) & 0x1,
                'Type': bit_fields & 0x7F,
            }
            explosions.append(explosion_info)

        return explosions

    def extract_dungeon_dat(self, buffer):
        dungeon = BufferReader(buffer)       
        data = dungeon.read_data(44)
        self.hdr = self._unpack_dungeon_header(data)
        # print(hdr)
        
        self.maps = []
        self.mapsinfo = {}
        for i in range(self.hdr['MapCount']):
            data = dungeon.read_data(16)
            map_def = struct.unpack('>HHHBBHHHH', data)
            map_info = {
                'RawMapDataByteOffset': map_def[0],
                'aUnreferenced': map_def[1], 
                'bUnreferenced':map_def[2], 
                'OffsetMapX':map_def[3], 
                'OffsetMapY':map_def[4], 
                'Height':  map_def[5] >> 11,
                'Width':  (map_def[5] >> 6) &0x1f,
                'Level':  (map_def[5] ) &0x3f,
                'RandomFloorOrnamentCount': (map_def[6] >> 12),
                'FloorOrnamentCount':       (map_def[6] >> 8) &0xf,
                'RandomWallOrnamentCount':  (map_def[6] >> 4) &0xf,
                'WallOrnamentCount':        (map_def[6])&0xf,
                'Difficulty':               (map_def[7] >> 12),
                'Unreferenced':             (map_def[7] >> 8) &0xf,
                'CreatureTypeCount':        (map_def[7] >> 4) &0xf,
                'DoorOrnamentCount':        (map_def[7])&0xf,
                'DoorSet1':                 (map_def[8] >> 12),
                'DoorSet0':                 (map_def[8] >> 8) &0xf,
                'WallSet':                  (map_def[8] >> 4) &0xf,
                'FloorSet':                 (map_def[8])&0xf,                
                'rawWidthHeightLevel':map_def[5], 
                'rawOrnamentCnt':map_def[6], 
                'rawCreatureDoorExp': map_def[7], 
                'rawGfxSets': map_def[8], 
            }
            
            level_key = str(map_info['Level'])
            self.mapsinfo[level_key] = map_info
            self.maps.append(map_info)  
            # print("Level:", map_info['Level'], "-w-", map_info['Width'],"-h-",map_info['Height'],"-rmdbo:",map_info['RawMapDataByteOffset']) 
        
        
        # Calculate DungeonColumnCount
        col = 0
        for i in range(self.hdr['MapCount']):
            # print("Level",maps[i]['Level']," Width ",maps[i]['Width'],"+1")
            col += self.maps[i]['Width']+1

        print("DungeonColumnCount", col)
        data = dungeon.read_data(col*2)
        print("Count SFTC: ",self.hdr['SquareFirstThingCount']*2)
        data = dungeon.read_data(self.hdr['SquareFirstThingCount']*2)
        print("Count TextDataWordCount: ",self.hdr['TextDataWordCount']*2)
        data = dungeon.read_data(self.hdr['TextDataWordCount']*2)
        # print("hdr", hdr)
        print("Starting ThingCount (16): ", dungeon.position)
        data = dungeon.read_data(self.hdr['ThingCount'][0]*4)  #         4,   /* Door */
        self.doorlist = self.decode_doorlist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][1]*6)  #         6,   /* Teleporter */
        self.teleporterlist = self.decode_teleporterlist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][2]*4)  #         4,   /* Text String */
        self.textstringlist = self.decode_textstringlist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][3]*8)  #         8,   /* Sensor */
        self.sensorlist = self.decode_sensorlist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][4]*16) #         16,  /* Creature (Group) */
        self.creaturelist = self.decode_creaturelist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][5]*4)  #         4,   /* Weapon */
        self.weaponlist = self.decode_weaponlist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][6]*4)  #         4,   /* Armour */
        self.armorlist = self.decode_armorlist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][7]*4)  #         4,   /* Scroll */
        self.scrolllist = self.decode_scrolllist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][8]*4)  #         4,   /* Potion */
        self.potionlist = self.decode_potionlist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][9]*8)  #         8,   /* Container */
        self.containerlist = self.decode_containerlist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][10]*4) #         4,   /* Junk */
        self.junklist = self.decode_junklist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][11]*0) #         0,   /* Unused */
        data = dungeon.read_data(self.hdr['ThingCount'][12]*0) #         0,   /* Unused */
        data = dungeon.read_data(self.hdr['ThingCount'][13]*0) #         0,   /* Unused */
        data = dungeon.read_data(self.hdr['ThingCount'][14]*8) #         8,   /* Projectile */
        self.projectilelist = self.decode_projectilelist(data)
        data = dungeon.read_data(self.hdr['ThingCount'][15]*4) #         4    /* Explosion */
        self.explosionlist = self.decode_explosionlist(data)
        
        self.thinglist = []
        self.thinglist.append(self.doorlist)
        self.thinglist.append(self.teleporterlist)
        self.thinglist.append(self.textstringlist)
        self.thinglist.append(self.sensorlist)
        self.thinglist.append(self.creaturelist)
        self.thinglist.append(self.weaponlist)
        self.thinglist.append(self.armorlist)
        self.thinglist.append(self.scrolllist)
        self.thinglist.append(self.potionlist)
        self.thinglist.append(self.containerlist)
        self.thinglist.append(self.junklist)
        self.thinglist.append(None)
        self.thinglist.append(None)
        self.thinglist.append(None)
        self.thinglist.append(self.projectilelist)
        self.thinglist.append(self.explosionlist)
        
        print("Reading Tilebuffer: ", self.hdr['RawMapDataByteCount'])
        self.tile_data = dungeon.read_data(self.hdr['RawMapDataByteCount'])

        if (len(buffer)- dungeon.position) > 0:
            print("Reading Chcksum: 2")
            self.chksum    = dungeon.read_data(2)
            
        print("Ending Data: ", dungeon.position, "Len of Buffer", len(buffer), " read.")
        dungeon_dat = {
            'header':       self.hdr,
            'maps_info':    self.mapsinfo,
            'thing_count':  self.thinglist
            # 'tile_data': self.tile_data,
        }
        return dungeon_dat

    def _dbg_print_dungeon(self, level):
        map_info = self.maps[level]
        txtmap= ""
        print(f"\nMap at Level {map_info['Level']} ----------------")
        print(f"  RawMapDataByteOffset: {map_info['RawMapDataByteOffset']}")
        # print(f"  aUnreferenced: {map_info['aUnreferenced']}")
        # print(f"  bUnreferenced: {map_info['bUnreferenced']}")
        print(f"  OffsetMapX: {map_info['OffsetMapX']}, OffsetMapY: {map_info['OffsetMapY']}")
        print(f"  Width: {map_info['Width']}, Height: {map_info['Height']}, Level: {map_info['Level']}")
        print(f"  RandomFloorOrnamentCount: {map_info['RandomFloorOrnamentCount']}")
        print(f"  FloorOrnamentCount: {map_info['FloorOrnamentCount']}")
        print(f"  RandomWallOrnamentCount: {map_info['RandomWallOrnamentCount']}")
        print(f"  WallOrnamentCount: {map_info['WallOrnamentCount']}")
        print(f"  Difficulty: {map_info['Difficulty']}")
        # print(f"  Unreferenced: {map_info['Unreferenced']}")
        print(f"  CreatureTypeCount: {map_info['CreatureTypeCount']}")
        print(f"  DoorOrnamentCount: {map_info['DoorOrnamentCount']}")
        print(f"  DoorSet1: {map_info['DoorSet1']}, DoorSet0: {map_info['DoorSet0']}")
        print(f"  WallSet: {map_info['WallSet']}, FloorSet: {map_info['FloorSet']}")
        print("\nCreatures/Wall/Floor/Doors used ----------------")

        start_index = map_info['RawMapDataByteOffset']

        # print("start_index:", start_index, "len:", len(self.tile_data)) 
        array = [[0 for _ in range(map_info['Width']+1)] for _ in range(map_info['Height']+1)]

        w = (map_info['Width']+1)
        h = (map_info['Height']+1)
        # print('w ', w, "h ",h)
        for x in range(w):
            for y in range(h):
                array[y][x] = self.tile_data[start_index + y + (x * h)]

        txtmap +="\n  "        
        for y in range(map_info['Height']+1):
            for x in range(map_info['Width']+1):
                type = (array[y][x] >>5) & 0x7
                if type == 0:
                    txtmap += "  "
                else:
                    txtmap += str(type)+" "
            txtmap +="\n  "
        creaturetypecount  = map_info['CreatureTypeCount']
        wallornamentcount  = map_info['WallOrnamentCount']
        floorornamentcount = map_info['FloorOrnamentCount']
        doordecocount      = map_info['DoorOrnamentCount']
        map_info2 = self.maps[level+1]
        map_info2['RawMapDataByteOffset']
        buffer = self.tile_data[(start_index+(w*h)):]
        # print("Check: Starting after Map:", start_index+(w*h), "reading until",
        #       (start_index+(w*h))+creaturetypecount+wallornamentcount+floorornamentcount+doordecocount, 
        #       " next map: ", map_info2['RawMapDataByteOffset'])

        txt ="  Creature: "
        for c in range(creaturetypecount):
            txt += str(buffer[c])+", "
        txt+="\n  WallOrnate: "
        buffer = self.tile_data[(start_index+(w*h))+creaturetypecount:]
        for c in range(wallornamentcount):
            txt += str(buffer[c])+", "
        txt+="\n  FloorOrnate: "
        buffer = self.tile_data[(start_index+(w*h))+creaturetypecount+wallornamentcount:]
        for c in range(floorornamentcount):
            txt += str(buffer[c])+", "
        txt+="\n  DoorDeco: "
        buffer = self.tile_data[(start_index+(w*h))+creaturetypecount+wallornamentcount+floorornamentcount:]
        for c in range(doordecocount):
            txt += str(buffer[c])+", "
        txt+="\n"
        print(txt)               
        print("MapData ----------------")
        print(txtmap)

    def load(self, filename):
        with open(filename, 'rb') as file:
            buffer = file.read()
            header_format = '>HlH'
            header_size = struct.calcsize(header_format)
            header_data = buffer[:header_size]
            signature, decompressed_byte_count, dungeon_id = struct.unpack(header_format, header_data)
            if signature == 0x8104:
                print("Compressed Dungeon.dat: uncompressing")
                buffer = self.decompress_dungeon(buffer[8:], decompressed_byte_count)
                return self.extract_dungeon_dat(buffer)
            elif signature == 0x0481:
                print("Compressed Dungeon.dat: Little Endian not supported at the moment.")
            elif buffer[1] == 0x00:
                print("Normal Dungeon.dat: Little Endian not supported at the moment.")
            elif buffer[1] == 0x63:
                print("Normal Dungeon.dat: extracting Data")
                return self.extract_dungeon_dat(buffer)
            else:
                print("Not a recognized Dungeon.dat file.")        
        return None
