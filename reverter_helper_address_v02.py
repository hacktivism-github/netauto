from netmiko import ConnectHandler
from dotenv import dotenv_values
import os
import getpass

# Carregar variáveis de ambiente do ficheiro .env
env_vars = dotenv_values(".env")

# Alternar entre modo interativo e ficheiro .env
USE_INTERACTIVE = False

# Ler credenciais do .env
USERNAME = env_vars.get("USERNAME") if not USE_INTERACTIVE else None
PASSWORD = env_vars.get("PASSWORD") if not USE_INTERACTIVE else None

TEST_VLAN = 777

HELPER_TO_REMOVE = "172.31.20.34"

switches = [
    {"host": "172.28.4.252", "name": "SW-CORE-CAMPUS-01"},
    {"host": "172.28.4.253", "name": "SW-CORE-CAMPUS-02"},
]

def remove_helper(switch):
    print(f"\n A Conectar ao {switch['name']} ({switch['host']})...")

    # Obter credenciais
    username = input("Username: ") if USE_INTERACTIVE else USERNAME
    password = getpass.getpass("Password: ") if USE_INTERACTIVE else PASSWORD

    device = {
        "device_type": "cisco_ios",
        "host": switch["host"],
        "username": username,
        "password": password,
    }

    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()
        output = net_connect.send_command("show run | section interface Vlan")
    except Exception as e:
        print(f" Erro na conexão ou comando: {e}")
        return

    interfaces = output.split("interface Vlan")
    # Inicializar uma variável para rastrear se houve mudanças
    changes_made = False

    # Iterar sobre cada seção de interface
    for section in interfaces[1:]:
        lines = section.strip().splitlines()
        vlan = lines[0].strip()
        helper_lines = [line for line in lines if "ip helper-address" in line]

        for line in helper_lines:
            current_helper = line.split()[-1]
            if current_helper == HELPER_TO_REMOVE:
                print(f" Vlan{vlan}: a remover {HELPER_TO_REMOVE}...")
                commands = [
                    f"interface Vlan{vlan}",
                    f"no ip helper-address {HELPER_TO_REMOVE}"
                ]
                net_connect.send_config_set(commands)
                changes_made = True

    net_connect.disconnect()
    if changes_made:
        print(f" Reversão concluída para {switch['name']}")
    else:
        print(f" Nenhum helper {HELPER_TO_REMOVE} encontrado em {switch['name']}")

def main():
    for sw in switches:
        remove_helper(sw)

if __name__ == "__main__":
    main()
