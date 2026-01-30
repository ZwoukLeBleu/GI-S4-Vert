#pragma once


#include <cstdint>


/**
 * FIXED HEADER TO DECLARE THE FILE SECTOR
 */
typedef union {
    struct {
        uint32_t fileVersion : 8;
        uint32_t controlFlags : 8;
        uint32_t reserved : 16;
        uint32_t fileLen;
    } frame;

    uint8_t byteMap[sizeof(frame)];
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

typedef union {
    struct {
        uint32_t nbOfActors:8;
        uint32_t playerActorId:8;
        uint32_t reserved:16;
    }frame;

    uint8_t byteMap[sizeof(frame)];
} ActorsHeader;

/**
 * Actor header to indicate at the console the number of sprite and its id. The console directly assign the sprite selection based on the sequence (sprite 0 = id 0 for actor id [actor_id.sprite_id])
 */
 typedef union {

    struct {
        uint8_t id;
        uint8_t nbOfSprite;
        uint16_t len; 
    } frame;

    uint8_t byteMap[sizeof(frame)];
} ActorMetaData;

/**
 * World header to get an id and control flags. 
 */
typedef union {
    struct {
        uint8_t id;
        uint8_t controlFlag;
        uint8_t backgroundColor;
        uint8_t nbOfTiles;
        uint32_t len;
    } frame;

    uint8_t byteMap[sizeof(frame)];
} WorldMetaData;

/**
 * This metadata needs to directly follow the WorldMetaData times the nbOfTiles.
 */
typedef union {
    struct {
        uint8_t id;
        uint8_t collision:1;
        uint8_t event:1;
        uint8_t type:2;
        uint8_t reserved:4;
        uint16_t len;
    } frame;

    uint8_t byteMap[sizeof(frame)];
} WorldTileMetaData;


/**
 * WARNING - EVERY LEN OF sprites needs to have a len_byte % 4 = 0
 */
typedef union {
    struct {
        FileMetaData data;
        ColorRegister colors;
        ActorsHeader actorHeader;

        /* -- TIMES THE NB OF ACTORS --*/
        ActorMetaData actor0;
        //actor0 sprites %4
        /* ----------------------------*/
        WorldMetaData world;
        /* -- TIMES THE NB OF TILES --*/
        WorldTileMetaData tileMeta;
        //tiles bmp %4
        /* ----------------------------*/
        //World with tiles ID
    } parameters;

    uint8_t byteMap[sizeof(parameters)];
} FileExample;