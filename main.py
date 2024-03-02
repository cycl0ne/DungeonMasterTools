from uncompress_dung import LoadDungeon

if __name__ == "__main__":
    dungeon = LoadDungeon()
    load = dungeon.load("DUNGEON.DAT")
    if load is not None:
        dungeon._dbg_print_dungeon(1)
    