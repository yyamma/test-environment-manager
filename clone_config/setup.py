#!/usr/bin/env python3
import os
import sys
import subprocess
import yaml
import lxc
import requests
import json
import apport
import encodings.idna
sys.path.append("../common")
import definevalue
from utils import *
import clone

def prepare_setup_zabbix_server(argument):
    print("Not implemented yet: prepare_setup_zabbix_server")
    return argument


def run_setup_zabbix_server(argument):
    print("Not implemented yet: run_setup_zabbix_server")


def prepare_setup_zabbix_agent(argument):
    print("Not implemented yet: prepare_setup_zabbix_agent")
    return argument


def run_setup_zabbix_agent(argument):
    print("Not implemented yet: run_setup_zabbix_agent")


def prepare_setup_nagios_server3(argument):
    print("Not implemented yet: prepare_setup_nagios_server3")
    return argument


def run_setup_nagios_server3(argument):
    print("Not implemented yet: run_setup_nagios_server3")


def prepare_setup_nagios_server4(argument):
    print("Not implemented yet: prepare_setup_nagios_server4")
    return argument


def run_setup_nagios_server4(argument):
    print("Not implemented yet: run_setup_nagios_server4")


def prepare_setup_nagios_nrpe(argument):
    nrpe_cfg = open("assets/nrpe.cfg").read()
    argument.append(nrpe_cfg)
    return argument


def run_setup_nagios_nrpe(argument):
    NRPE_FILE_PATH = "/etc/nagios/nrpe.cfg"
    os.remove(NRPE_FILE_PATH)

    nrpe_cfg = open(NRPE_FILE_PATH, "w")
    nrpe_cfg.write(argument[0])
    nrpe_cfg.close()


def prepare_setup_redmine(argument):
    file_list = ["database.yml", "configuration.yml", "my_setting",
                 "setting_command.sh"]

    for file_name in file_list:
        read_file = open(file_name)
        lines = read_file.readlines()
        read_file.close()

        argument.append(lines)

    return argument


def create_setup_file(file_path, argument):
    file = open(file_path, "w")
    file.writelines(argument)
    file.close()


def print_request_responce(request_result):
    if request_result.status_code == 201:
        print("Successed to create a new project")

    else:
        print("Failed to create a new project.")
        print(request_result.text + "\n")


def run_setup_redmine(argument):
    os.chdir("/var/lib/redmine")

    file_paths = ["/var/lib/redmine/config/database.yml",
                  "/var/lib/redmine/config/configuration.yml",
                  "/var/lib/redmine/my_setting",
                  "/var/lib/redmine/setting_command.sh"]

    project_data = {
                    "project":{
                      "name": argument[0]["project_name"],
                      "identifier": argument[0]["project_id"]
                    }
                   }

    send_data = json.dumps(project_data)

    for each_path_and_argument in range(len(file_paths)):
        create_setup_file(file_paths[each_path_and_argument],
                          argument[each_path_and_argument + 1])

    subprocess.call(["sh","setting_command.sh"])

    request_result = requests.post("http://127.0.0.1/projects.json",
                                   data = send_data,
                                   headers = {"Content-Type": "application/json"},
                                   auth = ("admin", "admin"))
    print_request_responce(request_result)

    subprocess.call(["service", "httpd", "restart"])


def prepare_setup_fluentd(argument):
    td_agent_conf = open("assets/td-agent.conf").read()
    argument.append(td_agent_conf)
    return argument


def run_setup_fluentd(argument):
    TD_AGENT_FILE_PATH = "/etc/td-agent/td-agent.conf"
    os.remove(TD_AGENT_FILE_PATH)

    td_agent_conf = open(TD_AGENT_FILE_PATH, "w")
    td_agent_conf.write(argument[0])
    td_agent_conf.close()


SETUP_FUNCTIONS = {"zabbix-server": run_setup_zabbix_server,
                   "zabbix-agent": run_setup_zabbix_agent,
                   "nagios3": run_setup_nagios_server3,
                   "nagios4": run_setup_nagios_server4,
                   "nrpe": run_setup_nagios_nrpe,
                   "redmine": run_setup_redmine,
                   "fluentd": run_setup_fluentd}

PREPARE_FUNCTIONS = {run_setup_zabbix_server: prepare_setup_zabbix_server,
                     run_setup_zabbix_agent: prepare_setup_zabbix_agent,
                     run_setup_nagios_server3: prepare_setup_nagios_server3,
                     run_setup_nagios_server4: prepare_setup_nagios_server4,
                     run_setup_nagios_nrpe: prepare_setup_nagios_nrpe,
                     run_setup_redmine: prepare_setup_redmine,
                     run_setup_fluentd: prepare_setup_fluentd}


def get_function_and_arguments(info_of_container_name, list_of_key_in_info):
    list_of_setup_function = SETUP_FUNCTIONS.keys()
    return_list = []
    for key_in_info in list_of_key_in_info:
        if not key_in_info in list_of_setup_function:
            continue
        else:
            info_of_function = info_of_container_name[key_in_info]
            function_argument = []
            if info_of_function is not None:
                function_argument.append(info_of_function)
            return_list.append([SETUP_FUNCTIONS[key_in_info], function_argument])

    return return_list


def get_container_name_and_function_to_setup(config_info_name):
    list_of_container_name = config_info_name.keys()
    return_list = []
    for container_name in list_of_container_name:
        info_of_container_name = config_info_name[container_name]
        list_of_key_in_info = info_of_container_name.keys()
        setup_functions = get_function_and_arguments(info_of_container_name,
                                                     list_of_key_in_info)
        return_list.append([container_name, setup_functions])

    return return_list


def setup_container(container_name, run_function_names):
    print("Start setup process: %s" % container_name)
    container = lxc.Container(container_name)
    container.start()
    container.get_ips(timeout=definevalue.TIMEOUT_VALUE)

    for (run_function_name, argument) in run_function_names:
        run_argument = PREPARE_FUNCTIONS[run_function_name](argument)
        container.attach_wait(run_function_name, run_argument)

    shutdown_container(container)


def setup_containers(list_of_setup_containers):
    for (container_name, setup_function) in list_of_setup_containers:
        setup_container(container_name, setup_function)


def start_setup(yaml_file_path):
    config_info = clone.get_config_info(yaml_file_path)
    list_of_setup_containers = \
        get_container_name_and_function_to_setup(config_info)
    setup_containers(list_of_setup_containers)


if __name__ == '__main__':
    argvs = sys.argv
    exit_if_user_run_this_as_general_user()
    exit_if_argument_is_not_given(len(argvs))

    start_setup(argvs[1])
