Name:		dnf-plugin-kmod-kernel
Version:	0.1
Release:	1%{?dist}
Summary:	DNF plugin needed to protect kmods
License:	MIT
BuildArch:	noarch

Source0:	kmod_kernel.py

BuildRequires: python3-devel

Requires:   python3-dnf


%description
When using precompiled kernel modules, this DNF plugin prevents kernel changes
if there is no matching precompiled kernel module package available.


%install
install -D -m 644 %{SOURCE0} %{buildroot}%{python3_sitelib}/dnf-plugins/kmod_kernel.py


%files
%{python3_sitelib}/dnf-plugins/*


%changelog
* Wed Nov 20 2024 Jonathan Dieter <jdieter@ciq.com> - 0.1-1
- Initial release
