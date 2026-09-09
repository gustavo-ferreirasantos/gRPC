from __future__ import print_function

import grpc
import tasks_pb2
import tasks_pb2_grpc
from colorama import Fore, Style
from tabulate import tabulate
from datetime import datetime, timezone
from google.protobuf import timestamp_pb2

STATUS_MAP = {
    0: "PENDING",
    10: "COMPLETED",
    20: "ERROR",
}

def formatar_hora(task):
    dt = datetime.fromtimestamp(task.created_at.seconds)
    return f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}.{task.created_at.nanos // 1_000_000:03d}"

def formatar_data_limit(task):
    if not task.HasField("data_limit"):
        return "-"
    dt = datetime.fromtimestamp(task.data_limit.seconds)
    return f"{dt.day:02d}/{dt.month:02d}/{dt.year} {dt.hour:02d}:{dt.minute:02d}"

def imprimir_tabela(lista_tarefas):
  cabecalho = ['id', 'título', 'descrição', 'status', 'data limit', 'hora criada']
  dados = []
  for task in lista_tarefas:
    dados.append([
      task.id,
      task.title,
      task.description,
      STATUS_MAP.get(task.status, str(task.status)),
      formatar_data_limit(task),
      formatar_hora(task),
    ])
  print(tabulate(dados, headers=cabecalho, tablefmt="grid"))

def criar_tarefa(stub, titulo: str, descricao: str, data_limit=None, status=0) -> tasks_pb2.CreateTaskResponse:
  task_kwargs = dict(title=titulo, description=descricao, status=status) #Usa dicionário para empacotar argumentos
  if data_limit:
    task_kwargs["data_limit"] = data_limit
  tarefa = stub.CreateTask(tasks_pb2.CreateTaskRequest(
      task=tasks_pb2.Task(**task_kwargs)
  ))
  return tarefa

def listar_tarefas(stub, exibir=True):
  response = stub.GetTasks(tasks_pb2.GetTasksRequest())
  if exibir: #Para não exibir quando for deletar tudo
    print(Fore.YELLOW + "\n=== Listando tarefas ===" + Style.RESET_ALL)
    imprimir_tabela(response.tasks)
  return response.tasks

def atualizar_tarefa(stub, id: int, titulo: str, descricao: str, data_limit=None, status=0) -> tasks_pb2.UpdateTaskResponse:
  task_kwargs = dict(id=id, title=titulo, description=descricao, status=status)
  if data_limit:
    task_kwargs["data_limit"] = data_limit
  updated = stub.UpdateTask(tasks_pb2.UpdateTaskRequest(
    task=tasks_pb2.Task(**task_kwargs)
  ))
  return updated

def deletar_tarefa(stub, id: int) -> tasks_pb2.DeleteTaskResponse:
  deleted = stub.DeleteTask(tasks_pb2.DeleteTaskRequest(id=id))
  return deleted


def teste_tarefas(stub):
  # Criar tarefas
  print(Fore.BLUE + "=== Criando tarefas ===" + Style.RESET_ALL)
  t1 = criar_tarefa(stub, titulo="Estudar Cálculo", descricao="Aprender os conceitos básicos")

  dl = timestamp_pb2.Timestamp()
  dl.FromSeconds(int(datetime(2026, 9, 10, tzinfo=timezone.utc).timestamp()))
  t2 = criar_tarefa(stub, titulo="Implementar CRUD", descricao="Criar operacoes no SQLite", data_limit=dl)

  listar_tarefas(stub)

  # Atualizar tarefa
  print(Fore.YELLOW + "\n=== Atualizando tarefa 1 ===" + Style.RESET_ALL)
  atualizar_tarefa(stub, id=t1.task.id, titulo="Estudar Cálculo Avançado", descricao="Aprender derivadas e integrais")

  # Deletar tarefa
  print(Fore.RED + "\n=== Deletando tarefa 2 ===" + Style.RESET_ALL)
  deletar_tarefa(stub, id=t2.task.id)

  # Listar tarefas finais
  listar_tarefas(stub)

# Wrappers
def criar_tarefa_wrapper(stub):
  titulo = input("Título: ")
  descricao = input("Descrição: ")
  data = None
  tem_data = True if input("Deseja definir data limite? [s/n]: ") == 's' else False
  if tem_data:
    ano = int(input("Ano: "))
    mes = int(input("Mês: "))
    dia = int(input("Dia: "))
    hora = int(input("Hora: "))
    minuto = int(input("Minuto: "))
    data = timestamp_pb2.Timestamp()
    data.FromSeconds(int(datetime(ano, mes, dia, hora, minuto, tzinfo=timezone.utc).timestamp()))
  return criar_tarefa(stub, titulo, descricao, data)

def get_tarefa_wrapper(stub):
  id = int(input("ID: "))
  task = stub.GetTaskById(tasks_pb2.GetTaskByIdRequest(id=id)).task
  imprimir_tabela([task])
  return task

def deletar_tarefa_wrapper(stub):
  id = int(input("ID: "))
  task = stub.DeleteTask(tasks_pb2.DeleteTaskRequest(id=id)).task
  print("Tarefa deletada")
  return task

def deletar_tudo_wrapper(stub):
  deletar = True if input("Tem certeza? [s/n]: ") == 's' else False
  if not deletar:
    print("Abortando...")
    return None
  lista_tarefas = listar_tarefas(stub, exibir=False)
  for task in lista_tarefas:
    deletar_tarefa(stub, task.id)
  print("Todas as tarefas foram deletadas")
  return lista_tarefas