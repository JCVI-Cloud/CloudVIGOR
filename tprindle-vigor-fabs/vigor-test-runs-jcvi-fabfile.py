#
# vigor-test-runs-jcvi-fabfile.py
# 20111116 tprindle
#

import os.path

USER = "tprindle"
GROUP = "tigr"
VIGOR_SVN_TAG = "GSCcloud-release-20111129"
ROOT_DIR = os.path.join("/usr/local/scratch/CORE", USER, "vigor-test")
SCRATCH_DIR = ROOT_DIR
VIGOR_SCRATCH_DIR = os.path.join(SCRATCH_DIR, "vigor-scratch")
AMAZONS3_URL = "https://s3.amazonaws.com/VIGOR"
VIGOR_SAMPLE_DATA_NAME = "vigor-sample-data"
VIGOR_SAMPLE_DATA_TAR_FILENAME = "%s.tgz" % VIGOR_SAMPLE_DATA_NAME

CONFIG = {
        "USER":USER,
        "GROUP":GROUP,
        "HOME":os.path.join("/home", USER),

        "SCRATCH_DIR":SCRATCH_DIR,
        "VIGOR_SCRATCH_DIR":VIGOR_SCRATCH_DIR,
        "VIGOR_TEMPSPACE_DIR":os.path.join(VIGOR_SCRATCH_DIR, "tempspace"),

        "ROOT_DIR":ROOT_DIR,
        "VIGOR_REPOS_DIR":os.path.join(ROOT_DIR, "VIGOR-REPOS"),

        "SVN_USER":USER,
        "SVN_URL":"http://svn.jcvi.org/ANNOTATION/vigor/tags/%s" % VIGOR_SVN_TAG,

        "VIGOR_SAMPLE_DATA_TAR_FILENAME":VIGOR_SAMPLE_DATA_TAR_FILENAME,
        "VIGOR_SAMPLE_DATA_URL": os.path.join(AMAZONS3_URL, VIGOR_SAMPLE_DATA_TAR_FILENAME),
        "VIGOR_SAMPLE_DATA_DIR": os.path.join(VIGOR_SCRATCH_DIR, "sample-data"),
        "VIGOR_TEST_OUTPUT_DIR": os.path.join(VIGOR_SCRATCH_DIR, "test-output"),
    }

from fabric.api import cd, env, prefix, run, task
from fabric.network import disconnect_all

@task(default=True)
def install():
    try:
        _initialize()
        # TODO - if dir exists, cancel install. which dir?
        _create_vigor_scratch_dir()
        _install_vigor()
        _install_vigor_sample_data()
    finally:
        disconnect_all()

@task
def clean_all():
    try:
        _initialize()
        _remove_vigor_repos_dir()
        _remove_vigor_scratch_dir()
        if _exists(CONFIG["ROOT_DIR"]):
            run("rmdir %(ROOT_DIR)s" % CONFIG)
    finally:
        disconnect_all()

