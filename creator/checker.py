#!/usr/bin/env python3
import lxc
import os
import sys
import os.path


containers_name = {
    "base": "env_base",
    "zabbix_server22": "env_zabbix_server22",
    "zabbix_server20": "env_zabbix_server20",
    "zabbix_agent22": "env_zabbix_agent22",
    "zabbix_agent20": "env_zabbix_agent20",
    "nagios_server3": "env_nagios_server3",
    "nagios_server4": "env_nagios_server4",
    "nagios_nrpe": "env_nagios_nrpe",
    "hatohol_build": "env_hatohol_build",
    "hatohol_rpm": "env_hatohol_rpm",
    "fluentd": "env_fluentd",
    "redmine": "env_redmine"
}


def print_container_exist_message(name):
    print("Container \"%s\": True" % name)


def print_container_non_exist_message(name):
    print("Container \"%s\": false" % name)


def print_container_name(name):
    print("Container name: %s" % name)


def is_container_existed(container):
    if lxc.Container(containers_name[container]).defined:
        print_container_exist_message(containers_name[container])
    else:
        print_container_non_exist_message(containers_name[container])


def check_container_exist():
    is_container_existed("base")
    is_container_existed("zabbix_server22")
    is_container_existed("zabbix_server20")
    is_container_existed("zabbix_agent22")
    is_container_existed("zabbix_agent20")
    is_container_existed("nagios_server3")
    is_container_existed("nagios_server4")
    is_container_existed("nagios_nrpe")
    is_container_existed("hatohol_build")
    is_container_existed("hatohol_rpm")
    is_container_existed("fluentd")
    is_container_existed("redmine")


def is_provided_file_existence(file_path):
    if os.path.isfile(file_path):
        print("The file is existed: \"%s\"" % file_path)
    else:
        print("The file isn't existed: \"%s\"" % file_path)


def is_provided_directory_existence(directory_path):
    if os.path.isdir(directory_path):
        print("The directory is existed: \"%s\"" % directory_path)
    else:
        print("The directory is existed: \"%s\"" % directory_path)


def check_zabbix_server_container(container_name):
    print_container_name(container_name)
    container = lxc.Container(containers_name[container_name])
    container.start()
    container.attach_wait(is_provided_file_existence, "/usr/sbin/zabbix_server")
    container.attach_wait(is_provided_file_existence, "/usr/sbin/zabbix_agentd")

    if not container.shutdown(30):
        container.stop()


def check_zabbix_agent_container(container_name):
    print_container_name(container_name)
    container = lxc.Container(containers_name[container_name])
    container.start()
    container.attach_wait(is_provided_file_existence, "/usr/sbin/zabbix_agentd")

    if not container.shutdown(30):
        container.stop()

def check_nagios_server3_container():
    container_name = "nagios_server3"
    print_container_name(container_name)
    container = lxc.Container(containers_name[container_name])
    container.start()
    container.attach_wait(is_provided_file_existence, "/usr/sbin/nagios")

    if not container.shutdown(30):
        container.stop()


def check_nagios_server4_container():
    container_name = "nagios_server4"
    print_container_name(container_name)
    container = lxc.Container(containers_name[container_name])
    container.start()
    container.attach_wait(is_provided_file_existence, "/usr/local/nagios/bin/nagios")

    if not container.shutdown(30):
        container.stop()


def check_hatohol_container():
    container_name = containers_name["hatohol_rpm"]
    print_container_name(container_name)
    container = lxc.Container(container_name)
    container.start()
    container.attach_wait(is_provided_file_existence, "/usr/sbin/hatohol")

    if not container.shutdown(30):
        container.stop()


if __name__ == '__main__':
    if not os.geteuid() == 0:
        print("You need root permission to use this script.")
        sys.exit(1)

    check_container_exist()
    check_hatohol_container()