

- Usa a biblioteca 'python-can' para enviar os sinais can de maneira simples.
- Usa a biblioteca 'binascii' para calcular o crc do firmware
- Usa a biblioteca 'os' para acessar o arquivo do firmware


#configurações:

- Define o inicio da aplicação onde será escrito o firmware (após o bootloader de 16kb).

- Define a interface 'slcan' para usar o candleLight com o adaptador escolhido.

- Em channel define a porta que o adaptador foi conectado (deve ser arrumado conforme uso).

- E define a bitrate de 250kbits/s.

#Definição_ECUs

- Usa a matriz ECUS para definir o nome, id e arquivo de firmware pra cada ECU. Pode ser melhorado com seleção de arquivo por interface com usuário. Também deve ser arrumado conforme uso.

- Usa loop for para mostrar as opções (da matriz) a serem atualizadas.

- Usa input para selecionar a escolha do usuário.

- Verifica se a escolha existe.

- Define ID da ECU a ser atualizada e localização do firmware

#Deinição_Comandos

- Usa um enum para definir os comandos:
	- 0x100: START
	- 0x101: ERASE
	- 0x102: WRITE
	- 0x103: END
	- 0x104: CRC
	- 0x0F0: RESET

#BIN
- Verifica a existência do firmware no local indicado no código

#Configurar_CAN
- Usa a função can.interface.Bus para configurar o can, com base nas definições do início

#Enviar_Comando
- Define a função #Enviar_Comando, a mais importante do script, com base em 3 variáveis, comando_id, o "tipo" do comando a ser enviado. O payload, que seria o tamanho da mensagem, quando é um comando simples pode ser nulo. E o ecu_id, o endereço do comando.
- Ainda na função verifica se payload já está em bytes, caso contrário torna-a.

#Aguardar_Retorno
- Usa o retorno ACK (quando uma mensagem é recebida) para verificar se o bloco de firmware foi recebido.
- A função opera com 3 variáveis, o endereço é o local onde o frame deveria ser escrito, a partir de 0x8004000. O timeout e o número de tentativas a serem executadas, ja definidas na declaração.
- Usa um loop for para executar as tentativas, se tem sucesso retorna True e encerra função. Se falha tenta repetir 5x, caso falhe todas retorna False.
- Usa a seguinte lógica -> tenta enviar (se enviar) msg não sera nulo e o ID será correto -> define o endereço ack com base na mensagem enviada -> verifica se o endereço esperado da função coincide com o ack retornado -> caso sim -> FIM msg enviada com sucesso.
- Caso tenta enviar -> retorna erro can -> tenta reenviar.
- Caso tenta enviar -> se for nula/id incorreto -> pass -> tenta reenviar.

#Calculo_CRC8
- Utiliza método XOR para percorrer os bits de um bloco de mensagem de 8 bytes e retorna o crc-8
- Calcula o crc de um único bloco de mensagens, não do firmware todo.

#Resetar_ECU
- Envia o comando (RESET), que deve estar definido na aplicação principal como reset para funcionar.
- Aguarda ECU reiniciar para entrar em modo bootloader.

#START
- Envia comando start (START) após reinício, necessário pois bootloader não apaga os dados sem receber ele antes como forma de segurança. Por isso é executado 3x.
- Como não carrega dados, payload é vazio.

#Apagar_FLASH
- Envia o comando erase (ERASE), bootloader só recebe se start foi sucesso.

#ler_BIN
- Usa função open do 'os' para abrir arquivo firmware.bin.
- Verifica se os blocos ja são múltiplos de 8bytes, que é tamanho dos blocos escritos, caso não sejam preenche com vazio.

#Enviar_Blocos
- usa loop for, início em 0, até o tamanho do firmware, de 3 em 3 bytes.
- Define os blocos a serem enviados com base no firmware.
- Define onde serão escritos os blocos, com base no início da aplicação e a cada loop adiciona 3 (tamanho dos blocos).
- Define o payload como o endereço convertido de bits -> bytes mais o bloco.
- Define o payload máximo de 7 bytes, ja que o primeiro da mensagem está reservado ao ECU_ID.
- Faz as verificações com a função #Aguardar_Retorno , tenta enviar 5x, usando a função #Enviar_Comando WRITE.


#calculo_CRC32
- Usa a função do 'binascii' para calcular o crc do firmware e calcula tamanho do firmware.
- Monta o crc_payload como o crc + tamanho, para ser verificada a integridade dos dados pelo bootloader.

#Enviar_CRC
- Usa a função #Enviar_Comando (CRC) para enviar o pacote do crc_payload para o bootloader.
- Referente ao crc32, do firmware completo.

#Enviar_end envia comando end (END) e finaliza programa. O comando end, no bootloader executa o salto para aplicação principal.








