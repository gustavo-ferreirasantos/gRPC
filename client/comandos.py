from __future__ import print_function

import grpc
import tasks_pb2
import tasks_pb2_grpc
from colorama import Fore, Style

def criar_tarefa(stub, titulo: str, descricao: str) -> tasks_pb2.CreateTaskResponse:
  # CreateTaskRequest é o dado que o cliente envia, e CreateTask é a função chamada remotamente
  tarefa = stub.CreateTask(tasks_pb2.CreateTaskRequest(
      task=tasks_pb2.Task(title=titulo, description=descricao)
  ))
  print(f"Criada: id={tarefa.task.id}, title={tarefa.task.title}, created_at={tarefa.task.created_at}")
  return tarefa

def listar_tarefas(stub):
  print(Fore.YELLOW + "\n=== Listando tarefas ===" + Style.RESET_ALL)
  response = stub.GetTasks(tasks_pb2.GetTasksRequest())
  for task in response.tasks:
    print(f"id={task.id}, title={task.title}, desc={task.description}, created_at={task.created_at}")

def atualizar_tarefa(stub, id: int, titulo: str, descricao: str) -> tasks_pb2.UpdateTaskResponse:
  updated = stub.UpdateTask(tasks_pb2.UpdateTaskRequest(
    task=tasks_pb2.Task(id=id, title=titulo, description=descricao)
  ))
  print(f"Atualizada: id={updated.task.id}, title={updated.task.title}, desc={updated.task.description}, created_at={updated.task.created_at}")
  return updated

def deletar_tarefa(stub, id: int) -> tasks_pb2.DeleteTaskResponse:
  deleted = stub.DeleteTask(tasks_pb2.DeleteTaskRequest(id=id))
  print(f"Deletada: id={deleted.task.id}, title={deleted.task.title}, created_at={deleted.task.created_at}")
  return deleted


def teste_tarefas(stub):
  # Criar tarefas
  print(Fore.BLUE + "=== Criando tarefas ===" + Style.RESET_ALL)
  t1 = criar_tarefa(stub, titulo= "Estudar Cálculo", descricao= "Aprender os conceitos básicos")
  t2 = criar_tarefa(stub, titulo="Implementar CRUD", descricao="Criar operacoes no SQLite")

  # Listar tarefas
  listar_tarefas(stub)

  # Atualizar tarefa
  print(Fore.YELLOW + "\n=== Atualizando tarefa 1 ===" + Style.RESET_ALL)
  atualizar_tarefa(stub, id = t1.task.id, titulo = "Estudar Cálculo Avançado", descricao = "Aprender derivadas e integrais")

  # Deletar tarefa
  print(Fore.RED + "\n=== Deletando tarefa 2 ===" + Style.RESET_ALL)
  deletar_tarefa(stub, id= t2.task.id)

  # Listar tarefas finais
  # print(Fore.YELLOW + "\n=== Tarefas restantes ===" + Style.RESET_ALL)
  listar_tarefas(stub)

