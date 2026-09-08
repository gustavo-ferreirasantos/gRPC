from concurrent import futures
import logging

import grpc
import tasks_pb2
import tasks_pb2_grpc
import database


class TasksService(tasks_pb2_grpc.TasksServicer):

    def GetTasks(self, request, context):
        tasks = database.get_all_tasks()
        return tasks_pb2.GetTasksResponse(
            tasks=[
                tasks_pb2.Task(
                    id=t["id"],
                    title=t["title"],
                    description=t["description"],
                )
                for t in tasks
            ]
        )

    def GetTaskById(self, request, context):
        task = database.get_task_by_id(request.id)
        if not task:
            context.abort(grpc.StatusCode.NOT_FOUND, "Task not found")
        return tasks_pb2.GetTaskByIdResponse(
            task=tasks_pb2.Task(
                id=task["id"],
                title=task["title"],
                description=task["description"],
            )
        )

    def CreateTask(self, request, context):
        task = database.create_task(request.task.title, request.task.description)
        return tasks_pb2.CreateTaskResponse(
            task=tasks_pb2.Task(
                id=task["id"],
                title=task["title"],
                description=task["description"],
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
            )
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    tasks_pb2_grpc.add_TasksServicer_to_server(TasksService(), server)

    server.add_insecure_port('[::]:50051')

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    print("Starting server in: %s" % ('localhost:50051'))
    serve()
