import can
import time
import os
import binascii
from enum import Enum


# ====== CONFIGURAÇÕES ======
APPLICATION_BASE = 0x08004000
INTERFACE = "slcan"  # driver candleLight via COM
CHANNEL = "COM5"     # depende do seu sistema (Verificar no Windows como o adaptador se conecta)
BITRATE = 250000

# ====== Definição das ECUs ======
ECUS = {
    "1": {"nome": "MECU", "id": 0x01, "bin": "C:/Users/gutob/Documents/baja/CASE/pythonInstalador/f1/firmware.bin"},
    "2": {"nome": "RECU", "id": 0x02, "bin": "C:/Users/gutob/Documents/baja/CASE/pythonInstalador/f2/firmware.bin"},
    "3": {"nome": "PTECU", "id": 0x03, "bin": "C:/Users/gutob/Documents/baja/CASE/pythonInstalador/f1/firmware.bin"},
    "4": {"nome": "AECU", "id": 0x04, "bin": "C:/Users/gutob/Documents/baja/CASE/pythonInstalador/f2/firmware.bin"},
    "5": {"nome": "FECU", "id": 0x05, "bin": "C:/Users/gutob/Documents/baja/CASE/pythonInstalador/f1/firmware.bin"}
}

print("Qual a ECU a ser atualizada?\n")
for chave, info in ECUS.items():
    print(f"{chave} – {info['nome']} (arquivo: {info['bin']})")

escolha = input("\nDigite o número da ECU: ").strip()

if escolha not in ECUS:
    print("Não existe.")
    exit(1)

selecionada = ECUS[escolha]
ECU_ID = selecionada["id"]
BIN_PATH = selecionada["bin"]
print(f"\nECU selecionada: {selecionada['nome']}, ID: 0x{ECU_ID:02X}")

#===== Definição dos comandos ======    
class COMANDOS(Enum):
    START = 0x100
    ERASE = 0x101
    WRITE = 0x102
    END = 0x103
    CRC = 0x104
    RESET = 0x0F0

#====== Verificar Arquivo BIN ======
if not os.path.isfile(BIN_PATH):
    print(f"Arquivo '{BIN_PATH}' não encontrado!")
    exit(1)

# ====== CONFIGURAR CAN ======
bus = can.interface.Bus(
    interface=INTERFACE,
    channel=CHANNEL,
    bitrate=BITRATE,
    fd=True  # CAN-FD ativado
)

#======= Função para enviar comandos =======
def enviar_comando(comando_id, payload, ecu_id):
    if not isinstance(payload, bytes):
        payload = bytes(payload)

    data = bytes([ecu_id]) + payload

    msg = can.Message(
        arbitration_id=comando_id,
        data=data,
        is_extended_id=False
    )
    bus.send(msg)
    time.sleep(0.01)

#======= Funcao para aguardar resposta do dispositivo =======
def aguardar_ack(endereco_esperado, timeout=0.1, tentativas=5):
    for tentativa in range(tentativas):
        try:
            msg = bus.recv(timeout)
            if msg is not None and msg.arbitration_id == 0x105:
                endereco_ack = int.from_bytes(msg.data[0:4], byteorder='little')
                if endereco_ack == endereco_esperado:
                    return True  # Sucesso
        except can.CanError:
            pass
        print(f"Reenviando bloco 0x{endereco_esperado:08X}")
    return False  # Falhou após todas tentativas

#======= Definicao do Calculo do CRC-8 =======
def calcular_crc8(data):
    crc = 0x00
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
            crc &= 0xFF
    return crc

#======= Resetar ECU =======

print(f"Enviando reset para ECU {ECU_ID}")
enviar_comando(COMANDOS.RESET, b'', ECU_ID)
time.sleep(3.0)  # Aguarda reinício da ECU

#======== ETAPA 0: START: ======

print("Enviando comando START...")
enviar_comando(COMANDOS.START, b'', ECU_ID)

# ====== ETAPA 1: Apagar FLASH ======

print("Enviando comando ERASE...")
enviar_comando(COMANDOS.ERASE, b'', ECU_ID)  # Nenhum dado necessário
time.sleep(0.1)

# ====== ETAPA 2: Ler arquivo BIN ======

with open(BIN_PATH, "rb") as f:
    firmware = f.read()

# Preencher firmware para múltiplo de 8 bytes

if len(firmware) % 8 != 0:
    firmware += b'\xFF' * (8 - len(firmware) % 8)

print(f"Tamanho do firmware: {len(firmware)} bytes")

# ====== ETAPA 3: Enviar blocos com CRC-8 ======

for i in range(0, len(firmware), 3):  # agora envia até 3 bytes úteis por vez
    bloco = firmware[i:i+3]           # máximo 3 bytes de dados
    bloco = bloco.ljust(3, b'\xFF')   # completa com 0xFF se tiver menos de 3

    endereco = APPLICATION_BASE + i
    payload_sem_crc = endereco.to_bytes(4, 'little') + bloco  # 7 bytes
    crc8 = calcular_crc8(payload_sem_crc)
    payload = payload_sem_crc + bytes([crc8])  # 8 bytes no total

    tentativas = 0
    sucesso = False

    while not sucesso and tentativas < 5:
        enviar_comando(COMANDOS.WRITE, payload, ECU_ID)
        print(f"[WRITE] Addr: 0x{endereco:08X}  Tentativa: {tentativas + 1}")
        sucesso = aguardar_ack(endereco)
        tentativas += 1

    if not sucesso:
        print(f"[ERRO] Falha ao enviar bloco 0x{endereco:08X}")
        exit(1)

# Calculo do CRC-32 

crc_val = binascii.crc32(firmware) & 0xFFFFFFFF
tamanho_firmware = len(firmware)

print(f"\nCRC calculado:      0x{crc_val:08X}")
print(f"Tamanho do firmware: {tamanho_firmware} bytes")

#===== ETAPA 5: Enviar CRC + tamanho
crc_payload = crc_val.to_bytes(4, 'little') + len(firmware).to_bytes(4, 'little')
enviar_comando(COMANDOS.CRC, crc_payload, ECU_ID)

#===== ETAPA 6: Enviar END (salto para aplicação)
print("Enviando comando END (ID 0x103)...")
enviar_comando(COMANDOS.END, b'', ECU_ID)
print("Upload concluído.")