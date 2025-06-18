from netmiko import ConnectHandler
from dotenv import load_dotenv
import os
import getpass
# Script para adicionar um novo DHCP helper às VLANs de switches Cisco

# Alternar entre modo interativo e credenciais fixas

# Se USE_INTERACTIVE for True, o script solicitará as credenciais ao utilizador
USE_INTERACTIVE = True


# Definir credenciais aqui se USE_INTERACTIVE = False
USERNAME = "Your AD username"
PASSWORD = "Your AD password"
# Atenção: não é recomendado guardar credenciais em texto claro.
# Se fizer isso, certifique-se de que o script é executado em um ambiente seguro.

# Modo de simulação (não aplica mudanças, apenas mostra o que seria feito)
#DRY_RUN = True
DRY_RUN = False

# VLAN específica para teste piloto (colocar None para testar todas)
#TEST_VLAN = None  # Ex: "10"

TEST_VLAN = 777

# DHCP secundário a adicionar (Remover o comentário para ativar)
#NEW_HELPER = "Endereço IP do DHCP secundário"
NEW_HELPER = "172.31.20.34"

# Lista de switches a atualizar
switches = [
    {"host": "172.28.4.252", "name": "SW-CORE-CAMPUS-01"},
    {"host": "172.28.4.253", "name": "SW-CORE-CAMPUS-02"},
]

# Função para conectar ao(s) switch(es) e atualizar o(s) helper(s)
def connect_and_update(switch):
    print(f"\n A conectar ao {switch['name']} ({switch['host']})...")

    # Verificar se NEW_HELPER está definido
    if not NEW_HELPER:
        print(" ERRO: Define o endereço IP do NEW_HELPER antes de executar o script.")
        return
    
    # Configurar o dispositivo para conexão
    device = {
        "device_type": "cisco_ios",
        "host": switch["host"],
        "username": USERNAME if not USE_INTERACTIVE else input("Username: "),
        "password": PASSWORD if not USE_INTERACTIVE else getpass.getpass("Password: "),
    }

    # Tentar conectar ao switch e executar o comando
    # Se houver erro na conexão ou comando, exibir mensagem de erro
    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()
        output = net_connect.send_command("show run | section interface Vlan")
    except Exception as e:
        print(f" Falha na conexão ou comando: {e}")
        return

    # Dividir a saída em seções de interfaces
    # e inicializar uma lista para armazenar as linhas de log
    # Se não houver helpers, continua para a próxima interface
    interfaces = output.split("interface Vlan")
    log_lines = []

    # Iterar sobre cada seção de interface
    print(f" A Analisar interfaces em {switch['name']}...")
    for section in interfaces[1:]:
        lines = section.strip().splitlines()
        vlan = lines[0].strip()
        if TEST_VLAN and vlan != str(TEST_VLAN):
            continue

        helper_lines = [line for line in lines if "ip helper-address" in line]
        if not helper_lines:
            continue

        # Verificar se o helper já está presente
        # Se não houver helpers, continua para a próxima interface
        current_helpers = [line.split()[-1] for line in helper_lines]
        if NEW_HELPER not in current_helpers:
            print(f"  Interface Vlan{vlan} - helpers atuais: {current_helpers}")
            print(f" {'[DRY-RUN] ' if DRY_RUN else ''}A adicionar helper {NEW_HELPER}...")
            log_lines.append(f"[{switch['name']}] Vlan{vlan}: {current_helpers} -> +{NEW_HELPER}")
            if not DRY_RUN:
                commands = [
                    f"interface Vlan{vlan}",
                    f"ip helper-address {NEW_HELPER}"
                ]
                net_connect.send_config_set(commands)
        else:
            print(f" Interface Vlan{vlan} já contém o helper {NEW_HELPER}")

    net_connect.disconnect()
    print(f" Concluído para {switch['name']}")

    # Guardar log localmente
    if log_lines:
        with open(f"log_dhcp_helper_{switch['name']}.txt", "w") as f:
            f.write("\n".join(log_lines))

def main():
    for sw in switches:
        connect_and_update(sw)

if __name__ == "__main__":
    main()
