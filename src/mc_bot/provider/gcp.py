from __future__ import annotations
from enum import Enum
from typing import List
from collections.abc import Iterable
from google.cloud import compute_v1

import logging

def get_instance_ipv4(
        logger: logging.Logger,
        project_id: str,
        zone: str,
        instance_name: str
) -> List[str]:

    logger.info(f"retrieving instance info for {instance_name}")

    instance_client = compute_v1.InstancesClient()
    instance = instance_client.get(
        project=project_id, zone=zone, instance=instance_name
    )
    ips = []
    if not instance.network_interfaces:
        return ips
    for interface in instance.network_interfaces:
        for config in interface.access_configs:
            if config.type_ == "ONE_TO_ONE_NAT":
                ips.append(config.nat_i_p)

    logger.info(f"got ips {ips}")
    return ips


def start_instance(
        logger: logging.Logger,
        project_id: str,
        zone: str,
        instance_name: str,
) -> None:

    logger.info("start server request received")
    instance_client = compute_v1.InstancesClient()

    operation = instance_client.start(
        project=project_id, zone=zone, instance=instance_name
    )
    wait_for_extended_operation(logger, operation, "instance start")

def stop_instance(
        logger: logging.Logger,
        project_id: str,
        zone: str,
        instance_name: str,
) -> None:

    logger.info("stop server request received")
    instance_client = compute_v1.InstancesClient()

    operation = instance_client.stop(
        project=project_id, zone=zone, instance=instance_name
    )

    wait_for_extended_operation(logger, operation, "instance stop")

def wait_for_extended_operation(
        logger: logging.Logger,
        operation: ExtendedOperation,
        verbose_name: str = "operation",
        timeout: int = 300,
) -> Any:

    result = operation.result(timeout=timeout)

    if operation.error_code:
        logger.error(
            f"Error during {verbose_name}: [Code: {operation.error_code}]: {operation.error_message}",
            file=sys.stderr, flush=True)

        logger.Error(f"Operation ID: {operation.name}", file=sys.stderr, flush=True)

        raise operation.exception() or RuntimeError(operation.error_message)

    if operation.warnings:
        logger.warning(f"Warnings during {verbose_name}:\n", file=sys.stderr, flush=True)

        for warning in operation.warnings:
            logger.warning(f" - {warning.code}: {warning.message}",
                           file=sys.stderr, flush=True)

    return result
