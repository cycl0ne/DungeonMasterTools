# DungeonMasterTools
DungeonMasterTools is a collection of Tools in Python for the Amiga/PC/Atari ST Game:

* uncompress_dung.py - Will load and extract the Data in the Dungeon.dat file (At the moment only Big Endian!)
* more coming soon

use the class in your code like shown in main.py. After calling load(filename), you get a dictionary (not finished), but you can also access all data from the class itself:

* hdr -> Header of the File 
* maps[] -> Maps_Info Structure 
* thinglist[] -> List of all Doors, Creatures, Items, Sensors, ...
* tile_data -> binary data of the dungeon
* chksum -> Checksum of the file (if existent)

for more info see: 
http://dmweb.free.fr/?q=node/217

example:
```
dungeon = LoadDungeon()
dungeon.load("Dungeon.dat")
print(dungeon.hdr['OrnamentRandomSeed'])
print(dungeon.maps[0]['Difficulty'])
```

---
When you run: py main.py a debug of Level 1 is done:

```
Normal Dungeon.dat: extracting Data
DungeonColumnCount 412
Count SFTC:  3364
Count TextDataWordCount:  3498
Starting ThingCount (16):  7954
Reading Tilebuffer:  12366
Ending Data:  33442 Len of Buffer 33442  read.
  ----------------
Map at Level 1:
  RawMapDataByteOffset: 376
  OffsetMapX: 0, OffsetMapY: 14
  Width: 31, Height: 31, Level: 1
  RandomFloorOrnamentCount: 2
  FloorOrnamentCount: 3
  RandomWallOrnamentCount: 3
  WallOrnamentCount: 12
  Difficulty: 1
  CreatureTypeCount: 2
  DoorOrnamentCount: 3
  DoorSet1: 1, DoorSet0: 0
  WallSet: 0, FloorSet: 0
  ----------------
start_index: 376 len: 12366
w  32 h  32
1 4 1 1 1 1 1 1   1 1 4 1 1   1 1 1         1     1 1 4 1   1 1 
1     3     4     1       1 1 1 1 1 4 4 1   1 1 1 1     1   1 5 
1 1         1   1 1 1 1       1 1 1     1   1 1       1 1 1     
  4         1   1 1   1   1 1           1   1   1 1 1     1 5   
  1                   1   1 1 1 1 1 1 1 5   4   1   1 4 1 1     
1 1   1 4 1 4 1 1   1 1   1   1 1 1 1     1 1   2               
1     1             1           1       1 1     1 1           1 
1 1 1 1   1 1 1     1   1 1 1   1 1 1 1 1 1       1   1 1 1 1 1 
1     1   1   2     1   1 1 1               1 1 1 1   1   1   4 
  1 1 1   4   1   1 1   1         1 1 1 1 1 1         1   1   1 
  1       1       1   1 1   1 1   1         1 1 1 1 1 1   1   1 
1 1 1 1 1 1   1   1   1 1 1 1 1   1   1   1       4       1     
1             1 1 1   4               1   1 1 1   1 1 1   1 1   
1 1 1 4 1 1 4 1       1         1 1 1 1 1 1   1 1     1         
  1                 1 1   1 1   1 1 1 1 1       1 1   1 1 1 1 1 
  1 1 1 1 4 1 1 1 1 1     2     1 1 1 1 1   1     1       1   1 
    1 1 1               1 5     1 1 1 1 1   1 1 1 1 1 1 1 1   1 
            1 1 1 1     1       1 1 1 1 1         1 1 1 1 1   1 
1 1 1 1 1 1 1     1     1   1       4       1                   
1 1 1 1 1 1 1   1 1     1   1 1 1 1 1 1 1 1 1         1 1 1 1   
1   1 1 1 1 1   1   1 1 1           4           1 1 1 1 1 1 1 5 
1 1 1         1 1   1 1 1   1 1 1   5 1 1 1 4 1 1 1 1 1 1     1 
  1           4     1       1   1 1 1   1                     1 
  1 1 1   1 1 1 1   1 1 1 1 1                     1   1 1 1 1 1 
      1   1 1 1 1                     1 1 1   1 1 1   1   1     
      1       1 1 1 1 1   1 1 1       1   1   1   1 1 1   1 1   
      1     3   1 1   1 1 1   1 1 4 1 1   1   1                 
      1     1     1 1   1       4         1   1 1 1 1 1 1 4 1   
      1     1     1 1   1 1 1   1       1 1 1     1         1   
      1     1 1 1       1 1 6           1 1 1 1 1 1 5 1 1 1 1   
    1 1 1 1     1       1   1 1         1 1 1                   
    1 1   1 1 1 1           1 1 
```

Many Thanks to ChristopheF & Sphenx
