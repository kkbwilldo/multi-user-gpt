from setuptools import setup, find_packages
import os
from setuptools.command.install import install

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        shell = os.getenv('SHELL')
        if 'zsh' in shell:
            rc_file = os.path.expanduser("~/.zshrc")
        elif 'bash' in shell:
            rc_file = os.path.expanduser("~/.bashrc")
        else:
            print("Unsupported shell. Please add the mug function to your shell config manually.")
            return

        function_definition = """
function mug() {
    if [ "$1" = "start" ]; then
        {
            mug_core start
            echo "You are now in a mug session. Type 'mug end' to end the session."
            source $(python3 -c "import mug_core; print(mug_core.get_command_hook_path())")
        } || {
            echo "An error occurred while starting the mug session."
        }
    elif [ "$1" = "end" ]; then
        {
            source $(python3 -c "import mug_core; print(mug_core.get_command_unset_path())")
            echo "Ending session."
        } || {
            echo "An error occurred while ending the mug session."
        }
    else
        question="$@"
        {
            mug_core "$question"
        } || {
            echo "An error occurred while asking the question: $question"
        }
    fi
}

"""
        with open(rc_file, 'a') as f:
            f.write(function_definition)

        print(f"Function definition added to {rc_file}. Please run 'source {rc_file}' to apply changes.")

def get_command_hook_path():
    import pkg_resources
    return pkg_resources.resource_filename('mug_core', 'scripts/command_hook.sh')

def get_command_unset_path():
    import pkg_resources
    return pkg_resources.resource_filename('mug_core', 'scripts/command_unset.sh')

setup(
    name='mug_core',
    version='0.1',
    packages=find_packages(include=['mug_core', 'mug_core.*']),
    install_requires=[
        'openai',
        'boto3',
    ],
    entry_points={
        'console_scripts': [
            'mug_core=mug_core.main:main',
        ],
    },
    package_data={
        'mug_core': ['scripts/command_hook.sh', 'scripts/command_unset.sh'],
    },
    include_package_data=True,
    long_description="Mug Core: A command line tool to interact with OpenAI's GPT models and AWS S3.",
    long_description_content_type='text/markdown',
    cmdclass={
        'install': PostInstallCommand,
    }
)
