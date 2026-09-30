Name:       kmod-test-meta
Version:    1.0
Release:    1
Summary:    Dummy meta kmod for rpm testing
License:    MIT

Requires:   kmod-test-meta-rt = %{version}-%{release}

%description
Dummy meta kmod whose config names the meta package, not its variant subpackage


%package rt
Summary:    Dummy kmod variant subpackage for rpm testing

Provides:   kernel-rt-modules >= 6.0.0-1.%{_arch}

Requires:   kernel-rt >= 6.0.0-1
Requires:   kernel-rt < 6.0.1-1

Requires:   kernel(sprint_OID) = 0xde665a40
Requires:   kernel(sprint_oid) = 0xd2ef3def
Requires:   kernel(sprint_symbol) = 0xf5863b4d
Requires:   kernel(sprint_symbol_build_id) = 0xdeac1ba1
Requires:   kernel(sprint_symbol_no_offset) = 0xde7b6c47
Requires:   kernel(sprintf) = 0xedc0e5a1

%description rt
Dummy kmod variant subpackage built for kernel-rt


%install
mkdir -p %{buildroot}%{_sysconfdir}/dnf/plugins/protected-kmods.d
cat << EOF > %{buildroot}%{_sysconfdir}/dnf/plugins/protected-kmods.d/kmod-test-meta-rt.conf
[protected_kmods]
kmod_names = kmod-test-meta
variant = rt
EOF


%files


%files rt
%config %{_sysconfdir}/dnf/plugins/protected-kmods.d/kmod-test-meta-rt.conf


%changelog
* Wed Sep 30 2026 Andrew Jorgensen <ajorgens@ciq.com> - 1.0-1
- Initial release
