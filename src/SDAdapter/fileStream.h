#pragma once


#include <stdint.h>

#define FILE_VERSION 3
#define FILE_VERSION 3
#define FILE_NAME "Game.bin"
#define WORLD_TILE 16
#define WORLD_LEN 4194304
#define WORLD_TILE 16
#define WORLD_LEN 4194304


/**
 * FIXED HEADER TO DECLARE THE FILE SECTOR
 */

typedef struct {
        uint32_t fileVersion : 8;
        uint32_t controlFlags : 8;
        uint32_t reserved : 16;
        uint32_t fileLen;
} FrameFileMetaData;

typedef union {
    FrameFileMetaData frame;
    uint8_t byteMap[sizeof(FrameFileMetaData)];
} FileMetaData;


typedef union {
    uint32_t code; // The entire 32-bit block
    struct {
        uint32_t id    : 8;
        uint32_t red   : 8;
        uint32_t green : 8;
        uint32_t blue  : 8;
    } channels; // The individual 8-bit components
} Color;

/**
 * Pallet of color registered in the memory via an ID
 */
typedef union {
    struct {
        Color colorMask;
        Color colors[15];
    }frame;

    uint8_t byteMap[sizeof(Color) * 16];
} ColorRegister;



typedef struct {
        uint32_t nbOfActors:8;
        uint32_t playerActorId:8;
        uint32_t lifeBar:8;
        uint32_t reserved:8;
        uint32_t lifeBar:8;
        uint32_t reserved:8;
} FrameActorsHeader;

typedef union {
    FrameActorsHeader frame;
    uint8_t byteMap[sizeof(FrameActorsHeader)];
} ActorsHeader;

/**
 * Actor header to indicate at the console the number of sprite and its id. The console directly assign the sprite selection based on the sequence (sprite 0 = id 0 for actor id [actor_id.sprite_id])
 */
typedef struct {
        uint8_t id;
        uint8_t nbOfSprite;
        uint16_t len; 
} FrameActorMetaData;
 typedef union {
    FrameActorMetaData frame;
    uint8_t byteMap[sizeof(FrameActorMetaData)];
} ActorMetaData;

typedef struct {
    uint32_t tilesWidth:8;
    uint32_t tilesHeight:8;
    uint32_t nbOfTiles:8;
    uint32_t reserved:8;
} FrameActorsTileMeta;

typedef union {
    FrameActorsTileMeta frame;
    uint8_t byteMap[sizeof(FrameActorsTileMeta)];
} ActorsTileMetaData;

typedef struct {
    uint32_t tilesWidth:8;
    uint32_t tilesHeight:8;
    uint32_t nbOfTiles:8;
    uint32_t reserved:8;
} FrameActorsTileMeta;

typedef union {
    FrameActorsTileMeta frame;
    uint8_t byteMap[sizeof(FrameActorsTileMeta)];
} ActorsTileMetaData;

/**
 * World header to get an id and control flags. 
 */
typedef struct {
        uint8_t id;
        uint8_t controlFlag;
        uint8_t backgroundColor;
        uint8_t reserved;
        uint8_t reserved;
        uint32_t len;
} FrameWorldMetadata;

typedef union {
    FrameWorldMetadata frame;
    uint8_t byteMap[sizeof(FrameWorldMetadata)];
} WorldMetaData;

/**
 * This metadata needs to directly follow the WorldMetaData times the nbOfTiles.
 */

typedef struct {
    uint16_t nbOfTiles;
    uint16_t len;
} FrameWorldTilesHeader;

typedef union {
    FrameWorldTilesHeader frame;
    uint8_t byteMap[sizeof(FrameWorldTilesHeader)];
} WorldTilesHeader;


typedef struct {
    uint16_t nbOfTiles;
    uint16_t len;
} FrameWorldTilesHeader;

typedef union {
    FrameWorldTilesHeader frame;
    uint8_t byteMap[sizeof(FrameWorldTilesHeader)];
} WorldTilesHeader;

typedef struct {
        uint8_t id;
        uint8_t collision:1;
        uint8_t event:1;
        uint8_t type:2;
        uint8_t reserved:4;
        uint16_t len;
} FrameWorldTileMetaData;

typedef union {
    FrameWorldTileMetaData frame;
    uint8_t byteMap[sizeof(FrameWorldTileMetaData)];
} WorldTileMetaData;


/**
 * WARNING - EVERY LEN OF sprites needs to have a len_byte % 4 = 0
 */
// typedef union {
//     struct {
//         FileMetaData data;
//         ColorRegister colors;
//         ActorsHeader actorHeader;

//         /* -- TIMES THE NB OF ACTORS --*/
//         ActorMetaData actor0;
//         //actor0 sprites %4
//         /* ----------------------------*/
//         WorldTilesHeader tilesHeader;
//         /* -- TIMES THE NB OF TILES --*/
//         WorldTileMetaData tileMeta;
//         //WORD TILE WITH ID %4
//         WorldMetaData world;
//         // ID OF TILES in bit map % 4
//         /* ----------------------------*/
//         //World with tiles ID
//     } parameters;
    
//     uint8_t b[sizeof(parameters)];
// } FileExample;