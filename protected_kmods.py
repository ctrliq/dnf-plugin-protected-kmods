import os
from functools import cmp_to_key
from configparser import ConfigParser, NoOptionError, NoSectionError

from dnfpluginscore import logger
from dnf.cli.option_parser import OptionParser
import dnf
import dnf.cli
import dnf.sack
import libdnf.transaction

PLUGIN_CONF = 'protected-kmods'


def evr_key(po, sack):
    func = cmp_to_key(sack.evr_cmp)
    return func(f'{str(po.epoch)}:{str(po.version)}-{str(po.release)}')


def print_cmd(is_cmd, msg):
    if is_cmd:
        print(msg)


class ProtectedKmodsPlugin(dnf.Plugin):
    name = 'protected-kmods'

    def __init__(self, base, cli):
        super(ProtectedKmodsPlugin, self).__init__(base, cli)
        self.protected_kmods = []
        self.configure()


    def configure(self):
        plugin_config = ConfigParser()
        config_files = []
        config_path = self.base.conf.pluginconfpath[0]

        default_config_file = os.path.join(config_path, PLUGIN_CONF + ".conf")
        if os.path.isfile(default_config_file):
            plugin_config.read(default_config_file)
            self._add_protected_kmods(plugin_config, default_config_file)

        # !!!!
        # Handle old pathnames.  Remove after a few releases since old paths never made GA
        try:
            for filename in os.listdir(os.path.join(config_path, "kmod-kernel.d")):
                if filename.endswith('.conf'):
                    plugin_config = ConfigParser()
                    config_file = os.path.join(config_path, "kmod-kernel.d", filename)
                    plugin_config.read(config_file)
                    self._add_protected_kmods(plugin_config, config_file)
        except FileNotFoundError as error:
            pass
        # !!!!

        try:
            for filename in os.listdir(os.path.join(config_path, PLUGIN_CONF + ".d")):
                if filename.endswith('.conf'):
                    plugin_config = ConfigParser()
                    config_file = os.path.join(config_path, PLUGIN_CONF + ".d", filename)
                    plugin_config.read(config_file)
                    self._add_protected_kmods(plugin_config, config_file)
        except FileNotFoundError as error:
            pass
        self.protected_kmods = list(set(self.protected_kmods))
        self.protected_kmods.sort()


    def _add_protected_kmods(self, config, config_file):
        kmod_names = self._read_config_item(config, config_file, "protected_kmods", "kmod_names", None)
        if kmod_names is None:
            return
        if type(kmod_names) == str:
            kmod_names = [kmod_names]
        elif type(kmod_names) != list:
            logger.warning(f'Invalid config in {config_file}: kmod_names should be a list or a string')
            return
        self.protected_kmods.extend(kmod_names)


    def _read_config_item(self, config, config_file, hub, section, default):
        try:
            return config.get(hub, section)
        except (NoOptionError, NoSectionError) as error:
            logger.warning(f'Invalid config in {config_file}: {error}')
            return default


    def sack(self):
        if len(self.protected_kmods) == 0:
            return

        is_cmd = False
        if hasattr(self.cli, "protected_kmods_is_cmd"):
            is_cmd = self.cli.protected_kmods_is_cmd

        sack = self.base.sack

        # check installed
        installed_kernel = list(sack.query().installed().filter(name = "kernel-core"))

        # container/chroot
        if not installed_kernel and not is_cmd:
            return

        # The most recent installed kernel package
        installed_kernels = sorted(installed_kernel, reverse = True, key = lambda p: evr_key(p, sack))
        if len(installed_kernels) > 0:
            installed_kernel  = installed_kernels[0]

        available_kernels = sack.query().available().filter(name = "kernel-core")
        dkms_kmod_modules = sack.query().available().filter(name__substr = "dkms")

        # Print debugging if running from CLI
        if installed_kernels:
            string_kernels = '\n  '.join([str(elem) for elem in installed_kernels])
            print_cmd(is_cmd, f'\nInstalled kernel(s):\n  {str(string_kernels)}')

        if available_kernels:
            string_kernels = '\n  '.join([str(elem) for elem in available_kernels])
            print_cmd(is_cmd, f'\nAvailable kernel(s):\n  {str(string_kernels)}')

        for kmod_name in self.protected_kmods:
            installed_modules = list(sack.query().installed().filter(name = kmod_name))
            available_modules = sack.query().available().filter(name = kmod_name).difference(dkms_kmod_modules)
            if len(available_modules) == 0:
                logger.warning(f"WARNING: No {kmod_name} packages available in the repositories, so not blocking updates based on {kmod_name}.")
                continue

            # Print debugging if running from CLI
            if installed_modules:
                string_modules = '\n  '.join([str(elem) for elem in installed_modules])
                print_cmd(is_cmd, f'\nInstalled kmod(s) for {kmod_name}:\n  {str(string_modules)}')

            if available_modules:
                string_all_modules = '\n  '.join([str(elem) for elem in available_modules])
                print_cmd(is_cmd, f'\nAvailable kmod(s) for {kmod_name}:\n  {str(string_all_modules)}')

            print_cmd(is_cmd, '')

            # DKMS stream enabled
            if installed_modules and 'dkms' in string_modules:
                continue

            # Strange things happen with priorities and kmods.  If there's a newer kmod available
            # for a newer kernel and the kernel is in a higher priority value repository (which
            # means the repo is actually lower priority) than an older kernel, the kernel and kmod
            # will be updated.  We work around that by excluding all kernels from lower priority
            # repos
            excluded_priority_kernels = []
            lowest_priority = 99999999 # Set to a ridiculously high value
            for kernelpkg in available_kernels:
                if lowest_priority > kernelpkg.base.repos[kernelpkg.reponame].priority:
                    lowest_priority = kernelpkg.base.repos[kernelpkg.reponame].priority
            for kernelpkg in available_kernels:
                if kernelpkg.base.repos[kernelpkg.reponame].priority > lowest_priority:
                    # Assemble a list of all packages that are built from the same kernel source rpm
                    all_rpms_of_kernel = list(sack.query().available().filter(release = kernelpkg.release))
                    excluded_priority_kernels.append(kernelpkg)

                    string_all_rpms_of_kernel = '\n  '.join([str(elem) for elem in all_rpms_of_kernel])
                    print_cmd(is_cmd, f'Other kernels in repositories with lower priority value than {kernelpkg} in {kernelpkg.reponame}')
                    print_cmd(is_cmd, f'Excluded kernel packages during update ({str(kernelpkg.version)}-{str(kernelpkg.release)}):\n  {str(string_all_rpms_of_kernel)}')
                    print_cmd(is_cmd, '')

                    # Exclude packages
                    if not is_cmd:
                        try:
                            sack.add_excludes(all_rpms_of_kernel)
                            logger.debug(f'DEBUG: {kmod_name}: filtering kernel {kernelpkg.version}-{kernelpkg.release}, repo priority value higher than other repos with kernels')
                        except Exception as error:
                            logger.warning('WARNING: kernel exclude error', error)

            # Iterate through each kernel, then iterate through each kmod, checking that the
            # kernel provides all the symbols and versions required by the kmod.  If this is
            # true for one kmod, then the kernel is good, otherwise exclude it.
            available_modules = sorted(available_modules, reverse = True, key = lambda p: evr_key(p, sack))
            no_match_kmods = list(available_modules)
            for kernelpkg in available_kernels:
                ksack = sack.query().available().filterm(name = ["kernel-core", "kernel-modules", "kernel-modules-core", "kernel-modules-extra"], version = kernelpkg.version, release = kernelpkg.release)
                match = False
                for kmodpkg in available_modules:
                    kmod_match = True
                    for item in kmodpkg.requires:
                        if not str(item).startswith("kernel"):
                            continue
                        if not ksack.filter(provides=item):
                            kmod_match = False
                    if kmod_match:
                        print_cmd(is_cmd, f'Found matching {kmodpkg} for {kernelpkg}')
                        if kmodpkg in no_match_kmods:
                            no_match_kmods.remove(kmodpkg)
                        match = True
                        break
                if not match:
                    # Assemble a list of all packages that are built from the same kernel source rpm
                    all_rpms_of_kernel = sack.query().available().filter(release = kernelpkg.release)

                    string_all_rpms_of_kernel = '\n  '.join([str(elem) for elem in all_rpms_of_kernel])
                    print_cmd(is_cmd, f'No matching {kmod_name} for {kernelpkg}')
                    if kernelpkg not in excluded_priority_kernels:
                        print_cmd(is_cmd, f'Excluded kernel packages during update ({str(kernelpkg.version)}-{str(kernelpkg.release)}):\n  {string_all_rpms_of_kernel}')
                        print_cmd(is_cmd, '')

                        # Exclude packages
                        if not is_cmd:
                            try:
                                sack.add_excludes(all_rpms_of_kernel)
                                logger.info(f'INFO: {kmod_name}: filtering kernel {kernelpkg.version}-{kernelpkg.release}, no precompiled modules available')
                            except Exception as error:
                                logger.warning('WARNING: kernel exclude error', error)

            # There may be situations where we have kmods that don't have any matching kernel.  In
            # this case, we want to exclude them so users don't end up with "none of the providers
            # can be installed" errors.
            excluded_kmods = no_match_kmods
            for kmodpkg in excluded_kmods:
                # Exclude packages
                if not is_cmd:
                    try:
                        sack.add_excludes([kmodpkg])
                    except Exception as error:
                        logger.warning('WARNING: kmod exclude error', error)
            if not is_cmd:
                string_excluded_kmods = ', '.join(f"{k.version}-{k.release}" for k in excluded_kmods)
                logger.debug(f'DEBUG: {kmod_name}: filtering kmods {string_excluded_kmods}, no matching kernel')
            string_all_rpms_excluded_kmods = '\n  '.join([str(elem) for elem in excluded_kmods])
            print_cmd(is_cmd, f'Excluded kmod packages during update due to non-matching kernels:\n  {string_all_rpms_excluded_kmods}')
            print_cmd(is_cmd, '')


@dnf.plugin.register_command
class ProtectedKmodsPluginCommand(dnf.cli.Command):
    aliases = ('protected-kmods-plugin',)
    summary = 'Helper plugin for DNF to ensure kernels don\'t get updated if kmods are missing'

    def configure(self):
        demands = self.cli.demands
        demands.sack_activation = True
        demands.available_repos = True
        self.cli.protected_kmods_is_cmd = True

    def run(self):
        pass
