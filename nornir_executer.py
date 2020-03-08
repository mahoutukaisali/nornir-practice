from nornir import InitNornir
from nornir.core.deserializer.inventory import InventoryElement
import json
import logging

''' Retrieve data from here'''
## Initialize nornir config file programmatically.
## It can be choised how to specify in nornir_executer.py or config.yaml
#nr = InitNornir(config_file="config.yaml")

##  initialize nornir programmatically without a configuration file:
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

## with a combination of both above methods
#nr = InitNornir(core={"num_workers": 50}) 

#print(nr.config.core.num_workers)
#print("hostname: {}".format(nr.inventory.hosts))
#print(nr.inventory.groups)
host = nr.inventory.hosts["host1.cmh"]
#print(host["domain"])

## retrieve under the data key
#print(host.keys())
#print(json.dumps(InventoryElement.schema(), indent=4))

## retrievied data supposed to both site=cmh and role=host
#print(nr.filter(site="cmh", role="host").inventory.hosts.keys())
print(nr.inventory.children_of_group("cmh"))


''' Execute tasks from here '''
from nornir.plugins.tasks import commands, networking, text
from nornir.plugins.functions.text import print_title, print_result

#result = cmh_hosts.run(task=commands.remote_command,
#                       command="show version")

## which just prints on screen the result of an executed task or group of tasks.
#print_result(result, vars=["stdout"])

def show_version():
    cmh_hosts = nr.filter(site="cmh", role="host")
    result = cmh_hosts.run(task=networking.napalm_get,
                        name="Correct facts",
                        getters=["facts"])
    print_result(result)


def basic_configuration(task):
    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="base.j2",
                 path=f"templates/{task.host.platform}")

    # Save the compiled configuration into a host variable
    task.host["config"] = r.result

    # Deploy that configuration to the device using NAPALM
    task.run(task=networking.napalm_get,
             name="Loading Configuration on the device",
             getters=["facts"])

cmh = nr.filter(site="cmh")
print_title("Playbook to configure the network")
result = cmh.run(task=basic_configuration)
print_result(result, severity_level=logging.DEBUG)