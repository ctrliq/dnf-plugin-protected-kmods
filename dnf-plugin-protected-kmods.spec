Name:       dnf-plugin-protected-kmods
Version:    0.7
Release:    1%{?dist}
Summary:    DNF plugin needed to protect kmods
License:    MIT
URL:        https://github.com/ctrliq/%{name}
Source0:    https://github.com/ctrliq/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.gz
BuildArch:  noarch

BuildRequires: python3-devel

Requires:   python3-dnf

Provides:   dnf-plugin-kmod-kernel = %{version}-%{release}
Obsoletes:  dnf-plugin-kmod-kernel <= %{version}-%{release}


%description
When using precompiled kernel modules, this DNF plugin prevents kernel changes
if there is no matching precompiled kernel module package available.


%prep
%autosetup


%install
mkdir -p %{buildroot}%{_sysconfdir}/dnf/plugins/protected-kmods.d/
install -D -m 644 src/protected_kmods.py %{buildroot}%{python3_sitelib}/dnf-plugins/protected_kmods.py


%files
%{python3_sitelib}/dnf-plugins/*
%{_sysconfdir}/dnf/plugins/protected-kmods.d/


%changelog
* Fri Dec 13 2024 Jonathan Dieter <jdieter@ciq.com> - 0.7-1
- Fix bug introduced in 0.6

* Thu Dec 12 2024 Jonathan Dieter <jdieter@ciq.com> - 0.6-1
- Ensure that available_modules are sorted by evr_key in reverse order
- Exclude kernels if they're in a higher priority value repo
- Exclude kmods without any matching kernels

* Fri Nov 29 2024 Jonathan Dieter <jdieter@ciq.com> - 0.5-1
- Fix output when no kmods are available

* Wed Nov 27 2024 Jonathan Dieter <jdieter@ciq.com> - 0.4-1
- Fix kmod sort order when reporting

* Tue Nov 26 2024 Jonathan Dieter <jdieter@ciq.com> - 0.3-1
- Rename to dnf-plugin-protected-kmods

* Wed Nov 20 2024 Jonathan Dieter <jdieter@ciq.com> - 0.2-1
- Initial release
- Add and own config directory
