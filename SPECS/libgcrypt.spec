# This is taken from gnutls.spec
%define srpmhash() %{lua:
local files = rpm.expand("%_specdir/libgcrypt.spec")
for i, p in ipairs(patches) do
   files = files.." "..p
end
for i, p in ipairs(sources) do
   files = files.." "..p
end
local sha256sum = assert(io.popen("cat "..files.."| sha256sum"))
local hash = sha256sum:read("*a")
sha256sum:close()
print(string.sub(hash, 0, 16))
}


Name: libgcrypt
Version: 1.10.0
Release: 10%{?dist}
URL: https://www.gnupg.org/
Source0: https://www.gnupg.org/ftp/gcrypt/libgcrypt/libgcrypt-%{version}.tar.bz2
Source1: https://www.gnupg.org/ftp/gcrypt/libgcrypt/libgcrypt-%{version}.tar.bz2.sig
Source2: wk@g10code.com
Patch1: libgcrypt-1.10.0-disable-brainpool.patch
Patch3: libgcrypt-1.10.0-ppc-hwf.patch
Patch4: libgcrypt-1.10.0-allow-small-RSA-verify.patch
Patch5: libgcrypt-1.10.0-allow-short-salt.patch
Patch6: libgcrypt-1.10.0-fips-getrandom.patch
# https://dev.gnupg.org/T6127
# https://lists.gnupg.org/pipermail/gcrypt-devel/2022-September/005379.html
Patch7: libgcrypt-1.10.0-fips-selftest.patch
# https://dev.gnupg.org/T6217
Patch9: libgcrypt-1.10.0-sha3-large.patch
# https://dev.gnupg.org/T5919
Patch10: libgcrypt-1.10.0-fips-keygen.patch
# https://dev.gnupg.org/T6219
# f4a861f3e5ae82f278284061e4829c03edf9c3a7
Patch11: libgcrypt-1.10.0-fips-kdf.patch
# c34c9e70055ee43e5ef257384fa15941f064e5a4
# https://gitlab.com/redhat-crypto/libgcrypt/libgcrypt-mirror/-/merge_requests/13
Patch12: libgcrypt-1.10.0-fips-indicator.patch
# beb5d6df5c5785db7c32a24a5d2a351cb964bfbc
# 521500624b4b11538d206137205e2a511dad7072
# 9dcf9305962b90febdf2d7cc73b49feadbf6a01f
# a340e980388243ceae6df57d101036f3f2a955be
Patch13: libgcrypt-1.10.0-fips-integrity.patch
# 3c8b6c4a9cad59c5e1db5706f6774a3141b60210
# 052c5ef4cea56772b7015e36f231fa0bcbf91410
# 3fd3bb31597f80c76a94ea62e42d58d796beabf1
Patch14: libgcrypt-1.10.0-fips-integrity2.patch
# 06ea5b5332ffdb44a0a394d766be8989bcb6a95c
Patch15: libgcrypt-1.10.0-fips-x931.patch
# bf1e62e59200b2046680d1d3d1599facc88cfe63
Patch16: libgcrypt-1.10.0-fips-rsa-pss.patch
# https://dev.gnupg.org/T6376
Patch17: libgcrypt-1.10.0-fips-indicator-md-hmac.patch
# https://dev.gnupg.org/T6394
# https://dev.gnupg.org/T6397
Patch18: libgcrypt-1.10.0-fips-pct.patch
# https://dev.gnupg.org/T6396
Patch19: libgcrypt-1.10.0-fips-status-sign-verify.patch
# https://dev.gnupg.org/T6393
Patch20: libgcrypt-1.10.0-fips-drbg.patch
# https://dev.gnupg.org/T6417
Patch21: libgcrypt-1.10.0-fips-indicator-pk-flags.patch

%global gcrylibdir %{_libdir}
%global gcrysoname libgcrypt.so.20
%global hmackey orboDeJITITejsirpADONivirpUkvarP

