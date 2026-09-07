from concurrent import futures
import logging

import grpc
import tasks_pb2
import tasks_pb2_grpc

class TasksService(tasks_pb2_grpc.TasksServicer):

    def __init__(self):
        pass

    def GetTasks(self, request, context):
        return tasks_pb2.getTasksResponse(tasks=[
            tasks_pb2.Task(
                id="1",
                title="dsd",
                description="dddddddddddds"
            )
        ])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    tasks_pb2_grpc.add_TasksServicer_to_server(TasksService() ,server)

    server.add_insecure_port('[::]:50051')

    server.start()

    server.wait_for_termination()


if __name__ == '__main__':

    logging.basicConfig()
    print("Starting server in: %s" % ('localhost:50051')) 

    serve()                                               







# if __name__ == "__main__":