from netmiko import ConnectHandler
import getpass


USE_INTERACTIVE = True
# Se USE_INTERACTIVE for True, o script solicitará as credenciais ao utilizador

# Se USE_INTERACTIVE for False, as credenciais serão definidas aqui

# Atenção: não é recomendado guardar credenciais em texto claro
USERNAME = "Your AD username"
PASSWORD = "Your AD password"


switches = [
    {"host": "172.28.4.252", "name": "SW-CORE-CAMPUS-01"},
    {"host": "172.28.4.253", "name": "SW-CORE-CAMPUS-02"},
]

# Função para testar a conexão com cada switch
def test_connection(sw, username, password):
    # Exibir mensagem de teste de conexão
    print(f"\n A Testar conexão com {sw['name']} ({sw['host']})...")
    # Configurar o dispositivo para conexão
    device = {
        "device_type": "cisco_ios",
        "host": sw["host"],
        "username": username,
        "password": password,
    }
    # Tentar conectar ao switch e exibir mensagem de sucesso ou falha
    try:
        net_connect = ConnectHandler(**device)
        print(f" Conexão bem-sucedida com {sw['name']}")
        net_connect.disconnect()
    # Se houver erro na conexão, exibir mensagem de erro
    except Exception as e:
        print(f" Falha na conexão com {sw['name']}: {e}")

# Função principal para executar o teste de conexão
# Se USE_INTERACTIVE for True, solicitará as credenciais ao utilizador
def main():
    if USE_INTERACTIVE:
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    # Se USE_INTERACTIVE for False, usará as credenciais definidas acima
    else:
        username = USERNAME
        password = PASSWORD
    # Iterar sobre cada switch e testar a conexão
    for sw in switches:
        test_connection(sw, username, password)

if __name__ == "__main__":
    main()
