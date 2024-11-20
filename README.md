# dnf-plugin-kmod-kernel

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Contributing](https://img.shields.io/badge/Contributing-Developer%20Certificate%20of%20Origin-violet)](https://developercertificate.org)

## Overview

Python DNF plugin that prevents new kernels from being updated if a protected kmod won't work with it.


## Installation

Copy `kmod-kernel.py` to the dnf plugins directory (usually `/usr/lib/python3.x/site-packages/dnf-plugins`)

Create a file in `/etc/dnf/plugins/kmod-kernel.conf`:
```
[protected_kmods]
kmod_names = <kmod to protect>
```

Example:
```
[protected_kmods]
kmod_names = kmod-idpf-irdma
```

You can also put a drop in configuration file in `/etc/dnf/plugins/kmod-kernel.d`
Example:
`/etc/dnf/plugins/kmod-kernel.d/kmod-idpf-irdma.conf`
```
[protected_kmods]
kmod_names = kmod-idpf-irdma
```


## Blocking kernel updates

* **RHEL8** or **RHEL9**
  Kernel updates will be blocked in the absence of the availability of a compatible kmod package for that kernel.

  The `kernel` and `kernel-core` packages will be removed from such `dnf` transactions and an error message will be printed, ex:

  > kmod-idpf-irdma: filtering kernel 5.14.0-503.14.1.el9_5, no precompiled modules available 


### Debugging

* **RHEL8** or **RHEL9**  
  Heuristic information can be printed via CLI, such as installed kernel, installed kmod packages, available kernels, available drivers, and available kmod packages.

  ```shell
  dnf kmod-kernel-plugin
  ```


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)
