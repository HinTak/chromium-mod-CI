%define _lto_cflags %{nil}

# enable|disable system build flags
%global system_build_flags 0

# set default numjobs for the koji build
%ifarch aarch64
%global numjobs 8
%else
%global numjobs %{_smp_build_ncpus}
%endif

# enable|disable all cpus for the build.
%global use_all_cpus 1

%if %{use_all_cpus}
%global numjobs %{_smp_build_ncpus}
%endif
 
# official builds have less debugging and go faster... but we have to shut some things off.
%global official_build 1

# enable|disble bootstrap
%global bootstrap 0
# workaround for broken gn on epel 8/9
%if 0%{?rhel} == 8 || 0%{?rhel} == 9
%global bootstrap 1
%endif

# Fancy build status, so we at least know, where we are..
# %1 where
# %2 what
%global build_target() \
	export NINJA_STATUS="[%2:%f/%t] " ; \
	ninja -j %{numjobs} -C '%1' '%2'

# enable|disable headless client build
%global build_headless 1

# enable|disable chrome-remote-desktop build
%global build_remoting 0

# set nodejs_version
%global nodejs_version v20.6.1

%global system_nodejs 1
# RHEL 8 needs newer nodejs
%if 0%{?rhel} == 8
%global system_nodejs 0
%endif

# set esbuild_version
%global esbuild_version 0.19.2

# set latest version for devtoolset and gcc-toolset
%global dts_version 12
%if 0%{?rhel} == 8 || 0%{?rhel} == 9
%global dts_version 13
%endif

# set latest version for llvm-toolset on el7
%global llvm_toolset_version 14.0

# set name for toolset
%if 0%{?rhel} == 7
%global toolset devtoolset
%else
%global toolset gcc-toolset
%endif

%if 0%{?rhel} == 7
%global chromium_pybin /usr/bin/python3
%else
%global chromium_pybin %{__python3}
%endif

# va-api only supported in rhel >= 9 and fedora
%global use_vaapi 1

# v4l2_codec only enable for fedora aarch64
%global use_v4l2_codec 0

# libva in EL7 and EL8 is too old.
%if 0%{?rhel} == 7 || 0%{?rhel} == 8
%global use_vaapi 0
%endif

# enable v4l2 and disable vaapi for aarch64 platform
%ifarch aarch64
%if 0%{?fedora} >= 36
%global use_vaapi 0
%global use_v4l2_codec 1
%endif
%endif

# Workaround for https://bugzilla.redhat.com/show_bug.cgi?id=2239523
# Disable BTI until this is fixed upstream.
%global disable_bti 0
%ifarch aarch64
%if 0%{?fedora}
%global optflags %(echo %{optflags} | sed 's/-mbranch-protection=standard /-mbranch-protection=pac-ret /')
%global disable_bti 1
%endif
%endif

# Seems like we might need this sometimes
# Practically, no. But it's here in case we do.
%global use_gold 0

%global build_clear_key_cdm 0

# Disabled because of Google, starting with Chromium 88.
%global userestrictedapikeys 0

# We can still use the api key though. For now.
%global useapikey 1

# Leave this alone, please.
%global builddir out/Release
%global headlessbuilddir out/Headless
%global remotingbuilddir out/Remoting

# enable|disable debuginfo
%global enable_debug 1
# disable debuginfo due to a bug in debugedit on el7
# error: canonicalization unexpectedly shrank by one character
# https://bugzilla.redhat.com/show_bug.cgi?id=304121
%if 0%{?rhel} == 7
%global enable_debug 0
%endif
%if ! %{enable_debug}
%global debug_package %{nil}
%global debug_level 0
%else
%global debug_level 1
# workaround for the error empty file debugsource
%undefine _debugsource_packages
%endif

# %%{nil} for Stable; -beta for Beta; -dev for Devel
# dash in -beta and -dev is intentional !
%global chromium_channel %{nil}
%global chromium_menu_name Chromium
%global chromium_browser_channel chromium-browser%{chromium_channel}
%global chromium_path %{_libdir}/chromium-browser%{chromium_channel}
%global crd_path %{_libdir}/chrome-remote-desktop

# We don't want any libs in these directories to generate Provides
# Requires is trickier.

# To generate this list, go into %%{buildroot}%%{chromium_path} and run
# for i in `find . -name "*.so" | sort`; do NAME=`basename -s .so $i`; printf "$NAME|"; done
# for RHEL7, append libfontconfig to the end
# make sure there is not a trailing | at the end of the list
# We always filter provides. We only filter Requires when building shared.
%global __provides_exclude_from ^(%{chromium_path}/.*\\.so|%{chromium_path}/.*\\.so.*)$
%global __requires_exclude ^(%{chromium_path}/.*\\.so|%{chromium_path}/.*\\.so.*)$

# enable|disable use_custom_libcxx
%global use_custom_libcxx 1

# enable clang by default
%global clang 1

# enable|disable control flow integrity support
%global cfi 0
%if %{clang}
%if 0%{?fedora} || 0%{?rhel} > 7
%global cfi 1
%endif
%endif

# set correct toolchain
%if %{clang}
%global toolchain clang
%else
%global toolchain gcc
%endif

# enable qt backend for el >= 8 and fedora
%if 0%{?rhel} >= 8 || 0%{?fedora}
%global use_qt 1
%else
%global use_qt 0
%endif

%if 0%{?rhel} > 9 || 0%{?fedora}
%global use_qt6 1
%else
%global use_qt6 0
%endif

# enable gtk3 by default
%global gtk3 1

# Chromium's fork of ICU is now something we can't unbundle.
# This is left here to ease the change if that ever switches.
%global bundleicu 1

# system libre2.so is not supported with use_custom_libcxx=true
# because the library's interface relies on libstdc++'s std::string and std::vector.
%global bundlere2 1

# The libxml_utils code depends on the specific bundled libxml checkout
# which is not compatible with the current code in the Fedora package as of
# 2017-06-08.
%global bundlelibxml 1

%global bundlelibaom 1

# Fedora's Python 2 stack is being removed, we use the bundled Python libraries
# This can be revisited once we upgrade to Python 3
%global bundlepylibs 0

# RHEL 7.9 dropped minizip.
# enable bundleminizip for Fedora > 39 due to switch to minizip-ng
# which breaks the build
%global bundleminizip 0
%if 0%{?rhel} == 7 || 0%{?fedora} > 39
%global bundleminizip 1
%endif

%if 0%{?rhel} == 7 || 0%{?rhel} == 8
%global bundleopus 1
%global bundlelibusbx 1
%global bundleharfbuzz 1
%global bundlelibwebp 1
%global bundlelibpng 1
%global bundlelibjpeg 1
%global bundlefreetype 1
%global bundlelibdrm 1
%global bundlefontconfig 1
%global bundleffmpegfree 1
%global bundlebrotli 1
%else
%if 0%{?fedora} > 37
%global bundleharfbuzz 0
%else
%global bundleharfbuzz 1
%endif
# disable system brotli due to old system brotli on el and fedora < 38
%if 0%{?fedora} > 38
%global bundlebrotli 0
%else
%global bundlebrotli 1
%endif
%global bundleopus 0
%global bundlelibusbx 0
%global bundlelibwebp 0
%global bundlelibpng 0
%global bundlelibjpeg 0
%global bundlelibdrm 0
%global bundlefontconfig 0
%global bundleffmpegfree 0
%global bundlefreetype 0
%endif

### From 2013 until early 2021, Google permitted distribution builds of
### Chromium to access Google APIs that added significant features to
### Chromium including, but not limited to, Sync and geolocation.
### As of March 15, 2021, any Chromium builds which pass client_id and/or
### client_secret during build will prevent end-users from signing into their
### Google account.

### With Chromium 88, I have removed the calls to "google_default_client_id"
### and "google_default_client_secret" to comply with their changes.

### Honestly, at this point, you might be better off looking for a different
### FOSS browser.

### Google API keys (see http://www.chromium.org/developers/how-tos/api-keys)
### Note: These are for Fedora use ONLY.
### For your own distribution, please get your own set of keys.
### http://lists.debian.org/debian-legal/2013/11/msg00006.html
%if %{useapikey}
%global api_key AIzaSyDUIXvzVrt5OkVsgXhQ6NFfvWlA44by-aw
%else
%global api_key %nil
%endif

%if %{userestrictedapikeys}
%global default_client_id 449907151817.apps.googleusercontent.com
%global default_client_secret miEreAep8nuvTdvLums6qyLK
%global chromoting_client_id 449907151817-8vnlfih032ni8c4jjps9int9t86k546t.apps.googleusercontent.com 
%else
%global default_client_id %nil
%global default_client_secret %nil
%global chromoting_client_id %nil
%endif

Name:	chromium%{chromium_channel}
Version: 122.0.6226.2
Release: 1%{?dist}
Summary: A WebKit (Blink) powered web browser that Google doesn't want you to use
Url: http://www.chromium.org/Home
License: BSD-3-Clause AND LGPL-2.1-or-later AND Apache-2.0 AND IJG AND MIT AND GPL-2.0-or-later AND ISC AND OpenSSL AND (MPL-1.1 OR GPL-2.0-only OR LGPL-2.0-only)

### Chromium Fedora Patches ###
Patch0: chromium-70.0.3538.67-sandbox-pie.patch

# Use /etc/chromium for initial_prefs
Patch1: chromium-115-initial_prefs-etc-path.patch

# system libusb
Patch2: chromium-120-system-libusb.patch

# Do not mangle zlib
Patch5: chromium-77.0.3865.75-no-zlib-mangle.patch

# Do not use unrar code, it is non-free
Patch6: chromium-119-norar.patch

# Try to load widevine from other places
Patch8: chromium-117-widevine-other-locations.patch

# Tell bootstrap.py to always use the version of Python we specify
Patch11: chromium-93.0.4577.63-py3-bootstrap.patch

# Add "Fedora" to the user agent string
Patch12: chromium-101.0.4951.41-fedora-user-agent.patch

# debian patch, disable font-test 
Patch20: chromium-disable-font-tests.patch

# https://gitweb.gentoo.org/repo/gentoo.git/tree/www-client/chromium/files/chromium-unbundle-zlib.patch
Patch52: chromium-81.0.4044.92-unbundle-zlib.patch

# Fix headers to look for system paths when we are using system minizip
Patch61: chromium-119-system-minizip-header-fix.patch

# Fix issue where closure_compiler thinks java is only allowed in android builds
# https://bugs.chromium.org/p/chromium/issues/detail?id=1192875
Patch65: chromium-91.0.4472.77-java-only-allowed-in-android-builds.patch

# Update rjsmin to 1.2.0
Patch69: chromium-103.0.5060.53-update-rjsmin-to-1.2.0.patch

# Update six to 1.16.0
Patch70: chromium-105.0.5195.52-python-six-1.16.0.patch

# Disable tests on remoting build
Patch82: chromium-98.0.4758.102-remoting-no-tests.patch

# patch for using system brotli
Patch89: chromium-116-system-brotli.patch

# disable GlobalMediaControlsCastStartStop to avoid crash
# when using the address bar media player button
# it works with use_custom_libcxx=true
Patch90: chromium-120-disable-GlobalMediaControlsCastStartStop.patch

# patch for using system opus
Patch91: chromium-108-system-opus.patch

# need to explicitly include a kernel header on EL7 to support MFD_CLOEXEC, F_SEAL_SHRINK, F_ADD_SEALS, F_SEAL_SEAL
Patch100: chromium-116-el7-include-fcntl-memfd.patch

# add define HAVE_STRNDUP on epel7
Patch101: chromium-108-el7-wayland-strndup-error.patch

# Work around old and missing headers on EPEL7
Patch103: chromium-110-epel7-old-headers-workarounds.patch

# Use old cups (chromium's code workaround breaks on gcc)
# Revert: https://github.com/chromium/chromium/commit/c3213f8779ddc427e89d982514185ed5e4c94e91
Patch104: chromium-99.0.4844.51-epel7-old-cups.patch

# libdrm on EL7 is rather old and chromium assumes newer
# This gets us by for now
Patch105: chromium-120-el7-old-libdrm.patch

# error: no matching function for call to 'std::basic_string<char>::erase(std::basic_string<char>::const_iterator, __gnu_cxx::__normal_iterator<const char*, std::basic_string<char> >&)'
#   33 |   property_name.erase(property_name.cbegin(), cur);
# Not sure how this EVER worked anywhere, but it only seems to fail on EPEL-7.
Patch106: chromium-98.0.4758.80-epel7-erase-fix.patch

# Add additional operator== to make el7 happy.
Patch107: chromium-120-el7-extra-operator.patch
# old v4l2 on el7
Patch108: chromium-118-el7_v4l2_quantization.patch 
# workaround for clang bug on el7
Patch109: chromium-114-wireless-el7.patch
Patch110: chromium-115-buildflag-el7.patch
Patch111: chromium-116-constexpr.patch
Patch112: chromium-117-el7-default_constructor.patch
# old clang on el7

Patch113: chromium-120-el7-clang-version-warning.patch
Patch114: chromium-120-el7-clang-build-failure.patch

# system ffmpeg
# need for old ffmpeg 5.x on epel9 and fedora 37
Patch115: chromium-107-ffmpeg-5.x-duration.patch
# disable the check
Patch116: chromium-107-proprietary-codecs.patch
# fix tab crash with SIGTRAP error when using system ffmpeg
Patch117: chromium-118-sigtrap_system_ffmpeg.patch

# revert AV1 VAAPI video encode due to old libva on el9
Patch130: chromium-119-revert-av1enc-el9.patch

# file conflict with old kernel on el8/el9
Patch140: chromium-118-dma_buf_export_sync_file-conflict.patch

# fixes for old clang version in fedora < 38 end epel < 8 (old clang <= 15)
# compiler build errors, no matching constructor for initialization
Patch300: chromium-120-no_matching_constructor.patch
Patch301: chromium-115-compiler-SkColor4f.patch

# workaround for clang bug, https://github.com/llvm/llvm-project/issues/57826
Patch302: chromium-120-workaround_clang_bug-structured_binding.patch

# missing typename
Patch303: chromium-120-typename.patch

# error: invalid operands to binary expression
Patch304: chromium-117-string-convert.patch

Patch306: chromium-119-assert.patch

# disable memory tagging in epel7 and epel8 on aarch64 due to new feature IFUNC-Resolver
# not supported in old glibc < 2.30, error: fatal error: 'sys/ifunc.h' file not found
Patch307: chromium-120-arm64-memory_tagging.patch

# missing include header files
Patch310: chromium-120-missing-header-files.patch

# clang warnings
Patch311: chromium-115-clang-warnings.patch

# enable fstack-protector-strong
Patch312: chromium-119-fstack-protector-strong.patch

# build error
Patch351: chromium-117-mnemonic-error.patch

# Workaround for https://bugzilla.redhat.com/show_bug.cgi?id=2239523
# https://bugs.chromium.org/p/chromium/issues/detail?id=1145581#c60
# Disable BTI until this is fixed upstream.
Patch352: chromium-117-workaround_for_crash_on_BTI_capable_system.patch

# gn workaround for the error: Assignment had no effect
Patch353: chromium-120-gn-workaround-atspi.patch
# remove flag split-threshold-for-reg-with-hint, it' not supported in clang <= 17
Patch354: chromium-120-split-threshold-for-reg-with-hint.patch
# error: unknown type name 'nullptr_t'
Patch355: chromium-120-nullptr_t-without-namespace-std.patch
# disable FFmpegAllowLists by default to allow external ffmpeg
patch356: chromium-120-disable-FFmpegAllowLists.patch
# remove ldflags -Wl,-mllvm,-disable-auto-upgrade-debug-info which is not supported
Patch357: chromium-120-clang16-disable-auto-upgrade-debug-info.patch

# upstream patches

# Use chromium-latest.py to generate clean tarball from released build tarballs, found here:
# http://build.chromium.org/buildbot/official/
# For Chromium Fedora use chromium-latest.py --stable --ffmpegclean --ffmpegarm
# If you want to include the ffmpeg arm sources append the --ffmpegarm switch
# https://commondatastorage.googleapis.com/chromium-browser-official/chromium-%%{version}.tar.xz
Source0: chromium-%{version}-clean.tar.xz
Source1: README.fedora
Source2: chromium.conf
Source3: chromium-browser.sh
Source4: %{chromium_browser_channel}.desktop
# Also, only used if you want to reproduce the clean tarball.
Source5: clean_ffmpeg.sh
Source6: chromium-latest.py
Source7: get_free_ffmpeg_source_files.py
# Get the names of all tests (gtests) for Linux
# Usage: get_linux_tests_name.py chromium-%%{version} --spec
Source8: get_linux_tests_names.py
# GNOME stuff
Source9: chromium-browser.xml
Source10: chrome-remote-desktop@.service
Source11: master_preferences

%if ! %{system_nodejs}
Source12: https://nodejs.org/dist/%{nodejs_version}/node-%{nodejs_version}-linux-x64.tar.xz
Source13: https://nodejs.org/dist/%{nodejs_version}/node-%{nodejs_version}-linux-arm64.tar.xz
%endif

# esbuild binary
%if 0%{?rhel}
Source14: https://registry.npmjs.org/@esbuild/linux-x64/-/linux-x64-%{esbuild_version}.tgz
Source15: https://registry.npmjs.org/@esbuild/linux-arm64/-/linux-arm64-%{esbuild_version}.tgz
%endif

# esbuild binary from fedora
%if 0%{?fedora}
BuildRequires: golang-github-evanw-esbuild
%endif

