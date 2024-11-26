Name:		dnf-plugin-protected-kmods
Version:	0.3
Release:	1%{?dist}
Summary:	DNF plugin needed to protect kmods
License:	MIT
BuildArch:	noarch

Source0:	protected_kmods.py

BuildRequires: python3-devel

Requires:   python3-dnf

Provides:   dnf-plugin-kmod-kernel = %{version}-%{release}
Obsoletes:  dnf-plugin-kmod-kernel <= %{version}-%{release}

%description
When using precompiled kernel modules, this DNF plugin prevents kernel changes
if there is no matching precompiled kernel module package available.


%install
mkdir -p %{buildroot}%{_sysconfdir}/dnf/plugins/protected-kmods.d/
install -D -m 644 %{SOURCE0} %{buildroot}%{python3_sitelib}/dnf-plugins/protected_kmods.py


%files
%{python3_sitelib}/dnf-plugins/*
%{_sysconfdir}/dnf/plugins/protected-kmods.d/

%changelog
* Tue Nov 26 2024 Jonathan Dieter <jdieter@ciq.com> - 0.3-1
- Rename to dnf-plugin-protected-kmods

* Wed Nov 20 2024 Jonathan Dieter <jdieter@ciq.com> - 0.2-1
- Initial release
- Add and own config directory
