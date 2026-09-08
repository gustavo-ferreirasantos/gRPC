from __future__ import print_function

import grpc
import tasks_pb2
import tasks_pb2_grpc

def teste_tarefas(stub):
    # Criar tarefas
    print("=== Criando tarefas ===")
    t1 = stub.CreateTask(tasks_pb2.CreateTaskRequest(
        task=tasks_pb2.Task(title="Estudar gRPC", description="Aprender os conceitos basicos")
    ))
    print(f"Criada: id={t1.task.id}, title={t1.task.title}")

    t2 = stub.CreateTask(tasks_pb2.CreateTaskRequest(
        task=tasks_pb2.Task(title="Implementar CRUD", description="Criar operacoes no SQLite")
    ))
    print(f"Criada: id={t2.task.id}, title={t2.task.title}")

    # Listar tarefas
    print("\n=== Listando tarefas ===")
    response = stub.GetTasks(tasks_pb2.GetTasksRequest())
    for task in response.tasks:
        print(f"  id={task.id}, title={task.title}, desc={task.description}")

    # Atualizar tarefa
    print("\n=== Atualizando tarefa 1 ===")
    updated = stub.UpdateTask(tasks_pb2.UpdateTaskRequest(
        task=tasks_pb2.Task(id=t1.task.id, title="Estudar gRPC Avancado", description="Aprender streaming e interceptors")
    ))
    print(f"Atualizada: id={updated.task.id}, title={updated.task.title}, desc={updated.task.description}")

    # Deletar tarefa
    print("\n=== Deletando tarefa 2 ===")
    deleted = stub.DeleteTask(tasks_pb2.DeleteTaskRequest(id=t2.task.id))
    print(f"Deletada: id={deleted.task.id}, title={deleted.task.title}")

    # Listar tarefas finais
    print("\n=== Tarefas restantes ===")
    response = stub.GetTasks(tasks_pb2.GetTasksRequest())
    for task in response.tasks:
        print(f"  id={task.id}, title={task.title}, desc={task.description}")

def run():
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = tasks_pb2_grpc.TasksStub(channel)
            teste_tarefas(stub)
    except grpc._channel._InactiveRpcError:
        print("Erro: Servidor nao esta rodando. Inicie o servidor primeiro.")


if __name__ == '__main__':
    run()
