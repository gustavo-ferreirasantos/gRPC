# gRPC - Sistema de Tarefas

Sistema cliente-servidor usando gRPC com SQLite para gerenciamento de tarefas.

## Pré-requisitos

- Python 3.11+
- Docker Desktop (para rodar via Docker)


## Compilação do Protocol Buffers
Execute os comandos no diretório raiz do repositório

**Servidor**
```bash
python -m grpc_tools.protoc -I./protos --python_out=./server --pyi_out=./server --grpc_python_out=./server ./protos/tasks.proto
```

**Cliente**
```bash
python -m grpc_tools.protoc -I./protos --python_out=./client --pyi_out=./client --grpc_python_out=./client ./protos/tasks.proto
```

## Rodando localmente

### Servidor

```bash
cd server
pip install -r requirements.txt
python server.py
```

### Cliente (em outro terminal)

```bash
cd client
pip install -r requirements.txt
python client.py
```

## Rodando via Docker

### Terminal 1

```bash
# Parar containers antigos
docker-compose down

# Construir e iniciar todos os containers
docker-compose up --build -d
```

```bash
# Conectar ao client
docker-compose exec client python client.py
```

### Terminal 2

```bash
# Conectar ao client2
docker-compose exec client2 python client.py
```

### Visualizar ips dos containers

```bash
docker network inspect grpc_default
```


### Parar tudo

```bash
docker-compose down
```

### Ver logs

```bash
docker-compose logs -f
```

### Autores

- Gustavo Ferreira Santos
- Lorenzo de Souza Oliveira
- Luiz Antonio Lacerda Amorim
