from __future__ import print_function

import grpc
import tasks_pb2
import tasks_pb2_grpc

def run():
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = tasks_pb2_grpc.TasksStub(channel)
            response = stub.GetTasks(tasks_pb2.GetTasksRequest())
        print(response.tasks)
    except grpc._channel._InactiveRpcError:
        print("Erro: Servidor não está rodando. Inicie o servidor primeiro.")


if __name__ == '__main__':
    run()

