from pathlib import Path
from make import Make
from build_generated_driver import get_targets, build
import logging

logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )

project_list = ["libvpx", "libaom", "libhtp", "cpu_features", "minijail", "pthreadpool"]
make_config = Path(__file__).absolute().parent / "make.yml"
build_config = Path(__file__).absolute().parent / "build.yml"


def build_project(project):
    make = Make(make_config)
    logging.info(f"Downloading {project}")
    make.download(project)
    logging.info(f"Building {project}")
    make.build(project)

def build_fuzzers(project):
    targets = get_targets(build_config, project)
    for target in sorted(targets.keys()):
        logging.info(f"Building fuzzers for {targets[target]['name']}")
        build(targets[target], "test")
        logging.info(f"Built fuzzers for {targets[target]['name']}")

for project in project_list:
    build_project(project)
    build_fuzzers(project)
