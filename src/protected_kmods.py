# dnf-plugin-protected-kmods
#
# DNF plugin to ensure that kernel updates do not occur if the update doesn't have
# a matching kmod available in the repositories.
#
# Forked from https://github.com/NVIDIA/yum-packaging-nvidia-plugin

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


def print_cmd(is_cli, msg):
    if is_cli:
        print(msg)


class ProtectedKmodsPlugin(dnf.Plugin):
    name = 'protected-kmods'

    def __init__(self, base, cli):
        super(ProtectedKmodsPlugin, self).__init__(base, cli)
        self.protected_kmods = {}
        self.block_updates_when_kmod_not_in_repos = True
        self.configure()


    def configure(self):
        plugin_config = ConfigParser()
        config_files = []
        config_path = self.base.conf.pluginconfpath[0]

        default_config_file = os.path.join(config_path, PLUGIN_CONF + ".conf")
        if os.path.isfile(default_config_file):
            plugin_config.read(default_config_file)
            self._add_protected_kmods(plugin_config, default_config_file, False)
            try:
                if plugin_config.get("main", "block_updates_when_kmod_not_in_repos").lower() in ("false", "f", "0"):
                    self.block_updates_when_kmod_not_in_repos = False
            except (NoOptionError, NoSectionError) as error:
                pass
        try:
            for filename in os.listdir(os.path.join(config_path, PLUGIN_CONF + ".d")):
                if filename.endswith('.conf'):
                    plugin_config = ConfigParser()
                    config_file = os.path.join(config_path, PLUGIN_CONF + ".d", filename)
                    plugin_config.read(config_file)
                    self._add_protected_kmods(plugin_config, config_file, True)
        except FileNotFoundError as error:
            pass
        for variant in self.protected_kmods:
            self.protected_kmods[variant] = list(set(self.protected_kmods[variant]))
            self.protected_kmods[variant].sort()


    def _add_protected_kmods(self, config, config_file, print_warning):
        kmod_names = self._read_config_item(config, config_file, "protected_kmods", "kmod_names", None, print_warning)
        variant = self._read_config_item(config, config_file, "protected_kmods", "variant", None, False)
        if kmod_names is None:
            return
        if type(kmod_names) == str:
            kmod_names = [kmod_names]
        elif type(kmod_names) != list:
            logger.warning(f'Invalid config in {config_file}: kmod_names should be a list or a string')
            return
        if variant not in self.protected_kmods:
            self.protected_kmods[variant] = []
        self.protected_kmods[variant].extend(kmod_names)


    def _read_config_item(self, config, config_file, hub, section, default, print_warning):
        try:
            return config.get(hub, section)
        except (NoOptionError, NoSectionError) as error:
            if print_warning:
                logger.warning(f'Invalid config in {config_file}: {error}')
            return default


    def sack(self):
        if len(self.protected_kmods) == 0:
            return

        is_cli = False
        if hasattr(self.cli, "protected_kmods_is_cli"):
            is_cli = self.cli.protected_kmods_is_cli

        sack = self.base.sack

        # If nothing's in the available sack, then it's not been populated, which means that we're
        # can just skip all this since we're modifying what's available
        if len(sack.query().available().filter()) == 0:
            logger.debug("DEBUG: available sack is empty, so temporarily disabling protected-kmods plugin")
            return

        # Check for *any* installed kernels, if none are installed, then skip all processing (we're in a container/chroot)
        any_installed_kernels = list(sack.query().installed().filter(name__glob = "kernel-core*"))
        if not any_installed_kernels:
            print("No installed kernels found")
            return

        for variant in self.protected_kmods:
            if variant is not None:
                cvariant = f"-{variant}"
            else:
                cvariant = ""
            # check installed
            installed_kernels = list(sack.query().installed().filter(name = f"kernel{cvariant}-core"))
            installed_kernels = sorted(installed_kernels, reverse = True, key = lambda p: evr_key(p, sack))

            available_kernels = list(sack.query().available().filter(name = f"kernel{cvariant}-core"))
            dkms_kmod_modules = sack.query().available().filter(name__substr = "dkms")

            # Print debugging if running from CLI
            if is_cli:
                if installed_kernels:
                    string_kernels = '\n  '.join([str(elem) for elem in installed_kernels])
                    print_cmd(is_cli, f'\nInstalled kernel(s):\n  {str(string_kernels)}')

                if available_kernels:
                    string_kernels = '\n  '.join([str(elem) for elem in available_kernels])
                    print_cmd(is_cli, f'\nAvailable kernel(s):\n  {str(string_kernels)}')

            for kmod_name in self.protected_kmods[variant]:
                installed_modules = list(sack.query().installed().filter(name = kmod_name))
                available_modules = list(sack.query().available().filter(name = kmod_name).difference(dkms_kmod_modules))
                if len(available_modules) == 0:
                    logger.warning(f"WARNING: {kmod_name} is installed, but there are no {kmod_name} packages available in the configured repositories.")
                    if not self.block_updates_when_kmod_not_in_repos:
                        logger.warning(f"WARNING: Kernel updates will not be blocked based on {kmod_name}.")
                        continue
                    else:
                        logger.warning(f"WARNING: Future kernel updates may be blocked until {kmod_name} is removed from this system.")

                # Print debugging if running from CLI
                if installed_modules:
                    string_modules = '\n  '.join([str(elem) for elem in installed_modules])
                    print_cmd(is_cli, f'\nInstalled kmod(s) for {kmod_name}:\n  {str(string_modules)}')
                if available_modules:
                    string_available_modules = '\n  '.join([str(elem) for elem in available_modules])
                    print_cmd(is_cli, f'\nAvailable kmod(s) for {kmod_name}:\n  {str(string_available_modules)}')
                print_cmd(is_cli, '')
                all_modules = available_modules[:]
                all_modules.extend(installed_modules)
                # Remove any duplicates
                all_modules = list(set(all_modules))

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

                        if not is_cli:
                            # Exclude packages
                            try:
                                sack.add_excludes(all_rpms_of_kernel)
                                logger.debug(f'DEBUG: {kmod_name}: filtering kernel{cvariant} {kernelpkg.version}-{kernelpkg.release}, repo priority value higher than other repos with kernels')
                            except Exception as error:
                                logger.warning('WARNING: kernel exclude error', error)
                                logger.warning('WARNING: any further actions would be undefined, so exiting dnf-plugin-protected-kmods')
                                return
                        else:
                            string_all_rpms_of_kernel = '\n  '.join([str(elem) for elem in all_rpms_of_kernel])
                            print_cmd(is_cli, f'Other kernels in repositories with lower priority value than {kernelpkg} in {kernelpkg.reponame}')
                            print_cmd(is_cli, f'Excluded kernel packages during update ({str(kernelpkg.version)}-{str(kernelpkg.release)}):\n  {str(string_all_rpms_of_kernel)}')
                            print_cmd(is_cli, '')


                # Iterate through each kernel, then iterate through each kmod, checking that the
                # kernel provides all the symbols and versions required by the kmod.  If this is
                # true for even one kmod, then the kernel is good, otherwise exclude it.
                all_modules = sorted(all_modules, reverse = True, key = lambda p: evr_key(p, sack))
                no_match_kmods = list(all_modules)
                for kernelpkg in available_kernels:
                    # Clear kernelpkg from installed_kernels if it is already installed so we don't
                    # process it twice
                    if kernelpkg in installed_kernels:
                        installed_kernels.remove(kernelpkg)

                    ksack = sack.query().available().filterm(
                        name = [
                            f"kernel{cvariant}",
                            f"kernel{cvariant}-core",
                            f"kernel{cvariant}-modules",
                            f"kernel{cvariant}-modules-core",
                            f"kernel{cvariant}-modules-extra"
                        ],
                        version = kernelpkg.version,
                        release = kernelpkg.release,
                    )
                    match = False
                    for kmodpkg in all_modules:
                        kmod_match = True
                        for item in kmodpkg.requires:
                            if not str(item).startswith("kernel"):
                                continue
                            if not ksack.filterm(provides=item):
                                # Most of the time filterm works as expected, but occasionally it gives a false negative, so verify once more with a new sack and filter()
                                # Worst case scenario, we do this a few times per kmod, but it's still significantly faster than using filter() each time
                                ksack = sack.query().available().filterm(
                                    name = [
                                        f"kernel{cvariant}",
                                        f"kernel{cvariant}-core",
                                        f"kernel{cvariant}-modules",
                                        f"kernel{cvariant}-modules-core",
                                        f"kernel{cvariant}-modules-extra"
                                    ],
                                    version = kernelpkg.version,
                                    release = kernelpkg.release,
                                )
                                if not ksack.filter(provides=item):
                                    kmod_match = False
                                    break
                        if kmod_match:
                            if is_cli:
                                excluded = ""
                                if kernelpkg in excluded_priority_kernels:
                                    excluded = " (excluded kernel)"
                                print_cmd(is_cli, f'Found matching {kmodpkg} for {kernelpkg}{excluded}')
                            if kmodpkg in no_match_kmods and kernelpkg not in excluded_priority_kernels:
                                no_match_kmods.remove(kmodpkg)
                            match = True
                    if not match:
                        # Assemble a list of all packages that are built from the same kernel source rpm
                        all_rpms_of_kernel = sack.query().available().filter(release = kernelpkg.release)

                        print_cmd(is_cli, f'No matching {kmod_name} for {kernelpkg}')
                        if kernelpkg not in excluded_priority_kernels:
                            if not is_cli:
                                # Exclude packages
                                try:
                                    sack.add_excludes(all_rpms_of_kernel)
                                    logger.info(f'INFO: {kmod_name}: filtering kernel{cvariant} {kernelpkg.version}-{kernelpkg.release}, no precompiled modules available')
                                except Exception as error:
                                    logger.warning('WARNING: kernel exclude error', error)
                                    logger.warning('WARNING: any further actions would be undefined, so exiting dnf-plugin-protected-kmods')
                                    return
                            else:
                                string_all_rpms_of_kernel = '\n  '.join([str(elem) for elem in all_rpms_of_kernel])
                                print_cmd(is_cli, f'Excluded kernel packages during update ({str(kernelpkg.version)}-{str(kernelpkg.release)}):\n  {string_all_rpms_of_kernel}')
                                print_cmd(is_cli, '')

                # Ensure we're not excluding kmods that work with the currently installed kernel, even
                # if the kernel is no longer available in the repos
                for kernelpkg in installed_kernels:
                    ksack = sack.query().installed().filterm(
                        name = [
                            f"kernel{cvariant}",
                            f"kernel{cvariant}-core",
                            f"kernel{cvariant}-modules",
                            f"kernel{cvariant}-modules-core",
                            f"kernel{cvariant}-modules-extra"
                        ],
                        version = kernelpkg.version,
                        release = kernelpkg.release,
                    )
                    match = False
                    for kmodpkg in all_modules:
                        kmod_match = True
                        for item in kmodpkg.requires:
                            if not str(item).startswith("kernel"):
                                continue
                            if not ksack.filterm(provides=item):
                                # Most of the time filterm works as expected, but occasionally it gives a false negative, so verify once more with a new sack and filter()
                                # Worst case scenario, we do this a few times per kmod, but it's still significantly faster than using filter() each time
                                ksack = sack.query().installed().filterm(
                                    name = [
                                        f"kernel{cvariant}",
                                        f"kernel{cvariant}-core",
                                        f"kernel{cvariant}-modules",
                                        f"kernel{cvariant}-modules-core",
                                        f"kernel{cvariant}-modules-extra"
                                    ],
                                    version = kernelpkg.version,
                                    release = kernelpkg.release,
                                )
                                if not ksack.filter(provides=item):
                                    kmod_match = False
                                    break
                        if kmod_match:
                            if is_cli:
                                excluded = ""
                                if kernelpkg in excluded_priority_kernels:
                                    excluded = " (excluded kernel)"
                                print_cmd(is_cli, f'Found matching {kmodpkg} for installed {kernelpkg}{excluded}')
                            if kmodpkg in no_match_kmods and kernelpkg not in excluded_priority_kernels:
                                no_match_kmods.remove(kmodpkg)

                # There may be situations where we have kmods that don't have any matching kernel.  In
                # this case, we want to exclude them so users don't end up with "none of the providers
                # can be installed" errors.
                excluded_kmods = no_match_kmods
                if not is_cli:
                    # Exclude packages
                    try:
                        sack.add_excludes(excluded_kmods)
                    except Exception as error:
                        logger.warning('WARNING: kmod exclude error', error)
                        logger.warning('WARNING: any further actions would be undefined, so exiting dnf-plugin-protected-kmods')
                        return
                    string_excluded_kmods = ', '.join(f"{k.version}-{k.release}" for k in excluded_kmods)
                    logger.debug(f'DEBUG: {kmod_name}: filtering kmods {string_excluded_kmods}, no matching kernel')
                else:
                    string_all_rpms_excluded_kmods = '\n  '.join([str(elem) for elem in excluded_kmods])
                    print_cmd(is_cli, f'Excluded kmod packages during update due to non-matching kernels:\n  {string_all_rpms_excluded_kmods}')
                    print_cmd(is_cli, '')


@dnf.plugin.register_command
class ProtectedKmodsPluginCommand(dnf.cli.Command):
    aliases = ('protected-kmods-plugin',)
    summary = 'Helper plugin for DNF to ensure kernels don\'t get updated if kmods are missing'

    def configure(self):
        demands = self.cli.demands
        demands.sack_activation = True
        demands.available_repos = True
        self.cli.protected_kmods_is_cli = True

    def run(self):
        pass