# Technically LGPLv2.1+, but Fedora's table doesn't draw a distinction.
# Documentation and some utilities are GPLv2+ licensed. These files
# are in the devel subpackage.
License: LGPLv2+
Summary: A general-purpose cryptography library
BuildRequires: gcc
BuildRequires: gawk, libgpg-error-devel >= 1.11, pkgconfig
# This is needed only when patching the .texi doc.
BuildRequires: texinfo
BuildRequires: autoconf, automake, libtool
BuildRequires: make

%package devel
Summary: Development files for the %{name} package
License: LGPLv2+ and GPLv2+
Requires: libgpg-error-devel
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: pkgconfig

%description
Libgcrypt is a general purpose crypto library based on the code used
in GNU Privacy Guard.  This is a development version.

%description devel
Libgcrypt is a general purpose crypto library based on the code used
in GNU Privacy Guard.  This package contains files needed to develop
applications using libgcrypt.

%prep
%setup -q
%patch1 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1
%patch21 -p1

%build
# This package has a configure test which uses ASMs, but does not link the
# resultant .o files.  As such the ASM test is always successful, even on
# architectures were the ASM is not valid when compiling with LTO.
#
# -ffat-lto-objects is sufficient to address this issue.  It is the default
# for F33, but is expected to only be enabled for packages that need it in
# F34, so we use it here explicitly
%define _lto_cflags -flto=auto -ffat-lto-objects

# should be all algorithms except SM3 and SM4
export DIGESTS='crc gostr3411-94 md4 md5 rmd160 sha1 sha256 sha512 sha3 tiger whirlpool stribog blake2'
export CIPHERS='arcfour blowfish cast5 des aes twofish serpent rfc2268 seed camellia idea salsa20 gost28147 chacha20'

eval $(sed -n 's/^\(\(NAME\|VERSION_ID\)=.*\)/OS_\1/p' /etc/os-release)
export FIPS_MODULE_NAME="$OS_NAME ${OS_VERSION_ID%%.*} %name"

autoreconf -f
%configure --disable-static \
%ifarch sparc64
     --disable-asm \
%endif
     --enable-noexecstack \
     --enable-hmac-binary-check=%{hmackey} \
     --disable-brainpool \
     --disable-jent-support \
     --enable-digests="$DIGESTS" \
     --enable-ciphers="$CIPHERS" \
     --with-fips-module-version="$FIPS_MODULE_NAME %{version}-%{srpmhash}"
sed -i -e '/^sys_lib_dlsearch_path_spec/s,/lib /usr/lib,/usr/lib /lib64 /usr/lib64 /lib,g' libtool
%make_build

%check
make check
# try in faked FIPS mode too
LIBGCRYPT_FORCE_FIPS_MODE=1 make check

