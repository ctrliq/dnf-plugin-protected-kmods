Name:       kernel-rt
Version:    6.0.0
Release:    2
Summary:    Dummy RT kernel for rpm testing
License:    MIT

Provides:   installonlypkg(kernel)

Requires:   kernel-rt-core-uname-r = 6.0.0-2.%{_arch}++rt
Requires:   kernel-rt-modules-core-uname-r = 6.0.0-2.%{_arch}++rt
Requires:   kernel-rt-modules-uname-r = 6.0.0-2.%{_arch}++rt


%description
Dummy base kernel package


%package core
Summary:    Dummy kernel-core for rpm testing

Provides:   kernel-rt = 6.0.0-2
Provides:   kernel(sprint_OID) = 0xde665a40
Provides:   kernel(sprint_oid) = 0xd2ef3def
Provides:   kernel(sprint_symbol) = 0xf5863b4d
Provides:   kernel(sprint_symbol_build_id) = 0xdeac1ba1
Provides:   kernel(sprint_symbol_no_offset) = 0xde7b6c47
Provides:   kernel(sprintf) = 0x5c75bb81
Provides:   kernel-rt-core = 6.0.0-2
Provides:   kernel-rt-core(x86-64) = 6.0.0-2
Provides:   kernel-rt-core-uname-r = 6.0.0-2.%{_arch}++rt
Provides:   kernel-uname-r = 6.0.0-2.%{_arch}++rt
Provides:   kernel-x86_64 = 6.0.0-2++rt
Provides:   installonlypkg(kernel)

Requires:   kernel-rt-modules-core-uname-r = 6.0.0-2.%{_arch}++rt

%description core
Dummy kernel-rt-core package


%package modules
Summary:    Dummy kernel-modules for rpm testing

Provides:   kernel-modules = 6.0.0-2++rt
Provides:   kernel-modules-x86_64 = 6.0.0-2++rt
Provides:   kernel-rt-modules = 6.0.0-2
Provides:   kernel-rt-modules(x86-64) = 6.0.0-2
Provides:   kernel-rt-modules-uname-r = 6.0.0-2.%{_arch}++rt
Provides:   kernel-rt-modules-x86_64 = 6.0.0-2
Provides:   installonlypkg(kernel-module)

Requires:   kernel-rt-modules-core-uname-r = 6.0.0-2.%{_arch}++rt
Requires:   kernel-uname-r = 6.0.0-2.%{_arch}++rt

%description modules
Dummy kernel-rt-modules package


%package modules-core
Summary:    Dummy kernel-modules-core for rpm testing

Provides:   kernel-modules-core = 6.0.0-2++rt
Provides:   kernel-modules-core-x86_64 = 6.0.0-2++rt
Provides:   kernel-rt-modules-core = 6.0.0-2
Provides:   kernel-rt-modules-core(x86-64) = 6.0.0-2
Provides:   kernel-rt-modules-core-uname-r = 6.0.0-2.%{_arch}++rt
Provides:   kernel-rt-modules-core-x86_64 = 6.0.0-2
Provides:   installonlypkg(kernel-module)

Requires:   kernel-uname-r = 6.0.0-2.%{_arch}++rt

%description modules-core
Dummy kernel-rt-modules-core package


%files

%files core

%files modules

%files modules-core

%changelog
* Tue Oct 28 2025 Jonathan Dieter <jdieter@ciq.com> - 6.0.0-2
- Second release

* Mon Oct 27 2025 Jonathan Dieter <jdieter@ciq.com> - 6.0.0-1
- Initial release
