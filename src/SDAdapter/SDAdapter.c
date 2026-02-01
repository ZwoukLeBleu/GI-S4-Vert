#include "SDAdapter.h"
#include <stdlib.h>

uint8_t readFileMeta(SDAdapter *adapter){

    if(SD_HAL_readBytes(adapter->fileMeta.byteMap, sizeof(FileMetaData)) != sizeof(FileMetaData)){
        // ERROR REG
        return 0;
    }

    if(adapter->fileMeta.frame.fileVersion > SD_ADAPTER_VERSION){
        //Error reg
        return 0;
    }

    return 1;
}

uint8_t readColorsRegister(SDAdapter* adapter){

    if(SD_HAL_readBytes(adapter->colorsRegister.byteMap, sizeof(ColorRegister) != sizeof(ColorRegister))){
        // ERROR REG
        return 0;
    }
    return 1;
}


uint8_t generateActors(SDAdapter* adapter){
    if(SD_HAL_readBytes(adapter->actorsHeader.byteMap, sizeof(ActorsHeader))){
        // ERROR REG
        return 0;
    }

    adapter->actors = (Actor*)malloc(adapter->actorsHeader.frame.nbOfActors * sizeof(Actor));
    for(unsigned int i=0; i < adapter->actorsHeader.frame.nbOfActors; i++){
        Actor* act = (adapter->actors+i);
        if(SD_HAL_readBytes(act->meta.byteMap, sizeof(ActorMetaData)) != sizeof(ActorMetaData)){
            // ERR REG
            return 0;
        }

        act->actorSprite = (uint8_t*)malloc(act->meta.frame.len * sizeof(uint8_t));
        act->spriteLenght = act->meta.frame.len/act->meta.frame.nbOfSprite;
        if (act->spriteLenght %4 != 0){
            //ERROR REG
            return 0;
        }
        
        for(unsigned int j=0; j < act->meta.frame.nbOfSprite; j++){
            
            //uint32_t offset = act->spriteLenght*j;
            
            if(SD_HAL_readBytes(act->actorSprite, act->spriteLenght) != act->spriteLenght){
                //ERR REG
                return 0;
            }
        }
    }
    return 1;
}

uint8_t generateWorld(SDAdapter* adapter){
    
    if(SD_HAL_readBytes(adapter->worldMeta.byteMap, sizeof(WorldMetaData) != sizeof(WorldMetaData))){
        // ERR REG
        return 0;
    }
    
    adapter->world.tileLenght = adapter->worldMeta.frame.len / adapter->worldMeta.frame.nbOfTiles;
    if(adapter->world.tileLenght % 4 != 0){
        //ERR REG
        return 0;
    }

    adapter->world.tiles = (Tile*)malloc(adapter->worldMeta.frame.nbOfTiles * sizeof(Tile));

    for(unsigned int i=0; i < adapter->worldMeta.frame.nbOfTiles; i++){
        Tile* t = (adapter->world.tiles+i);
        if(SD_HAL_readBytes(t->meta.byteMap, sizeof(WorldTileMetaData)) != sizeof(WorldTileMetaData)){
            //ERR REG
            return 0;
        }

        t->tileSprite = (uint8_t*)malloc(adapter->world.tileLenght * sizeof(uint8_t));

        if(SD_HAL_readBytes(t->tileSprite, adapter->world.tileLenght) != adapter->world.tileLenght){
            // ERR REG
            return 0;
        }

    }

    return 1;
}

uint8_t SD_ReadFile(SDAdapter *adapter)
{
    if(hal.status != SD_HAL_READY_STATUS){
        //ERROR reg
        return 0;
    }

    if(readFileMeta(adapter) == 0){
        return 0;
    }

    if(readColorsRegister(adapter) == 0){
        return 0;
    }

    if(generateActors(adapter) == 0){
        return 0;
    }

    if(generateWorld(adapter) == 0){
        return 0;
    }

    return 1;
}