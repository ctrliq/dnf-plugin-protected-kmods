Name:       kernel
Version:    6.0.0
Release:    2
Summary:    Dummy kernel for rpm testing
License:    MIT

Provides:   installonlypkg(kernel)

Requires:   kernel-core-uname-r = 6.0.0-2.%{_arch}
Requires:   kernel-modules-core-uname-r = 6.0.0-2.%{_arch}
Requires:   kernel-modules-uname-r = 6.0.0-2.%{_arch}


%description
Dummy base kernel package


%package core
Summary:    Dummy kernel-core for rpm testing

Provides:   kernel = 6.0.0-2
Provides:   kernel(sprint_OID) = 0x2680bd81
Provides:   kernel(sprint_oid) = 0xfc201b66
Provides:   kernel(sprint_symbol) = 0x661601de
Provides:   kernel(sprint_symbol_build_id) = 0x6dd5680d
Provides:   kernel(sprint_symbol_no_offset) = 0xe769232e
Provides:   kernel(sprintf) = 0x3c3ff9fd
Provides:   kernel-core = 6.0.0-2
Provides:   kernel-core(x86-64) = 6.0.0-2
Provides:   kernel-core-uname-r = 6.0.0-2.%{_arch}
Provides:   kernel-uname-r = 6.0.0-2.%{_arch}
Provides:   kernel-x86_64 = 6.0.0-2
Provides:   installonlypkg(kernel)

Requires:   kernel-modules-core-uname-r = 6.0.0-2.%{_arch}

%description core
Dummy kernel-core package


%package modules
Summary:    Dummy kernel-modules for rpm testing

Provides:   kernel-modules = 6.0.0-2
Provides:   kernel-modules(x86-64) = 6.0.0-2
Provides:   kernel-modules-uname-r = 6.0.0-2.%{_arch}
Provides:   kernel-modules-x86_64 = 6.0.0-2
Provides:   installonlypkg(kernel-module)

Requires:   kernel-modules-core-uname-r = 6.0.0-2.%{_arch}
Requires:   kernel-uname-r = 6.0.0-2.%{_arch}

%description modules
Dummy kernel-modules package


%package modules-core
Summary:    Dummy kernel-modules-core for rpm testing

Provides:   kernel-modules-core = 6.0.0-2
Provides:   kernel-modules-core(x86-64) = 6.0.0-2
Provides:   kernel-modules-core-uname-r = 6.0.0-2.%{_arch}
Provides:   kernel-modules-core-x86_64 = 6.0.0-2
Provides:   installonlypkg(kernel-module)

Requires:   kernel-uname-r = 6.0.0-2.%{_arch}

%description modules-core
Dummy kernel-modules-core package


%files

%files core

%files modules

%files modules-core
