from __future__ import print_function

import grpc
import tasks_pb2
import tasks_pb2_grpc

def run():
    response = []

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = tasks_pb2_grpc.TasksStub(channel)

        response = stub.getTasks(tasks_pb2.getTasksRequest())

    print(response.taks)


if __name__ == '__main__':
    run()

