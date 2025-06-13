Name:       dnf-plugin-protected-kmods
Version:    0.9.3
Release:    1%{?dist}
Summary:    DNF plugin needed to protect kmods
License:    Apache-2.0
URL:        https://github.com/ctrliq/%{name}
Source0:    %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
BuildArch:  noarch

BuildRequires: python3-devel


%global _description %{expand:
When using precompiled kernel modules, this DNF plugin prevents kernel changes
if there is no matching precompiled kernel module package available.}

%description %_description


%package -n python3-%{name}
Summary:    %{summary}

Requires:   python3-dnf
Provides:   %{name} = %{version}-%{release}
Obsoletes:  %{name} < %{version}-%{release}


%description -n python3-%{name} %_description


%prep
%autosetup


%install
mkdir -p %{buildroot}%{_sysconfdir}/dnf/plugins/protected-kmods.d/
install -D -m 644 src/protected_kmods.py %{buildroot}%{python3_sitelib}/dnf-plugins/protected_kmods.py


%files -n python3-%{name}
%license LICENSE
%pycached %{python3_sitelib}/dnf-plugins/protected_kmods.py
%dir %{_sysconfdir}/dnf/plugins/protected-kmods.d/
%doc README


%changelog
* Sat Jun 07 2025 Jonathan Dieter <jdieter@ciq.com> - 0.9.3-1
- Initial release for EPEL
