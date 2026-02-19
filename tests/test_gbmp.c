#include "../src/SDAdapter/fileStream.h"
#include <stdio.h>
#include <string.h>

const char *FILE_PATH = "../gbmp/game.bin";

void read_next_actor(FILE *file);
void read_next_world_tile_metadata(FILE *file);


void read_file_metadata(FILE *file) {
    printf("\n==================== File MetaData ====================\n");
    FileMetaData metaData;
    if (fread(&metaData, sizeof(FileMetaData), 1, file) != 1) {
        perror("Failed to read FileMetaData");
        return;
    }

    printf("File Version: %u\n", metaData.frame.fileVersion);
    printf("Control Flags: %u\n", metaData.frame.controlFlags);
    printf("Reserved: %u\n", metaData.frame.reserved);
    printf("File Length: %u bytes\n", metaData.frame.fileLen);
}

void read_color_register(FILE *file) {
    printf("\n==================== Color Register ====================\n");
    ColorRegister colorRegister;
    if (fread(&colorRegister, sizeof(ColorRegister), 1, file) != 1) {
        perror("Failed to read ColorRegister");
        return;
    }
    printf("Color Mask ID %d: (%u, %u, %u)\n",
        colorRegister.frame.colorMask.channels.id, 
        colorRegister.frame.colorMask.channels.red,
        colorRegister.frame.colorMask.channels.green,
        colorRegister.frame.colorMask.channels.blue);

    for (int i = 0; i < 15; i++) {
        printf("Color ID %d: (%u, %u, %u)\n", 
            colorRegister.frame.colors[i].channels.id,
            colorRegister.frame.colors[i].channels.red,
            colorRegister.frame.colors[i].channels.green,
            colorRegister.frame.colors[i].channels.blue);
    }
}

void read_actors_header(FILE *file) {
    printf("\n==================== Actors Header ====================\n");
    FrameActorsHeader actorsHeader;
    if (fread(&actorsHeader, sizeof(FrameActorsHeader), 1, file) != 1) {
        perror("Failed to read FrameActorsHeader");
        return;
    }
    printf("Number of Actors: %u\n", actorsHeader.nbOfActors);
    printf("Player Actor ID: %u\n", actorsHeader.playerActorId);
    printf("Life Bar: %u\n", actorsHeader.lifeBar);
    printf("Reserved: %u\n", actorsHeader.reserved);

    printf("\n==================== Actor MetaData ====================\n");
    for (int i = 0; i < actorsHeader.nbOfActors; i++) {
        read_next_actor(file);
    }
}

//     if (fread(&worldMetaData, sizeof(WorldMetaData), 1, file) != 1) {
//         perror("Failed to read WorldMetaData");
//        }
//     printf("Length: %u bytes\n", worldMetaData.frame.len);
// }

void read_next_actor(FILE *file) {
    FrameActorMetaData actorMetaData;
    if (fread(&actorMetaData, sizeof(FrameActorMetaData), 1, file) != 1) {
        perror("Failed to read FrameActorMetaData");
        return;
    }
    printf("Actor ID: %u\n", actorMetaData.id);
    printf("Number of Sprites: %u\n", actorMetaData.nbOfSprite);
    printf("Length: %u bytes\n", actorMetaData.len);

    if (fseek(file, actorMetaData.len, SEEK_CUR) != 0) {
        perror("Failed to seek past actor sprite data");
    }
}


void read_world_tiles_header(FILE *file) {
    printf("\n==================== World Tiles Header ====================\n");
    FrameWorldTilesHeader tilesHeader;
    if (fread(&tilesHeader, sizeof(FrameWorldTilesHeader), 1, file) != 1) {
        perror("Failed to read FrameWorldTilesHeader");
        return;
    }
    printf("Number of Tiles: %u\n", tilesHeader.nbOfTiles);
    printf("Length: %u bytes\n", tilesHeader.len);

    printf("\n==================== World Tile MetaData ====================\n");
    for (int i = 0; i < tilesHeader.nbOfTiles; i++) {
        read_next_world_tile_metadata(file);
    }
}

void read_next_world_tile_metadata(FILE *file) {
    

    FrameWorldTileMetaData tileMetaData;
    if (fread(&tileMetaData, sizeof(FrameWorldTileMetaData), 1, file) != 1) {
        perror("Failed to read FrameWorldTileMetaData");
        return;
    }


    printf("Tile ID: %u  collision=%u event=%u type=%u len=%u bytes\n",
        tileMetaData.id, tileMetaData.collision, tileMetaData.event,
        tileMetaData.type, tileMetaData.len);

    if (fseek(file, tileMetaData.len, SEEK_CUR) != 0) {
        perror("Failed to seek past tile pixel data");
    }
}

void read_world_metadata(FILE *file) {
    printf("\n==================== World MetaData ====================\n");

    WorldMetaData worldMetaData;
    if (fread(&worldMetaData, sizeof(WorldMetaData), 1, file) != 1) {
        perror("Failed to read WorldMetaData");
        return;
    }
    printf("World ID: %u\n", worldMetaData.frame.id);
    printf("Control Flag: %u\n", worldMetaData.frame.controlFlag);
    printf("Background Color: %u\n", worldMetaData.frame.backgroundColor);
    printf("Reserved: %u\n", worldMetaData.frame.reserved);
    printf("Length: %u bytes\n", worldMetaData.frame.len);
}

void read_worldmap_ids(FILE *file) {
    printf("\n==================== World Map IDs ====================\n");
    uint8_t worldMapId;
    printf("World Map IDs: ");
    while (fread(&worldMapId, sizeof(uint8_t), 1, file) == 1) {
        printf("%u, ", worldMapId);
    }
    printf("\n");

}

int main() {
    FILE *file = fopen(FILE_PATH, "rb");
    if (!file) {
        perror("Failed to open file");
        return 1;
    }
    read_file_metadata(file);
    read_color_register(file);
    read_actors_header(file);
    read_world_tiles_header(file);
    read_world_metadata(file);
    read_worldmap_ids(file);

    

    fclose(file);
    return 0;
}