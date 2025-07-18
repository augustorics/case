#include "flash_utils.h"
#include "stm32g0xx_hal.h"
#include <string.h>
#include "main.h"


#define FLASH_PAGE_SIZE 0x800 // 2KB
#define FLASH_APP_START_ADDR  0x08004000
#define FLASH_APP_END_ADDR    0x0803FFFF



uint8_t calcular_crc8(const uint8_t* dados, uint8_t tamanho) {
    uint8_t crc = 0x00;
    for (uint8_t i = 0; i < tamanho; i++) {
        crc ^= dados[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x80)
                crc = (crc << 1) ^ 0x07;
            else
                crc <<= 1;
        }
    }
    return crc;
}

uint32_t calcular_crc_da_aplicacao(uint32_t endereco, uint32_t tamanho_bytes)
{
	if (tamanho_bytes % 4 != 0)
	        return 0xFFFFFFFF;  // Erro: tamanho inválido para CRC


    HAL_CRC_Init(&hcrc);
    return HAL_CRC_Calculate(&hcrc, (uint32_t*)endereco, tamanho_bytes / 4);
}



void apagar_flash_aplicacao(void)
{
    HAL_FLASH_Unlock();

    FLASH_EraseInitTypeDef erase;
    uint32_t pageError = 0;

    uint32_t startPage = (FLASH_APP_START_ADDR - 0x08000000) / FLASH_PAGE_SIZE;
    uint32_t numPages  = (FLASH_APP_END_ADDR - FLASH_APP_START_ADDR + 1) / FLASH_PAGE_SIZE;

    erase.TypeErase = FLASH_TYPEERASE_PAGES;
    erase.Banks = FLASH_BANK_1;  // << IMPORTANTE!
    erase.Page = startPage;
    erase.NbPages = numPages;

    if (HAL_FLASHEx_Erase(&erase, &pageError) != HAL_OK)
    {
        HAL_FLASH_Lock();
        return;  // Erro ao apagar
    }

    HAL_FLASH_Lock();
}

void gravar_bloco_na_flash(uint32_t endereco, uint8_t* dados, uint32_t tamanho)
{
    HAL_FLASH_Unlock();

    for (uint32_t i = 0; i < tamanho; i += 8)
    {
        uint64_t dado64 = 0;

        // Protege contra acesso fora dos limites
        uint32_t bytes_para_copiar = (tamanho - i >= 8) ? 8 : (tamanho - i);
        memcpy(&dado64, dados + i, bytes_para_copiar);

        if (HAL_FLASH_Program(FLASH_TYPEPROGRAM_DOUBLEWORD, endereco + i, dado64) != HAL_OK)
        {
            break;  // Erro na gravação
        }
    }

    HAL_FLASH_Lock();
}
