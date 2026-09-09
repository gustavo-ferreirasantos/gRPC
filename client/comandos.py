from __future__ import print_function

import grpc
import tasks_pb2
import tasks_pb2_grpc
from colorama import Fore, Style
from tabulate import tabulate
from datetime import datetime

def imprimir_tabela(lista_tarefas):
  # print(type(lista_tarefas))
  cabecalho = ['id','título','descrição','hora']
  dados = []
  for task in lista_tarefas:
    dt = datetime.fromtimestamp(task.created_at.seconds)
    hora = f"{dt.hour}:{dt.minute}:{dt.second}:{task.created_at.nanos // 1_000_000:03d}"
    dados.append([task.id, task.title, task.description, hora])
    # print(f"id={task.id}, title={task.title}, desc={task.description}, created_at={task.created_at}")
  print(tabulate(dados, headers=cabecalho, tablefmt="grid"))

def criar_tarefa(stub, titulo: str, descricao: str) -> tasks_pb2.CreateTaskResponse:
  # CreateTaskRequest é o dado que o cliente envia, e CreateTask é a função chamada remotamente
  tarefa = stub.CreateTask(tasks_pb2.CreateTaskRequest(
      task=tasks_pb2.Task(title=titulo, description=descricao)
  ))
  # print(f"Criada: id={tarefa.task.id}, title={tarefa.task.title}, created_at={tarefa.task.created_at}")
  imprimir_tabela([tarefa.task])
  return tarefa

def listar_tarefas(stub):
  print(Fore.YELLOW + "\n=== Listando tarefas ===" + Style.RESET_ALL)
  response = stub.GetTasks(tasks_pb2.GetTasksRequest())
  imprimir_tabela(response.tasks)

def atualizar_tarefa(stub, id: int, titulo: str, descricao: str) -> tasks_pb2.UpdateTaskResponse:
  updated = stub.UpdateTask(tasks_pb2.UpdateTaskRequest(
    task=tasks_pb2.Task(id=id, title=titulo, description=descricao)
  ))
  imprimir_tabela([updated.task])
  return updated

def deletar_tarefa(stub, id: int) -> tasks_pb2.DeleteTaskResponse:
  deleted = stub.DeleteTask(tasks_pb2.DeleteTaskRequest(id=id))
  imprimir_tabela([deleted.task])
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

