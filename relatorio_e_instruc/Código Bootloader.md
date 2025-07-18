
- No arquivo flash_utils.h estão declaradas várias funções, especificadas em flash_utils.c. 

Funções:

#calcular_crc_da_aplicacao
- Verifica se o tamanho da aplicação é divisível por 4 (essencial para o cálculo).
- Usa a função nativa HAL_CRC_calculate para retornar o crc, usando a variável hcrc declarada em main.h

#calcular_crc8
- Utiliza lógica similar ao código python, para calcular o crc 8 de um bloco de mensagem.
- Percorre os bits da mensagem com método XOR para fazer a verificação.

#apagar_flash_aplicação
- usa o HAL_FLASH_unlock() e futuramente o lock para abrir e fechar a escrita.
- Tenta apagar os dados da aplicação principal por páginas, usando as definições de início do endereço e final e também do tamanho das páginas = 2kb.
- Verifica sucesso e retorna (atualmente não faz nada em caso de erro).

#gravar_bloco_na_flash 
- Usa o HAL_FLASH_unlock() e lock para abrir e fechar a escrita.
- Usa um loop for para ir escrevendo bloco a bloco (8 bytes).
- Usa função memcpy do <string.h> para escrever.
- Verifica sucesso, caso não tenha -> break. Caso tenha -> continua e lock (em ambos os casos fecha).


Main.c
Onde as funções são usadas e contém a estrutura do bootloader, boa parte do código foi gerado automaticamente pelo stm32CubeIDE. Comentarei a parte adicionada depois do gerador.

Onde está definido o #define ECU_ID, no bootloader de cada ECU deve ter um diferente, 0x01, 0x02, 0x03...

Declara algumas variáveis. 'RxData', 'crc_recebido', 'firmware_tamanho' e 'start_recebido'.

Define a função #jump_to_application que é responsável por sair do bootloader e ir para a aplicação principal.

Função main():

- Começa iniciando o FDCAN -> HAL_FDCAN_Start(&hfdcan1); e ativa o periférico que faz com que toda mensagem recebida emita uma notificação -> HAL_FDCAN_ActivateNotification.

- Verifica se alguma notificação chega, ou seja, espera o START, possui um timer de 3s de espera. Caso seja recebido -> continua no bootloader. Caso não receba -> #jump_to_application.


Função HAL_FDCAN_RxFifo0Callback():

Coração do sistema, é onde as mensagens recebidas do script são interpretadas e seus respectivos comandos são executados.

- Inicia com uma verificação de notificação, se falsa, acaba a função, se verdadeira segue.
- Usa a função HAL_FDCAN_GetRxMessage para receber a mensagem, declara uma variável destino e adiciona o dado 0 da mensagem, ou seja o ECU_ID, então verifica esse id com o definido no bootloader, caso bata prossegue, caso não, ignora a mensagem.
- Antes de prosseguir, ao receber uma mensagem faz uma verificação se ela possui um crc8.
- Se possuir um crc8 prossegue, guardando o crc do bloco em uma variável, e guardando o calculo do crc, feito usando a função #calcular_crc8 em outra variável. 
- Verificando se, o crc8 do  bloco confere com o calculado. Se sim segue, ou então ignora a mensagem.
- Usa a função switch com base no identifier (0x100, 0x101...) das mensagem para executar os comandos.
- Caso 0x100: START, torna a variável start_recebido.
- Caso 0x101: ERASE, usa a função #apagar_flash_aplicação e define firmware_tamanho como nula.
- Caso 0x102: WRITE, define o endereço com base na mensagem, começando do 1 para pular o ECU_ID, faz uma verificação se o endereço está dentro do permitido pra aplicação. 
	- Usa a função #gravar_bloco_na_flash com o endereço calculado e RxData[5], começando em 5  pois 0 = ECU_ID, 1-4 = identifier comando e 5 em diante = mensagem propriamente dita. O ultimo byte da mensagem é reservado ao crc8.
	- A função também guarda em uma variável o tamanho do firmware escrito, para calculo do crc depois.
	- Prepara o ack da mensagem escrita, para confirmação no script.
	- Então manda um sinal de retorno para o computador, incluindo o ack (0x105).
- Caso 0x103: END, calcula o crc do firmware recebido e compara com o enviado pelo script, caso seja igual -> #jump_to_application caso não reinicia a ECU para entrar em bootloader novamente.
- Caso 0x104: Recebe o crc e tamanho calculados do script e salva em variáveis.













