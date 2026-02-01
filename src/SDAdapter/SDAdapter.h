#pragma once

#include "fileStream.h"
#include "SDHal.h"

#define SD_ADAPTER_VERSION 1

typedef struct {
    ActorMetaData meta;
    uint32_t spriteLenght;
    uint8_t* actorSprite;
} Actor;

typedef struct {
    WorldTileMetaData meta;
    uint8_t* tileSprite;
} Tile;

typedef struct {
    uint32_t tileLenght;
    Tile* tiles;
} World;

typedef struct
{
    uint32_t errorRegister;
    ColorRegister colorsRegister;
    FileMetaData fileMeta;
    ActorsHeader actorsHeader;
    Actor* actors;
    WorldMetaData worldMeta;
    World world;
    
} SDAdapter;




uint8_t SD_ReadFile(SDAdapter* adapter);
