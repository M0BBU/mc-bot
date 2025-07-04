from __future__ import annotations
from collections.abc import Iterable
from google.cloud import compute_v1

import logging

def start_instance(
        logger: logging.Logger,
        project_id: str,
        zone: str,
        instance_name: str,
) -> None:
    """
    Starts a stopped Google Compute Engine instance (with unencrypted disks).
    Args:
        project_id: project ID or project number of the Cloud project your instance belongs to.
        zone: name of the zone your instance belongs to.
        instance_name: name of the instance your want to start.
    """
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
    """
    Starts a stopped Google Compute Engine instance (with unencrypted disks).
    Args:
        project_id: project ID or project number of the Cloud project your instance belongs to.
        zone: name of the zone your instance belongs to.
        instance_name: name of the instance your want to start.
    """
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
    """
    Waits for the extended (long-running) operation to complete.

    If the operation is successful, it will return its result.
    If the operation ends with an error, an exception will be raised.
    If there were any warnings during the execution of the operation
    they will be printed to sys.stderr.

    Args:
        operation: a long-running operation you want to wait on.
        verbose_name: (optional) a more verbose name of the operation,
            used only during error and warning reporting.
        timeout: how long (in seconds) to wait for operation to finish.
            If None, wait indefinitely.

    Returns:
        Whatever the operation.result() returns.

    Raises:
        This method will raise the exception received from `operation.exception()`
        or RuntimeError if there is no exception set, but there is an `error_code`
        set for the `operation`.

        In case of an operation taking longer than `timeout` seconds to complete,
        a `concurrent.futures.TimeoutError` will be raised.
    """
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
