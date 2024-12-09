"""Test antiSMASH command line generation"""
import pytest

from antismash_models import SyncJob as Job

from dispatcher.cmdline import create_commandline, InvalidJobType

COMMON_EXPECTED_ARGS = [
        'fake.gbk',
        '--cpus', '1',
        '--taxon', 'bacteria',
        '--output-dir', '/data/antismash/upload/bacteria-fake',
        '--logfile', '/data/antismash/upload/bacteria-fake/bacteria-fake.log',
        '--debug',
        '--limit', '1000',
]


def test_create_commandline6_minimal(conf, db):
    job = Job(db, 'bacteria-fake')
    job.jobtype = 'antismash6'
    job.filename = 'fake.gbk'
    job.minimal = True

    expected = COMMON_EXPECTED_ARGS[::] + ["--minimal"]

    cmdline = create_commandline(job, conf)
    assert cmdline == expected


def test_create_commandline6_minimal_gff3(conf, db):
    job = Job(db, 'bacteria-fake')
    job.jobtype = 'antismash6'
    job.filename = 'fake.fa'
    job.gff3 = 'fake.gff'
    job.minimal = True

    expected = ["fake.fa"] + COMMON_EXPECTED_ARGS[1::] + [
        '--genefinding-gff3', '/input/fake.gff',
        '--minimal'
    ]

    cmdline = create_commandline(job, conf)
    assert cmdline == expected


def test_create_commandline6_all_options(conf, db):
    job = Job(db, 'bacteria-fake')
    job.jobtype = 'antismash6'
    job.filename = 'fake.gbk'
    job.asf = True
    job.clusterhmmer = True
    job.pfam2go = True
    job.clusterblast = True
    job.knownclusterblast = True
    job.subclusterblast = True
    job.genefinding = 'none'
    job.cassis = True

    expected = COMMON_EXPECTED_ARGS[::] + [
        '--asf',
        '--clusterhmmer',
        '--pfam2go',
        '--cb-general',
        '--cb-knownclusters',
        '--cb-subclusters',
        '--genefinding-tool', 'none',
        '--cassis',
    ]

    cmdline = create_commandline(job, conf)
    assert cmdline == expected


def test_create_commandline6_pfam2go_adds_clusterhmmer(conf, db):
    job = Job(db, 'bacteria-fake')
    job.jobtype = 'antismash6'
    job.filename = 'fake.gbk'
    job.pfam2go = True

    expected = COMMON_EXPECTED_ARGS[::] + [
        '--clusterhmmer',
        '--pfam2go',
        '--genefinding-tool', 'none',
    ]

    cmdline = create_commandline(job, conf)
    assert cmdline == expected


def test_create_commandline6_cassis_override(conf, db):
    conf.run_cassis = False

    job = Job(db, 'fungi-fake')
    job.jobtype = 'antismash6'
    job.filename = 'fake.gbk'
    job.cassis = True

    expected = [
        'fake.gbk',
        '--cpus', '1',
        '--taxon', 'fungi',
        '--output-dir', '/data/antismash/upload/fungi-fake',
        '--logfile', '/data/antismash/upload/fungi-fake/fungi-fake.log',
        '--debug',
        '--limit', '1000',
        '--genefinding-tool', 'none',
    ]

    cmdline = create_commandline(job, conf)
    assert cmdline == expected


def test_create_commandline7_tbfs(conf, db):
    job = Job(db, 'bacteria-fake')
    job.jobtype = "antismash7"
    job.filename = "fake.gbk"
    job.tfbs = True

    expected = COMMON_EXPECTED_ARGS[::] + [
        '--genefinding-tool', 'none',
        '--tfbs'
    ]

    cmdline = create_commandline(job, conf)
    assert cmdline == expected


def test_create_commandline8_all_options(conf, db):
    job = Job(db, 'bacteria-fake')
    job.jobtype = 'antismash8'
    job.filename = 'fake.gbk'
    job.hmmdetection_strictness = "loose"
    job.asf = True
    job.clusterhmmer = True
    job.pfam2go = True
    job.tigrfam = True
    job.clusterblast = True
    job.knownclusterblast = True
    job.subclusterblast = True
    job.cc_mibig = True
    job.genefinding = 'none'
    job.smcog_trees = True
    job.rre = True
    job.rre_minlength = 5
    job.rre_cutoff = 7
    job.sideloads = ["sideload1.json", "sideload2.json"]
    job.sideload_simple = "EXMPL_01234:2345-4567"
    job.ncbi_context = True
    job.cassis = True  # This should have no effect, make sure it doesn't

    expected = COMMON_EXPECTED_ARGS[::] + [
        '--asf',
        '--hmmdetection-strictness', 'loose',
        '--clusterhmmer',
        '--pfam2go',
        '--tigrfam',
        '--cb-general',
        '--cb-knownclusters',
        '--cb-subclusters',
        '--cc-mibig',
        '--genefinding-tool', 'none',
        '--smcog-trees',
        '--rre',
        '--rre-minlength', '5',
        '--rre-cutoff', '7',
        '--sideload', '/input/sideload1.json,/input/sideload2.json',
        '--sideload-simple', 'EXMPL_01234:2345-4567',
        '--html-ncbi-context'
    ]

    cmdline = create_commandline(job, conf)
    assert cmdline == expected


def test_valid_jobtype(conf, db):

    for jobtype in ["antismash6", "antismash7", "antismash8"]:
        job = Job(db, 'bacteria-fake')
        job.jobtype = jobtype
        job.filename = "fake.gbk"

        cmdline = create_commandline(job, conf)
        assert cmdline == COMMON_EXPECTED_ARGS[::] + ["--genefinding-tool", "none"]

    for jobtype in ["antismash5", "antismash9", "bob"]:
        job = Job(db, 'bacteria-fake')
        job.jobtype = jobtype
        job.filename = "fake.gbk"

        with pytest.raises(InvalidJobType):
            create_commandline(job, conf)
