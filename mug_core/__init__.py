from .aws_s3 import sync_s3_to_local, sync_local_to_s3

def get_command_hook_path():
    """
    Returns the path to the command_hook.sh script.
    """
    import pkg_resources
    return pkg_resources.resource_filename('mug_core', 'scripts/command_hook.sh')

def get_command_unset_path():
    """
    Returns the path to the command_unset.sh script.
    """
    import pkg_resources
    return pkg_resources.resource_filename('mug_core', 'scripts/command_unset.sh')