@task
def run_tests():
    try:
        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Adenovirus.pm \
                -x %(VIGOR_REPOS_DIR)s/conf/hadv_FJ349096.cfg \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Adenovirus/34615.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/34615""") % CONFIG
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Coronavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Coronavirus/GCV_35931.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/GCV_35931""") % CONFIG
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Coronavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Coronavirus/GCV_32276.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/GCV_32276""") % CONFIG
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Coronavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Coronavirus/GCV_32265.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/GCV_32265""") % CONFIG
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Flu.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Flu/FluB.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/FluB""") % CONFIG
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Rhinovirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Rhinovirus/Rhinovirus_genomes.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/Rhinovirus_genomes""") % CONFIG
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -l %(VIGOR_REPOS_DIR)s/Rotavirus.pm \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/Rotavirus/rotaV_10_22_genome.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/rotaV_10_22_genome""") % CONFIG
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

        cmd = ("""%(VIGOR_REPOS_DIR)s/VIGOR.pl \
                -i %(VIGOR_SAMPLE_DATA_DIR)s/YellowFeverV/YFV_genome.fasta \
                -O %(VIGOR_TEST_OUTPUT_DIR)s/YFV_genome""") % CONFIG
        print "DEBUG: cmd[%s]" % cmd
        run(cmd)

    finally:
        disconnect_all()

def _create_vigor_scratch_dir():
    if not _exists(CONFIG["VIGOR_SCRATCH_DIR"]):
        run("mkdir -p %(VIGOR_SCRATCH_DIR)s" % CONFIG)
    if not _exists(CONFIG["VIGOR_TEMPSPACE_DIR"]):
        run("mkdir -p %(VIGOR_TEMPSPACE_DIR)s" % CONFIG)
    if not _exists(CONFIG["VIGOR_TEST_OUTPUT_DIR"]):
        run("mkdir -p %(VIGOR_TEST_OUTPUT_DIR)s" % CONFIG)
    run("find %(VIGOR_SCRATCH_DIR)s -type f -exec chmod -R 644 {} \;" % CONFIG)
    run("find %(VIGOR_SCRATCH_DIR)s -type d -exec chmod -R 755 {} \;" % CONFIG)

def _exists(path):
    found = False
    result = run("if [ -e %s ]; then echo 'true'; else echo 'false'; fi" % path )
    if result == "true": found = True
    return found

def _initialize():
    env.user = CONFIG["USER"]
    print("User[%s]" % env.user)
    print("Host[%s]" % env.host)

def _install_vigor():
    if not _exists(CONFIG["VIGOR_REPOS_DIR"]):
        run("svn --username=%(SVN_USER)s export %(SVN_URL)s %(VIGOR_REPOS_DIR)s"
            % CONFIG)
    run("find %(VIGOR_REPOS_DIR)s -type f -exec chmod -R ugo-w {} \;" % CONFIG)
    run("find %(VIGOR_REPOS_DIR)s -type d -exec chmod -R 555 {} \;" % CONFIG)

def _install_vigor_sample_data():
    if not _exists(CONFIG["VIGOR_SAMPLE_DATA_DIR"]):
        run("mkdir -p %(VIGOR_SAMPLE_DATA_DIR)s" % CONFIG)
    if not _exists("%(VIGOR_SAMPLE_DATA_DIR)s/%(VIGOR_SAMPLE_DATA_TAR_FILENAME)s"
                   % CONFIG):
        run(("""wget --no-host-directories --cut-dirs=1 \
            --directory-prefix=%(VIGOR_SAMPLE_DATA_DIR)s \
             %(VIGOR_SAMPLE_DATA_URL)s""") % CONFIG)
    with cd(CONFIG["VIGOR_SAMPLE_DATA_DIR"]):
        run("tar xvfz %(VIGOR_SAMPLE_DATA_TAR_FILENAME)s" % CONFIG)
    run("find %(VIGOR_SAMPLE_DATA_DIR)s -type f -exec chmod -R ugo-w {} \;" % CONFIG)
    run("find %(VIGOR_SAMPLE_DATA_DIR)s -type d -exec chmod -R 555 {} \;" % CONFIG)

def _remove_vigor_repos_dir():
    # with prefix doesn't work in this case.
    if _exists(CONFIG["VIGOR_REPOS_DIR"]):
        run("find %(VIGOR_REPOS_DIR)s -type d -exec chmod -R 755 {} \;" % CONFIG)
        run("find %(VIGOR_REPOS_DIR)s -type f -exec chmod -R 644 {} \;" % CONFIG)
        run("rm -rf %(VIGOR_REPOS_DIR)s" % CONFIG)

def _remove_vigor_scratch_dir():
    # with prefix doesn't work in this case.
    if _exists(CONFIG["VIGOR_SCRATCH_DIR"]):
        run("find %(VIGOR_SCRATCH_DIR)s -type d -exec chmod -R 755 {} \;" % CONFIG)
        run("find %(VIGOR_SCRATCH_DIR)s -type f -exec chmod -R 644 {} \;" % CONFIG)
        run("rm -rf %(VIGOR_SCRATCH_DIR)s" % CONFIG)
