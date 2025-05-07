"""Command line handling"""
from antismash_models import AsyncJob
import os

from dispatcher.errors import InvalidJobType


def create_commandline(job, conf) -> list[str]:
    """Create the command line to run an antiSMASH job

    :param job: Job object representing the job to run
    :param conf: RunConfig object with the runtime configuration
    :return: A list of strings with the command line args
    """

    if job.jobtype not in ["epssmash"]:
        raise InvalidJobType(job.jobtype)

    job_folder = _get_job_folder(job)

    args = [
        job.filename,
        '--cpus', str(conf.cpus),
        '--taxon', job.taxon,
        '--output-dir', job_folder,
        '--logfile', os.path.join(job_folder, '{}.log'.format(job.job_id)),
        '--debug',  # TODO: read this from the config later
        '--limit', str(conf.limit),
    ]

    if job.clusterblast:
        args.append('--cb-general')
    return args


def _get_job_folder(job: AsyncJob) -> str:
    """Get the folder to store the job into inside the container."""
    return os.path.join(os.sep, 'data', 'antismash', 'upload', job.job_id)
