#!/usr/bin/env python3
import definevalue

def print_success_message(name):
    print("Create Container: %s" % name)


def print_exists_message(name):
    print("Container already exists: %s" % name)


def print_container_name(name):
    print("Container name: %s" % name)


def print_new_line():
    print("")


def shutdown_container(container):
    print_new_line()
    if not container.shutdown(definevalue.TIMEOUT_VALUE):
        container.stop()
