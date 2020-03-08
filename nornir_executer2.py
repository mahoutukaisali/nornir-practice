# note that these imports are only needed if you are annotating your code with types
from typing import Dict

from nornir import InitNornir
from nornir.core import Nornir
from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult, MultiResult, Result, Task
import json

nr = InitNornir(
  core={"num_workers": 100},
  inventory={
    "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
        "options": {
            "host_file": "inventory/hosts.yaml",
            "group_file": "inventory/groups.yaml"
          }
  }
)

class PrintResult:
    def task_started(self, task: Task) -> None:
        print(f">>> starting: {task.name}")

    def task_completed(self, task: Task, result: AggregatedResult) -> None:
        print(f">>> completed: {task.name}")

    def task_instance_started(self, task: Task, host: Host) -> None:
        pass

    def task_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        print(f"  - {host.name}: - {result.result}")

    def subtask_instance_started(self, task: Task, host: Host) -> None:
        pass  # to keep example short and sweet we ignore subtasks

    def subtask_instance_completed(self, task: Task, host: Host, result: MultiResult) -> None:
        pass  # to keep example short and sweet we ignore subtasks

class SaveResultToDict:
    def __init__(self, data: Dict[str, None]) -> None:
        self.data = data

    def task_started(self, task: Task) -> None:
        self.data[task.name] = {}
        self.data[task.name]["started"] = True

    def task_completed(self, task: Task, result: AggregatedResult) -> None:
        self.data[task.name]["completed"] = True

    def task_instance_started(self, task: Task, host: Host) -> None:
        self.data[task.name][host.name] = {"started": True}

    def task_instance_completed(self, task: Task, host: Host, result: MultiResult) -> None:
        self.data[task.name][host.name] = {
            "completed": True,
            "result": result.result,
        }

    def subtask_instance_started(self, task: Task, host: Host) -> None:
        pass  # to keep example short and sweet we ignore subtasks

    def subtask_instance_completed(self, task: Task, host: Host, result: MultiResult) -> None:
        pass  # to keep example short and sweet we ignore subtasks

def greeter(task: Task, greet: str, onemore: str) -> Result:
    return Result(host=task.host, result=f"{greet, onemore}! my name is {task.host.name}")

data = {}  # this is the dictionary where SaveResultToDict will store the information

# similary to .filter, with_processors returns a copy of the nornir object but with
# the processors assigned to it. Let's now use the method to assign both processors
nr_with_processors = nr.with_processors([SaveResultToDict(data), PrintResult()])

# now we can use nr_with_processors to execute our greeter task
## greeterに引数とtypeを渡せばいくらでもキーを生成できる
nr_with_processors.run(
    name="hi!",
    task=greeter,
    greet="hi",
    onemore="hihi",
)
nr_with_processors.run(
    name="bye!",
    task=greeter,
    greet="bye",
    onemore="byebye",
)

print(json.dumps(data, indent=4))