%if %{clang}
%if 0%{?rhel} == 7
BuildRequires: llvm-toolset-%{llvm_toolset_version}
%else
BuildRequires: clang
BuildRequires: clang-tools-extra
BuildRequires: llvm
BuildRequires: lld
%endif
# needs for libatomic
%if 0%{?rhel} >= 7
BuildRequires: %{toolset}-%{dts_version}-libatomic-devel
%endif
%else
%if 0%{?rhel} == 7 || 0%{?rhel} == 8
BuildRequires: %{toolset}-%{dts_version}-binutils, %{toolset}-%{dts_version}-libatomic-devel
%endif
%if 0%{?fedora} || 0%{?rhel} > 8
BuildRequires: gcc-c++
BuildRequires: gcc
BuildRequires: binutils
%endif
%endif

# build with system ffmpeg-free
%if ! %{bundleffmpegfree}
BuildRequires: pkgconfig(libavcodec)
BuildRequires: pkgconfig(libavfilter)
BuildRequires: pkgconfig(libavformat)
BuildRequires: pkgconfig(libavutil)
# chromium fail to start for rpmfusion users due to ABI break in ffmpeg-free-6.0.1
# bethween fedora and rpmfussion.
%if 0%{?rhel} == 9 || 0%{?fedora} == 37
Conflicts: libavformat-free%{_isa} < 5.1.4
Conflicts: ffmpeg-libs%{_isa} < 5.1.4
%else
Conflicts: libavformat-free%{_isa} < 6.0.1
Conflicts: ffmpeg-libs%{_isa} < 6.0.1-2
%endif
%endif

# build with system libaom
%if ! %{bundlelibaom}
BuildRequires: libaom-devel
%endif

BuildRequires:	alsa-lib-devel
BuildRequires:	atk-devel
BuildRequires:	bison
BuildRequires:	cups-devel
BuildRequires:	dbus-devel
BuildRequires:	desktop-file-utils
BuildRequires:	expat-devel
BuildRequires:	flex
BuildRequires:	fontconfig-devel
BuildRequires:	glib2-devel
BuildRequires:	glibc-devel
BuildRequires:	gperf

%if %{use_qt}
BuildRequires: pkgconfig(Qt5Core)
BuildRequires: pkgconfig(Qt5Widgets)
%endif

%if %{use_qt6}
BuildRequires: pkgconfig(Qt6Core)
BuildRequires: pkgconfig(Qt6Widgets)
%endif

%if %{cfi}
BuildRequires: compiler-rt
%endif

%if ! %{bundleharfbuzz}
BuildRequires:	harfbuzz-devel >= 2.4.0
%endif

BuildRequires: libatomic
BuildRequires:	libcap-devel
BuildRequires:	libcurl-devel

%if ! %{bundlelibdrm}
BuildRequires:	libdrm-devel
%endif

BuildRequires:	libgcrypt-devel
BuildRequires:	libudev-devel
BuildRequires:	libuuid-devel

%if 0%{?fedora} >= 37
BuildRequires:	libusb-compat-0.1-devel
%else
BuildRequires:	libusb-devel
%endif

BuildRequires:	libutempter-devel
BuildRequires:	libXdamage-devel
BuildRequires:	libXtst-devel
BuildRequires:	xcb-proto
BuildRequires:	mesa-libgbm-devel

# Old Fedora (before 30) uses the 1.2 minizip by default.
# Newer Fedora needs to use the compat package
# Fedora > 39 uses minizip-ng
%if ! %{bundleminizip}
%if 0%{?fedora} > 39 || 0%{?rhel} > 9
# BuildRequires: minizip-ng-devel
BuildRequires: minizip-compat-devel
%else
BuildRequires: minizip-compat-devel
%endif
%endif

%if %{system_nodejs}
BuildRequires: nodejs
%endif

%if ! %{bootstrap}
BuildRequires: gn
%endif

BuildRequires:	nss-devel >= 3.26
BuildRequires:	pciutils-devel
BuildRequires:	pulseaudio-libs-devel

# For screen sharing on Wayland
%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires:	pkgconfig(libpipewire-0.3)
%endif

# for /usr/bin/appstream-util
BuildRequires: libappstream-glib

%if %{bootstrap}
# gn needs these
BuildRequires: libstdc++-static
%endif

# Fedora tries to use system libs whenever it can.
BuildRequires:	bzip2-devel
BuildRequires:	dbus-glib-devel
# For eu-strip
BuildRequires:	elfutils
BuildRequires:	elfutils-libelf-devel
BuildRequires:	flac-devel

%if ! %{bundlefreetype}
BuildRequires:	freetype-devel
%endif

# One of the python scripts invokes git to look for a hash. So helpful.
BuildRequires:	/usr/bin/git
BuildRequires:	hwdata
BuildRequires:	kernel-headers
BuildRequires:	libevent-devel
BuildRequires:	libffi-devel

%if ! %{bundleicu}
# If this is true, we're using the bundled icu.
# We'd like to use the system icu every time, but we cannot always do that.
# Not newer than 54 (at least not right now)
BuildRequires:	libicu-devel = 54.1
%endif

%if ! %{bundlelibjpeg}
# If this is true, we're using the bundled libjpeg
# which we need to do because the RHEL 7 libjpeg doesn't work for chromium anymore
BuildRequires:	libjpeg-devel
%endif

%if ! %{bundlelibpng}
# If this is true, we're using the bundled libpng
# which we need to do because the RHEL 7 libpng doesn't work right anymore
BuildRequires:	libpng-devel
%endif

BuildRequires:	libudev-devel

%if ! %{bundlelibusbx}
Requires: libusbx >= 1.0.21-0.1.git448584a
BuildRequires: libusbx-devel >= 1.0.21-0.1.git448584a
%endif

%if %{use_vaapi}
BuildRequires:	libva-devel
%endif

# We don't use libvpx anymore because Chromium loves to
# use bleeding edge revisions here that break other things
# ... so we just use the bundled libvpx.
%if ! %{bundlelibwebp}
BuildRequires:	libwebp-devel
%endif

BuildRequires:	libxslt-devel
BuildRequires:	libxshmfence-devel

# Same here, it seems.
# BuildRequires: libyuv-devel
BuildRequires:	mesa-libGL-devel

%if ! %{bundleopus}
BuildRequires:	opus-devel
%endif

BuildRequires:	perl(Switch)
BuildRequires: %{chromium_pybin}
BuildRequires:	pkgconfig(gtk+-3.0)
BuildRequires:	python3-devel
BuildRequires: python3-zipp
BuildRequires: python3-simplejson
BuildRequires: python3-importlib-metadata

%if 0%{?rhel} == 7 || 0%{?rhel} == 8  
BuildRequires: python3-dataclasses
%endif

%if ! %{bundlepylibs}
%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires: python3-beautifulsoup4
BuildRequires: python3-html5lib
BuildRequires: python3-markupsafe
BuildRequires: python3-ply
BuildRequires: python3-jinja2
%else
BuildRequires: python-beautifulsoup4
BuildRequires: python-html5lib
BuildRequires: python-markupsafe
BuildRequires: python-ply
BuildRequires: python-jinja2
%endif
%endif

%if ! %{bundlere2}
Requires: re2 >= 20160401
BuildRequires: re2-devel >= 20160401
%endif

%if ! %{bundlebrotli}
BuildRequires: brotli-devel
%endif

BuildRequires: speech-dispatcher-devel
BuildRequires: yasm
BuildRequires: zlib-devel

# remote desktop needs this
BuildRequires:	pam-devel
BuildRequires:	systemd

# using the built from source version on aarch64
BuildRequires: ninja-build

# Yes, java is needed as well..
%if %{build_headless}
BuildRequires:	java-1.8.0-openjdk-headless
%endif

BuildRequires: libevdev-devel

# There is a hardcoded check for nss 3.26 in the chromium code (crypto/nss_util.cc)
Requires: nss%{_isa} >= 3.26
Requires: nss-mdns%{_isa}

# GTK modules it expects to find for some reason.
%if %{gtk3}
Requires: libcanberra-gtk3%{_isa}
%else
Requires: libcanberra-gtk2%{_isa}
%endif

%if 0%{?fedora}
# This enables support for u2f tokens
Requires: u2f-hidraw-policy
%endif

Requires: chromium-common%{_isa} = %{version}-%{release}

# rhel 7: x86_64
# rhel 8+ and fedora 37+: x86_64 aarch64
%if 0%{?rhel} == 7
ExclusiveArch: x86_64
%else
ExclusiveArch: x86_64 aarch64
%endif

# Bundled bits (I'm sure I've missed some)
Provides: bundled(angle) = 2422
Provides: bundled(bintrees) = 1.0.1
# This is a fork of openssl.
Provides: bundled(boringssl)

%if %{bundlebrotli}
Provides: bundled(brotli) = 222564a95d9ab58865a096b8d9f7324ea5f2e03e
%endif

Provides: bundled(bspatch)
Provides: bundled(cacheinvalidation) = 20150720
Provides: bundled(colorama) = 799604a104
Provides: bundled(crashpad)
Provides: bundled(dmg_fp)
Provides: bundled(expat) = 2.2.0
Provides: bundled(fdmlibm) = 5.3

# Don't get too excited. MPEG and other legally problematic stuff is stripped out.
%if %{bundleffmpegfree}
Provides: bundled(ffmpeg) = 6.0
%endif

%if %{bundlelibaom}
Provides: bundled(libaom)
%endif

Provides: bundled(fips181) = 2.2.3

%if %{bundlefontconfig}
Provides: bundled(fontconfig) = 2.12.6
%endif

%if %{bundlefreetype}
Provides: bundled(freetype) = 2.11.0git
%endif

Provides: bundled(gperftools) = svn144

%if %{bundleharfbuzz}
Provides: bundled(harfbuzz) = 2.4.0
%endif

Provides: bundled(hunspell) = 1.6.0
Provides: bundled(iccjpeg)

%if %{bundleicu}
Provides: bundled(icu) = 58.1
%endif

Provides: bundled(kitchensink) = 1
Provides: bundled(leveldb) = 1.20
Provides: bundled(libaddressinput) = 0

%if %{bundlelibdrm}
Provides: bundled(libdrm) = 2.4.85
%endif

Provides: bundled(libevent) = 1.4.15
Provides: bundled(libjingle) = 9564

%if %{bundlelibjpeg}
Provides: bundled(libjpeg-turbo) = 1.4.90
%endif

Provides: bundled(libphonenumber) = a4da30df63a097d67e3c429ead6790ad91d36cf4

%if %{bundlelibpng}
Provides: bundled(libpng) = 1.6.22
%endif

Provides: bundled(libsrtp) = 2cbd85085037dc7bf2eda48d4cf62e2829056e2d

%if %{bundlelibusbx}
Provides: bundled(libusbx) = 1.0.17
%endif

Provides: bundled(libvpx) = 1.6.0

%if %{bundlelibwebp}
Provides: bundled(libwebp) = 0.6.0
%endif

%if %{bundlelibxml}
# Well, it's actually newer than 2.9.4 and has code in it that has been reverted upstream... but eh.
Provides: bundled(libxml) = 2.9.4
%endif

Provides: bundled(libXNVCtrl) = 302.17
Provides: bundled(libyuv) = 1651
Provides: bundled(lzma) = 15.14
Provides: bundled(libudis86) = 1.7.1
Provides: bundled(mesa) = 9.0.3
Provides: bundled(NSBezierPath) = 1.0
Provides: bundled(mozc)

%if %{bundleopus}
Provides: bundled(opus) = 1.1.3
%endif

Provides: bundled(ots) = 8d70cffebbfa58f67a5c3ed0e9bc84dccdbc5bc0
Provides: bundled(protobuf) = 3.0.0.beta.3
Provides: bundled(qcms) = 4

%if %{bundlere2}
Provides: bundled(re2)
%endif

Provides: bundled(sfntly) = 04740d2600193b14aa3ef24cd9fbb3d5996b9f77
Provides: bundled(skia)
Provides: bundled(SMHasher) = 0
Provides: bundled(snappy) = 1.1.4-head
Provides: bundled(speech-dispatcher) = 0.7.1
Provides: bundled(sqlite) = 3.17patched
Provides: bundled(superfasthash) = 0
Provides: bundled(talloc) = 2.0.1
Provides: bundled(usrsctp) = 0
Provides: bundled(v8) = 5.9.211.31
Provides: bundled(webrtc) = 90usrsctp
Provides: bundled(woff2) = 445f541996fe8376f3976d35692fd2b9a6eedf2d
Provides: bundled(xdg-mime)
Provides: bundled(xdg-user-dirs)
# Provides: bundled(zlib) = 1.2.11

# For selinux scriptlet
Requires(post): /usr/sbin/semanage
Requires(post): /usr/sbin/restorecon

%description
Chromium is an open-source web browser, powered by WebKit (Blink).

%package common
Summary: Files needed for both the headless_shell and full Chromium

# -common doesn't have chrome-remote-desktop bits
# but we need to clean it up if it gets disabled again
# NOTE: Check obsoletes version to be sure it matches
%if ! %{build_remoting}
Provides: chrome-remote-desktop = %{version}-%{release}
Obsoletes: chrome-remote-desktop <= 81.0.4044.138
%endif

%description common
%{summary}.

%if %{build_remoting}
%package -n chrome-remote-desktop
Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires: xorg-x11-server-Xvfb
Requires: python3-psutil
Requires: chromium-common%{_isa} = %{version}-%{release}
Summary: Remote desktop support for google-chrome & chromium

%description -n chrome-remote-desktop
Remote desktop support for google-chrome & chromium.
%endif

%package -n chromedriver
Summary: WebDriver for Google Chrome/Chromium
Requires: chromium-common%{_isa} = %{version}-%{release}

%description -n chromedriver
WebDriver is an open source tool for automated testing of webapps across many
browsers. It provides capabilities for navigating to web pages, user input,
JavaScript execution, and more. ChromeDriver is a standalone server which
implements WebDriver's wire protocol for Chromium. It is being developed by
members of the Chromium and WebDriver teams.

%package headless
Summary:	A minimal headless shell built from Chromium
Requires: chromium-common%{_isa} = %{version}-%{release}

%description headless
A minimal headless client built from Chromium. headless_shell is built
without support for alsa, cups, dbus, gconf, gio, kerberos, pulseaudio, or 
udev.

%prep
%setup -q -n chromium-%{version}

### Chromium Fedora Patches ###
%patch -P0 -p1 -b .sandboxpie
%patch -P1 -p1 -b .etc
%patch -P2 -p1 -b .system-libusb
%patch -P5 -p1 -b .nozlibmangle
%patch -P6 -p1 -b .nounrar
%patch -P8 -p1 -b .widevine-other-locations
%patch -P11 -p1 -b .py3

%patch -P20 -p1 -b .disable-font-test

%if ! %{bundleminizip}
%patch -P52 -p1 -b .unbundle-zlib
%patch -P61 -p1 -b .system-minizip
%endif

%patch -P65 -p1 -b .java-only-allowed
%patch -P69 -p1 -b .update-rjsmin-to-1.2.0
%patch -P70 -p1 -b .update-six-to-1.16.0
%patch -P82 -p1 -b .remoting-no-tests

%if ! %{bundlebrotli}
%patch -P89 -p1 -b .system-brotli
%endif

%if ! %{use_custom_libcxx}
%patch -P90 -p1 -b .disable-GlobalMediaControlsCastStartStop
%endif

%if ! %{bundleopus}
%patch -P91 -p1 -b .system-opus
%endif

# Fedora branded user agent
%if 0%{?fedora}
%patch -P12 -p1 -b .fedora-user-agent
%endif

%if ! %{bundleffmpegfree}
%if 0%{?rhel} == 9 || 0%{?fedora} == 37
%patch -P115 -p1 -b .ffmpeg-5.x-duration
%endif
%patch -P116 -p1 -b .prop-codecs
%patch -P117 -p1 -b .sigtrap_system_ffmpeg
%endif

# EPEL specific patches
%if 0%{?rhel} == 7
%patch -P100 -p1 -b .el7-memfd-fcntl-include
%patch -P101 -p1 -b .wayland-strndup-error
%patch -P103 -p1 -b .epel7-header-workarounds
%patch -P104 -p1 -b .el7cups
%patch -P105 -p1 -b .el7-old-libdrm
%patch -P106 -p1 -b .el7-erase-fix
%patch -P107 -p1 -b .el7-extra-operator-equalequal
%patch -P108 -p1 -b .el7_v4l2_quantization
%patch -P109 -p1 -b .wireless
%patch -P110 -p1 -b .buildflag-el7
%patch -P111 -p1 -b .constexpr
%patch -P112 -p1 -b .default_constructor
%patch -P113 -p1 -b .el7-clang-version-warning
%patch -P114 -p1 -R -b .clang-build-failure
%endif

%if 0%{?rhel} == 8 || 0%{?rhel} == 9
%patch -P140 -p1 -b .dma_buf_export_sync_file-conflict
%endif

%if 0%{?rhel} == 9
%patch -P130 -p1 -b .revert-av1enc
%endif

%if %{clang}
%if 0%{?rhel} < 8 || 0%{?fedora} < 38
%patch -P300 -p1 -b .no_matching_constructor
%patch -P301 -p1 -b .workaround_clang-SkColor4f
%patch -P302 -p1 -b .workaround_clang_bug-structured_binding
%patch -P303 -p1 -b .typename
%patch -P304 -p1 -b .string-convert
%patch -P306 -p1 -b .assert
%endif
%endif

%ifarch aarch64
%if 0%{?rhel} <= 8
%patch -P307 -p1 -b .memory_tagging
%endif
%endif

%patch -P310 -p1 -b .missing-header-files
%patch -P311 -p1 -b .clang-warnings
%patch -P312 -p1 -b .fstack-protector-strong

%patch -P351 -p1 -b .mnemonic-error

%if %{disable_bti}
%patch -P352 -p1 -b .workaround_for_crash_on_BTI_capable_system
%endif

