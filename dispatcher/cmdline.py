"""Command line handling"""
import os

from antismash_models import AsyncJob

from dispatcher.errors import InvalidJobType


def create_commandline(job, conf) -> list[str]:
    """Create the command line to run an antiSMASH job

    :param job: Job object representing the job to run
    :param conf: RunConfig object with the runtime configuration
    :return: A list of strings with the command line args
    """

    if job.jobtype not in conf.jobtype_config:
        raise InvalidJobType(job.jobtype)

    if job.jobtype.startswith("experimentalsmash-"):
        return create_commandline_experimentalsmash(job, conf)

    raise InvalidJobType(job.jobtype)


def create_commandline_experimentalsmash(job, conf) -> list[str]:
    """Create the command line to run experimentalSMASH jobs

    :param job: Job object representing the job to run
    :param conf: RunConfig object with the runtime configuration
    :return: A list of strings with the command line args
    """
    job_folder = _get_job_folder(job)\

    args = [
        job.filename,
        '--cpus', str(conf.cpus),
        '--taxon', job.taxon,
        '--output-dir', job_folder,
        '--logfile', os.path.join(job_folder, f'{job.job_id}.log'),
        '--debug',
        '--limit', str(conf.limit),
        '--experimental-name', _get_experimental_name(job)
    ]

    if job.gff3:
        args.extend(['--genefinding-gff3', os.path.join(os.sep, 'input', job.gff3)])

    if job.genefinding:
        args.extend(['--genefinding-tool', job.genefinding])
    else:
        args.extend(['--genefinding-tool', 'none'])

    return args


def _get_job_folder(job: AsyncJob) -> str:
    """Get the folder to store the job into inside the container."""
    return os.path.join(os.sep, 'data', 'antismash', 'upload', job.job_id)


def _get_experimental_name(job: AsyncJob) -> str:
    """Get the experimentalsmash name from the jobtype"""
    return job.jobtype[18:]  # type: ignore
