#include "xaxivdma.h"
#include "xparameters.h"
#include "scaler.h"
#include "xil_cache.h"

// Création de l'image en RAM (256x224, 3 octets par pixel pour le RGB)
static u8 FrameBuffer[256 * 224 * 3];
XAxiVdma VdmaInst;

int main() {
    // 1. Remplir tout le tableau avec du ROUGE
    for (int i = 0; i < (256 * 224 * 3); i += 3) {
        FrameBuffer[i]   = 0xFF; // Rouge au maximum
        FrameBuffer[i+1] = 0x00; // Pas de vert
        FrameBuffer[i+2] = 0x00; // Pas de bleu
    }
    // Vider la mémoire cache pour que le matériel voie les couleurs
    Xil_DCacheFlushRange((UINTPTR)FrameBuffer, sizeof(FrameBuffer));

    // 2. Allumer le Scaler (obligatoire pour que l'écran HDMI reçoive un signal)
    configureScaler();

    // 3. Initialiser le VDMA
    // On utilise maintenant l'adresse de base générée par Vivado au lieu de l'ID
    XAxiVdma_Config *Config = XAxiVdma_LookupConfig(XPAR_XAXIVDMA_0_BASEADDR);
    XAxiVdma_CfgInitialize(&VdmaInst, Config, Config->BaseAddress);

    // 4. Configurer la taille de l'image à lire
    XAxiVdma_DmaSetup ReadCfg = {0};
    ReadCfg.VertSizeInput = 224;             // Hauteur
    ReadCfg.HoriSizeInput = 256 * 3;         // Largeur en octets
    ReadCfg.Stride        = 256 * 3;         // Saut de ligne
    ReadCfg.EnableCircularBuf = 1;           // Mode vidéo continu
    ReadCfg.EnableSync    = 1;
    XAxiVdma_DmaConfig(&VdmaInst, XAXIVDMA_READ, &ReadCfg);

    // 5. Donner l'adresse mémoire et démarrer !
    UINTPTR Addr = (UINTPTR)FrameBuffer;
    XAxiVdma_DmaSetBufferAddr(&VdmaInst, XAXIVDMA_READ, &Addr);
    XAxiVdma_DmaStart(&VdmaInst, XAXIVDMA_READ);
  
    //tests
    xil_printf("\n\r--- TEST DE LECTURE RAM ---\n\r");
    xil_printf("Adresse lue par le VDMA : 0x%08X\n\r", Addr);
    
    // On va lire seulement les 4 premiers pixels pour ne pas faire exploser la console
    u8* ram_pointer = (u8*)Addr; 
    
    for(int i = 0; i < 4; i++) {
        int index = i * 3; // 3 octets par pixel (RGB)
        xil_printf("Pixel %d (en RAM) -> R: %02X | G: %02X | B: %02X\n\r", 
                   i, ram_pointer[index], ram_pointer[index+1], ram_pointer[index+2]);
    }
    
    // On vérifie aussi si le VDMA a planté en essayant de lire
    u32 status = XAxiVdma_GetStatus(&VdmaInst, XAXIVDMA_READ);
    if(status & 0x00000001) {
        xil_printf("ETAT : Le VDMA est a l'arret (HALTED) !\n\r");
    } else {
        xil_printf("ETAT : Le VDMA tourne et pompe la RAM (RUNNING) !\n\r");
    }

    // Fin du programme, le matériel travaille tout seul.
    while(1) {}

    return 0;
}