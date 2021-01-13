from configparser import ExtendedInterpolation as EI, ConfigParser
from glob import glob
from os import path

from fire import Fire
from jinja2 import Template


__version__ = '0.0.1'

def scan_dir(dir_):
    for file in glob(f"{path.join(dir_)}/*.config"):
        yield file


def _config(name: str) -> ConfigParser:
    # load template name
    print(f'Reading config file from: {name}')
    quick_config = ConfigParser(interpolation=EI())
    quick_config.read(name)
    temp_name = quick_config["path"]["template"]

    # get defaults from templates dir
    default_config = ConfigParser(interpolation=EI())
    default_config.read(f"{temp_name}.defaults")

    config = ConfigParser(
        interpolation=EI(),
        defaults={s: dict(default_config.items(s)) for s in default_config.sections()},
    )
    config.read(name)
    return config


def proc_file(name: str, stdio=False):
    config = _config(name)
    with open(f"{config['path']['template']}.jinja2") as f:
        template_data = f.read()

    t = Template(template_data)
    if stdio:
        print(t.render(**config))
    else:
        render = t.render(**config)
        with open(f"{config['path']['output']}", 'w') as f:
            f.write(render)


def run_dir(dir_: str):
    for file in scan_dir(dir_):
        proc_file(file)


def run_file(file: str):
    proc_file(file)


def preview_file(file: str):
    proc_file(file, stdio=True)


if __name__ == "__main__":
    Fire({
        'dir': run_dir,
        'file': run_file,
        'preview_file': preview_file,
        'version': lambda: __version__
    })

    # black format option (or pipe to black for stdio)
    # lint option, and optionally fail on write if lint fails
