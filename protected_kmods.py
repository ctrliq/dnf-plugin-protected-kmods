from __future__ import absolute_import
from __future__ import unicode_literals

import os
import shutil
from functools import cmp_to_key
from configparser import ConfigParser, NoOptionError, NoSectionError

from dnf.cli.option_parser import OptionParser
import dnf
import dnf.cli
import dnf.sack
import libdnf.transaction

PLUGIN_CONF = 'protected-kmods'


def evr_key(po, sack):
    func = cmp_to_key(sack.evr_cmp)
    return func(f'{str(po.epoch)}:{str(po.version)}-{str(po.release)}')


def revive_msg(var, msg, val = ''):
    if var:
        print(msg)

    return val


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
            print(f'Invalid config in {config_file}: kmod_names should be a list or a string')
            return
        self.protected_kmods.extend(kmod_names)


    def _read_config_item(self, config, config_file, hub, section, default):
        try:
            return config.get(hub, section)
        except (NoOptionError, NoSectionError) as error:
            print(f'Invalid config in {config_file}: {error}')
            return default


    def sack(self):
        if len(self.protected_kmods) == 0:
            return

        debug = False
        if hasattr(self.cli, "protected_kmods_debug"):
            debug = self.cli.protected_kmods_debug

        sack = self.base.sack

        # check installed
        installed_kernel = list(sack.query().installed().filter(name = "kernel-core"))

        # container/chroot
        if not installed_kernel and not debug:
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
            revive_msg(debug, f'\nInstalled kernel(s):\n  {str(string_kernels)}')

        if available_kernels:
            string_kernels = '\n  '.join([str(elem) for elem in available_kernels])
            revive_msg(debug, f'\nAvailable kernel(s):\n  {str(string_kernels)}')

        for kmod_name in self.protected_kmods:
            installed_modules = list(sack.query().installed().filter(name = kmod_name))
            available_modules = sack.query().available().filter(name = kmod_name).difference(dkms_kmod_modules)
            if len(available_modules) == 0:
                print("WARNING: No {kmod_name} packages available in the repositories, so not blocking updates based on {kmod_name}.")
                continue

            # Print debugging if running from CLI
            if installed_modules:
                string_modules = '\n  '.join([str(elem) for elem in installed_modules])
                revive_msg(debug, f'\nInstalled kmod(s) for {kmod_name}:\n  {str(string_modules)}')

            if available_modules:
                string_all_modules = '\n  '.join([str(elem) for elem in available_modules])
                revive_msg(debug, f'\nAvailable kmod(s) for {kmod_name}:\n  {str(string_all_modules)}')

            revive_msg(debug, '')

            # DKMS stream enabled
            if installed_modules and 'dkms' in string_modules:
                continue

            # Iterate through each kernel, then iterate through each kmod, checking that the
            # kernel provides all the symbols and versions required by the kmod.  If this is
            # true for one kmod, then the kernel is good, otherwise exclude it.
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
                        revive_msg(debug, f'Found matching {kmodpkg} for {kernelpkg}')
                        match = True
                        break
                if not match:
                    # Assemble a list of all packages that are built from the same kernel source rpm
                    all_rpms_of_kernel = sack.query().available().filter(release = kernelpkg.release)

                    string_all_rpms_of_kernel = '\n  '.join([str(elem) for elem in all_rpms_of_kernel])
                    revive_msg(debug, f'No matching {kmod_name} for {kernelpkg}')
                    revive_msg(debug, f'Excluded kernel packages during update ({str(kernelpkg.version)}-{str(kernelpkg.release)}):\n  {str(string_all_rpms_of_kernel)}')
                    revive_msg(debug, '')

                    # Exclude packages
                    if not debug:
                        try:
                            sack.add_excludes(all_rpms_of_kernel)
                            print(f'{kmod_name}: filtering kernel {kernelpkg.version}-{kernelpkg.release}, no precompiled modules available')
                        except Exception as error:
                            print('WARNING: kernel exclude error', error)


@dnf.plugin.register_command
class ProtectedKmodsPluginCommand(dnf.cli.Command):
    aliases = ('protected-kmods-plugin',)
    summary = 'Helper plugin for DNF to ensure kernels don\'t get updated if kmods are missing'

    def configure(self):
        demands = self.cli.demands
        demands.sack_activation = True
        demands.available_repos = True
        self.cli.protected_kmods_debug = True

    def run(self):
        pass