%patch -P353 -p1 -b .gn-workaround-atspi
%patch -P354 -p1 -b .revert-split-threshold-for-reg-with-hint
%if ! %{use_custom_libcxx}
%patch -P355 -p1 -b .nullptr_t-without-namespace-std
%endif
%patch -P356 -p1 -b .disable-FFmpegAllowLists
%patch -P357 -p1 -b .clang16-disable-auto-upgrade-debug-info

# Change shebang in all relevant files in this directory and all subdirectories
# See `man find` for how the `-exec command {} +` syntax works
find -type f \( -iname "*.py" \) -exec sed -i '1s=^#! */usr/bin/\(python\|env python\)[23]\?=#!%{__python3}=' {} +

# Add correct path for nodejs binary
%if ! %{system_nodejs}
  pushd third_party/node/linux
%ifarch x86_64
  tar xf %{SOURCE12}
  mv node-%{nodejs_version}-linux-x64 node-linux-x64
%endif
%ifarch aarch64
  tar xf %{SOURCE13}
  mv node-%{nodejs_version}-linux-arm64 node-linux-arm64
  # This is weird, but whatever
  ln -s node-linux-arm64 node-linux-x64
%endif
popd
%else
  mkdir -p third_party/node/linux/node-linux-x64/bin
  ln -s %{_bindir}/node third_party/node/linux/node-linux-x64/bin/node
%endif

# Get rid of the bundled esbuild
%if 0%{?fedora}
  ln -sf %{_bindir}/esbuild third_party/devtools-frontend/src/third_party/esbuild/esbuild
%else
  %ifarch x86_64
    tar -zxf %{SOURCE14} --directory %{_tmppath}
  %endif
  %ifarch aarch64
    tar -zxf %{SOURCE15} --directory %{_tmppath}
  %endif
  mv %{_tmppath}/package/bin/esbuild third_party/devtools-frontend/src/third_party/esbuild/esbuild
%endif

# Get rid of the pre-built eu-strip binary, it is x86_64 and of mysterious origin
rm -rf buildtools/third_party/eu-strip/bin/eu-strip
  
# Replace it with a symlink to the Fedora copy
ln -s %{_bindir}/eu-strip buildtools/third_party/eu-strip/bin/eu-strip

%if %{bundlelibusbx}
# no hackity hack hack
%else
# hackity hack hack
rm -rf third_party/libusb/src/libusb/libusb.h
# we _shouldn't need to do this, but it looks like we do.
cp -a %{_includedir}/libusb-1.0/libusb.h third_party/libusb/src/libusb/libusb.h
%endif

# Hard code extra version
sed -i 's/getenv("CHROME_VERSION_EXTRA")/"Fedora Project"/' chrome/common/channel_info_posix.cc

# Fix hardcoded path in remoting code
sed -i 's|/opt/google/chrome-remote-desktop|%{crd_path}|g' remoting/host/setup/daemon_controller_delegate_linux.cc

%build
# utf8 issue on epel7, Internal parsing error 'ascii' codec can't
# decode byte 0xe2 in position 474: ordinal not in range(128)
%if 0%{?rhel} == 7
export LANG=en_US.UTF-8
%endif

# reduce warnings
%if %{clang}
FLAGS=' -Wno-deprecated-declarations -Wno-unknown-warning-option -Wno-unused-command-line-argument'
FLAGS+=' -Wno-unused-but-set-variable -Wno-unused-result -Wno-unused-function -Wno-unused-variable'
FLAGS+=' -Wno-unused-const-variable -Wno-unneeded-internal-declaration -Wno-unknown-attributes'
%endif

%if %{system_build_flags}
CFLAGS=${CFLAGS/-g }
CFLAGS=${CFLAGS/-fexceptions}
CFLAGS=${CFLAGS/-Wp,-D_GLIBCXX_ASSERTIONS}
CFLAGS=${CFLAGS/-fcf-protection}
CFLAGS=${CFLAGS/-fstack-clash-protection}
CFLAGS="$CFLAGS $FLAGS"
CXXFLAGS="$CFLAGS"
%else
# override system build flags
CFLAGS="$FLAGS"
CXXFLAGS="$FLAGS"
%endif

%if %{clang}
export CC=clang
export CXX=clang++
export AR=llvm-ar
export NM=llvm-nm
export READELF=llvm-readelf
%else
export CC=gcc
export CXX=g++ 
export AR=ar
export NM=nm
export READELF=readelf
%endif
export CFLAGS
export CXXFLAGS

# enable toolset on el7
%if 0%{?rhel} == 7
%if %{clang}
. /opt/rh/llvm-toolset-%{llvm_toolset_version}/enable
%else
. /opt/rh/%{toolset}-%{dts_version}/enable
%endif
%endif

# enable gcc toolset on el8
%if 0%{?rhel} == 8 && ! %{clang}
. /opt/rh/%{toolset}-%{dts_version}/enable
%endif

# Core defines are flags that are true for both the browser and headless.
CHROMIUM_CORE_GN_DEFINES=""
# using system toolchain
CHROMIUM_CORE_GN_DEFINES+=' custom_toolchain="//build/toolchain/linux/unbundle:default"'
CHROMIUM_CORE_GN_DEFINES+=' host_toolchain="//build/toolchain/linux/unbundle:default"'
CHROMIUM_CORE_GN_DEFINES+=' is_debug=false dcheck_always_on=false dcheck_is_configurable=false'
CHROMIUM_CORE_GN_DEFINES+=' use_goma=false'
CHROMIUM_CORE_GN_DEFINES+=' enable_nacl=false'
CHROMIUM_CORE_GN_DEFINES+=' system_libdir="%{_lib}"'

%if %{official_build}
CHROMIUM_CORE_GN_DEFINES+=' is_official_build=true'
sed -i 's|OFFICIAL_BUILD|GOOGLE_CHROME_BUILD|g' tools/generate_shim_headers/generate_shim_headers.py
%endif

%if 0%{?rhel} || 0%{?fedora} < 39
CHROMIUM_CORE_GN_DEFINES+=' chrome_pgo_phase=0'
%endif

%if %{cfi}
CHROMIUM_CORE_GN_DEFINES+=' is_cfi=true'
%else
CHROMIUM_CORE_GN_DEFINES+=' is_cfi=false'
%endif

%if %{useapikey}
CHROMIUM_CORE_GN_DEFINES+=' google_api_key="%{api_key}"'
%endif

%if %{userestrictedapikeys}
CHROMIUM_CORE_GN_DEFINES+=' google_default_client_id="%{default_client_id}"'
CHROMIUM_CORE_GN_DEFINES+=' google_default_client_secret="%{default_client_secret}"'
%endif

%if %{clang}
CHROMIUM_CORE_GN_DEFINES+=' is_clang=true'
CHROMIUM_CORE_GN_DEFINES+=' clang_base_path="%{_prefix}"'
CHROMIUM_CORE_GN_DEFINES+=' clang_use_chrome_plugins=false'
CHROMIUM_CORE_GN_DEFINES+=' use_lld=true'
%else
CHROMIUM_CORE_GN_DEFINES+=' is_clang=false'
CHROMIUM_CORE_GN_DEFINES+=' use_lld=false'
%endif

# disable rust, it's only using for testing
CHROMIUM_CORE_GN_DEFINES+=' enable_rust=false'

CHROMIUM_CORE_GN_DEFINES+=' use_sysroot=false disable_fieldtrial_testing_config=true'

%if %{use_gold}
CHROMIUM_CORE_GN_DEFINES+=' use_gold=true'
%else
CHROMIUM_CORE_GN_DEFINES+=' use_gold=false'
%endif

%ifarch aarch64
CHROMIUM_CORE_GN_DEFINES+=' target_cpu="arm64"'
%endif

CHROMIUM_CORE_GN_DEFINES+=' icu_use_data_file=true'
CHROMIUM_CORE_GN_DEFINES+=' target_os="linux"'
CHROMIUM_CORE_GN_DEFINES+=' current_os="linux"'
CHROMIUM_CORE_GN_DEFINES+=' treat_warnings_as_errors=false'
%if %{use_custom_libcxx}
CHROMIUM_CORE_GN_DEFINES+=' use_custom_libcxx=true'
%else
CHROMIUM_CORE_GN_DEFINES+=' use_custom_libcxx=false'
%endif
CHROMIUM_CORE_GN_DEFINES+=' enable_iterator_debugging=false'
CHROMIUM_CORE_GN_DEFINES+=' enable_vr=false'
CHROMIUM_CORE_GN_DEFINES+=' build_dawn_tests=false enable_perfetto_unittests=false'
CHROMIUM_CORE_GN_DEFINES+=' disable_fieldtrial_testing_config=true'
CHROMIUM_CORE_GN_DEFINES+=' symbol_level=%{debug_level}'
CHROMIUM_CORE_GN_DEFINES+=' blink_enable_generated_code_formatting=false'
CHROMIUM_CORE_GN_DEFINES+=' angle_has_histograms=false'
export CHROMIUM_CORE_GN_DEFINES

# browser gn defines
CHROMIUM_BROWSER_GN_DEFINES=""

# if systemwide ffmpeg free is used, the proprietary codecs can be set to true to load the codecs from ffmpeg-free
# the codecs computation is passed to ffmpeg-free in this case
%if ! %{bundleffmpegfree}
CHROMIUM_BROWSER_GN_DEFINES+=' ffmpeg_branding="Chrome" proprietary_codecs=true is_component_ffmpeg=true enable_ffmpeg_video_decoders=true media_use_ffmpeg=true'
%else
CHROMIUM_BROWSER_GN_DEFINES+=' ffmpeg_branding="Chromium" proprietary_codecs=false is_component_ffmpeg=false enable_ffmpeg_video_decoders=false media_use_ffmpeg=true'
%endif
CHROMIUM_BROWSER_GN_DEFINES+=' media_use_openh264=false'
CHROMIUM_BROWSER_GN_DEFINES+=' rtc_use_h264=false'
CHROMIUM_BROWSER_GN_DEFINES+=' use_kerberos=true'

%if %{use_qt}
CHROMIUM_BROWSER_GN_DEFINES+=' use_qt=true moc_qt5_path="%{_libdir}/qt5/bin/"'
%else
CHROMIUM_BROWSER_GN_DEFINES+=' use_qt=false'
%endif

%if %{use_qt6}
CHROMIUM_BROWSER_GN_DEFINES+=' use_qt6=true moc_qt6_path="%{_libdir}/qt6/libexec/"'
%else
CHROMIUM_BROWSER_GN_DEFINES+=' use_qt6=false'
%endif

CHROMIUM_BROWSER_GN_DEFINES+=' use_gio=true use_pulseaudio=true'
CHROMIUM_BROWSER_GN_DEFINES+=' enable_hangout_services_extension=true'
CHROMIUM_BROWSER_GN_DEFINES+=' use_aura=true'
CHROMIUM_BROWSER_GN_DEFINES+=' enable_widevine=true'

%if %{use_vaapi}
CHROMIUM_BROWSER_GN_DEFINES+=' use_vaapi=true'
%else
CHROMIUM_BROWSER_GN_DEFINES+=' use_vaapi=false'
%endif

%if %{use_v4l2_codec} 
CHROMIUM_BROWSER_GN_DEFINES+=' use_v4l2_codec=true'
%endif

%if 0%{?fedora} || 0%{?rhel} >= 8
CHROMIUM_BROWSER_GN_DEFINES+=' rtc_use_pipewire=true rtc_link_pipewire=true'
%endif

CHROMIUM_BROWSER_GN_DEFINES+=' use_system_libffi=true'
export CHROMIUM_BROWSER_GN_DEFINES

# headless gn defines
CHROMIUM_HEADLESS_GN_DEFINES=""
CHROMIUM_HEADLESS_GN_DEFINES+=' use_ozone=true ozone_auto_platforms=false ozone_platform="headless" ozone_platform_headless=true'
CHROMIUM_HEADLESS_GN_DEFINES+=' angle_enable_vulkan=true angle_enable_swiftshader=true headless_use_embedded_resources=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' headless_use_prefs=false headless_use_policy=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' v8_use_external_startup_data=false enable_print_preview=false enable_remoting=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' use_alsa=false use_bluez=false use_cups=false use_dbus=false use_gio=false use_kerberos=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' use_libpci=false use_pulseaudio=false use_udev=false rtc_use_pipewire=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' v8_enable_lazy_source_positions=false use_glib=false use_gtk=false use_pangocairo=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' use_qt=false use_qt6=false is_component_build=false enable_ffmpeg_video_decoders=false media_use_ffmpeg=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' media_use_libvpx=false proprietary_codecs=false'
export CHROMIUM_HEADLESS_GN_DEFINES

build/linux/unbundle/replace_gn_files.py --system-libraries \
%if ! %{bundlelibaom}
	libaom \
%endif
%if ! %{bundlebrotli}
	brotli \
%endif
%if ! %{bundlefontconfig}
	fontconfig \
%endif
%if ! %{bundleffmpegfree}
	ffmpeg \
%endif
%if ! %{bundlefreetype}
	freetype \
%endif
%if ! %{bundleharfbuzz}
	harfbuzz-ng \
%endif
%if ! %{bundleicu}
	icu \
%endif
%if ! %{bundlelibdrm}
	libdrm \
%endif
%if ! %{bundlelibjpeg}
	libjpeg \
%endif
%if ! %{bundlelibpng}
	libpng \
%endif
%if ! %{bundlelibusbx}
	libusb \
%endif
%if ! %{bundlelibwebp}
	libwebp \
%endif
%if ! %{bundlelibxml}
	libxml \
%endif
	libxslt \
%if ! %{bundleopus}
	opus \
%endif
%if ! %{bundlere2}
	re2 \
%endif
%if ! %{bundleminizip}
	zlib \
%endif
	flac

# Check that there is no system 'google' module, shadowing bundled ones:
if python3 -c 'import google ; print google.__path__' 2> /dev/null ; then \
    echo "Python 3 'google' module is defined, this will shadow modules of this build"; \
    exit 1 ; \
fi

%if %{bootstrap}
tools/gn/bootstrap/bootstrap.py --gn-gen-args="$CHROMIUM_CORE_GN_DEFINES $CHROMIUM_BROWSER_GN_DEFINES"
%else
mkdir -p %{builddir} && cp -a %{_bindir}/gn %{builddir}/
%endif

%{builddir}/gn --script-executable=%{chromium_pybin} gen --args="$CHROMIUM_CORE_GN_DEFINES $CHROMIUM_BROWSER_GN_DEFINES" %{builddir}

%if %{build_headless}
%{builddir}/gn --script-executable=%{chromium_pybin} gen --args="$CHROMIUM_CORE_GN_DEFINES $CHROMIUM_HEADLESS_GN_DEFINES" %{headlessbuilddir}
%endif

%if %{build_remoting}
%{builddir}/gn --script-executable=%{chromium_pybin} gen --args="$CHROMIUM_CORE_GN_DEFINES $CHROMIUM_BROWSER_GN_DEFINES" %{remotingbuilddir}
%endif

%if %{build_headless}
# Do headless first.
%build_target %{headlessbuilddir} headless_shell
%endif

%build_target %{builddir} chrome
%build_target %{builddir} chrome_sandbox
%build_target %{builddir} chromedriver

%if %{build_clear_key_cdm}
%build_target %{builddir} clear_key_cdm
%endif

%build_target %{builddir} policy_templates

%if %{build_remoting}
%build_target %{remotingbuilddir} remoting_all
%endif

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_bindir} \
         %{buildroot}%{chromium_path}/locales \
         %{buildroot}%{_sysconfdir}/%{name}

# install system wide chromium config
cp -a %{SOURCE2} %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
cp -a %{SOURCE3} %{buildroot}%{chromium_path}/%{chromium_browser_channel}.sh

%if ! %{use_vaapi}
# remove vaapi flags
echo "# system wide chromium flags" > %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
%endif

export BUILD_TARGET=`cat /etc/redhat-release`
export CHROMIUM_PATH=%{chromium_path}
export CHROMIUM_BROWSER_CHANNEL=%{chromium_browser_channel}

sed -i "s|@@BUILD_TARGET@@|$BUILD_TARGET|g" %{buildroot}%{chromium_path}/%{chromium_browser_channel}.sh
sed -i "s|@@CHROMIUM_PATH@@|$CHROMIUM_PATH|g" %{buildroot}%{chromium_path}/%{chromium_browser_channel}.sh
sed -i "s|@@CHROMIUM_BROWSER_CHANNEL@@|$CHROMIUM_BROWSER_CHANNEL|g" %{buildroot}%{chromium_path}/%{chromium_browser_channel}.sh

%if "%{chromium_channel}" == "%{nil}"
	sed -i "s|@@EXTRA_FLAGS@@||g" %{buildroot}%{chromium_path}/%{chromium_browser_channel}.sh
%else
	# Enable debug outputs for beta and dev channels
	export EXTRA_FLAGS="--enable-logging=stderr --v=2"
	sed -i "s|@@EXTRA_FLAGS@@|$EXTRA_FLAGS|g" %{buildroot}%{chromium_path}/%{chromium_browser_channel}.sh
%endif

ln -s ../..%{chromium_path}/%{chromium_browser_channel}.sh %{buildroot}%{_bindir}/%{chromium_browser_channel}
mkdir -p %{buildroot}%{_mandir}/man1/

