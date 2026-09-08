from concurrent import futures
import logging

from datetime import datetime
from google.protobuf import timestamp_pb2

import grpc
import tasks_pb2
import tasks_pb2_grpc
import database

from colorama import Fore, Style

# Transforma a data em formato de texto para google.protobuf.Timestamp
def to_timestamp(iso_string):
    dt = datetime.fromisoformat(iso_string)
    ts = timestamp_pb2.Timestamp()
    ts.seconds = int(dt.timestamp())
    ts.nanos = int(dt.microsecond * 1000)
    return ts


class TasksService(tasks_pb2_grpc.TasksServicer):
    # Retorna todas as tarefas
    def GetTasks(self, request, context):
        tasks = database.get_all_tasks() # Lista de dicionários
        # Retorna um GetTasksResponse, que contém uma lista de task
        return tasks_pb2.GetTasksResponse(
            tasks=[
                tasks_pb2.Task(
                    id=t["id"],
                    title=t["title"],
                    description=t["description"],
                    created_at=to_timestamp(t["created_at"]),
                )
                for t in tasks
            ]
        )
    # Retorna a tarefa com base no ID
    def GetTaskById(self, request, context):
        task = database.get_task_by_id(request.id) # Dicionário ou None
        if not task:
            context.abort(grpc.StatusCode.NOT_FOUND, "Task not found")
        # Retorna GetTaskByIdResponse
        return tasks_pb2.GetTaskByIdResponse(
            task=tasks_pb2.Task(
                id=task["id"],
                title=task["title"],
                description=task["description"],
                created_at=to_timestamp(task["created_at"]),
            )
        )

    def CreateTask(self, request, context):
        task = database.create_task(request.task.title, request.task.description) # Dicionário
        # Retorna CreateTaskResponse
        return tasks_pb2.CreateTaskResponse(
            task=tasks_pb2.Task(
                id=task["id"],
                title=task["title"],
                description=task["description"],
                created_at=to_timestamp(task["created_at"]),
            )
        )

    def UpdateTask(self, request, context):
        task = database.update_task(request.task.id, request.task.title, request.task.description)
        if not task:
            context.abort(grpc.StatusCode.NOT_FOUND, "Task not found")
        return tasks_pb2.UpdateTaskResponse(
            task=tasks_pb2.Task(
                id=task["id"],
                title=task["title"],
                description=task["description"],
                created_at=to_timestamp(task["created_at"]),
            )
        )

    def DeleteTask(self, request, context):
        task = database.delete_task(request.id)
        if not task:
            context.abort(grpc.StatusCode.NOT_FOUND, "Task not found")
        return tasks_pb2.DeleteTaskResponse(
            task=tasks_pb2.Task(
                id=task["id"],
                title=task["title"],
                description=task["description"],
                created_at=to_timestamp(task["created_at"]),
            )
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    tasks_pb2_grpc.add_TasksServicer_to_server(TasksService(), server)

    server.add_insecure_port('[::]:50051')

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig() # Permite o gRPC exibir mensagens
    print("\nStarting server in: %s" % ('localhost:50051'))
    try:
        serve()
    except RuntimeError:
        print(Fore.RED + "Erro: " + Style.RESET_ALL + "A porta 50051 ja esta em uso. Feche o outro processo ou mude a porta.\n")
    except KeyboardInterrupt: # Ctrl + C
        print(Fore.BLUE + "\nServidor finalizado.\n" + Style.RESET_ALL)
