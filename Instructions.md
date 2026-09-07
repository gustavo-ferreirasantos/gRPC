



python3 -m venv venv
.\venv\Scripts\Activate.ps1 

pip install grpcio
pip install grpcio-tools

pip freeze > requirements.txt

python -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/tasks.proto



