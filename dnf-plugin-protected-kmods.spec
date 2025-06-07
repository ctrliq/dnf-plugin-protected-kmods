Name:       dnf-plugin-protected-kmods
Version:    0.9.2
Release:    2%{?dist}
Summary:    DNF plugin needed to protect kmods
License:    Apache-2.0
URL:        https://github.com/ctrliq/%{name}
Source0:    %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
BuildArch:  noarch

BuildRequires: python3-devel
BuildRequires: pandoc


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


%build
pandoc README.md -t plain -o README


%install
mkdir -p %{buildroot}%{_sysconfdir}/dnf/plugins/protected-kmods.d/
install -D -m 644 src/protected_kmods.py %{buildroot}%{python3_sitelib}/dnf-plugins/protected_kmods.py
mkdir -p %{buildroot}%{_docdir}/%{name}
install -m 0644 README %{buildroot}%{_docdir}/%{name}/


%files -n python3-%{name}
%license LICENSE
%{python3_sitelib}/dnf-plugins/protected_kmods.py
%{python3_sitelib}/dnf-plugins/__pycache__/protected_kmods.cpython-*.pyc
%dir %{_sysconfdir}/dnf/plugins/protected-kmods.d/
%doc %{_docdir}/%{name}/


%changelog
* Sat Jun 07 2025 Jonathan Dieter <jdieter@ciq.com> - 0.9.2-2
- Initial release for EPEL
