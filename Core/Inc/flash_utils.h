#ifndef FLASH_UTILS_H
#define FLASH_UTILS_H

#include <stdint.h>
#include <stdbool.h>

uint32_t calcular_crc_da_aplicacao(uint32_t endereco, uint32_t tamanho_bytes);
void apagar_flash_aplicacao(void);
void gravar_bloco_na_flash(uint32_t endereco, uint8_t* dados, uint32_t tamanho);

#endif
