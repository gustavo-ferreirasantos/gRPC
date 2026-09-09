from __future__ import print_function

import grpc
import tasks_pb2
import tasks_pb2_grpc
import comandos as cmds
from colorama import Fore, Style

def run():
    try:
        with grpc.insecure_channel('server:50051') as channel:
            stub = tasks_pb2_grpc.TasksStub(channel)
            cmds.teste_tarefas(stub)
    except grpc._channel._InactiveRpcError:
        print(Fore.RED + "Erro: "+ Style.RESET_ALL + "Servidor nao esta rodando. Inicie o servidor primeiro.")
    # input()


if __name__ == '__main__':
    run()
