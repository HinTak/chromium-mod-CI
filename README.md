# Chromium SVG in OpenType support

This is a set of patches to address
Chromium [Issue 306078: SVG in OpenType support](https://bugs.chromium.org/p/chromium/issues/detail?id=306078).
Chromium is too large to be built within github's 6 hour limit, so this CI only attempts to build Blink as a library,
just to verify that the patches build. And that takes just over 5 hours, and I reckon constitute about 40% of chromium.
The patches are tested in the QT6 versions mentioned below.

m120 is current stable, and the patches are identical to the QT6 m118 versions except relocated (QT6 WebEngine has
the chromium source tree under `src/3rdparty/chromium/`).

Earlier 118 versions are built in [QT6 WebEngine](https://github.com/HinTak/Qt6WE-OT-SVG) and
tested with the QT6 browser example in [minimal web browser collections](https://github.com/HinTak/minimal-web-browsers/).

## Discussion

The patches are logically in 3 parts, but in 2 files:

- a one-line hook to connect Skia's SVG module with the skia's FreeType font manager. It only needs to be done once. In Skia Python, it is done at
[python module loading time](https://github.com/kyamagu/skia-python/commit/e5f2e6361d0e6a40e5077fa46897a556f793a18d), although the earlier work to
[test and set just before it is needed](https://github.com/kyamagu/skia-python/commit/9039fbd0848b63070ef1b7392ab7d546de125622) is gauranteed to work,
at the risk of doing unnessary work multiple times. Here I do both, as I am not sure `skia/ext/fontmgr_default_linux.cc`
(or `skia/ext/font_utils.cc` in m122 onwards) is the only entry point.
Somebody more knowledgeable might be able to indicate a better location otherwise. Plus some changes to the skia build script to include the
optional svg module and what it depends on.

- Modify the included OpenType Sanitizer related code to pass SVG through. This is quite straight-forward, referencing treatment of other tables.

These two allows OT-SVG to work on Linux, so it is combined into a "patch 1".

- Blink already includes diversion from CoreText/DirectWrite to FreeType on non-Linux, for font formats not supported by the host OS. A small addition
along the same line as other font formats is added for SVG too.

This "patch 2" is only passively tested on Linux (as in it has no affect on "patch 1").

## misc

Bare:

```
overlay         87204404 60571144  26616876  70% /
```

```
-rw-r--r-- 1 root root 3278880830 Dec 29 00:40 a.rpm
```

All dependencies:

```
overlay         87204404 66291436  20896584  77% /
```

Unpacking tarball:

```
overlay         87204404 85434128   1753892  98% /
```

cleaned tarball:
```
overlay         87204404 79232528   7955492  91% /
```

```
2592652	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/angle/third_party
2666348	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/angle
314040	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/blink
138676	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/boringssl
339104	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/catapult/third_party
383284	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/catapult
404140	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/dawn/third_party
885088	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/dawn
417944	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/devtools-frontend
100560	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/harfbuzz-ng
230368	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/icu
1882116	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/llvm
4322576	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/rust-src
555028	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/swiftshader/third_party
1072660	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109/third_party/swiftshader
19145080	/github/home/rpmbuild/BUILD/chromium-120.0.6099.109
```

```
[headless_shell:31366/41287] CXX obj/content/browser/browser/screen_change_monitor.o
[headless_shell:31336/41287] CXX obj/content/browser/browser/render_widget_host_impl.o
[chrome:39361/57874] CXX obj/chrome/browser/extensions/extensions/sync_storage_backend.o
[chrome:39546/57874] CXX obj/chrome/browser/extensions/extensions/webstore_installer.o
```

```
obj/skia/libskia.a
obj/third_party/ots/libots.a
obj/third_party/blink/renderer/platform/libblink_platform.a
```

```
[third_party/blink/renderer/platform:6018/23003] CXX obj/third_party/ots/ots/ots.o
[third_party/blink/renderer/platform:8141/23003] CXX obj/skia/skia/fontmgr_default_linux.o
[third_party/blink/renderer/platform:8330/23003] CXX obj/skia/skia/SkFontHost_FreeType.o
[third_party/blink/renderer/platform:21067/23003] CXX obj/third_party/blink/renderer/platform/platform/font_format_check.o
[third_party/blink/renderer/platform:21118/23003] CXX obj/third_party/blink/renderer/platform/platform/web_font_typeface_factory.o
[third_party/blink/renderer/platform:21121/23003] CXX obj/third_party/blink/renderer/platform/platform/web_font_decoder.o
```

```
chromium-121.0.6167.47-clean.tar.xz
3351519184
[third_party/blink/renderer/platform:6065/23206] CXX obj/third_party/ots/ots/ots.o
[third_party/blink/renderer/platform:8248/23206] CXX obj/skia/skia/fontmgr_default_linux.o
[third_party/blink/renderer/platform:8434/23206] CXX obj/skia/skia/SkFontHost_FreeType.o
[third_party/blink/renderer/platform:21264/23206] CXX obj/third_party/blink/renderer/platform/platform/font_format_check.o
[third_party/blink/renderer/platform:21316/23206] CXX obj/third_party/blink/renderer/platform/platform/web_font_typeface_factory.o
[third_party/blink/renderer/platform:21319/23206] CXX obj/third_party/blink/renderer/platform/platform/web_font_decoder.o
```

```
chromium-122.0.6226.2-clean.tar.xz
3335866628
[third_party/blink/renderer/platform:6105/23237] CXX obj/third_party/ots/ots/ots.o
[third_party/blink/renderer/platform:8267/23237] CXX obj/skia/skia/font_utils.o
[third_party/blink/renderer/platform:8466/23237] CXX obj/skia/skia/SkFontHost_FreeType.o
[third_party/blink/renderer/platform:21293/23237] CXX obj/third_party/blink/renderer/platform/platform/font_format_check.o
[third_party/blink/renderer/platform:21345/23237] CXX obj/third_party/blink/renderer/platform/platform/web_font_typeface_factory.o
[third_party/blink/renderer/platform:21348/23237] CXX obj/third_party/blink/renderer/platform/platform/web_font_decoder.o
```

```
chromium-122.0.6238.2-clean.tar.xz
3319947288
[third_party/blink/renderer/platform:6138/23238] CXX obj/third_party/ots/ots/ots.o
[third_party/blink/renderer/platform:8266/23238] CXX obj/skia/skia/font_utils.o
[third_party/blink/renderer/platform:8464/23238] CXX obj/skia/skia/SkFontHost_FreeType.o
[third_party/blink/renderer/platform:21294/23238] CXX obj/third_party/blink/renderer/platform/platform/font_format_check.o
[third_party/blink/renderer/platform:21346/23238] CXX obj/third_party/blink/renderer/platform/platform/web_font_typeface_factory.o
[third_party/blink/renderer/platform:21349/23238] CXX obj/third_party/blink/renderer/platform/platform/web_font_decoder.o
```

## Fedora build logs

```
[Hin-Tak@localhost logs]$ grep obj/third_party/ots/ots/ots. */b*
aarch64/build.log:[headless_shell:8649/42215] CXX obj/third_party/ots/ots/ots.o
aarch64/build.log:[chrome:10645/58803] CXX obj/third_party/ots/ots/ots.o
x86_64/build.log:[headless_shell:8802/41287] CXX obj/third_party/ots/ots/ots.o
x86_64/build.log:[chrome:10684/57889] CXX obj/third_party/ots/ots/ots.o
[Hin-Tak@localhost logs]$ grep obj/skia/skia/fontmgr_default_linux. */b*
aarch64/build.log:[headless_shell:14005/42215] CXX obj/skia/skia/fontmgr_default_linux.o
aarch64/build.log:[chrome:18488/58803] CXX obj/skia/skia/fontmgr_default_linux.o
x86_64/build.log:[headless_shell:13961/41287] CXX obj/skia/skia/fontmgr_default_linux.o
x86_64/build.log:[chrome:15222/57889] CXX obj/skia/skia/fontmgr_default_linux.o
[Hin-Tak@localhost logs]$ grep obj/skia/skia/SkFontHost_FreeType */b*
aarch64/build.log:[headless_shell:14310/42215] CXX obj/skia/skia/SkFontHost_FreeType.o
aarch64/build.log:[headless_shell:14353/42215] CXX obj/skia/skia/SkFontHost_FreeType_common.o
aarch64/build.log:[chrome:18812/58803] CXX obj/skia/skia/SkFontHost_FreeType.o
aarch64/build.log:[chrome:18927/58803] CXX obj/skia/skia/SkFontHost_FreeType_common.o
x86_64/build.log:[headless_shell:14173/41287] CXX obj/skia/skia/SkFontHost_FreeType.o
x86_64/build.log:[headless_shell:14182/41287] CXX obj/skia/skia/SkFontHost_FreeType_common.o
x86_64/build.log:[chrome:15437/57889] CXX obj/skia/skia/SkFontHost_FreeType.o
x86_64/build.log:[chrome:15443/57889] CXX obj/skia/skia/SkFontHost_FreeType_common.o
[Hin-Tak@localhost logs]$ grep obj/third_party/blink/renderer/platform/platform/font_format_check */b*
aarch64/build.log:[headless_shell:38901/42215] CXX obj/third_party/blink/renderer/platform/platform/font_format_check.o
aarch64/build.log:[chrome:52180/58803] CXX obj/third_party/blink/renderer/platform/platform/font_format_check.o
x86_64/build.log:[headless_shell:39059/41287] CXX obj/third_party/blink/renderer/platform/platform/font_format_check.o
x86_64/build.log:[chrome:52154/57889] CXX obj/third_party/blink/renderer/platform/platform/font_format_check.o
[Hin-Tak@localhost logs]$ grep obj/third_party/blink/renderer/platform/platform/web_font_ */b*
aarch64/build.log:[headless_shell:38864/42215] CXX obj/third_party/blink/renderer/platform/platform/web_font_description.o
aarch64/build.log:[headless_shell:39021/42215] CXX obj/third_party/blink/renderer/platform/platform/web_font_render_style.o
aarch64/build.log:[headless_shell:39086/42215] CXX obj/third_party/blink/renderer/platform/platform/web_font_typeface_factory.o
aarch64/build.log:[headless_shell:39161/42215] CXX obj/third_party/blink/renderer/platform/platform/web_font_decoder.o
aarch64/build.log:[chrome:52150/58803] CXX obj/third_party/blink/renderer/platform/platform/web_font_description.o
aarch64/build.log:[chrome:52309/58803] CXX obj/third_party/blink/renderer/platform/platform/web_font_render_style.o
aarch64/build.log:[chrome:52326/58803] CXX obj/third_party/blink/renderer/platform/platform/web_font_typeface_factory.o
aarch64/build.log:[chrome:52529/58803] CXX obj/third_party/blink/renderer/platform/platform/web_font_decoder.o
x86_64/build.log:[headless_shell:39012/41287] CXX obj/third_party/blink/renderer/platform/platform/web_font_description.o
x86_64/build.log:[headless_shell:39135/41287] CXX obj/third_party/blink/renderer/platform/platform/web_font_render_style.o
x86_64/build.log:[headless_shell:39141/41287] CXX obj/third_party/blink/renderer/platform/platform/web_font_typeface_factory.o
x86_64/build.log:[headless_shell:39158/41287] CXX obj/third_party/blink/renderer/platform/platform/web_font_decoder.o
x86_64/build.log:[chrome:52108/57889] CXX obj/third_party/blink/renderer/platform/platform/web_font_description.o
x86_64/build.log:[chrome:52233/57889] CXX obj/third_party/blink/renderer/platform/platform/web_font_render_style.o
x86_64/build.log:[chrome:52237/57889] CXX obj/third_party/blink/renderer/platform/platform/web_font_typeface_factory.o
x86_64/build.log:[chrome:52261/57889] CXX obj/third_party/blink/renderer/platform/platform/web_font_decoder.o
```

```
$ grep 'ninja -j ' */b*
aarch64/build.log:+ ninja -j 224 -C out/Headless headless_shell
aarch64/build.log:+ ninja -j 224 -C out/Release chrome
aarch64/build.log:+ ninja -j 224 -C out/Release chrome_sandbox
aarch64/build.log:+ ninja -j 224 -C out/Release chromedriver
aarch64/build.log:+ ninja -j 224 -C out/Release policy_templates
x86_64/build.log:+ ninja -j 48 -C out/Headless headless_shell
x86_64/build.log:+ ninja -j 48 -C out/Release chrome
x86_64/build.log:+ ninja -j 48 -C out/Release chrome_sandbox
x86_64/build.log:+ ninja -j 48 -C out/Release chromedriver
x86_64/build.log:+ ninja -j 48 -C out/Release policy_templates

$ grep -i rpmbuild */sta*
aarch64/state.log:2024-01-16 22:51:00,160 - Start: rpmbuild chromium-120.0.6099.224-1.fc39.src.rpm
aarch64/state.log:2024-01-17 02:50:50,299 - Finish: rpmbuild chromium-120.0.6099.224-1.fc39.src.rpm
x86_64/state.log:2024-01-16 22:48:08,129 - Start: rpmbuild chromium-120.0.6099.224-1.fc39.src.rpm
x86_64/state.log:2024-01-17 03:23:04,069 - Finish: rpmbuild chromium-120.0.6099.224-1.fc39.src.rpm
```
