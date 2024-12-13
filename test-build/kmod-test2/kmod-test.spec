Name:       kmod-test
Version:    1.0
Release:    2
Summary:    Dummy kmod for rpm testing
License:    MIT

Provides:   kernel-modules >= 6.0.0-1.%{_arch}

Requires:   kernel >= 6.0.0-1
Requires:   kernel < 6.0.1-1

Requires:   kernel(sprint_OID) = 0x2680bd81
Requires:   kernel(sprint_oid) = 0xfc201b66
Requires:   kernel(sprint_symbol) = 0x661601de
Requires:   kernel(sprint_symbol_build_id) = 0x6dd5680d
Requires:   kernel(sprint_symbol_no_offset) = 0xe769232e
Requires:   kernel(sprintf) = 0xabcd1234


%description
Dummy base kernel package


%install
mkdir -p %{buildroot}%{_sysconfdir}/dnf/plugins/protected-kmods.d
cat << EOF > %{buildroot}%{_sysconfdir}/dnf/plugins/protected-kmods.d/kmod-test.conf
[protected_kmods]
kmod_names = kmod-test
EOF


%files
%config %{_sysconfdir}/dnf/plugins/protected-kmods.d/kmod-test.conf
