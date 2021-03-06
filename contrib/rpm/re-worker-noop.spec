%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%global _pkg_name replugin
%global _src_name reworkernoop

Name: re-worker-noop
Summary: Winternewt Noop Worker
Version: 1.0.0
Release: 1%{?dist}

Group: Applications/System
License: AGPLv3
Source0: %{_src_name}-%{version}.tar.gz
Url: https://github.com/rhinception/re-worker-noop

BuildArch: noarch
BuildRequires: python2-devel
BuildRequires: python-setuptools
Requires: re-worker
Requires: python-setuptools

%description
A simple noop worker who accepts all subcommands and does
nothing. Comes with one hard-coded subcommand 'noop:fail' which forces
a deployment failure.

%prep
%setup -q -n %{_src_name}-%{version}

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --root=$RPM_BUILD_ROOT --record=re-worker-noop-files.txt

%files -f re-worker-noop-files.txt
%defattr(-, root, root)
%doc README.md LICENSE AUTHORS
%dir %{python2_sitelib}/%{_pkg_name}
%exclude %{python2_sitelib}/%{_pkg_name}/__init__.py*

%changelog
* Tue Jan  6 2015 Tim Bielawa <tbielawa@redhat.com> - 1.0.0-1
- First real release

* Mon Dec  1 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.1-1
- First release
