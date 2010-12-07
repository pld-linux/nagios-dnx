#
# Conditional build:
%bcond_without	tests		# build without tests

Summary:	DNX Nagios Event Broker (NEB) module
Name:		nagios-dnx
Version:	0.20.1
Release:	0.5
License:	GNU v2
Group:		Networking
URL:		http://dnx.sourceforge.net/
Source0:	http://downloads.sourceforge.net/project/dnx/dnx-%{version}.tar.gz
# Source0-md5:	6a027e0595877e07a02e0046d4603a4d
Source1:	dnxcld.init
BuildRequires:	doxygen
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	sed >= 4.0
Requires:	nagios
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nagios
%define		dnxrundir	/var/run/%{name}
%define		dnxlogdir	/var/log

%description
This package contains the Distributed Nagios eXecutor NEB module,
which is a shared library that Nagios loads dynamically when
configured to do so. It redirects Nagios service checks to remote DNX
clients. This package also contains the sample configuration file for
the DNX NEB module. This package also contains the dnxstats utility,
which can be used to query and control a dnx client process remotely.

%package client
Summary:	DNX client daemon
Group:		Networking
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts

%description client
This package contains the Distributed Nagios eXecutor client daemon
and sample configuration files.

%package apidoc
Summary:	Full DNX Documentation
Group:		Documentation

%description apidoc
This package contains the OpenOffice and PDF documentation for the DNX
package.

%prep
%setup -q -n dnx-%{version}

%undos LEGAL AUTHORS INSTALL ChangeLog NEWS README

%build
%configure \
	--with-run-dir=%{dnxrundir} \
	--with-log-dir=%{dnxlogdir} \
	--with-nagios-user=nagios \
	--with-nagios-group=nagios \
	--with-dnx-user=nagios \
	--with-dnx-group=nagios \
	--libexecdir=%{_libdir}/nagios/plugins \
	--datadir=%{_datadir}/nagios \
	--with-init-dir=/etc/rc.d/init.d \
	--libdir=%{_libdir}/nagios/brokers \
	--localstatedir=%{_var}/%{_lib}/nagios

%{__make}

%if %{with tests}
%{__make} check
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -j1 install install-cfg install-initscript \
	DESTDIR=$RPM_BUILD_ROOT

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/dnxcld
# pointless symlink to initscript
rm $RPM_BUILD_ROOT%{_sbindir}/rcdnxcld

# use only the new model (see README)
rm -rf $RPM_BUILD_ROOT%{_libdir}/nagios/brokers/dnxServer.so

# in pld linux, we propagete installing rpm packages
rm $RPM_BUILD_ROOT%{_libdir}/nagios/plugins/sync_plugins.pl

rm -f $RPM_BUILD_ROOT%{_libdir}/nagios/brokers/dnxPlugin.*a
rm -rf $RPM_BUILD_ROOT%{_docdir}/dnx

%post client
/sbin/chkconfig --add dnxcld
%service dnxcld restart

%preun client
if [ "$1" = "0" ]; then
	%service -q dnxcld stop
	/sbin/chkconfig --del dnxcld
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc LEGAL AUTHORS INSTALL ChangeLog NEWS README
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dnxServer.cfg
%attr(755,root,root) %{_libdir}/nagios/brokers/dnxPlugin.so
%attr(755,root,root) %{_libdir}/nagios/plugins/dnxServer
%attr(755,root,root) %{_bindir}/dnxstats

%files client
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dnxClient.cfg
%attr(754,root,root) /etc/rc.d/init.d/dnxcld
%attr(755,root,root) %{_sbindir}/dnxClient

%files apidoc
%defattr(644,root,root,755)
%doc doc/DNX_Workflow.pdf
%doc doc/html/*
