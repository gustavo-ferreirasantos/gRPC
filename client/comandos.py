from __future__ import print_function

import grpc
import tasks_pb2
import tasks_pb2_grpc
from colorama import Fore, Style
from tabulate import tabulate
from datetime import datetime, timezone
from google.protobuf import timestamp_pb2
from zoneinfo import ZoneInfo
LOCAL_TZ = ZoneInfo("America/Bahia") 

STATUS_MAP = {
  0: "PENDING",
  10: "COMPLETED",
  20: "ERROR",
}

def ler_data():
  while True:
    try:
      ano = int(input("Ano: "))
      mes = int(input("Mês: "))
      dia = int(input("Dia: "))
      hora = int(input("Hora: "))
      minuto = int(input("Minuto: "))
      dt_local = datetime(ano, mes, dia, hora, minuto, tzinfo=LOCAL_TZ)
      data = timestamp_pb2.Timestamp()
      data.FromDatetime(dt_local)
      return data
    except (ValueError, OverflowError):
      print(Fore.RED + "Data inválida, tente novamente.\n" + Style.RESET_ALL)

def ler_status(status_atual):
  try:
    aux = int(input("Novo Status: "))
  except (ValueError, OverflowError):
    print("Status inválido, colocando para ERROR")
    return 20
  if aux not in (0, 10, 20):
    print("Status Inválido, mantendo Status atual")
    return status_atual
  return aux

def formatar_hora(task):
    dt = datetime.fromtimestamp(task.created_at.seconds, tz=LOCAL_TZ)
    return f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}.{task.created_at.nanos // 1_000_000:03d}"

def formatar_data_limit(task):
    if not task.HasField("data_limit"):
        return "-"
    dt = datetime.fromtimestamp(task.data_limit.seconds, tz=LOCAL_TZ)
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

# Lida com o erro de tarefa não encontrada, usando função genérica e classe como parâmetro
# Usar o dicionário para os argumentos e fazer unpacking dele aumenta a flexibilidade
def not_found_handler(funcao, classe_interna, argumentos: dict):
  try:
    task = funcao(classe_interna(**argumentos)).task
  except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
      print(Fore.RED + "Erro: " + Style.RESET_ALL + "Tarefa não encontrada")
      return None
    else:
      print("Erro desconhecido")
      exit(1)
  return task

def criar_tarefa_wrapper(stub):
  titulo = input("Título: ")
  descricao = input("Descrição: ")
  data = None
  tem_data = True if input("Deseja definir data limite? [s/n]: ") == 's' else False
  if tem_data:
    data = ler_data()
  return criar_tarefa(stub, titulo, descricao, data).task

def get_tarefa_wrapper(stub):
  id = int(input("ID: "))
  task = not_found_handler(stub.GetTaskById, tasks_pb2.GetTaskByIdRequest, {'id': id})
  if task is not None:
    imprimir_tabela([task])
    return task
  return None

def update_tarefa_wrapper(stub):
  id = int(input("ID: "))
  task = not_found_handler(stub.GetTaskById, tasks_pb2.GetTaskByIdRequest, {'id': id})
  if task is None:
    return None
  imprimir_tabela([task])
  titulo = task.title
  descricao = task.description
  status = task.status
  data = task.data_limit if task.HasField("data_limit") else None
  print("Selecione o que você deseja mudar\n")
  print("t - Título")
  print("d - Descrição")
  print("s - Status")
  print("ts - Data limite")
  print("a - tudo\n")
  selecionado = input()

  match selecionado:
    case "t":
      titulo = input("Novo Título: ")
    case "d":
      descricao = input("Nova Descrição: ")
    case "s":
      status = ler_status(status)
    case "ts":
      data = ler_data()
    case "a":
      titulo = input("Novo Título: ")
      descricao = input("Nova Descrição: ")
      status = ler_status(status)
      data = ler_data()
    case _:
      print("Opção inválida")
      return None
  return atualizar_tarefa(stub, id = id, titulo= titulo, descricao=descricao, data_limit=data, status=status).task




def deletar_tarefa_wrapper(stub):
  id = int(input("ID: "))
  task = not_found_handler(stub.DeleteTask, tasks_pb2.DeleteTaskRequest, {'id': id})
  if task is not None:
    print("Tarefa deletada")
    return task
  return None

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