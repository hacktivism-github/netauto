from netmiko import ConnectHandler
#from dotenv import load_dotenv
from dotenv import dotenv_values
import os
import getpass

# Carregar variáveis de ambiente do ficheiro .env
#load_dotenv()
#load_dotenv(dotenv_path=".env")
#dotenv_values(".env")
env_vars = dotenv_values(".env")

# Alternar entre modo interativo e ficheiro .env
USE_INTERACTIVE = False

# Ler credenciais do .env
#USERNAME = os.getenv("USERNAME")
#PASSWORD = os.getenv("PASSWORD")
USERNAME = env_vars.get("USERNAME") if not USE_INTERACTIVE else None
PASSWORD = env_vars.get("PASSWORD") if not USE_INTERACTIVE else None
print(f"[DEBUG] USERNAME: {USERNAME}")
print(f"[DEBUG] PASSWORD: {'*' * len(PASSWORD) if PASSWORD else 'MISSING'}")


# Modo de simulação (não aplica mudanças)
DRY_RUN = False

# VLAN para teste piloto
TEST_VLAN = 777

# IP do novo DHCP helper
NEW_HELPER = "172.31.20.34"

# Lista de switches
switches = [
    {"host": "172.28.4.252", "name": "SW-CORE-CAMPUS-01"},
    {"host": "172.28.4.253", "name": "SW-CORE-CAMPUS-02"},
]

def connect_and_update(switch):
    print(f"\nA conectar ao {switch['name']} ({switch['host']})...")

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
        print(f" Falha na conexão ou comando: {e}")
        return

    interfaces = output.split("interface Vlan")
    log_lines = []

    print(f" A Analisar interfaces em {switch['name']}...")
    for section in interfaces[1:]:
        lines = section.strip().splitlines()
        vlan = lines[0].strip()
        if TEST_VLAN and vlan != str(TEST_VLAN):
            continue

        helper_lines = [line for line in lines if "ip helper-address" in line]
        if not helper_lines:
            continue

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

    if log_lines:
        with open(f"log_dhcp_helper_{switch['name']}.txt", "w") as f:
            f.write("\n".join(log_lines))

def main():
    for sw in switches:
        connect_and_update(sw)

if __name__ == "__main__":
    main()
