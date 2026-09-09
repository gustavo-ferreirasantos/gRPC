from __future__ import print_function

import grpc
import tasks_pb2
import tasks_pb2_grpc
import comandos as cmds
from colorama import Fore, Style

def run():
    selecionada = 0
    try: # 'server:50051'
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = tasks_pb2_grpc.TasksStub(channel)
            while(True):
                print("\nSelecione uma opção\n")
                print("1 - Adicionar Tarefa")
                print("2 - Ver tarefa específica")
                print("3 - Listar todas as tarefas")
                print("4 - Atualizar tarefa")
                print("5 - Deletar tarefa")
                print("6 - Deletar todas as tarefas")
                print("7 - Teste rápido")
                print("default - Sair\n")

                selecionada = int(input())
                match selecionada:
                    case 1:
                        cmds.criar_tarefa_wrapper(stub)
                    case 2:
                        cmds.get_tarefa_wrapper(stub)
                    case 3:
                        cmds.listar_tarefas(stub)
                    case 4:
                        cmds.update_tarefa_wrapper(stub)
                    case 5:
                        cmds.deletar_tarefa_wrapper(stub)
                    case 6:
                        cmds.deletar_tudo_wrapper(stub)
                    case 7:
                        cmds.teste_tarefas(stub)
                    case _:
                        print("Finalizando...")
                        exit(0)
            

    except grpc._channel._InactiveRpcError:
        print(Fore.RED + "Erro: " + Style.RESET_ALL + "Servidor não está rodando. Inicie o servidor primeiro.")
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            print(Fore.RED + "Erro: " + Style.RESET_ALL + e.details())
        else:
            print(Fore.RED + "Erro gRPC: " + Style.RESET_ALL + f"{e.code().name} - {e.details()}")
    # input()


if __name__ == '__main__':
    run()
