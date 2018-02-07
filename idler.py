"""
Checks all RStudio deployments and idles those matching criteria
"""

from datetime import datetime, timezone
import logging

from kubernetes import client, config


IDLED = 'idled'
IDLED_AT = 'mojanalytics.xyz/idled-at'


api = None
log = logging.getLogger(__name__)


def idle_deployments():
    for deployment in eligible_deployments():
        idle(deployment)


def eligible_deployments():
    deployments = api.list_deployment_for_all_namespaces(
        label_selector=f'!{IDLED},app=rstudio')
    return filter(eligible, deployments.items)


def eligible(deployment):
    return True


def idle(deployment):
    mark_idled(deployment)
    # redirect_to_unidler(deployment)
    # zero_replicas(deployment)
    write_changes(deployment)
    log.debug(
        f'{deployment.metadata.name} '
        f'in namespace {deployment.metadata.namespace} '
        f'idled')


def mark_idled(deployment):
    timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    deployment.metadata.labels[IDLED] = 'true'
    deployment.metadata.annotations[IDLED_AT] = (
        f'{timestamp},{deployment.spec.replicas}')


def redirect_to_unidler(deployment):
    pass


def zero_replicas(deployment):
    deployment.spec.replicas = 0


def write_changes(deployment):
    api.patch_namespaced_deployment(
        deployment.metadata.name,
        deployment.metadata.namespace,
        deployment
    )


if __name__ == '__main__':
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()

    api = client.AppsV1beta1Api()

    idle_deployments()