# Add generation of HMAC checksums of the final stripped binaries 
%define libpath $RPM_BUILD_ROOT%{gcrylibdir}/%{gcrysoname}.?.?
%define __spec_install_post \
    %{?__debug_package:%{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
    cd src \
    sed -i -e 's|FILE=.*|FILE=\\\$1|' gen-note-integrity.sh \
    READELF=readelf AWK=awk ECHO_N="-n" bash gen-note-integrity.sh %{libpath} > %{libpath}.hmac \
    objcopy --update-section .note.fdo.integrity=%{libpath}.hmac %{libpath} %{libpath}.new \
    mv -f %{libpath}.new %{libpath} \
    rm -f %{libpath}.hmac
%{nil}

%install
%make_install

# Change /usr/lib64 back to /usr/lib.  This saves us from having to patch the
# script to "know" that -L/usr/lib64 should be suppressed, and also removes
# a file conflict between 32- and 64-bit versions of this package.
# Also replace my_host with none.
sed -i -e 's,^libdir="/usr/lib.*"$,libdir="/usr/lib",g' $RPM_BUILD_ROOT/%{_bindir}/libgcrypt-config
sed -i -e 's,^my_host=".*"$,my_host="none",g' $RPM_BUILD_ROOT/%{_bindir}/libgcrypt-config

rm -f ${RPM_BUILD_ROOT}/%{_infodir}/dir ${RPM_BUILD_ROOT}/%{_libdir}/*.la
/sbin/ldconfig -n $RPM_BUILD_ROOT/%{_libdir}

%if "%{gcrylibdir}" != "%{_libdir}"
# Relocate the shared libraries to %{gcrylibdir}.
mkdir -p $RPM_BUILD_ROOT%{gcrylibdir}
for shlib in $RPM_BUILD_ROOT%{_libdir}/*.so* ; do
	if test -L "$shlib" ; then
		rm "$shlib"
	else
		mv "$shlib" $RPM_BUILD_ROOT%{gcrylibdir}/
	fi
done

# Add soname symlink.
/sbin/ldconfig -n $RPM_BUILD_ROOT/%{_lib}/
%endif

# Overwrite development symlinks.
pushd $RPM_BUILD_ROOT/%{gcrylibdir}
for shlib in lib*.so.?? ; do
	target=$RPM_BUILD_ROOT/%{_libdir}/`echo "$shlib" | sed -e 's,\.so.*,,g'`.so
%if "%{gcrylibdir}" != "%{_libdir}"
	shlib=%{gcrylibdir}/$shlib
%endif
	ln -sf $shlib $target
done
popd

# Create /etc/gcrypt (hardwired, not dependent on the configure invocation) so
# that _someone_ owns it.
mkdir -p -m 755 $RPM_BUILD_ROOT/etc/gcrypt

%ldconfig_scriptlets

%files
%dir /etc/gcrypt
%{gcrylibdir}/libgcrypt.so.*.*
%{gcrylibdir}/%{gcrysoname}
%license COPYING.LIB
%doc AUTHORS NEWS THANKS

%files devel
%{_bindir}/%{name}-config
%{_bindir}/dumpsexp
%{_bindir}/hmac256
%{_bindir}/mpicalc
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/libgcrypt.pc
%{_datadir}/aclocal/*
%{_mandir}/man1/*

%{_infodir}/gcrypt.info*
%license COPYING

%changelog
* Mon Mar 20 2023 Jakub Jelen <jjelen@redhat.com> - 1.10.0-10
- Provide FIPS indicators for MD and HMACs
- Improve PCT tests for ECDSA and always run them after key is generated
- Add missing guards for FIPS status in md_sign/verify function
- Provider FIPS indicators for public key operation flags

* Tue Jan 24 2023 Jakub Jelen <jjelen@redhat.com> - 1.10.0-9
- Avoid usage of invalid arguments sizes for PBKDF2 in FIPS mode
- Do not allow large salt lengths with RSA-PSS padding
- Disable X9.31 key generation in FIPS mode
- Update the FIPS integrity checking code to upstream version
- Update cipher modes FIPS indicators for AES WRAP and GCM
- Disable jitter entropy generator

* Thu Oct 20 2022 Jakub Jelen <jjelen@redhat.com> - 1.10.0-8
- Fix unneeded PBKDF2 passphrase length limitation in FIPS mode
- Enforce HMAC key lengths in MD API in FIPS mode

* Thu Oct 06 2022 Jakub Jelen <jjelen@redhat.com> - 1.10.0-7
- Properly enforce KDF limits in FIPS mode (#2130275)
- Fix memory leak in large digest test (#2129150)
- Fix function name FIPS service indicator by disabling PK encryption and decryption (#2130275)
- Skip RSA encryption/decryption selftest in FIPS mode (#2130275)

* Tue Sep 27 2022 Jakub Jelen <jjelen@redhat.com> - 1.10.0-6
- Fix SHA3 digests with large inputs (#2129150)
- Fix FIPS RSA PCT (#2128455)
- Fix RSA FIPS Keygen that non-deterministically fails (#2130275)
- Get max 32B from getrandom in FIPS mode (#2130275)

* Wed Aug 17 2022 Jakub Jelen <jjelen@redhat.com> - 1.10.0-5
- Allow signature verification with smaller RSA keys (#2083846)
- Allow short salt for KDF (#2114870)
- Reseed the kernel DRBG by using GRND_RANDOM (#2118695)
- Address FIPS review comments around selftests (#2118695)
- Disable RSA-OAEP in FIPS mode (#2118695)

* Fri May 06 2022 Jakub Jelen <jjelen@redhat.com> - 1.10.0-4
- Backport ppc hardware flags detection (#2051307)
- Disable PKCS#1.5 encryption in FIPS mode (#2061328)

* Thu Mar 31 2022 Jakub Jelen <jjelen@redhat.com> - 1.10.0-3
- Use correct FIPS module name (#2067123)

* Thu Feb 17 2022 Jakub Jelen <jjelen@redhat.com> - 1.10.0-2
- Systematic FIPS module name with other FIPS modules

* Wed Feb 02 2022 Jakub Jelen <jjelen@redhat.com> - 1.10.0-1
- Final release (#2026636)

* Thu Jan 27 2022 Jakub Jelen <jjelen@redhat.com> - 1.10.0-0.3
- Fix broken soname in the previous beta

* Thu Jan 27 2022 Jakub Jelen <jjelen@redhat.com> - 1.10.0-0.2
- Provide compat soname symlink as the new release is backward compatible

* Wed Jan 26 2022 Jakub Jelen <jjelen@redhat.com> - 1.10.0-0.1
- New upstream pre-release (#2026636)
- Upstream all patches
- Implement FIPS 140-3 support

* Tue Oct 12 2021 Jakub Jelen <jjelen@redhat.com> - 1.9.3-5
- Allow HW optimizations in FIPS mode (#1990059)

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.9.3-4
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue Jun 15 2021 Jakub Jelen <jjelen@redhat.com> - 1.9.3-3
- Fix for CVE-2021-33560 (#1970098)

* Wed Apr 28 2021 Jakub Jelen <jjelen@redhat.com> - 1.9.3-2
- Restore the CET protection (#1954049)

* Tue Apr 20 2021 Jakub Jelen <jjelen@redhat.com> - 1.9.3-1
- New upstream release (#1951325)

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 1.9.2-4
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Thu Apr 15 2021 Jakub Jelen <jjelen@redhat.com> - 1.9.2-3
- Fix issues reported by coverity

* Mon Mar 29 2021 Jakub Jelen <jjelen@redhat.com> - 1.9.2-2
- Fix OCB tag creation on s390x (failing gnupg2 tests)

* Wed Feb 17 2021 Jakub Jelen <jjelen@redhat.com> - 1.9.2-1
- New upstream release (#1929630)

* Fri Jan 29 2021 Jakub Jelen <jjelen@redhat.com> - 1.9.1-1
- New upstream release (#1922156, #1922097)

* Wed Jan 20 2021 Jakub Jelen <jjelen@redhat.com> - 1.9.0-1
- New upstream release (#1917878)

* Tue Nov 24 2020 Jakub Jelen <jjelen@redhat.com> - 1.8.7-1
- new upstream release (#1891123)

* Fri Aug 21 2020 Jeff Law <law@redhat.com> - 1.8.6-4
- Re-enable LTO

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 21 2020 Tom Stellard <tstellar@redhat.com> - 1.8.6-2
- Use make macros
- https://fedoraproject.org/wiki/Changes/UseMakeBuildInstallMacro

* Mon Jul 20 2020 Tomáš Mráz <tmraz@redhat.com> 1.8.6-1
- new upstream version 1.8.6

* Wed Jul  1 2020 Tomáš Mráz <tmraz@redhat.com> 1.8.5-7
- use the hmac256 tool to calculate the library hmac

* Tue Jun 30 2020 Jeff Law <law@redhat.com>
- Disable LTO

* Thu Apr 23 2020 Tomáš Mráz <tmraz@redhat.com> 1.8.5-6
- Fix regression - missing -ldl linkage

* Wed Apr 22 2020 Tomáš Mráz <tmraz@redhat.com> 1.8.5-5
- AES performance improvements backported from master branch

* Mon Apr 20 2020 Tomáš Mráz <tmraz@redhat.com> 1.8.5-4
- FIPS selftest is run directly from the constructor
- FIPS module is implicit with kernel FIPS flag

* Thu Jan 30 2020 Tomáš Mráz <tmraz@redhat.com> 1.8.5-3
- fix the build on ARMv7

* Thu Jan 23 2020 Tomáš Mráz <tmraz@redhat.com> 1.8.5-2
- Intel CET support by H. J. Lu

* Tue Sep  3 2019 Tomáš Mráz <tmraz@redhat.com> 1.8.5-1
- new upstream version 1.8.5
- add CMAC selftest for FIPS POST
- add continuous FIPS entropy test
- disable non-approved FIPS hashes in the enforced FIPS mode

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Feb 12 2019 Tomáš Mráz <tmraz@redhat.com> 1.8.4-3
- fix the build tests to pass in the FIPS mode

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Nov 20 2018 Tomáš Mráz <tmraz@redhat.com> 1.8.4-1
- new upstream version 1.8.4

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jul 12 2018 Tomáš Mráz <tmraz@redhat.com> 1.8.3-2
- make only_urandom a default in non-presence of configuration file
- run the full FIPS selftests only when the library is called from
  application

* Thu Jun 14 2018 Tomáš Mráz <tmraz@redhat.com> 1.8.3-1
- new upstream version 1.8.3

* Tue Feb  6 2018 Tomáš Mráz <tmraz@redhat.com> 1.8.2-2
- fix behavior when getrandom syscall is not present (#1542453)

* Thu Dec 21 2017 Tomáš Mráz <tmraz@redhat.com> 1.8.2-1
- new upstream version 1.8.2

* Tue Dec  5 2017 Tomáš Mráz <tmraz@redhat.com> 1.8.1-3
- do not try to access() /dev/urandom either if getrandom() works

* Mon Dec  4 2017 Tomáš Mráz <tmraz@redhat.com> 1.8.1-2
- do not try to open /dev/urandom if getrandom() works (#1380866)

* Tue Sep  5 2017 Tomáš Mráz <tmraz@redhat.com> 1.8.1-1
- new upstream version 1.8.1

* Wed Aug 16 2017 Tomáš Mráz <tmraz@redhat.com> 1.8.0-1
- new upstream version 1.8.0

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jun 29 2017 Tomáš Mráz <tmraz@redhat.com> 1.7.8-1
- new upstream version 1.7.8

* Fri Jun  2 2017 Tomáš Mráz <tmraz@redhat.com> 1.7.7-1
- new upstream version 1.7.7
- GOST is now enabled

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Jan 30 2017 Tomáš Mráz <tmraz@redhat.com> 1.7.6-1
- new upstream version 1.7.6

* Fri Dec 16 2016 Tomáš Mráz <tmraz@redhat.com> 1.7.5-1
- new upstream version 1.7.5

* Wed Nov 23 2016 Tomáš Mráz <tmraz@redhat.com> 1.7.3-1
- new upstream version 1.7.3

* Wed Aug 17 2016 Tomáš Mráz <tmraz@redhat.com> 1.6.6-1
- new upstream version with important security fix (CVE-2016-6316)

* Thu Jul 21 2016 Tomáš Mráz <tmraz@redhat.com> 1.6.5-1
- new upstream version fixing low impact issue CVE-2015-7511

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.6.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Sep  9 2015 Tomáš Mráz <tmraz@redhat.com> 1.6.4-1
- new upstream version

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Apr  3 2015 Tomáš Mráz <tmraz@redhat.com> 1.6.3-4
- deinitialize the RNG after the selftest is run

* Tue Mar 24 2015 Tomáš Mráz <tmraz@redhat.com> 1.6.3-3
- touch only urandom in the selftest and when /dev/random is
  unavailable for example by SELinux confinement
- fix the RSA selftest key (p q swap) (#1204517)

* Fri Mar 13 2015 Tomáš Mráz <tmraz@redhat.com> 1.6.3-2
- do not use strict aliasing for bufhelp functions (#1201219)

* Fri Mar  6 2015 Tomáš Mráz <tmraz@redhat.com> 1.6.3-1
- new upstream version

* Wed Feb 25 2015 Tomáš Mráz <tmraz@redhat.com> 1.6.2-4
- do not initialize secure memory during the selftest (#1195850)

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 1.6.2-3
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Wed Jan 14 2015 Tomáš Mráz <tmraz@redhat.com> 1.6.2-2
- fix buildability of programs using gcrypt.h with -ansi (#1182200)

* Mon Dec  8 2014 Tomáš Mráz <tmraz@redhat.com> 1.6.2-1
- new upstream version

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 17 2014 Tom Callaway <spot@fedoraproject.org> - 1.6.1-6
- fix license handling

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 20 2014 Kyle McMartin <kyle@fedoraproject.org> 1.6.1-4
- Re-enable below algos, apply patch from upstream list to make
  that code -fPIC friendly. (rhbz#1069792)

* Mon May 19 2014 Kyle McMartin <kyle@fedoraproject.org> 1.6.1-3
- Disable rijndael, cast5, camellia ARM assembly, as it's non-PIC as
  presently written, which results in .text relocations in the shared
  library. (rhbz#1069792)

* Thu Apr 24 2014 Tomáš Mráz <tmraz@redhat.com> 1.6.1-2
- drop the temporary compat shared library version
- fix the soname version in -use-fipscheck.patch

* Fri Feb 28 2014 Tomáš Mráz <tmraz@redhat.com> 1.6.1-1
- new upstream version breaking ABI compatibility
- this release temporarily includes old compatibility .so

* Tue Jan 21 2014 Tomáš Mráz <tmraz@redhat.com> 1.5.3-3
- add back the nistp521r1 EC curve
- fix a bug in the Whirlpool hash implementation
- speed up the PBKDF2 computation

* Sun Oct 20 2013 Tom Callaway <spot@fedoraproject.org> - 1.5.3-2
- add cleared ECC support

* Fri Jul 26 2013 Tomáš Mráz <tmraz@redhat.com> 1.5.3-1
- new upstream version fixing cache side-channel attack on RSA private keys

* Thu Jun 20 2013 Tomáš Mráz <tmraz@redhat.com> 1.5.2-3
- silence false error detected by valgrind (#968288)

* Thu Apr 25 2013 Tomáš Mráz <tmraz@redhat.com> 1.5.2-2
- silence strict aliasing warning in Rijndael
- apply UsrMove
- spec file cleanups

* Fri Apr 19 2013 Tomáš Mráz <tmraz@redhat.com> 1.5.2-1
- new upstream version

* Wed Mar 20 2013 Tomas Mraz <tmraz@redhat.com> 1.5.1-1
- new upstream version

* Tue Mar  5 2013 Tomas Mraz <tmraz@redhat.com> 1.5.0-11
- use poll() instead of select() when gathering randomness (#913773)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jan  3 2013 Tomas Mraz <tmraz@redhat.com> 1.5.0-9
- allow empty passphrase in PBKDF2 needed for cryptsetup (=891266)

* Mon Dec  3 2012 Tomas Mraz <tmraz@redhat.com> 1.5.0-8
- fix multilib conflict in libgcrypt-config
- fix minor memory leaks and other bugs found by Coverity scan

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Apr  5 2012 Tomas Mraz <tmraz@redhat.com> 1.5.0-5
- Correctly rebuild the info documentation

* Wed Apr  4 2012 Tomas Mraz <tmraz@redhat.com> 1.5.0-4
- Add GCRYCTL_SET_ENFORCED_FIPS_FLAG command

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Aug 15 2011 Kalev Lember <kalevlember@gmail.com> 1.5.0-2
- Rebuilt for rpm bug #728707

* Thu Jul 21 2011 Tomas Mraz <tmraz@redhat.com> 1.5.0-1
- new upstream version

* Mon Jun 20 2011 Tomas Mraz <tmraz@redhat.com> 1.4.6-4
- Always xor seed from /dev/urandom over /etc/gcrypt/rngseed

* Mon May 30 2011 Tomas Mraz <tmraz@redhat.com> 1.4.6-3
- Make the FIPS-186-3 DSA implementation CAVS testable
- add configurable source of RNG seed /etc/gcrypt/rngseed
  in the FIPS mode (#700388)

* Fri Feb 11 2011 Tomas Mraz <tmraz@redhat.com> 1.4.6-1
- new upstream version with minor changes

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.5-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Feb  4 2011 Tomas Mraz <tmraz@redhat.com> 1.4.5-6
- fix a bug in the fips-186-3 dsa parameter generation code

* Tue Feb  1 2011 Tomas Mraz <tmraz@redhat.com> 1.4.5-5
- use /dev/urandom for seeding in the FIPS mode
- make the tests to pass in the FIPS mode also fixing
  the FIPS-186-3 DSA keygen

* Sun Feb 14 2010 Rex Dieter <rdieter@fedoraproject.org> 1.4.5-4
- FTBFS libgcrypt-1.4.5-3.fc13: ImplicitDSOLinking (#564973)

* Wed Feb  3 2010 Tomas Mraz <tmraz@redhat.com> 1.4.5-3
- drop the S390 build workaround as it is no longer needed
- additional spec file cleanups for merge review (#226008)

* Mon Dec 21 2009 Tomas Mraz <tmraz@redhat.com> 1.4.5-1
- workaround for build on S390 (#548825)
- spec file cleanups
- upgrade to new minor upstream release

* Tue Aug 11 2009 Tomas Mraz <tmraz@redhat.com> 1.4.4-8
- fix warning when installed with --excludedocs (#515961)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.4-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jun 18 2009 Tomas Mraz <tmraz@redhat.com> 1.4.4-6
- and now really apply the padlock patch

* Wed Jun 17 2009 Tomas Mraz <tmraz@redhat.com> 1.4.4-5
- fix VIA padlock RNG inline assembly call (#505724)

* Thu Mar  5 2009 Tomas Mraz <tmraz@redhat.com> 1.4.4-4
- with the integrity verification check the library needs to link to libdl
  (#488702)

* Tue Mar  3 2009 Tomas Mraz <tmraz@redhat.com> 1.4.4-3
- add hmac FIPS integrity verification check

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jan 30 2009 Tomas Mraz <tmraz@redhat.com> 1.4.4-1
- update to 1.4.4
- do not abort when the fips mode kernel flag is inaccessible
  due to permissions (#470219)
- hobble the library to drop the ECC support

* Mon Oct 20 2008 Dennis Gilmore <dennis@ausil.us> 1.4.3-2
- disable asm on sparc64

* Thu Sep 18 2008 Nalin Dahyabhai <nalin@redhat.com> 1.4.3-1
- update to 1.4.3
- own /etc/gcrypt

* Mon Sep 15 2008 Nalin Dahyabhai <nalin@redhat.com>
- invoke make with %%{?_smp_mflags} to build faster on multi-processor
  systems (Steve Grubb)

* Mon Sep  8 2008 Nalin Dahyabhai <nalin@redhat.com> 1.4.2-1
- update to 1.4.2

* Tue Apr 29 2008 Nalin Dahyabhai <nalin@redhat.com> 1.4.1-1
- update to 1.4.1
- bump libgpgerror-devel requirement to 1.4, matching the requirement enforced
  by the configure script

* Thu Apr  3 2008 Joe Orton <jorton@redhat.com> 1.4.0-3
- add patch from upstream to fix severe performance regression
  in entropy gathering

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.4.0-2
- Autorebuild for GCC 4.3

* Mon Dec 10 2007 Nalin Dahyabhai <nalin@redhat.com> - 1.4.0-1
- update to 1.4.0

* Tue Oct 16 2007 Nalin Dahyabhai <nalin@redhat.com> - 1.2.4-6
- use ldconfig to build the soname symlink for packaging along with the
  shared library (#334731)

* Wed Aug 22 2007 Nalin Dahyabhai <nalin@redhat.com> - 1.2.4-5
- add missing gawk buildrequirement
- switch from explicitly specifying the /dev/random RNG to just verifying
  that the non-LGPL ones were disabled by the configure script

* Thu Aug 16 2007 Nalin Dahyabhai <nalin@redhat.com> - 1.2.4-4
- clarify license
- force use of the linux /dev/random RNG, to avoid accidentally falling back
  to others which would affect the license of the resulting library

* Mon Jul 30 2007 Nalin Dahyabhai <nalin@redhat.com> - 1.2.4-3
- disable static libraries (part of #249815)

* Fri Jul 27 2007 Nalin Dahyabhai <nalin@redhat.com> - 1.2.4-2
- move libgcrypt shared library to /%%{_lib} (#249815)

* Tue Feb  6 2007 Nalin Dahyabhai <nalin@redhat.com> - 1.2.4-1
- update to 1.2.4

* Mon Jan 22 2007 Nalin Dahyabhai <nalin@redhat.com> - 1.2.3-2
- make use of install-info more failsafe (Ville Skyttä, #223705)

* Fri Sep  1 2006 Nalin Dahyabhai <nalin@redhat.com> - 1.2.3-1
- update to 1.2.3

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.2.2-3.1
- rebuild

* Mon Jun 05 2006 Jesse Keating <jkeating@redhat.com> 1.2.2-3
- Added missing buildreq pkgconfig

* Tue May 16 2006 Nalin Dahyabhai <nalin@redhat.com> 1.2.2-2
- remove file conflicts in libgcrypt-config by making the 64-bit version
  think the libraries are in /usr/lib (which is wrong, but which it also
  prunes from the suggest --libs output, so no harm done, hopefully)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.2.2-1.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.2.2-1.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Oct  5 2005 Nalin Dahyabhai <nalin@redhat.com> 1.2.2-1
- update to 1.2.2

* Wed Mar 16 2005 Nalin Dahyabhai <nalin@redhat.com> 1.2.1-1
- update to 1.2.1

* Fri Jul 30 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- another try to package the symlink

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sun May  2 2004 Bill Nottingham <notting@redhat.com> - 1.2.0-1
- update to official 1.2.0

* Fri Apr 16 2004 Bill Nottingham <notting@redhat.com> - 1.1.94-1
- update to 1.1.94

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sat Feb 21 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- add symlinks to shared libs at compile time

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Mar 20 2003 Jeff Johnson <jbj@redhat.com> 1.1.12-1
- upgrade to 1.1.12 (beta).

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May 21 2002 Jeff Johnson <jbj@redhat.com>
- update to 1.1.7
- change license to LGPL.
- include splint annotations patch.
- install info pages.

* Tue Apr  2 2002 Nalin Dahyabhai <nalin@redhat.com> 1.1.6-1
- update to 1.1.6

* Thu Jan 10 2002 Nalin Dahyabhai <nalin@redhat.com> 1.1.5-1
- fix the Source tag so that it's a real URL

* Thu Dec 20 2001 Nalin Dahyabhai <nalin@redhat.com>
- initial package