pushd %{builddir}
	cp -a chrom*.pak resources.pak icudtl.dat %{buildroot}%{chromium_path}
	cp -a locales/*.pak %{buildroot}%{chromium_path}/locales/
	%ifarch x86_64 aarch64
		cp -a libvk_swiftshader.so %{buildroot}%{chromium_path}
		cp -a libvulkan.so.1 %{buildroot}%{chromium_path}
		cp -a vk_swiftshader_icd.json %{buildroot}%{chromium_path}
	%endif
	cp -a chrome %{buildroot}%{chromium_path}/%{chromium_browser_channel}
	cp -a chrome_sandbox %{buildroot}%{chromium_path}/chrome-sandbox
	cp -a chrome_crashpad_handler %{buildroot}%{chromium_path}/chrome_crashpad_handler
	cp -a ../../chrome/app/resources/manpage.1.in %{buildroot}%{_mandir}/man1/%{chromium_browser_channel}.1
	sed -i "s|@@PACKAGE@@|%{chromium_browser_channel}|g" %{buildroot}%{_mandir}/man1/%{chromium_browser_channel}.1
	sed -i "s|@@MENUNAME@@|%{chromium_menu_name}|g" %{buildroot}%{_mandir}/man1/%{chromium_browser_channel}.1

	# V8 initial snapshots
	# https://code.google.com/p/chromium/issues/detail?id=421063
	cp -a v8_context_snapshot.bin %{buildroot}%{chromium_path}

	# This is ANGLE, not to be confused with the similarly named files under swiftshader/
	cp -a libEGL.so libGLESv2.so %{buildroot}%{chromium_path}

	%if %{use_qt}
		cp -a libqt5_shim.so %{buildroot}%{chromium_path}
	%endif

	%if %{use_qt6}
		cp -a libqt6_shim.so %{buildroot}%{chromium_path}
	%endif

	%if %{build_clear_key_cdm}
		%ifarch x86_64
			cp -a ClearKeyCdm/_platform_specific/linux_x64/libclearkeycdm.so %{buildroot}%{chromium_path}
		%else
			%ifarch aarch64
				cp -a ClearKeyCdm/_platform_specific/linux_arm64/libclearkeycdm.so %{buildroot}%{chromium_path}
			%else
				cp -a libclearkeycdm.so %{buildroot}%{chromium_path}
			%endif
		%endif
	%endif

	# chromedriver
	cp -a chromedriver %{buildroot}%{chromium_path}/chromedriver
	ln -s ../..%{chromium_path}/chromedriver %{buildroot}%{_bindir}/chromedriver

	%if %{build_remoting}
		# Remote desktop bits
		mkdir -p %{buildroot}%{crd_path}
	%endif
popd

%if %{build_remoting}
	pushd %{remotingbuilddir}
		# Hey, there is a library now.
		cp -a libremoting_core.so %{buildroot}%{crd_path}/

		# See remoting/host/installer/linux/Makefile for logic
		mkdir -p %{buildroot}%{crd_path}/remoting_locales
		cp -a remoting_native_messaging_host %{buildroot}%{crd_path}/native-messaging-host
		cp -a remote_assistance_host %{buildroot}%{crd_path}/remote-assistance-host
		cp -a remoting_locales/*.pak %{buildroot}%{crd_path}/remoting_locales/
		cp -a remoting_me2me_host %{buildroot}%{crd_path}/chrome-remote-desktop-host
		cp -a remoting_start_host %{buildroot}%{crd_path}/start-host
		cp -a remoting_user_session %{buildroot}%{crd_path}/user-session
		chmod +s %{buildroot}%{crd_path}/user-session

		# chromium
		mkdir -p %{buildroot}%{_sysconfdir}/chromium/native-messaging-hosts
		# google-chrome
		mkdir -p %{buildroot}%{_sysconfdir}/opt/chrome/
		cp -a remoting/* %{buildroot}%{_sysconfdir}/chromium/native-messaging-hosts/
		for i in %{buildroot}%{_sysconfdir}/chromium/native-messaging-hosts/*.json; do
			sed -i 's|/opt/google/chrome-remote-desktop|%{crd_path}|g' $i
		done
		mkdir -p %{buildroot}%{_sysconfdir}/opt/chrome/native-messaging-hosts
		pushd %{buildroot}%{_sysconfdir}/opt/chrome/native-messaging-hosts
			for i in ../../../chromium/native-messaging-hosts/*; do
				# rpm gets unhappy when we symlink here
				cp -a $i .
			done
		popd
	popd

	mkdir -p %{buildroot}/var/lib/chrome-remote-desktop
	touch %{buildroot}/var/lib/chrome-remote-desktop/hashes

	mkdir -p %{buildroot}%{_sysconfdir}/pam.d/
	pushd %{buildroot}%{_sysconfdir}/pam.d/
		ln -s system-auth chrome-remote-desktop
	popd

   cp -a remoting/host/linux/linux_me2me_host.py %{buildroot}%{crd_path}/chrome-remote-desktop
   cp -a remoting/host/installer/linux/is-remoting-session %{buildroot}%{crd_path}/

   mkdir -p %{buildroot}%{_unitdir}
   cp -a %{SOURCE10} %{buildroot}%{_unitdir}/
   sed -i 's|@@CRD_PATH@@|%{crd_path}|g' %{buildroot}%{_unitdir}/chrome-remote-desktop@.service
%endif

%if %{build_headless}
	pushd %{headlessbuilddir}
		cp -a headless_lib_data.pak headless_lib_strings.pak headless_shell %{buildroot}%{chromium_path}
	popd
%endif

# need to strip binaries explicitly when debug is disable
%if ! %{enable_debug}
pushd %{buildroot}%{chromium_path}/
for f in *.so chrome_crashpad_handler chrome-sandbox chromium-browser headless_shell chromedriver ; do
   [ -f $f ] && strip $f
done
popd
%endif

# Add directories for policy management
mkdir -p %{buildroot}%{_sysconfdir}/chromium/policies/managed
mkdir -p %{buildroot}%{_sysconfdir}/chromium/policies/recommended

cp -a out/Release/gen/chrome/app/policy/common/html/en-US/*.html .
cp -a out/Release/gen/chrome/app/policy/linux/examples/chrome.json .

mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
cp -a chrome/app/theme/chromium/product_logo_256.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/%{chromium_browser_channel}.png
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps
cp -a chrome/app/theme/chromium/product_logo_128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{chromium_browser_channel}.png
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/64x64/apps
cp -a chrome/app/theme/chromium/product_logo_64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{chromium_browser_channel}.png
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/48x48/apps
cp -a chrome/app/theme/chromium/product_logo_48.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{chromium_browser_channel}.png
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/24x24/apps
cp -a chrome/app/theme/chromium/product_logo_24.png %{buildroot}%{_datadir}/icons/hicolor/24x24/apps/%{chromium_browser_channel}.png

# Install the master_preferences file
install -m 0644 %{SOURCE11} %{buildroot}%{_sysconfdir}/%{name}/

mkdir -p %{buildroot}%{_datadir}/applications/
desktop-file-install --dir %{buildroot}%{_datadir}/applications %{SOURCE4}

install -D -m0644 chrome/installer/linux/common/chromium-browser/chromium-browser.appdata.xml \
  ${RPM_BUILD_ROOT}%{_datadir}/metainfo/%{chromium_browser_channel}.appdata.xml
appstream-util validate-relax --nonet ${RPM_BUILD_ROOT}%{_datadir}/metainfo/%{chromium_browser_channel}.appdata.xml

mkdir -p %{buildroot}%{_datadir}/gnome-control-center/default-apps/
cp -a %{SOURCE9} %{buildroot}%{_datadir}/gnome-control-center/default-apps/

# README.fedora
cp %{SOURCE1} .

%post
# Set SELinux labels - semanage itself will adjust the lib directory naming
# But only do it when selinux is enabled, otherwise, it gets noisy.
if selinuxenabled; then
	semanage fcontext -a -t bin_t /usr/lib/%{chromium_browser_channel} &>/dev/null || :
	semanage fcontext -a -t bin_t /usr/lib/%{chromium_browser_channel}/%{chromium_browser_channel}.sh &>/dev/null || :
	semanage fcontext -a -t chrome_sandbox_exec_t /usr/lib/chrome-sandbox &>/dev/null || :
	restorecon -R -v %{chromium_path}/%{chromium_browser_channel} &>/dev/null || :
fi

%if %{build_remoting}
%pretrans -n chrome-remote-desktop -p <lua> 
path = "/etc/opt/chrome/native-messaging-hosts"
st = posix.stat(path)
if st and st.type == "link" then
  os.remove(path)
end
%endif

%if %{build_remoting}
%pre -n chrome-remote-desktop
getent group chrome-remote-desktop >/dev/null || groupadd -r chrome-remote-desktop

%post -n chrome-remote-desktop
%systemd_post chrome-remote-desktop@.service

%preun -n chrome-remote-desktop
%systemd_preun chrome-remote-desktop@.service

%postun -n chrome-remote-desktop
%systemd_postun_with_restart chrome-remote-desktop@.service
%endif

%files
%doc AUTHORS README.fedora
%doc chrome_policy_list.html *.json
%license LICENSE
%config(noreplace) %{_sysconfdir}/%{name}/chromium.conf
%config %{_sysconfdir}/%{name}/master_preferences
%config %{_sysconfdir}/%{name}/policies/
%if %{build_remoting}
%exclude %{_sysconfdir}/%{name}/native-messaging-hosts/*
%endif
%{_bindir}/%{chromium_browser_channel}
%{chromium_path}/*.bin
%{chromium_path}/chrome_*.pak
%{chromium_path}/chrome_crashpad_handler
%{chromium_path}/resources.pak
%{chromium_path}/%{chromium_browser_channel}
%{chromium_path}/%{chromium_browser_channel}.sh
%attr(4755, root, root) %{chromium_path}/chrome-sandbox
%if %{use_qt}
%{chromium_path}/libqt5_shim.so
%endif
%if %{use_qt6}
%{chromium_path}/libqt6_shim.so
%endif
%{_mandir}/man1/%{chromium_browser_channel}.*
%{_datadir}/icons/hicolor/*/apps/%{chromium_browser_channel}.png
%{_datadir}/applications/*.desktop
%{_datadir}/metainfo/*.appdata.xml
%{_datadir}/gnome-control-center/default-apps/chromium-browser.xml

%files common
%if %{build_clear_key_cdm}
%{chromium_path}/libclearkeycdm.so
%endif
%ifarch x86_64 aarch64
%{chromium_path}/libvk_swiftshader.so*
%{chromium_path}/libvulkan.so*
%{chromium_path}/vk_swiftshader_icd.json
%{chromium_path}/libEGL.so*
%{chromium_path}/libGLESv2.so*
%endif
%{chromium_path}/icudtl.dat
%dir %{chromium_path}/
%dir %{chromium_path}/locales/
%lang(af) %{chromium_path}/locales/af.pak
%lang(am) %{chromium_path}/locales/am.pak
%lang(ar) %{chromium_path}/locales/ar.pak
%lang(bg) %{chromium_path}/locales/bg.pak
%lang(bn) %{chromium_path}/locales/bn.pak
%lang(ca) %{chromium_path}/locales/ca.pak
%lang(cs) %{chromium_path}/locales/cs.pak
%lang(da) %{chromium_path}/locales/da.pak
%lang(de) %{chromium_path}/locales/de.pak
%lang(el) %{chromium_path}/locales/el.pak
%lang(en_GB) %{chromium_path}/locales/en-GB.pak
# Chromium _ALWAYS_ needs en-US.pak as a fallback
# This means we cannot apply the lang code here.
# Otherwise, it is filtered out on install.
%{chromium_path}/locales/en-US.pak
%lang(es) %{chromium_path}/locales/es.pak
%lang(es) %{chromium_path}/locales/es-419.pak
%lang(et) %{chromium_path}/locales/et.pak
%lang(fa) %{chromium_path}/locales/fa.pak
%lang(fi) %{chromium_path}/locales/fi.pak
%lang(fil) %{chromium_path}/locales/fil.pak
%lang(fr) %{chromium_path}/locales/fr.pak
%lang(gu) %{chromium_path}/locales/gu.pak
%lang(he) %{chromium_path}/locales/he.pak
%lang(hi) %{chromium_path}/locales/hi.pak
%lang(hr) %{chromium_path}/locales/hr.pak
%lang(hu) %{chromium_path}/locales/hu.pak
%lang(id) %{chromium_path}/locales/id.pak
%lang(it) %{chromium_path}/locales/it.pak
%lang(ja) %{chromium_path}/locales/ja.pak
%lang(kn) %{chromium_path}/locales/kn.pak
%lang(ko) %{chromium_path}/locales/ko.pak
%lang(lt) %{chromium_path}/locales/lt.pak
%lang(lv) %{chromium_path}/locales/lv.pak
%lang(ml) %{chromium_path}/locales/ml.pak
%lang(mr) %{chromium_path}/locales/mr.pak
%lang(ms) %{chromium_path}/locales/ms.pak
%lang(nb) %{chromium_path}/locales/nb.pak
%lang(nl) %{chromium_path}/locales/nl.pak
%lang(pl) %{chromium_path}/locales/pl.pak
%lang(pt_BR) %{chromium_path}/locales/pt-BR.pak
%lang(pt_PT) %{chromium_path}/locales/pt-PT.pak
%lang(ro) %{chromium_path}/locales/ro.pak
%lang(ru) %{chromium_path}/locales/ru.pak
%lang(sk) %{chromium_path}/locales/sk.pak
%lang(sl) %{chromium_path}/locales/sl.pak
%lang(sr) %{chromium_path}/locales/sr.pak
%lang(sv) %{chromium_path}/locales/sv.pak
%lang(sw) %{chromium_path}/locales/sw.pak
%lang(ta) %{chromium_path}/locales/ta.pak
%lang(te) %{chromium_path}/locales/te.pak
%lang(th) %{chromium_path}/locales/th.pak
%lang(tr) %{chromium_path}/locales/tr.pak
%lang(uk) %{chromium_path}/locales/uk.pak
%lang(ur) %{chromium_path}/locales/ur.pak
%lang(vi) %{chromium_path}/locales/vi.pak
%lang(zh_CN) %{chromium_path}/locales/zh-CN.pak
%lang(zh_TW) %{chromium_path}/locales/zh-TW.pak
# These are psuedolocales, not real ones.
# They only get generated when is_official_build=false
%if ! %{official_build}
%{chromium_path}/locales/ar-XB.pak
%{chromium_path}/locales/en-XA.pak
%endif

%if %{build_headless}
%files headless
%{chromium_path}/headless_shell
%{chromium_path}/headless_lib_data.pak
%{chromium_path}/headless_lib_strings.pak
%endif

%if %{build_remoting}
%files -n chrome-remote-desktop
%{crd_path}/chrome-remote-desktop
%{crd_path}/chrome-remote-desktop-host
%{crd_path}/is-remoting-session
%{crd_path}/libremoting_core.so*
%{crd_path}/native-messaging-host
%{crd_path}/remote-assistance-host
%{_sysconfdir}/pam.d/chrome-remote-desktop
%{_sysconfdir}/chromium/native-messaging-hosts/*
%{_sysconfdir}/opt/chrome/
%{crd_path}/remoting_locales/
%{crd_path}/start-host
%{crd_path}/user-session
%{_unitdir}/chrome-remote-desktop@.service
/var/lib/chrome-remote-desktop/
%endif

%files -n chromedriver
%doc AUTHORS
%license LICENSE
%{_bindir}/chromedriver
%{chromium_path}/chromedriver

%changelog
* Thu Dec 21 2023 Than Ngo <than@redhat.com> - 120.0.6099.129-1
- update to 120.0.6099.129
  * High CVE-2023-7024: Heap buffer overflow in WebRTC

* Wed Dec 13 2023 Than Ngo <than@redhat.com> - 120.0.6099.109-1
- update to 120.0.6099.109
   * High CVE-2023-6702: Type Confusion in V8
   * High CVE-2023-6703: Use after free in Blink
   * High CVE-2023-6704: Use after free in libavif
   * High CVE-2023-6705: Use after free in WebRTC
   * High CVE-2023-6706: Use after free in FedCM
   * Medium CVE-2023-6707: Use after free in CSS

* Fri Dec 08 2023 Than Ngo <than@redhat.com> - 120.0.6099.71-1
- update to 120.0.6099.71

* Wed Dec 06 2023 Than Ngo <than@redhat.com> - 120.0.6099.62-2
- drop unsupported ldflag which caused build failure

* Tue Dec 05 2023 Than Ngo <than@redhat.com> - 120.0.6099.62-1
- update to 120.0.6099.62
- fixed bz#2252874, built with control flow integrity (CFI) support

* Sat Dec 02 2023 Than Ngo <than@redhat.com> - 120.0.6099.56-1
- update to 120.0.6099.56 
- enable qt6 UI backend

* Sat Dec 02 2023 Than Ngo <than@redhat.com> - 119.0.6045.199-2
- fixed bz#2242271, built with bundleminizip in fedora > 39
- fixed bz#2251884, built with fstack-protector-strong for improved security

* Wed Nov 29 2023 Than Ngo <than@redhat.com> - 119.0.6045.199-1
- update to 119.0.6045.199

* Sun Nov 19 2023 Than Ngo <than@redhat.com> - 119.0.6045.159-2
- fix ffmpeg conflicts

* Wed Nov 15 2023 Than Ngo <than@redhat.com> - 119.0.6045.159-1
- update to 119.0.6045.159, upstream security release
   High CVE-2023-5997, use after free in Garbage Collection
   High CVE-2023-6112, use after free in Navigation
- add Requires/Conflicts for ABI break in fmpeg-free 6.0.1
- drop first_dts patch, reintroduce first_dts patch in ffmpeg-free-6.0.1
- fixed python3 syntaxWarning: invalid escape sequenc
- skip clang's patches for epel8 that now gets clang-16 update

* Mon Nov 13 2023 Than Ngo <than@redhat.com> - 119.0.6045.123-2
- fixed bz#2240127, Some h.264 mp4s do not play 

* Wed Nov 08 2023 Than Ngo <than@redhat.com> - 119.0.6045.123-1
- update to 119.0.6045.123, include following security fixes:
  high CVE-2023-5996: Use after free in WebAudio

* Tue Nov 07 2023 Than Ngo <than@redhat.com> - 119.0.6045.105-2
- enable debuginfo

* Wed Nov 01 2023 Than Ngo <than@redhat.com> - 119.0.6045.105-1
- update to 119.0.6045.105

* Fri Oct 27 2023 Than Ngo <than@redhat.com> - 119.0.6045.59-1
- update 119.0.6045.59

* Wed Oct 25 2023 Than Ngo <than@redhat.com> - 118.0.5993.117-1
- update to 118.0.5993.117

* Wed Oct 18 2023 Than Ngo <than@redhat.com> - 118.0.5993.88-1
- update to 118.0.5993.88
- cleanup the package dependencies

* Mon Oct 16 2023 Than Ngo <than@redhat.com> - 118.0.5993.70-2
- fix tab crash with SIGTRAP when using system ffmpeg

* Wed Oct 11 2023 Than Ngo <than@redhat.com> - 118.0.5993.70-1
- update to 118.0.5993.70
    - CVE-2023-5218: Use after free in Site Isolation.
    - CVE-2023-5487: Inappropriate implementation in Fullscreen.
    - CVE-2023-5484: Inappropriate implementation in Navigation.
    - CVE-2023-5475: Inappropriate implementation in DevTools.
    - CVE-2023-5483: Inappropriate implementation in Intents.
    - CVE-2023-5481: Inappropriate implementation in Downloads.
    - CVE-2023-5476: Use after free in Blink History.
    - CVE-2023-5474: Heap buffer overflow in PDF.
    - CVE-2023-5479: Inappropriate implementation in Extensions API.
    - CVE-2023-5485: Inappropriate implementation in Autofill.
    - CVE-2023-5478: Inappropriate implementation in Autofill.
    - CVE-2023-5477: Inappropriate implementation in Installer.
    - CVE-2023-5486: Inappropriate implementation in Input.
    - CVE-2023-5473: Use after free in Cast.

* Sat Oct 07 2023 Than Ngo <than@redhat.com> - 118.0.5993.54-1
- update to 118.0.5993.54
- drop use_gnome_keyring as it's removed by upstream

* Thu Oct 05 2023 Than Ngo <than@redhat.com> - 117.0.5938.149-1
- update to 117.0.5938.149
- fix CVE-2023-5346: Type Confusion in V8

* Fri Sep 29 2023 Than Ngo <than@redhat.com> - 117.0.5938.132-2
- add workaround for the crash on BTI capable system 

* Thu Sep 28 2023 Than Ngo <than@redhat.com> - 117.0.5938.132-1
- update to 117.0.5938.132
- CVE-2023-5217, heap buffer overflow in vp8 encoding in libvpx.
- CVE-2023-5186, use after free in Passwords.
- CVE-2023-5187, use after free in Extensions.
￼	
* Sat Sep 23 2023 Than Ngo <than@redhat.com> - 117.0.5938.92-2
- backport upstream patch to fix memory leak

* Fri Sep 22 2023 Than Ngo <than@redhat.com> - 117.0.5938.92-1
- update to 117.0.5938.92

* Sun Sep 17 2023 Than Ngo <than@redhat.com> - 117.0.5938.88-1
- update to 117.0.5938.88

* Wed Sep 13 2023 Than Ngo <than@redhat.com> - 117.0.5938.62-1
- update to 117.0.5938.62

* Tue Sep 12 2023 Than Ngo <than@redhat.com> - 116.0.5845.187-1
- update to 116.0.5845.187

* Fri Sep 08 2023 Than Ngo <than@redhat.com> - 116.0.5845.179-1
- update to 116.0.5845.179

* Tue Aug 15 2023 Than Ngo <than@redhat.com> - 116.0.5845.96-1
- update to 116.0.5845.96 

* Wed Aug 09 2023 Than Ngo <than@redhat.com> - 115.0.5790.170-2
- set use_all_cpus=1 for aarch64

* Thu Aug 03 2023 Than Ngo <than@redhat.com> - 115.0.5790.170-1
- update to 115.0.5790.170

* Wed Jul 26 2023 Than Ngo <than@redhat.com> - 115.0.5790.110-1
- update to 115.0.5790.110

* Sat Jul 22 2023 Than Ngo <than@redhat.com> - 115.0.5790.102-1
- update to 115.0.5790.102

* Tue Jul 18 2023 Than Ngo <than@redhat.com> - 115.0.5790.98-1
- update to 115.0.5790.98

* Tue Jun 27 2023 Than Ngo <than@redhat.com> - 114.0.5735.198-1
- update to 114.0.5735.198

* Wed Jun 14 2023 Than Ngo <than@redhat.com> - 114.0.5735.133-1
- update to 114.0.5735.133 
- Enable AllowQt feature flag
- Fix Qt deps
- Fix Qt logical scale factor

* Wed Jun 07 2023 Than Ngo <than@redhat.com> - 114.0.5735.106-1
- update to 114.0.5735.106

* Sun May 28 2023 Than Ngo <than@redhat.com> - 114.0.5735.45-1
- update to 114.0.5735.45
- add qt6 linuxui backend
- backport: handle scale factor changes
- backport: fix font double_scaling

* Wed May 17 2023 Than Ngo <than@redhat.com> - 113.0.5672.126-1
- drop clang workaround for el8
- update to 113.0.5672.126

* Tue May 09 2023 Than Ngo <than@redhat.com> - 113.0.5672.92-1
- update to 113.0.5672.92

* Wed May 03 2023 Than Ngo <than@redhat.com> - 113.0.5672.63-1
- update to 113.0.5672.63

* Sun Apr 23 2023 Than Ngo <than@redhat.com> - 112.0.5615.165-2
- make --use-gl=egl default for x11/wayland
- enable WebUIDarkMode

* Thu Apr 20 2023 Than Ngo <than@redhat.com> - 112.0.5615.165-1
- update to 112.0.5615.165

* Mon Apr 17 2023 Than Ngo <than@redhat.com> - 112.0.5615.121-2
- fix vaapi issue on xwayland
- fix the build order, chrome_feed_response_metadata.pb.h file not found
- fix compiler flags and typo

* Sat Apr 15 2023 Than Ngo <than@redhat.com> - 112.0.5615.121-1
- update to 112.0.5615.121

* Wed Apr 05 2023 Than Ngo <than@redhat.com> - 112.0.5615.49-1
- update to 112.0.5615.49
- fix #2184142, Small fonts in menus

* Tue Mar 28 2023 Than Ngo <than@redhat.com> - 111.0.5563.146-1
- update to 111.0.5563.146

* Sat Mar 25 2023 Neal Gompa <ngompa@fedoraproject.org> - 111.0.5563.110-2
- Fix ffmpeg note in README.fedora

* Wed Mar 22 2023 Than Ngo <than@redhat.com> - 111.0.5563.110-1
- update to 111.0.5563.110

* Sun Mar 12 2023 Neal Gompa <ngompa@fedoraproject.org> - 111.0.5563.64-2
- Rebuild for ffmpeg 6.0

* Tue Mar 07 2023 Than Ngo <than@redhat.com> - 111.0.5563.64-1
- update to 111.0.5563.64

* Mon Mar 06 2023 Than Ngo <than@redhat.com> - 111.0.5563.50-1
- update to 111.0.5563.50
- system freetype on fedora > 36

* Thu Feb 23 2023 Than Ngo <than@redhat.com> - 110.0.5481.177-1
- update to 110.0.5481.177
- workaround for crash on aarch64, rhel8

* Wed Feb 22 2023 Jan Grulich <jgrulich@redhat.com> - 110.0.5481.100-3
- Enable PipeWire screen sharing on RHEL8+

* Tue Feb 21 2023 Than Ngo <than@redhat.com> - 110.0.5481.100-2
- fixed bz#2036205, failed to load GLES library

* Fri Feb 17 2023 Than Ngo <than@redhat.com> - 110.0.5481.100-1
- update to 110.0.5481.100

* Thu Feb 16 2023 Than Ngo <than@redhat.com> - 110.0.5481.77-2
- fix #2071126, enable support V4L2 stateless decoders for aarch64 plattform
- fix prefers-color-scheme
- drop snapshot_blob.bin, replace snapshot_blob.bin with v8_context_snapshot.bin
- move headless_lib*.pak to headless subpackage

* Wed Feb 08 2023 Than Ngo <than@redhat.com> - 110.0.5481.77-1
- update to 110.0.5481.77

* Sat Feb 04 2023 Than Ngo <than@redhat.com> - 110.0.5481.61-1
- update to 110.0.5481.61

* Thu Feb 02 2023 Jan Grulich <jgrulich@redhat.com> - 109.0.5414.119-2
- Use ffmpeg decoders for h264 support

* Wed Jan 25 2023 Than Ngo <than@redhat.com> - 109.0.5414.119-1
- update to 109.0.5414.119

* Sun Jan 22 2023 Than Ngo <than@redhat.com> - 109.0.5414.74-4
- clean up

* Wed Jan 18 2023 Fedora Release Engineering <releng@fedoraproject.org> - 109.0.5414.74-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Sun Jan 15 2023 Than Ngo <than@redhat.com> - 109.0.5414.74-2
- conditionalize system_build_flags
- cleaned up gn defines
- add BR on python3-importlib-metadata
- set correct toolchain gcc|clang
- fix FTBFS with gcc13

* Wed Jan 11 2023 Than Ngo <than@redhat.com> - 109.0.5414.74-1
- update to 109.0.5414.74

* Tue Jan 10 2023 Than Ngo <than@redhat.com> - 108.0.5359.124-5
- enable qt backend for el >= 9 and fedora >= 35
- drop i686
- conditional BR on java-1.8.0-openjdk-headless

* Sun Jan 08 2023 Than Ngo <than@redhat.com> - 108.0.5359.124-4
- vaapi support for wayland

* Wed Jan 04 2023 Than Ngo <than@redhat.com> - 108.0.5359.124-3
- build with system ffmpeg-free and system libaom
- fix widewine extension issue
- vaapi, disable UseChromeOSDirectVideoDecoder
- workaround for linking issue in clang <= 14

* Sun Jan  1 2023 Tom Callaway <spot@fedoraproject.org> - 108.0.5359.124-2
- turn headless back on (chrome-remote-desktop will stay off, probably forever)

* Wed Dec 28 2022 Than Ngo <than@redhat.com> - 108.0.5359.124-1
- update to 108.0.5359.124
- switch to clang

* Tue Nov 29 2022 Than Ngo <than@redhat.com> - 107.0.5304.121-1
- update to 107.0.5304.121

* Fri Nov 11 2022 Than Ngo <than@redhat.com> - 107.0.5304.110-1
- update to 107.0.5304.110

* Fri Sep 23 2022 Tom Callaway <spot@fedoraproject.org> - 105.0.5195.125-2
- apply upstream fix for wayland menu misplacement bug

* Mon Sep 19 2022 Tom Callaway <spot@fedoraproject.org> - 105.0.5195.125-1
- update to 105.0.5195.125

* Thu Sep  1 2022 Tom Callaway <spot@fedoraproject.org> - 105.0.5195.52-1
- update to 105.0.5195.52

* Thu Aug 18 2022 Tom Callaway <spot@fedoraproject.org> - 104.0.5112.101-1
- update to 104.0.5112.101

* Wed Jul 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 103.0.5060.114-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Wed Jul 13 2022 Tom Callaway <spot@fedoraproject.org> - 103.0.5060.114-1
- update to 103.0.5060.114

* Wed Jun 22 2022 Tom Callaway <spot@fedoraproject.org> - 103.0.5060.53-1
- update to 103.0.5060.53

* Thu Jun 16 2022 Tom Callaway <spot@fedoraproject.org> - 102.0.5005.115-2
- fix minizip Requires for EL9

* Fri Jun 10 2022 Tom Callaway <spot@fedoraproject.org> - 102.0.5005.115-1
- update to 102.0.5005.115

* Fri Jun  3 2022 Tom Callaway <spot@fedoraproject.org> - 102.0.5005.61-1
- update to 102.0.5005.61

* Wed Apr 27 2022 Tom Callaway <spot@fedoraproject.org> - 101.0.4951.41-1
- update to 101.0.4951.41

* Thu Apr 21 2022 Tom Callaway <spot@fedoraproject.org> - 100.0.4896.127-1
- update to 100.0.4896.127

* Tue Apr  5 2022 Tom Callaway <spot@fedoraproject.org> - 100.0.4896.75-1
- update to 100.0.4896.75

* Sat Apr  2 2022 Tom Callaway <spot@fedoraproject.org> - 100.0.4896.60-1
- update to 100.0.4896.60

* Sun Mar 27 2022 Tom Callaway <spot@fedoraproject.org> - 99.0.4844.84-1
- update to 99.0.4844.84
- package up libremoting_core.so* for chrome-remote-desktop
- strip all the .so files (and binaries)

* Sat Mar 19 2022 Tom Callaway <spot@fedoraproject.org> - 99.0.4844.74-1
- update to 99.0.4844.74

* Sat Mar  5 2022 Tom Callaway <spot@fedoraproject.org> - 99.0.4844.5-1
- update to 99.0.4844.5

* Fri Feb 25 2022 Tom Callaway <spot@fedoraproject.org> - 98.0.4758.102-1
- update to 98.0.4758.102
- fix build issue with subzero and gcc12

* Tue Feb  8 2022 Tom Callaway <spot@fedoraproject.org> - 98.0.4758.80-1
- update to 98.0.4758.80

* Sat Feb 05 2022 Jiri Vanek <jvanek@redhat.com> - 96.0.4664.110-9
- Rebuilt for java-17-openjdk as system jdk

* Wed Jan 19 2022 Fedora Release Engineering <releng@fedoraproject.org> - 96.0.4664.110-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Wed Jan  5 2022 Tom Callaway <spot@fedoraproject.org> - 96.0.4664.110-7
- i hate regex. trying again

* Tue Jan  4 2022 Tom Callaway <spot@fedoraproject.org> - 96.0.4664.110-6
- always filter provides, was previously inside conditional for shared builds

* Mon Jan  3 2022 Tom Callaway <spot@fedoraproject.org> - 96.0.4664.110-5
- fix provides filtering to be more inclusive (and work properly)

* Thu Dec 30 2021 Tom Callaway <spot@fedoraproject.org> - 96.0.4664.110-4
- package up more swiftshader/angle stuff
- move swiftshader files to -common so headless can use them

* Mon Dec 27 2021 Tom Callaway <spot@fedoraproject.org> - 96.0.4664.110-3
- have chromium-browser.sh check for wayland env vars and if found, set ozone flags appropriately
  Thanks to Neal Gompa for the nudge

* Mon Dec 20 2021 Tom Callaway <spot@fedoraproject.org> - 96.0.4664.110-2
- enable WebRTCPipeWireCapturer by default

* Thu Dec 16 2021 Tom Callaway <spot@fedoraproject.org> - 96.0.4664.110-1
- update to 96.0.4664.110

* Fri Nov 19 2021 Tom Callaway <spot@fedoraproject.org> - 96.0.4664.45-1
- update to 96.0.4664.45

* Fri Nov 12 2021 Tom Callaway <spot@fedoraproject.org> - 95.0.4638.69-1
- update to 95.0.4638.69

* Fri Oct  8 2021 Tom Callaway <spot@fedoraproject.org> - 94.0.4606.81-1
- update to 94.0.4606.81

* Wed Oct  6 2021 Tom Callaway <spot@fedoraproject.org> - 94.0.4606.71-2
- add official_build flag
- apply upstream patch to handle nullptr correctly in PartitionGetSizeEstimate()

* Tue Oct  5 2021 Tom Callaway <spot@fedoraproject.org> - 94.0.4606.71-1
- update to 94.0.4606.71

* Fri Sep 24 2021 Tom Callaway <spot@fedoraproject.org> - 94.0.4606.61-1
- update to 94.0.4606.61

* Thu Sep 23 2021 Tom Callaway <spot@fedoraproject.org> - 94.0.4606.54-1
- update to 94.0.4606.54

* Mon Sep 20 2021 Tom Callaway <spot@fedoraproject.org> - 93.0.4577.82-2
- add fix for harfbuzz v3 (thanks to Jan Beich @ FreeBSD)

* Thu Sep 16 2021 Tom Callaway <spot@fedoraproject.org> - 93.0.4577.82-1
- update to 93.0.4577.82

* Thu Sep  2 2021 Tom Callaway <spot@fedoraproject.org> - 93.0.4577.63-1
- update to 93.0.4577.63

* Mon Aug 30 2021 Tom Callaway <spot@fedoraproject.org> - 92.0.4515.159-2
- disable userfaultd code in epel8
- include crashpad_handler (it works a lot better when it doesn't immediately crash because of this missing file)

* Tue Aug 17 2021 Tom Callaway <spot@fedoraproject.org> - 92.0.4515.159-1
- update to 92.0.4515.159

* Mon Aug 16 2021 Tom Callaway <spot@fedoraproject.org> - 92.0.4515.131-1
- update to 92.0.4515.131
- apply upstream fix for clone3 crash

* Mon Jul 26 2021 Tom Callaway <spot@fedoraproject.org> - 92.0.4515.107-1
- update to 92.0.4515.107
- drop python2 deps (finally)

* Wed Jul 21 2021 Fedora Release Engineering <releng@fedoraproject.org> - 91.0.4472.164-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Fri Jul 16 2021 Tom Callaway <spot@fedoraproject.org> - 91.0.4472.164-1
- update to 91.0.4472.164

* Tue Jul  6 2021 Tom Callaway <spot@fedoraproject.org> - 91.0.4472.114-2
- fix ThemeService crash (thanks OpenSUSE)

* Wed Jun 23 2021 Tom Callaway <spot@fedoraproject.org> - 91.0.4472.114-1
- update to 91.0.4472.114

* Tue Jun  1 2021 Tom Callaway <spot@fedoraproject.org> - 91.0.4472.77-1
- update to 91.0.4472.77

* Tue May 18 2021 Tom Callaway <spot@fedoraproject.org> - 90.0.4430.212-1
- update to 90.0.4430.212

* Tue Apr 27 2021 Tom Callaway <spot@fedoraproject.org> - 90.0.4430.93-1
- update to 90.0.4430.93

* Wed Apr 21 2021 Tom Callaway <spot@fedoraproject.org> - 90.0.4430.85-1
- update to 90.0.4430.85

* Fri Apr 16 2021 Tom Callaway <spot@fedoraproject.org> - 90.0.4430.72-1
- update to 90.0.4430.72

* Wed Apr 14 2021 Tom Callaway <spot@fedoraproject.org> - 89.0.4389.128-1
- update to 89.0.4389.128

* Wed Mar 31 2021 Jonathan Wakely <jwakely@redhat.com> - 89.0.4389.90-5
- Rebuilt for removed libstdc++ symbols (#1937698)

* Mon Mar 29 2021 Tom Callaway <spot@fedoraproject.org> - 89.0.4389.90-4
- fix libva compile in rawhide

* Thu Mar 25 2021 Tom Callaway <spot@fedoraproject.org> - 89.0.4389.90-3
- apply upstream fix for newer system libva

* Wed Mar 24 2021 Tom Callaway <spot@fedoraproject.org> - 89.0.4389.90-2
- fix crashes with components/cast_*

* Thu Mar 18 2021 Tom Callaway <spot@fedoraproject.org> - 89.0.4389.90-1
- update to 89.0.4389.90
- disable auto-download of widevine binary only blob

* Mon Mar 15 2021 Tom Callaway <spot@fedoraproject.org> - 89.0.4389.82-2
- add support for futex_time64

* Mon Mar  8 2021 Tom Callaway <spot@fedoraproject.org> - 89.0.4389.82-1
- update to 89.0.4389.82

* Thu Mar  4 2021 Tom Callaway <spot@fedoraproject.org> - 89.0.4389.72-1
- update to 89.0.4389.72

* Tue Mar 02 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 88.0.4324.182-3
- Rebuilt for updated systemd-rpm-macros
  See https://pagure.io/fesco/issue/2583.

* Thu Feb 25 2021 Tom Callaway <spot@fedoraproject.org> - 88.0.4234.182-2
- fix swiftshader symbols in libEGL/libGLESv2 with gcc

* Wed Feb 17 2021 Tom Callaway <spot@fedoraproject.org> - 88.0.4234.182-1
- update to 88.0.4234.182

* Fri Feb  5 2021 Tom Callaway <spot@fedoraproject.org> - 88.0.4234.150-1
- update to 88.0.4234.150

* Tue Feb  2 2021 Tom Callaway <spot@fedoraproject.org> - 88.0.4234.146-1
- update to 88.0.4234.146

* Tue Feb  2 2021 Tom Callaway <spot@fedoraproject.org> - 88.0.4234.96-4
- turn on the API key (just the API key, not the client_id or client_secret)

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 88.0.4324.96-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jan 25 2021 Tom Callaway <spot@fedoraproject.org> - 88.0.4324.96-2
- apply fix from Kevin Kofler for new glibc fstat sandbox handling

* Wed Jan 20 2021 Tom Callaway <spot@fedoraproject.org> - 88.0.4324.96-1
- 88 goes from beta to stable
- disable use of api keys (Google shut off API access)

* Wed Jan 13 2021 Tom Callaway <spot@fedoraproject.org>
- update to 87.0.4280.141

* Wed Dec 30 2020 Tom Callaway <spot@fedoraproject.org> - 88.0.4324.50-1
- update to 88.0.4324.50
- drop patches 74 & 75 (applied upstream)

* Thu Dec 17 2020 Tom Callaway <spot@fedoraproject.org>
- add two patches for missing headers to build with gcc 11

* Thu Dec  3 2020 Tom Callaway <spot@fedoraproject.org> - 88.0.4324.27-1
- dev release to prepare for next stable

* Thu Dec  3 2020 Tom Callaway <spot@fedoraproject.org> - 87.0.4280.88-1
- update to 87.0.4280.88

* Wed Nov 18 2020 Tom Callaway <spot@fedoraproject.org> - 87.0.4280.66-1
- update to 87.0.4280.66

* Thu Nov 12 2020 Jeff Law <law@fedoraproject.org> - 86.0.4240.198-1
- Fix missing #inclues for gcc-11
- Fix bogus volatile caught by gcc-11

* Thu Nov 12 2020 Tom Callaway <spot@fedoraproject.org> - 86.0.4240.198-1
- update to 86.0.4240.198

* Tue Nov 10 2020 Tom Callaway <spot@fedoraproject.org> - 86.0.4240.193-1
- update to 86.0.4240.193

* Wed Nov  4 2020 Tom Callaway <spot@fedoraproject.org> - 86.0.4240.183-1
- update to 86.0.4240.183

* Mon Nov  2 2020 Tom Callaway <spot@fedoraproject.org> - 86.0.4240.111-2
- fix conditional typo that was causing console logging to be turned on

* Wed Oct 21 2020 Tom Callaway <spot@fedoraproject.org> - 86.0.4240.111-1
- update to 86.0.4240.111

* Tue Oct 20 2020 Tom Callaway <spot@fedoraproject.org> - 86.0.4240.75-2
- use bundled zlib/minizip on el7 (thanks Red Hat. :P)

* Wed Oct 14 2020 Tom Callaway <spot@fedoraproject.org> - 86.0.4240.75-1
- update to 86.0.4240.75

* Mon Sep 28 2020 Tom Callaway <spot@fedoraproject.org> - 85.0.4183.121-2
- rebuild for libevent

* Mon Sep 21 2020 Tom Callaway <spot@fedoraproject.org> - 85.0.4183.121-1
- update to 85.0.4183.121
- apply upstream fix for networking issue with CookieMonster

* Tue Sep  8 2020 Tom Callaway <spot@fedoraproject.org> - 85.0.4183.102-1
- update to 85.0.4183.102
- install ANGLE so files (libEGL.so, libGLESv2.so)

* Wed Aug 26 2020 Tom Callaway <spot@fedoraproject.org> - 85.0.4183.83-1
- update to 85.0.4183.83

* Thu Aug 20 2020 Tom Callaway <spot@fedoraproject.org> - 84.0.4147.135-1
- update to 84.0.4147.135
- conditionalize build_clear_key_cdm
- disable build_clear_key_cdm on F33+ aarch64 until binutils bug is fixed
- properly install libclearkeycdm.so everywhere else (whoops)

* Mon Aug 17 2020 Tom Callaway <spot@fedoraproject.org> - 84.0.4147.125-2
- force fix_textrels fix in ffmpeg for i686 (even without lld)

* Mon Aug 10 2020 Tom Callaway <spot@fedoraproject.org> - 84.0.4147.125-1
- update to 84.0.4147.125

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 84.0.4147.105-2
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Jul 31 2020 Tom Callaway <spot@fedoraproject.org> - 84.0.4147.105-1
- update to 84.0.4147.105

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 84.0.4147.89-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 15 2020 Tom Callaway <spot@fedoraproject.org> - 84.0.4147.89-1
- update to 84.0.4147.89

* Sat Jun 27 2020 Tom Callaway <spot@fedoraproject.org> - 83.0.4103.116-3
- only set ozone on headless
- enable use_kerberos

* Tue Jun 23 2020 Tom Callaway <spot@fedoraproject.org> - 83.0.4103.116-2
- do not force ozone into x11

* Tue Jun 23 2020 Tom Callaway <spot@fedoraproject.org> - 83.0.4103.116-1
- update to 83.0.4103.116

* Thu Jun 18 2020 Tom Callaway <spot@fedoraproject.org> - 83.0.4103.106-1
- update to 83.0.4103.106
- remove duplicate ServiceWorker fix
- add fix to work around gcc bug on aarch64
- disable python byte compiling (we do not need it)

* Tue Jun 16 2020 Tom Callaway <spot@fedoraproject.org> - 83.0.4103.97-5
- add ServiceWorker fix

* Mon Jun 15 2020 Tom Callaway <spot@fedoraproject.org> - 83.0.4103.97-4
- use old cups handling on epel7
- fix skia attribute overrides with gcc

* Wed Jun 10 2020 Tom Callaway <spot@fedoraproject.org> - 83.0.4103.97-3
- fix issue on epel7 where linux/kcmp.h does not exist

* Mon Jun  8 2020 Tom Callaway <spot@fedoraproject.org> - 83.0.4103.97-2
- more fixes from gentoo

* Sun Jun  7 2020 Tom Callaway <spot@fedoraproject.org> - 83.0.4103.97-1
- update to 83.0.4103.97

* Tue Jun  2 2020 Tom Callaway <spot@fedoraproject.org> - 83.0.4103.61-1
- update to 83.0.4103.61
- conditionalize and disable remoting

* Thu May  7 2020 Tom Callaway <spot@fedoraproject.org> - 81.0.4044.138-1
- update to 81.0.4044.138

* Tue May  5 2020 Tom Callaway <spot@fedoraproject.org> - 81.0.4044.129-1
- update to 81.0.4044.129

* Thu Apr 23 2020 Tom Callaway <spot@fedoraproject.org> - 81.0.4044.122-1
- update to 81.0.4044.122

* Tue Apr 21 2020 Tom Callaway <spot@fedoraproject.org> - 81.0.4044.113-2
- add explicit Requires: chromium-common

* Thu Apr 16 2020 Tom Callaway <spot@fedoraproject.org> - 81.0.4044.113-1
- update to 81.0.4044.113

* Mon Apr 13 2020 Tom Callaway <spot@fedoraproject.org> - 81.0.4044.92-1
- update to 81.0.4044.92
- squelch the selinux output in the post scriptlet
- add Provides/Obsoletes in case we're build with shared set to 0
- add ulimit -n 4096 (needed for static builds, probably not harmful for shared builds either)
- do static build

* Sat Apr  4 2020 Tom Callaway <spot@fedoraproject.org> - 80.0.3987.163-1
- update to 80.0.3987.163

* Wed Apr  1 2020 Tom Callaway <spot@fedoraproject.org> - 80.0.3987.162-1
- update to 80.0.3987.162

* Wed Mar 18 2020 Tom Callaway <spot@fedoraproject.org> - 80.0.3987.149-1
- update to 80.0.3987.149

* Thu Feb 27 2020 Tom Callaway <spot@fedoraproject.org> - 80.0.3987.132-1
- update to 80.0.3987.132
- disable C++17 changes (this means f32+ will no longer build, but it segfaulted immediately)

* Thu Feb 27 2020 Tom Callaway <spot@fedoraproject.org> - 80.0.3987.122-1
- update to 80.0.3987.122

* Mon Feb 17 2020 Tom Callaway <spot@fedoraproject.org> - 80.0.3987.106-1
- update to 80.0.3987.106

* Wed Feb  5 2020 Tom Callaway <spot@fedoraproject.org> - 80.0.3987.87-1
- update to 80.0.3987.87

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 79.0.3945.130-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Jan 17 2020 Tom Callaway <spot@fedoraproject.org> - 79.0.3945.130-1
- update to 79.0.3945.130

* Thu Jan  9 2020 Tom Callaway <spot@fedoraproject.org> - 79.0.3945.117-1
- update to 79.0.3945.117

* Tue Dec 17 2019 Tom Callaway <spot@fedoraproject.org> - 79.0.3945.88-1
- update to 79.0.3945.88

* Tue Dec 10 2019 Tom Callaway <spot@fedoraproject.org> - 79.0.3945.79-1
- update to 79.0.3945.79

* Wed Dec  4 2019 Tom Callaway <spot@fedoraproject.org> - 79.0.3945.56-2
- fix lib provides filtering

* Tue Dec  3 2019 Tom Callaway <spot@fedoraproject.org> - 79.0.3945.56-1
- update to current beta (rawhide only)
- switch to upstream patch for clock_nanosleep fix

* Mon Nov 25 2019 Tom Callaway <spot@fedoraproject.org> - 78.0.3904.108-1
- update to 78.0.3904.108

* Sun Nov 17 2019 Tom Callaway <spot@fedoraproject.org> - 78.0.3904.97-2
- allow clock_nanosleep through seccomp (bz #1773289)

* Thu Nov  7 2019 Tom Callaway <spot@fedoraproject.org> - 78.0.3904.97-1
- update to 78.0.3904.97

* Fri Nov  1 2019 Tom Callaway <spot@fedoraproject.org> - 78.0.3904.87-1
- update to 78.0.3904.87
- apply most of the freeworld changes in PR 23/24/25

* Wed Oct 23 2019 Tom Callaway <spot@fedoraproject.org> - 78.0.3904.80-1
- update to 78.0.3904.80

* Wed Oct 16 2019 Tom Callaway <spot@fedoraproject.org> - 77.0.3865.120-4
- upstream fix for zlib symbol exports with gcc

* Wed Oct 16 2019 Tom Callaway <spot@fedoraproject.org> - 77.0.3865.120-3
- silence outdated build noise (bz1745745)

* Tue Oct 15 2019 Tom Callaway <spot@fedoraproject.org> - 77.0.3865.120-2
- fix node handling for EPEL-8

* Mon Oct 14 2019 Tomas Popela <tpopela@redhat.com> - 77.0.3865.120-1
- Update to 77.0.3865.120

* Thu Oct 10 2019 Tom Callaway <spot@fedoraproject.org> - 77.0.3865.90-4
- enable aarch64 for EPEL-8

* Wed Oct  9 2019 Tom Callaway <spot@fedoraproject.org> - 77.0.3865.90-3
- spec cleanups and changes to make EPEL8 try to build

* Mon Sep 23 2019 Tomas Popela <tpopela@redhat.com> - 77.0.3865.90-2
- Fix the icon
- Remove quite a few of downstream patches
- Fix the crashes by backporting an upstream bug
- Resolves: rhbz#1754179

* Thu Sep 19 2019 Tomas Popela <tpopela@redhat.com> - 77.0.3865.90-1
- Update to 77.0.3865.90

* Mon Sep 16 2019 Tomas Popela <tpopela@redhat.com> - 77.0.3865.75-2
- Update the list of private libraries

* Fri Sep 13 2019 Tomas Popela <tpopela@redhat.com> - 77.0.3865.75-1
- Update to 77.0.3865.75

* Tue Sep 03 2019 Tomas Popela <tpopela@redhat.com> - 76.0.3809.132-2
- Backport patch to fix certificate transparency

* Tue Aug 27 2019 Tomas Popela <tpopela@redhat.com> - 76.0.3809.132-1
- Update to 76.0.3809.132

* Tue Aug 13 2019 Tomas Popela <tpopela@redhat.com> - 76.0.3809.100-1
- Update to 76.0.3809.100

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 75.0.3770.100-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Jul  2 2019 Tom Callaway <spot@fedoraproject.org> - 75.0.3770.100-3
- apply upstream fix to resolve issue where it is dangerous to post a
  task with a RenderProcessHost pointer because the RenderProcessHost
  can go away before the task is run (causing a segfault).

* Tue Jun 25 2019 Tom Callaway <spot@fedoraproject.org> - 75.0.3770.100-2
- fix v8 compile with gcc

* Thu Jun 20 2019 Tom Callaway <spot@fedoraproject.org> - 75.0.3770.100-1
- update to 75.0.3770.100

* Fri Jun 14 2019 Tom Callaway <spot@fedoraproject.org> - 75.0.3770.90-1
- update to 75.0.3770.90

* Wed Jun  5 2019 Tom Callaway <spot@fedoraproject.org> - 75.0.3770.80-1
- update to 75.0.3770.80
- disable vaapi (via conditional), too broken

* Fri May 31 2019 Tom Callaway <spot@fedoraproject.org> - 74.0.3729.169-1
- update to 74.0.3729.169

* Thu Apr 11 2019 Tom Callaway <spot@fedoraproject.org> - 73.0.3683.103-1
- update to 73.0.3683.103
- add CLONE_VFORK logic to seccomp filter for linux to handle glibc 2.29 change

* Wed Mar 27 2019 Tom Callaway <spot@fedoraproject.org> - 73.0.3683.86-2
- remove lang macro from en-US.pak* because Chromium crashes if it is not present
  (bz1692660)

* Fri Mar 22 2019 Tom Callaway <spot@fedoraproject.org> - 73.0.3683.86-1
- update to 73.0.3683.86

* Tue Mar 19 2019 Tom Callaway <spot@fedoraproject.org> - 73.0.3683.75-2
- do not include pyproto/protoc files in package

* Tue Mar 12 2019 Tom Callaway <spot@fedoraproject.org> - 73.0.3683.75-1
- update to 73.0.3683.75

* Sat Mar  9 2019 Tom Callaway <spot@fedoraproject.org> - 72.0.3626.121-1
- update to 72.0.3626.121

* Tue Feb 26 2019 Tom Callaway <spot@fedoraproject.org> - 71.0.3578.98-5
- rebuild for libva api change

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 71.0.3578.98-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 21 2019 Tom Callaway <spot@fedoraproject.org> - 71.0.3578.98-3
- rebuild with widevine fix

* Tue Jan  8 2019 Tom Callaway <spot@fedoraproject.org> - 71.0.3578.98-2
- drop rsp clobber, which breaks gcc9 (thanks to Jeff Law)

* Fri Dec 14 2018 Tom Callaway <spot@fedoraproject.org> - 71.0.3578.98-1
- update to 71.0.3578.98

* Tue Nov 27 2018 Tom Callaway <spot@fedoraproject.org> - 70.0.3538.110-2
- enable vaapi support (thanks to Akarshan Biswas for doing the hard work here)

* Mon Nov 26 2018 Tom Callaway <spot@fedoraproject.org> - 70.0.3538.110-1
- update to .110

* Wed Nov  7 2018 Tom Callaway <spot@fedoraproject.org> - 70.0.3538.77-4
- fix library requires filtering

* Tue Nov  6 2018 Tom Callaway <spot@fedoraproject.org> - 70.0.3538.77-3
- fix build with harfbuzz2 in rawhide

* Mon Nov  5 2018 Tom Callaway <spot@fedoraproject.org> - 70.0.3538.77-2
- drop jumbo_file_merge_limit to 8 to (hopefully) avoid OOMs on aarch64

* Fri Nov  2 2018 Tom Callaway <spot@fedoraproject.org> - 70.0.3538.77-1
- .77 came out while I was working on this. :/

* Fri Nov  2 2018 Tom Callaway <spot@fedoraproject.org> - 70.0.3538.67-1
- update to 70

* Tue Oct 16 2018 Tom Callaway <spot@fedoraproject.org> - 69.0.3497.100-2
- do not play with fonts on freeworld builds

* Thu Oct  4 2018 Tom Callaway <spot@fedoraproject.org> - 69.0.3497.100-1
- update to 69.0.3497.100

* Wed Sep 12 2018 Tom Callaway <spot@fedoraproject.org> - 69.0.3497.92-1
- update to 69.0.3497.92

* Wed Sep  5 2018 Tom Callaway <spot@fedoraproject.org> - 69.0.3497.81-1
- update to 69.0.3497.81

* Tue Aug 28 2018 Patrik Novotný <panovotn@redhat.com> - 68.0.3440.106-4
- change requires to minizip-compat(-devel), rhbz#1609830, rhbz#1615381

* Sun Aug 19 2018 Tom Callaway <spot@fedoraproject.org> - 68.0.3440.106-3
- fix library filters

* Fri Aug 17 2018 Tom Callaway <spot@fedoraproject.org> - 68.0.3440.106-2
- fix error with defaulting on redeclaration

* Thu Aug  9 2018 Tom Callaway <spot@fedoraproject.org> - 68.0.3440.106-1
- update to 68.0.3440.106

* Wed Aug  8 2018 Tom Callaway <spot@fedoraproject.org> - 68.0.3440.84-1
- update to 68.0.3440.84

* Mon Jul 30 2018 Tom Callaway <spot@fedoraproject.org> - 68.0.3440.75-1
- update to 68.0.3440.75

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 67.0.3396.99-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jul  9 2018 Tom Callaway <spot@fedoraproject.org> 67.0.3396.99-1
- update to 67.0.3396.99

* Mon Jun 25 2018 Tom Callaway <spot@fedoraproject.org> 67.0.3396.87-2
- add "Fedora" to the user agent string

* Tue Jun 19 2018 Tom Callaway <spot@fedoraproject.org> 67.0.3396.87-1
- update to 67.0.3396.87

* Thu Jun  7 2018 Tom Callaway <spot@fedoraproject.org> 67.0.3396.79-1
- update to 67.0.3396.79

* Wed Jun  6 2018 Tom Callaway <spot@fedoraproject.org> 67.0.3396.62-2
- work around bug in RHEL7 python exec

* Wed May 30 2018 Tom Callaway <spot@fedoraproject.org> 67.0.3396.62-1
- 67 releases of chromium on the wall...

* Tue May 29 2018 Tom Callaway <spot@fedoraproject.org> 66.0.3359.181-3
- also filter out fontconfig on epel7

* Wed May 23 2018 Tom Callaway <spot@fedoraproject.org> 66.0.3359.181-2
- fix missing files

* Mon May 21 2018 Tom Callaway <spot@fedoraproject.org> 66.0.3359.181-1
- update to 66.0.3359.181

* Tue May 15 2018 Tom Callaway <spot@fedoraproject.org> 66.0.3359.170-2
- only x86_64 i686 have swiftshader
- fix gcc8 alignof issue on i686

* Mon May 14 2018 Tom Callaway <spot@fedoraproject.org> 66.0.3359.170-1
- update to 66.0.3359.170
- include swiftshader files

* Tue May  1 2018 Tom Callaway <spot@fedoraproject.org> 66.0.3359.139-1
- update to 66.0.3359.139

* Wed Apr 18 2018 Tom Callaway <spot@fedoraproject.org> 66.0.3359.117-1
- update to 66.0.3359.117

* Tue Apr 17 2018 Tom Callaway <spot@fedoraproject.org> 65.0.3325.181-3
- use system fontconfig (except on epel7)

* Wed Apr  4 2018 Tom Callaway <spot@fedoraproject.org> 65.0.3325.181-2
- add explicit dependency on minizip (bz 1534282)

* Wed Mar 28 2018 Tom Callaway <spot@fedoraproject.org>
- check that there is no system 'google' module, shadowing bundled ones
- conditionalize api keys (on by default)

* Wed Mar 21 2018 Tom Callaway <spot@fedoraproject.org> 65.0.3325.181-1
- update to 65.0.3325.181

* Mon Mar 19 2018 Tom Callaway <spot@fedoraproject.org> 65.0.3325.162-3
- use bundled libdrm on epel7

* Fri Mar 16 2018 Tom Callaway <spot@fedoraproject.org> 65.0.3325.162-2
- disable StartupNotify in chromium-browser.desktop (not in google-chrome desktop file)
  (bz1545241)
- use bundled freetype on epel7

* Wed Mar 14 2018 Tom Callaway <spot@fedoraproject.org> 65.0.3325.162-1
- update to 65.0.3325.162

* Wed Mar  7 2018 Tom Callaway <spot@fedoraproject.org> 65.0.3325.146-1
- update to 65.0.3325.146

* Mon Mar  5 2018 Tom Callaway <spot@fedoraproject.org> 64.0.3282.186-1
- update to 64.0.3282.186

* Fri Feb 16 2018 Tom Callaway <spot@fedoraproject.org> 64.0.3282.167-1
- update to 64.0.3282.167
- include workaround for gcc8 bug in gn
- disable unnecessary aarch64 glibc symbol change

* Fri Feb  2 2018 Tom Callaway <spot@fedoraproject.org> 64.0.3282.140-1
- update to 64.0.3282.140

* Thu Feb  1 2018 Tom Callaway <spot@fedoraproject.org> 64.0.3282.119-2
- include user-session binary in chrome-remote-desktop subpackage

* Thu Jan 25 2018 Tom Callaway <spot@fedoraproject.org> 64.0.3282.119-1
- update to 64.0.3282.119

* Fri Dec 15 2017 Tomas Popela <tpopela@redhat.com> 63.0.3239.108-1
- Update to 63.0.3239.108

* Thu Dec  7 2017 Tom Callaway <spot@fedoraproject.org> 63.0.3239.84-1
- update to 63.0.3239.84

* Wed Nov  8 2017 Tom Callaway <spot@fedoraproject.org> 62.0.3202.89-1
- update to 62.0.3202.89

* Fri Oct 27 2017 Tom Callaway <spot@fedoraproject.org> 62.0.3202.75-1
- update to 62.0.3202.75
- use devtoolset-7-toolchain to build on epel7

* Tue Oct 24 2017 Tom Callaway <spot@fedoraproject.org> 62.0.3202.62-1.1
- do not attempt std=c++14 on epel7

* Wed Oct 18 2017 Tom Callaway <spot@fedoraproject.org> 62.0.3202.62-1
- update to 62.0.3202.62

* Fri Sep 22 2017 Tom Callaway <spot@fedoraproject.org> 61.0.3163.100-1
- update to 61.0.3163.100
- lots of epel7 specific fixes
- use bundled libpng on epel7

* Wed Sep  6 2017 Tom Callaway <spot@fedoraproject.org> 61.0.3163.79-1
- update to 61.0.3163.79

* Mon Aug 28 2017 Tom Callaway <spot@fedoraproject.org> 60.0.3112.113-2
- disable aarch64 on rhel7, missing libatomic.so for some reason

* Wed Aug 23 2017 Tom Callaway <spot@fedoraproject.org> 60.0.3112.113-1
- fix ffmpeg clean script to not delete aarch64 file
- update to 60.0.3112.113

* Wed Aug 23 2017 Tom Callaway <spot@fedoraproject.org> 60.0.3112.101-3
- apply aarch64 fixes from Ryan Blakely <rblakely@redhat.com>

* Thu Aug 17 2017 Tom Callaway <spot@fedoraproject.org> 60.0.3112.101-2
- fix dep issue with chrome-remote-desktop on el7

* Wed Aug 16 2017 Tom Callaway <spot@fedoraproject.org> 60.0.3112.101-1
- update to 60.0.3112.101
- apply upstream fix for cameras which report zero resolution formats
  (bz1465357)

* Mon Aug 14 2017 Tom Callaway <spot@fedoraproject.org> 60.0.3112.90-3
- apply more workarounds to coax code to build with epel7 gcc

* Wed Aug  9 2017 Tom Callaway <spot@fedoraproject.org> 60.0.3112.90-2
- apply post 60 code commit to get code building on epel7

* Fri Aug  4 2017 Tom Callaway <spot@fedoraproject.org> 60.0.3112.90-1
- update to 60.0.3112.90

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 59.0.3071.115-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Mon Jul 31 2017 Tom Callaway <spot@fedoraproject.org> 60.0.3112.78-1
- update to 60.0.3112.78

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 59.0.3071.115-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 21 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.115-4
- put common files in -common subpackage
- build headless_shell for -headless subpackage

* Fri Jul 21 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.115-3
- use posttrans to ensure that old libs are gone before trying to make alternative symlinks

* Thu Jul 13 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.115-2
- fix scriptlets

* Wed Jul 12 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.115-1
- 59.0.3071.115
- conditionalize spec so it can be easily used to make -libs-media-freeworld

* Wed Jun 28 2017 Dominik Mierzejewski <dominik@greysector.net> 59.0.3071.109-6
- use alternatives for widevine stub and media libs to allow third-party
  packages to replace them without conflicts

* Mon Jun 26 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.109-5
- fix path in pretrans scriptlet

* Fri Jun 23 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.109-4
- copy files into /etc/opt/chrome/native-messaging-hosts instead of making symlinks
  this results in duplicate copies of the same files, but eh. making rpm happy.

* Fri Jun 23 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.109-3
- use pretrans scriptlet to remove symlink on /etc/opt/chrome/native-messaging-hosts
  (it is now a directory)

* Thu Jun 22 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.109-2
- fix duplication between chrome-remote-desktop and chromium

* Thu Jun 22 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.109-1
- update to .109
- fix native-messaging-hosts dir to be a true dir instead of a symlink

* Fri Jun 16 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.104-1
- update to .104

* Fri Jun 16 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.86-4
- actually fix mp3 playback support

* Tue Jun 13 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.86-3
- fix filtering

* Mon Jun 12 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.86-2
- pnacl/nacl now needs llvm to build the bootstrap lib

* Mon Jun 12 2017 Tom Callaway <spot@fedoraproject.org> 59.0.3071.86-1
- update to 59.0.3071.86
- include smaller logo files

* Tue May 16 2017 Tom Callaway <spot@fedoraproject.org> 58.0.3029.110-2
- strip provides/requires on libsensors

* Mon May 15 2017 Tom Callaway <spot@fedoraproject.org> 58.0.3029.110-1
- update to 58.0.3029.110

* Mon May  8 2017 Tom Callaway <spot@fedoraproject.org> 58.0.3029.96-1
- update to 58.0.3029.96

* Fri Apr 21 2017 Tom Callaway <spot@fedoraproject.org> 58.0.3029.81-1
- update to 58.0.3029.81

* Thu Mar 30 2017 Tom Callaway <spot@fedoraproject.org> 57.0.2987.133-1
- update to 57.0.2987.133

* Sun Mar 26 2017 Tom Callaway <spot@fedoraproject.org> 57.0.2987.110-4
- copy compat stdatomic.h in for RHEL. Re-enable mp3 enablement.
- fix issue in gtk_ui.cc revealed by RHEL build

* Sun Mar 26 2017 Tom Callaway <spot@fedoraproject.org> 57.0.2987.110-3
- fix mp3 enablement
- disable mp3 enablement on RHEL (compiler too old)

* Tue Mar 21 2017 Tom Callaway <spot@fedoraproject.org> 57.0.2987.110-2
- fix privlibs

* Mon Mar 20 2017 Tom Callaway <spot@fedoraproject.org> 57.0.2987.110-1
- update to 57.0.2987.110

* Tue Mar 14 2017 Tom Callaway <spot@fedoraproject.org> 57.0.2987.98-1
- update to 57.0.2987.98

* Sun Mar  5 2017 Tom Callaway <spot@fedoraproject.org> 56.0.2924.87-8
- enable mp3 support

* Sat Mar  4 2017 Tom Callaway <spot@fedoraproject.org> 56.0.2924.87-7
- fix desktop file to have "new window" and "new private window" actions

* Tue Feb 28 2017 Tom Callaway <spot@fedoraproject.org> 56.0.2924.87-6
- fix issue with gcc7 compile in v8 (thanks to Ben Noordhuis)

* Fri Feb 24 2017 Tom Callaway <spot@fedoraproject.org> 56.0.2924.87-5
- versioning sync build on rawhide

* Fri Feb 24 2017 Tom Callaway <spot@fedoraproject.org> 56.0.2924.87-4.1
- fix issue with unique_ptr move on return with old gcc

* Tue Feb 21 2017 Tom Callaway <spot@fedoraproject.org> 56.0.2924.87-4
- disable debuginfo

* Mon Feb 13 2017 Tom Callaway <spot@fedoraproject.org> 56.0.2924.87-3
- fix compilation issue
- build third_party/WebKit with -fpermissive
- use bundled jinja everywhere

* Fri Feb 10 2017 Tom Callaway <spot@fedoraproject.org> 56.0.2924.87-2
- add BR: gtk3-devel

* Fri Feb 10 2017 Tom Callaway <spot@fedoraproject.org> 56.0.2924.87-1
- update to 56.0.2924.87

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 55.0.2883.87-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Dec 13 2016 Tom Callaway <spot@fedoraproject.org> 55.0.2883.87-1.1
- use bundled jinja2 on RHEL (or Fedora older than 23)
- fix rvalue issue in remoting code

* Tue Dec 13 2016 Tom Callaway <spot@fedoraproject.org> 55.0.2883.87-1
- update to 55.0.2883.87

* Mon Dec 12 2016 Tom Callaway <spot@fedoraproject.org> 55.0.2883.75-1
- update to 55.0.2883.75

* Fri Dec  2 2016 Tom Callaway <spot@fedoraproject.org> 54.0.2840.100-1
- update to 54.0.2840.100

* Fri Nov  4 2016 Tom Callaway <spot@fedoraproject.org> 54.0.2840.90-3
- when use_aura is on, chrome/browser needs to link to ui/snapshot

* Wed Nov  2 2016 Tom Callaway <spot@fedoraproject.org> 54.0.2840.90-2
- export setOpaque in cc_blink

* Wed Nov  2 2016 Tom Callaway <spot@fedoraproject.org> 54.0.2840.90-1
- update to 54.0.2840.90
- undo ld manipulation for i686, just use -g1 there

* Tue Nov  1 2016 Tom Callaway <spot@fedoraproject.org> 54.0.2840.71-2
- disable debugging

* Wed Oct 26 2016 Tom Callaway <spot@fedoraproject.org> 54.0.2840.71-1
- update to 54.0.2840.71

* Wed Oct 26 2016 Tom Callaway <spot@fedoraproject.org> 54.0.2840.59-2
- fix deps

* Thu Oct 13 2016 Tom Callaway <spot@fedoraproject.org> 54.0.2840.59-1
- 54.0.2840.59
- use bundled opus, libevent

* Fri Sep 30 2016 Tom Callaway <spot@fedoraproject.org> 53.0.2785.143-1
- 53.0.2785.143

* Tue Sep 20 2016 Tom Callaway <spot@fedoraproject.org> 53.0.2785.116-1
- 53.0.2785.116

* Wed Sep 14 2016 Tom Callaway <spot@fedoraproject.org> 53.0.2785.113-1
- 53.0.2785.113

* Thu Sep  8 2016 Tom Callaway <spot@fedoraproject.org> 53.0.2785.101-1
- 53.0.2785.101
- happy star trek day. live long and prosper.

* Wed Sep  7 2016 Tom Callaway <spot@fedoraproject.org> 53.0.2785.92-1
- add basic framework for gn tooling (disabled because it doesn't work yet)
- update to 53.0.2785.92
- fix HOME environment issue in chrome-remote-desktop service file

* Mon Aug 29 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.116-11
- conditionalize Requires: u2f-hidraw-policy so that it is only used on Fedora
- use bundled harfbuzz on EL7

* Thu Aug 18 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.116-10
- disable gtk3 because it breaks lots of things
- re-enable hidpi setting

* Tue Aug 16 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.116-9
- filter out Requires/Provides for chromium-only libs and plugins

* Tue Aug 16 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.116-8
- fix path on Requires(post) line for semanage

* Mon Aug 15 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.116-7
- add Requires(post) items for selinux scriptlets

* Mon Aug 15 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.116-6
- disable the "hidpi" setting
- unset MADV_FREE if set (should get F25+ working again)

* Fri Aug 12 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.116-5
- do not package libwidevinecdm*.so, they are just empty shells
  instead, to enable widevine, get these files from Google Chrome

* Fri Aug 12 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.116-4
- add "freeworld" conditional for testing netflix/widevine

* Fri Aug 12 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.116-3
- move PepperFlash directory out of the nacl conditional (thanks to churchyard)
- fix widevine (thanks to David Vásquez and UnitedRPMS)

* Wed Aug 10 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.116-2
- include clearkeycdm and widevinecdm files in libs-media

* Mon Aug  8 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.116-1
- update to 52.0.2743.116

* Thu Aug  4 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-13
- change libs split to "libs-media", as that actually works.
- add PepperFlash directory (nothing in it though, sorry)

* Wed Aug  3 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-12
- split out libs package beyond ffmpeg, into libs and libs-content
- fix libusbx conditional for el7 to not nuke libusb headers
- disable speech-dispatcher header prefix setting if not fedora (el7)

* Wed Aug  3 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-11
- split out chromium-libs-ffmpeg so it can be easily replaced
- conditionalize opus and libusbx for el7

* Wed Aug  3 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-10
- Add ICU Text Codec aliases (from openSUSE via Russian Fedora)
- Use PIE in the Linux sandbox (from openSUSE via Russian Fedora)
- Enable ARM CPU detection for webrtc (from archlinux via Russian Fedora)
- Do not force -m32 in icu compile on ARM (from archlinux via Russian Fedora)
- Enable gtk3 support (via conditional)
- Enable fpic on linux
- Enable hidpi
- Force aura on
- Enable touch_ui
- Add chromedriver subpackage (from Russian Fedora)
- Set default master_preferences location to /etc/chromium
- Add master_preferences file as config file
- Improve chromium-browser.desktop (from Russian Fedora)

* Thu Jul 28 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-9
- fix conditional to disable verbose logging output unless beta/dev

* Thu Jul 28 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-8
- disable nacl/pnacl for Fedora 23 (and older)

* Thu Jul 28 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-7
- fix post scriptlet so that selinux stuff only happens when selinux is enabled

* Thu Jul 28 2016 Richard Hughes <richard@hughsie.com> 52.0.2743.82-6
- Add an AppData file so that Chromium appears in the software center

* Wed Jul 27 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-5
- enable nacl/pnacl (chromium-native_client has landed in Fedora)
- fix chromium-browser.sh to report Fedora build target properly

* Wed Jul 27 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-4
- compile with -fno-delete-null-pointer-checks (fixes v8 crashes, nacl/pnacl)
- turn nacl/pnacl off until chromium-native_client lands in Fedora

* Tue Jul 26 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-3
- turn nacl back on for x86_64

* Thu Jul 21 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-2
- fix cups 2.2 support
- try to enable widevine compatibility (you still need to get the binary .so files from chrome)

* Thu Jul 21 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.82-1
- update to 52.0.2743.82
- handle locales properly
- cleanup spec

* Tue Jul 19 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.75-1
- update to 52.0.2743.75

* Wed Jul 6 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2743.60-1
- bump to 52.0.2743.60, disable nacl for now

* Mon May 9 2016 Tom Callaway <spot@fedoraproject.org> 52.0.2723.2-1
- force to dev to see if it works better on F24+

* Wed May 4 2016 Tom Callaway <spot@fedoraproject.org> 50.0.2661.94-6
- apply upstream fix for https://bugs.chromium.org/p/chromium/issues/detail?id=604534

* Tue May 3 2016 Tom Callaway <spot@fedoraproject.org> 50.0.2661.94-5
- use bundled re2 (conditionalize it)

* Tue May 3 2016 Tom Callaway <spot@fedoraproject.org> 50.0.2661.94-4
- disable asan (it never quite built)
- do not preserve re2 bundled tree, causes header/library mismatch

* Mon May 2 2016 Tom Callaway <spot@fedoraproject.org> 50.0.2661.94-3
- enable AddressSanize (ASan) for debugging

* Sat Apr 30 2016 Tom Callaway <spot@fedoraproject.org> 50.0.2661.94-2
- use bundled icu always. *sigh*

* Fri Apr 29 2016 Tom Callaway <spot@fedoraproject.org> 50.0.2661.94-1
- update to 50.0.2661.94

* Wed Apr 27 2016 Tom Callaway <spot@fedoraproject.org> 50.0.2661.86-1
- update to 50.0.2661.86

* Thu Mar 17 2016 Tom Callaway <spot@fedoraproject.org> 49.0.2623.87-4
- protect third_party/woff2

* Thu Mar 17 2016 Tom Callaway <spot@fedoraproject.org> 49.0.2623.87-3
- add BuildRequires: libffi-devel

* Thu Mar 17 2016 Tom Callaway <spot@fedoraproject.org> 49.0.2623.87-2
- explicitly disable sysroot

* Thu Mar 17 2016 Tom Callaway <spot@fedoraproject.org> 49.0.2623.87-1
- update to 49.0.2623.87

* Mon Feb 29 2016 Tom Callaway <spot@fedoraproject.org> 48.0.2564.116-3
- Happy Leap Day!
- add Requires: u2f-hidraw-policy for u2f token support
- add Requires: xorg-x11-server-Xvfb for chrome-remote-desktop

* Fri Feb 26 2016 Tom Callaway <spot@fedoraproject.org> 48.0.2564.116-2
- fix icu BR

* Wed Feb 24 2016 Tom Callaway <spot@fedoraproject.org> 48.0.2564.116-1
- Update to 48.0.2564.116
- conditionalize icu properly
- fix libusbx handling (bz1270324)

* Wed Feb 17 2016 Tom Callaway <spot@fedoraproject.org> 48.0.2564.103-2
- fixes for gcc6

* Mon Feb  8 2016 Tom Callaway <spot@fedoraproject.org> 48.0.2564.103-1
- update to 48.0.2564.103
- use bundled libsrtp (because upstream has coded themselves into an ugly corner)

* Fri Jan 22 2016 Tom Callaway <spot@fedoraproject.org> 48.0.2564.82-1
- update to 48.0.2564.82

* Fri Jan 15 2016 Tom Callaway <spot@fedoraproject.org> 47.0.2526.111-1
- update to 47.0.2526.111

* Thu Jan 07 2016 Tomas Popela <tpopela@redhat.com> 47.0.2526.106-2
- compare hashes when downloading the tarballs
- Google started to include the Debian sysroots in tarballs - remove them while
  processing the tarball
- add a way to not use the system display server for tests instead of Xvfb
- update the depot_tools checkout to get some GN fixes
- use the remove_bundled_libraries script
- update the clean_ffmpeg script to print errors when some files that we are
  processing are missing
- update the clean_ffmpeg script to operate on tarball's toplevel folder
- don't show comments as removed tests in get_linux_tests_names script
- rework the process_ffmpeg_gyp script (also rename it to
  get_free_ffmpeg_source_files) to use the GN files insted of GYP (but we still
  didn't switched to GN build)

* Wed Dec 16 2015 Tom Callaway <spot@fedoraproject.org> 47.0.2526.106-1
- update to 47.0.2526.106

* Tue Dec 15 2015 Tom Callaway <spot@fedoraproject.org> 47.0.2526.80-4
- entirely patch out the broken fd counter from the nacl loader code
  killing it with fire would be better, but then chromium is on fire
  and that somehow makes it worse.

* Mon Dec 14 2015 Tom Callaway <spot@fedoraproject.org> 47.0.2526.80-3
- revert nacl fd patch (now we see 6 fds! 6 LIGHTS!)

* Fri Dec 11 2015 Tom Callaway <spot@fedoraproject.org> 47.0.2526.80-2
- build everything shared, but when we do shared builds, make -libs subpackage
- make chrome-remote-desktop dep on -libs subpackage in shared builds

* Wed Dec  9 2015 Tom Callaway <spot@fedoraproject.org> 47.0.2526.80-1
- update to 47.0.2526.80
- only build ffmpeg shared, not any other libs
  this is because if we build the other libs shared, then our
  chrome-remote-desktop build deps on those libs and we do not want that

* Tue Dec  8 2015 Tom Callaway <spot@fedoraproject.org> 47.0.2526.73-2
- The nacl loader claims it sees 7 fds open ALL THE TIME, and fails
  So, we tell it that it is supposed to see 7.
  I suspect building with shared objects is causing this disconnect.

* Wed Dec  2 2015 Tom Callaway <spot@fedoraproject.org> 47.0.2526.73-1
- update to 47.0.2526.73
- rework chrome-remote-desktop subpackage to work for google-chrome and chromium

* Wed Dec  2 2015 Tomas Popela <tpopela@redhat.com> 47.0.2526.69-1
- Update to 47.0.2526.69

* Tue Dec  1 2015 Tom Callaway <spot@fedoraproject.org> 46.0.2490.86-4
- still more remote desktop changes

* Mon Nov 30 2015 Tom Callaway <spot@fedoraproject.org> 46.0.2490.86-3
- lots of remote desktop cleanups

* Thu Nov 12 2015 Tom Callaway <spot@fedoraproject.org> 46.0.2490.86-2
- re-enable Requires/BuildRequires for libusbx
- add remote-desktop subpackage

* Wed Nov 11 2015 Tomas Popela <tpopela@redhat.com> 46.0.2490.86-1
- update to 46.0.2490.86
- clean the SPEC file
- add support for policies: https://www.chromium.org/administrators/linux-quick-start
- replace exec_mem_t SELinux label with bin_t - see rhbz#1281437
- refresh scripts that are used for processing the original tarball

* Fri Oct 30 2015 Tom Callaway <spot@fedoraproject.org> 46.0.2490.80-5
- tls_edit is a nacl thing. who knew?

* Thu Oct 29 2015 Tom Callaway <spot@fedoraproject.org> 46.0.2490.80-4
- more nacl fixups for i686 case

* Thu Oct 29 2015 Tom Callaway <spot@fedoraproject.org> 46.0.2490.80-3
- conditionalize nacl/nonacl, disable nacl on i686, build for i686

* Mon Oct 26 2015 Tom Callaway <spot@fedoraproject.org> 46.0.2490.80-2
- conditionalize shared bits (enable by default)

* Fri Oct 23 2015 Tom Callaway <spot@fedoraproject.org> 46.0.2490.80-1
- update to 46.0.2490.80

* Thu Oct 15 2015 Tom Callaway <spot@fedoraproject.org> 46.0.2490.71-1
- update to 46.0.2490.71

* Thu Oct 15 2015 Tom Callaway <spot@fedoraproject.org> 45.0.2454.101-2
- fix icu handling for f21 and older

* Mon Oct  5 2015 Tom Callaway <spot@fedoraproject.org> 45.0.2454.101-1
- update to 45.0.2454.101

* Thu Jun 11 2015 Tom Callaway <spot@fedoraproject.org> 43.0.2357.124-1
- update to 43.0.2357.124

* Tue Jun  2 2015 Tom Callaway <spot@fedoraproject.org> 43.0.2357.81-1
- update to 43.0.2357.81

* Thu Feb 26 2015 Tom Callaway <spot@fedoraproject.org> 40.0.2214.115-1
- update to 40.0.2214.115

* Thu Feb 19 2015 Tom Callaway <spot@fedoraproject.org> 40.0.2214.111-1
- update to 40.0.2214.111

* Mon Feb  2 2015 Tom Callaway <spot@fedoraproject.org> 40.0.2214.94-1
- update to 40.0.2214.94

* Tue Jan 27 2015 Tom Callaway <spot@fedoraproject.org> 40.0.2214.93-1
- update to 40.0.2214.93

* Sat Jan 24 2015 Tom Callaway <spot@fedoraproject.org> 40.0.2214.91-1
- update to 40.0.2214.91

* Wed Jan 21 2015 Tom Callaway <spot@fedoraproject.org> 39.0.2171.95-3
- use bundled icu on Fedora < 21, we need 5.2

* Tue Jan  6 2015 Tom Callaway <spot@fedoraproject.org> 39.0.2171.95-2
- rebase off Tomas's spec file for Fedora

* Fri Dec 12 2014 Tomas Popela <tpopela@redhat.com> 39.0.2171.95-1
- Update to 39.0.2171.95
- Resolves: rhbz#1173448

* Wed Nov 26 2014 Tomas Popela <tpopela@redhat.com> 39.0.2171.71-1
- Update to 39.0.2171.71
- Resolves: rhbz#1168128

* Wed Nov 19 2014 Tomas Popela <tpopela@redhat.com> 39.0.2171.65-2
- Revert the chrome-sandbox rename to chrome_sandbox
- Resolves: rhbz#1165653

* Wed Nov 19 2014 Tomas Popela <tpopela@redhat.com> 39.0.2171.65-1
- Update to 39.0.2171.65
- Use Red Hat Developer Toolset for compilation
- Set additional SELinux labels
- Add more unit tests
- Resolves: rhbz#1165653

* Fri Nov 14 2014 Tomas Popela <tpopela@redhat.com> 38.0.2125.122-1
- Update to 38.0.2125.122
- Resolves: rhbz#1164116

* Wed Oct 29 2014 Tomas Popela <tpopela@redhat.com> 38.0.2125.111-1
- Update to 38.0.2125.111
- Resolves: rhbz#1158347

* Fri Oct 24 2014 Tomas Popela <tpopela@redhat.com> 38.0.2125.104-2
- Fix the situation when the return key (and keys from numpad) does not work
  in HTML elements with input
- Resolves: rhbz#1153988
- Dynamically determine the presence of the PepperFlash plugin
- Resolves: rhbz#1154118

* Thu Oct 16 2014 Tomas Popela <tpopela@redhat.com> 38.0.2125.104-1
- Update to 38.0.2125.104
- Resolves: rhbz#1153012

* Thu Oct 09 2014 Tomas Popela <tpopela@redhat.com> 38.0.2125.101-2
- The boringssl is used for tests, without the possibility of using
  the system openssl instead. Remove the openssl and boringssl sources
  when not building the tests.
- Resolves: rhbz#1004948

* Wed Oct 08 2014 Tomas Popela <tpopela@redhat.com> 38.0.2125.101-1
- Update to 38.0.2125.101
- System openssl is used for tests, otherwise the bundled boringssl is used
- Don't build with clang
- Resolves: rhbz#1004948

* Wed Sep 10 2014 Tomas Popela <tpopela@redhat.com> 37.0.2062.120-1
- Update to 37.0.2062.120
- Resolves: rhbz#1004948

* Wed Aug 27 2014 Tomas Popela <tpopela@redhat.com> 37.0.2062.94-1
- Update to 37.0.2062.94
- Include the pdf viewer library

* Wed Aug 13 2014 Tomas Popela <tpopela@redhat.com> 36.0.1985.143-1
- Update to 36.0.1985.143
- Use system openssl instead of bundled one
- Resolves: rhbz#1004948

* Thu Jul 17 2014 Tomas Popela <tpopela@redhat.com> 36.0.1985.125-1
- Update to 36.0.1985.125
- Add libexif as BR
- Resolves: rhbz#1004948

* Wed Jun 11 2014 Tomas Popela <tpopela@redhat.com> 35.0.1916.153-1
- Update to 35.0.1916.153
- Resolves: rhbz#1004948

* Wed May 21 2014 Tomas Popela <tpopela@redhat.com> 35.0.1916.114-1
- Update to 35.0.1916.114
- Bundle python-argparse
- Resolves: rhbz#1004948

* Wed May 14 2014 Tomas Popela <tpopela@redhat.com> 34.0.1847.137-1
- Update to 34.0.1847.137
- Resolves: rhbz#1004948

* Mon May 5 2014 Tomas Popela <tpopela@redhat.com> 34.0.1847.132-1
- Update to 34.0.1847.132
- Bundle depot_tools and switch from make to ninja
- Remove PepperFlash
- Resolves: rhbz#1004948

* Mon Feb 3 2014 Tomas Popela <tpopela@redhat.com> 32.0.1700.102-1
- Update to 32.0.1700.102

* Thu Jan 16 2014 Tomas Popela <tpopela@redhat.com> 32.0.1700.77-1
- Update to 32.0.1700.77
- Properly kill Xvfb when tests fails
- Add libdrm as BR
- Add libcap as BR

* Tue Jan 7 2014 Tomas Popela <tpopela@redhat.com> 31.0.1650.67-2
- Minor changes in spec files and scripts
- Add Xvfb as BR for tests
- Add policycoreutils-python as Requires
- Compile unittests and run them in chech phase, but turn them off by default
  as many of them are failing in Brew

* Thu Dec 5 2013 Tomas Popela <tpopela@redhat.com> 31.0.1650.67-1
- Update to 31.0.1650.63

* Thu Nov 21 2013 Tomas Popela <tpopela@redhat.com> 31.0.1650.57-1
- Update to 31.0.1650.57

* Wed Nov 13 2013 Tomas Popela <tpopela@redhat.com> 31.0.1650.48-1
- Update to 31.0.1650.48
- Minimal supported RHEL6 version is now RHEL 6.5 due to GTK+

* Fri Oct 25 2013 Tomas Popela <tpopela@redhat.com> 30.0.1599.114-1
- Update to 30.0.1599.114
- Hide the infobar with warning that this version of OS is not supported
- Polished the chromium-latest.py

* Thu Oct 17 2013 Tomas Popela <tpopela@redhat.com> 30.0.1599.101-1
- Update to 30.0.1599.101
- Minor changes in scripts

* Wed Oct 2 2013 Tomas Popela <tpopela@redhat.com> 30.0.1599.66-1
- Update to 30.0.1599.66
- Automated the script for cleaning the proprietary sources from ffmpeg.

* Thu Sep 19 2013 Tomas Popela <tpopela@redhat.com> 29.0.1547.76-1
- Update to 29.0.1547.76
- Added script for removing the proprietary sources from ffmpeg. This script is called during cleaning phase of ./chromium-latest --rhel

* Mon Sep 16 2013 Tomas Popela <tpopela@redhat.com> 29.0.1547.65-2
- Compile with Dproprietary_codecs=0 and Dffmpeg_branding=Chromium to disable proprietary codecs (i.e. MP3)

* Mon Sep 9 2013 Tomas Popela <tpopela@redhat.com> 29.0.1547.65-1
- Initial version based on Tom Callaway's <spot@fedoraproject.org> work

