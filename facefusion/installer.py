import os
import shutil
import signal
import subprocess
import sys
from argparse import ArgumentParser, HelpFormatter
from functools import partial
from types import FrameType

from facefusion import metadata
from facefusion.common_helper import is_linux, is_windows

LOCALES =\
{
	'install_dependency': 'install the {dependency} package',
	'force_reinstall': 'force reinstall of packages',
	'uv_not_installed': 'uv is not installed'
}
ONNXRUNTIME_SET =\
{
	'default': 'cpu'
}
if is_windows() or is_linux():
	ONNXRUNTIME_SET['cuda@12'] = 'cuda-12'
	ONNXRUNTIME_SET['cuda@13'] = 'cuda-13'
	ONNXRUNTIME_SET['openvino'] = 'openvino'
if is_windows():
	ONNXRUNTIME_SET['directml'] = 'directml'
	ONNXRUNTIME_SET['qnn'] = 'qnn'
if is_linux():
	ONNXRUNTIME_SET['migraphx'] = 'migraphx'
	ONNXRUNTIME_SET['rocm'] = 'rocm'


def cli() -> None:
	signal.signal(signal.SIGINT, signal_exit)
	program = ArgumentParser(formatter_class = partial(HelpFormatter, max_help_position = 50))
	program.add_argument('onnxruntime', help = LOCALES.get('install_dependency').format(dependency = 'onnxruntime'), choices = ONNXRUNTIME_SET.keys())
	program.add_argument('--force-reinstall', help = LOCALES.get('force_reinstall'), action = 'store_true')
	program.add_argument('-v', '--version', version = metadata.get('name') + ' ' + metadata.get('version'), action = 'version')
	run(program)


def signal_exit(signum : int, frame : FrameType) -> None:
	sys.exit(0)


def run(program : ArgumentParser) -> None:
	args = program.parse_args()
	uv_path = shutil.which('uv')

	if uv_path:
		dependency_group = ONNXRUNTIME_SET[args.onnxruntime]
		commands = [ uv_path, 'sync', '--only-group', dependency_group ]

		if args.force_reinstall:
			commands.append('--reinstall')

		subprocess.call(commands)
	else:
		sys.stdout.write(LOCALES.get('uv_not_installed') + os.linesep)
		sys.exit(1)
