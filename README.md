# OrangeFox Action Builder
Compile your first custom recovery from OrangeFox Recovery using Github Action.

# How to Use
1. Fork this repository.

2. Go to `Action` tab > `All workflows` > `OrangeFox - Build` > `Run workflow`. The form defaults to Xiaomi Mi 10S (`thyme`); change the inputs to build another device:
 * MANIFEST_BRANCH (`12.1` and `11.0`)
 * DEVICE_TREE (Your device tree repository link.)
 * DEVICE_TREE_BRANCH (Your device tree repository branch.)
 * DEVICE_PATH (`device/vendor/codename`)
 * DEVICE_NAME (Your device codename)
 * BUILD_TARGET (`boot`, `recovery`, `vendorboot`)

## Default build inputs

| Input | Default |
| --- | --- |
| `MANIFEST_BRANCH` | `12.1` |
| `DEVICE_TREE` | `https://git.thinh2701p.xyz/thinhzero/android_device_xiaomi_thyme.git` |
| `DEVICE_TREE_BRANCH` | `fox_12.1` |
| `DEVICE_PATH` | `device/xiaomi/thyme` |
| `DEVICE_NAME` | `thyme` |
| `BUILD_TARGET` | `boot` |

These are defaults, **not a fixed device configuration**. Each nonempty input
overrides its default throughout cloning, building, and release upload. If an
optional text field is left empty, its default is used. When building another
device, provide its tree URL, branch, device path, codename, and matching target;
blank fields do not infer values from other fields.

## Thyme PixelOS 17 temporary boot test

Keep the inputs above, but set `DEVICE_TREE_BRANCH=fox_12.1-aosp` and
`BUILD_TARGET=boot`. The tree's `prebuilt/pixelos/manifest.json` identifies this
profile; the workflow rejects other targets for it. Baseline defaults are unchanged.

- Missing-dependency bypasses remain unset after envsetup and before lunch/build.
  The minimal 12.1 manifest removes `test/vts-testcase/fuzz`, although the HIDL
  Soong generator still refers to `vts_proto_fuzzer_default`. This profile restores
  the **real AOSP project**, tag `android-12.1.0_r4`, with commit verified against
  `6148b27ab136ae012e97fdeae96978edcb5ca7b7`; no fake defaults or HAL changes.
  It also restores `packages/modules/NeuralNetworks` at the same AOSP tag,
  verified commit `987db53d74e02ab01abdb0db36eb8ccea00e2548`, because retained
  HAL utility declarations inherit `neuralnetworks_utils_defaults` from it.
  Restoring source definitions does not add NNAPI packages to the recovery.
  Framework test declarations also need CTS defaults: sparse checkouts restore
  `cts/Android.bp` and the `tools/cts-tradefed` harness declarations/assets at
  `5c5a1cac99f23a61564c60be33f9274ff7fcd5fa`, and
  `platform_testing/libraries/annotations` at
  `af7eaff31e0aed03c06f6bade385397d792f4008` (both at the same AOSP tag).
  These are upstream definitions and Java sources, not dummy modules; complete
  CTS/platform test suites are not checked out or added to the recovery.
  ADB's retained `FastDeployHostTests` references `cts-tradefed`. Its unmodified
  harness Blueprint, wrapper, resources and `DynamicConfig.xml` are preserved,
  along with `OWNERS`/`README`; the separate harness tests are outside this checkout.
  The retained Soong `tradefed_binary_host` plugin generates suite metadata and
  adds the existing Tradefed imports below. Its load hook is not changed.
  GKI's retained `GkiInstallTest` also references `cts-host-utils`: the same pinned
  CTS checkout includes `hostsidetests/utils/` (the original Blueprint and two Java
  runner sources). Its libraries are the already restored `cts-tradefed` and
  `tradefed`; no GKI tests or kernel changes are added to the recovery.
  SDK Extensions/APEX host tests also need `cts-install-lib-host` and its
  `cts-shim-host-lib` dependency. The same pinned CTS checkout retains complete
  `libs/install/`, `libs/shim/` and `hostsidetests/stagedinstall/` subtrees. Their
  unmodified Blueprints also declare device libraries, APKs and APEX resources,
  so preserve all sources/manifests/resources, public CTS fixture signing keys,
  lineage and staged-install test data rather than carving out a host-only
  replacement. Existing CTS harness/utilities remain selected; no test packages,
  fixture keys or APK/APEX data are added to the recovery image. Standalone host
  compilation/simulated-device checks do not prove full CTS/Soong build or boot.
  Tethering test declarations require NetworkStack's
  `tests/unit/Android.bp:libnetworkstackutilsjni_deps`; the matching project is
  restored at `ae471a43f6198859028f3f987c72aa17ae890ff1` (same AOSP tag), including
  its actual JNI sources. NetworkStack is not added to recovery packages.
  Retained Harmony JDWP tests also reference JUnit, which requires Hamcrest;
  source projects `external/junit` and `external/hamcrest` are restored at
  `7c5c0ba1f123304da6f14f9d34d83b89851ccda2` and
  `b6b17dc33ec3cfffb9bc227e14c3042626c08f4e`, respectively (same AOSP tag).
  Retained `vts-tradefed-tests` statically references `easymock`. The complete
  `external/easymock` source project is restored at
  `51beb6618fd32fa0f2d51082f04c80c07c8677c9` (same AOSP tag), preserving its
  `easymock` host/device variants, `easymocklib` wrapper and license files.
  This version has no other explicit library dependencies; no VTS tests or
  mocking libraries are added to recovery packages.
- Retained `dx-docs` requires `droiddoc-templates-sdk` from Doclava. The profile
  restores the complete Doclava project (templates and Java modules), together
  with the following source dependencies at `android-12.1.0_r4`, verifying every
  commit. ErrorProne includes its upstream JARs and Soong configuration plugin;
  no compiler-check settings are overridden. These are build dependencies, not
  additions to recovery packages.

  | Project under `external/` | Verified commit |
  | --- | --- |
  | `doclava` | `0f582d0d69044f28b50aad2de59bd6f8673a5027` |
  | `jsilver` | `3092867230f876bb6459261ceceac687ef58d9c5` |
  | `guava` | `9b79d654ebb1a2adf1caafbaa7029c5252f74f1b` |
  | `antlr` | `b3332f240724bb50d4387aca9a5ecbaf713df8d0` |
  | `tagsoup` | `4c3e83b5676516de4ee40e61884f86020cbe44c1` |
  | `jsr305` | `ef7ea7b4611582d4c3cd14b868694bab8604a670` |
  | `error_prone` | `aa48ec720e6665859f4442850b1988791df2af18` |

- Retained framework/MediaProvider ErrorProne checks reference Auto Service's real
  annotations and annotation processor. At the same AOSP tag, `external/auto` is
  restored at `40f6e33309de080c50ade433c4a7fc08a7c9d853` with root package/license
  metadata and complete `common`/`service` subtrees. OpenCensus also requires
  complete `value` and `android-annotation-stubs` subtrees from that same pin;
  unrelated AutoFactory remains unselected. No upstream Blueprint is edited.
  `auto_common` requires existing Guava and `external/javapoet`, restored as a full
  source project at `6458e0481b8e78a562805da73c016e8772755e31` (same AOSP tag).
  The actual `AutoServiceProcessor` is retained; compiler checks are not disabled
  or replaced with placeholder annotations/plugins. These are build dependencies,
  not additions to recovery packages.

- Metalava and retained fs_mgr host-test declarations also need Kotlin, Maven,
  Gradle and Tradefed modules. These upstream projects are restored at the same
  AOSP tag with the commits below. Kotlin includes its actual compiler and runtime;
  Tradefed includes its original imports/filegroups and prebuilt JARs. The
  `platformprotos` and `asm-7.0` dependencies are checked in the retained framework
  and misc prebuilts, not replaced with placeholders.

  | Project | Verified commit | Checkout scope |
  | --- | --- | --- |
  | `external/kotlinc` | `5a266bf3adea01dbf7c5453e240333446eeee8cc` | Complete project |
  | `tools/tradefederation/prebuilts` | `2a5fd21caf0d161ef6fc2efec1fadf2f31986039` | Complete project |
  | `prebuilts/tools` | `742ee2c4a94f04fb86ffbc5a72cb6eaa3e9c4ea0` | Root declarations/metadata, complete `common/m2` (including `robolectric.bp`), `common/api-versions` and `common/netbeans-visual` |
  | `prebuilts/gradle-plugin` | `521e990cdd59af10203ca5cbacb34a89eddc4ed7` | Root declarations/metadata and all 13 versioned artifact directories declared by its Metalava import |

  Sparse checkout avoids unrelated large prebuilt trees; upstream build files are
  not edited and all files declared by the selected imports are preserved. No
  tests or documentation tools are added to recovery packages.

- Retained kernel proc-file/development host tests require three Python libraries
  and `vts_vndk_utils`. Their complete source projects are restored at the same
  AOSP tag, including root licenses and nested Blueprint declarations. VNDK's
  golden-data genrule also needs the original ABI dump project with all dump inputs;
  the archive rule is not stubbed or supplied with an empty input tree.

  | Project | Verified commit |
  | --- | --- |
  | `external/python/parse_type` | `c377f51ae22f7a96136d9f83b6f8aa2132dc03eb` |
  | `external/ply` | `0463af9bd0afb0adf7803fd4066d90d163dbe7b1` |
  | `external/python/pyfakefs` | `4a8b5a290814e51105ed0d3297296de0f3c75a9e` |
  | `test/vts-testcase/vndk` | `ea6b1eeb118f329ffdaef7120db5bf7adde90ae3` |
  | `prebuilts/abi-dumps/vndk` | `f3cda30722da4ad96bc305d65367bab02c326380` |

  Other VNDK data filegroups/Python utilities are checked in retained projects.
  The tools sparse checkout also preserves `hierarchyviewer`'s upstream NetBeans
  JAR imports and `NOTICE` under `common/netbeans-visual`; its commit is unchanged.
  These source/build dependencies do not add host tests or SDK tools to recovery.

- Retained audio-policy generators require `EddParser.py`, `hostConfig.py` and
  `PFWScriptGenerator.py`, plus the latter's `PfwBaseTranslator.py` dependency.
  The complete `external/parameter-framework` source project is restored at
  `2adbdd6b6523793ed33e291b3915fe7f2a704eb5` (same AOSP tag). Its root Blueprint,
  licenses, Python sources, native connector/libraries, XML schemas and original
  `asio -> asio-1.10.6` symlink/headers are preserved. The native library's only
  explicit external library dependency, `libxml2`, is checked in retained sources.
  No audio-policy declarations are removed or replaced; restoring source definitions
  does not add PFW tools, libraries or test programs to recovery packages.

- Platform-compat's retained host libraries need BCEL, dexlib2 and the SDK-level
  test helper. The following real source projects are restored at the same AOSP
  tag; dexlib2's JCommander dependency is included. Upstream Blueprints/licenses
  are unchanged, and no host tools or tests are added to recovery packages.

  | Project | Verified commit | Checkout scope |
  | --- | --- | --- |
  | `external/apache-commons-bcel` | `040b6144329cdd183b1d79998995800f2b9c003f` | Complete project |
  | `external/jcommander` | `8ce937f3ef2ed68f188cc0637664933a711124de` | Complete project |
  | `external/smali` | `bb22a92b16eb0453f7f42a540679fad20382b68d` | Root declarations/license/metadata and their script/Gradle inputs, complete `dexlib2` subtree |
  | `frameworks/libs/modules-utils` | `0a8bde0eb27a5de62e73faf9de06a498a4ccec69` | Root package/metadata and complete `java/com/android/modules/utils/build/testing` directory |

  Other explicit dependencies are existing Guava, JSR305, Tradefed, the retained
  `commons-cli-1.2` import and the retained AndroidX annotation import. Source/JAR
  guards check these without replacing libraries or removing platform-compat code.

- Framework codegen/XML persistence host tools require `javaparser` and
  `javaparser-symbol-solver`. The complete `external/javaparser` project is restored
  at `acd7a527fc44f5e516a50ff61eb1da2ba9272d31`, including its generated parser
  sources and all license files. The solver's `external/javassist` dependency is
  restored at `7bd5da870ec56352887396c1c188350f733e4f3c`; Guava is already restored.
  Both pins use the same AOSP tag. Upstream Blueprints remain unchanged, and no
  parser libraries, generators or tests are added to recovery packages.

- The retained Robolectric runtime prebuilt depends on its real
  `robolectric-host-android_all` source library. Restore the following projects
  from the same AOSP tag, preserving original Blueprints/licenses, the Soong
  build-property plugin, Java/test resources and Makefile helpers. Mockito keeps
  its upstream Byte Buddy JARs; no placeholders or replacement runtimes are used.

  | Project | Verified commit | Checkout scope |
  | --- | --- | --- |
  | `external/robolectric-shadows` | `fc6f4e51fa28f85090051012a491dd1ab0233eef` | Complete project, including `soong` |
  | `external/mockito` | `7eb0861430819806dced351813582a5aa666e670` | Complete project |
  | `external/objenesis` | `6392daddb9a890ad7a2142efb470d105e5824ac9` | Complete project |
  | `packages/services/Car` | `af051f0a86d0ded75e4be48aa3387c68d569202b` | Root metadata and complete `car-lib` source/API/native inputs; not the Automotive service/UI or their root Makefile |

  `android.car` is an explicit input of the original android-all host library.
  Framework resource/tzdata modules and the remaining retained/restored libraries
  are not replaced. These source declarations do not add Robolectric, mocking
  libraries, Automotive code or host tests to recovery packages.

- Retained `class2nonsdklistlib` links TestNG. Restore the complete TestNG,
  SnakeYAML, Guice and JSR330 projects from `android-12.1.0_r4`, with their original
  Blueprints, licenses and source inputs. Keep TestNG's generated version and
  Android replacements, Guice's `munge.jar`-based `NO_AOP` source generation, and
  SnakeYAML's four Android-only patches; do not patch source checkouts in place.

  | Project | Verified commit |
  | --- | --- |
  | `external/testng` | `7d03e9745613c3e46e9af47afbf91be445f53403` |
  | `external/snakeyaml` | `d971be9389db578ce6c6805f566c0261a27cc503` |
  | `external/guice` | `30203d0536ebb60ce6d60c291e93bd658558a1d3` |
  | `external/jsr330` | `bd6043d83744a331fe1cf5336cfcf15051b36854` |

  JCommander, JUnit and Guava are already restored; `soong_zip` is a retained
  upstream build tool. No host tests, TestNG or dependency-injection libraries
  are added to recovery packages.

- Retained `libhardware_headers` exports `libaudio_system_headers` and
  `libbluetooth-types-header` for its non-recovery variants. Restore their real
  AOSP definitions without changing libhardware's variant/exclusion rules:

  | Project | Verified commit | Checkout scope |
  | --- | --- | --- |
  | `system/media` | `612d1707ddd53b341512a8de9b3255c314e7c0b2` | Root Blueprint/license/metadata and complete `audio` and `audio_utils` subtrees |
  | `system/bt` | `9827945fd41eb3c7940b5ce983e21757fdbae5f6` | Complete project, preserving original type library/test declarations, defaults, Soong plugin, generators and inputs |

  Both use `android-12.1.0_r4`. The audio headers use retained `libcutils_headers`.
  Bluetooth's original `types` Blueprint also declares libraries/tests using
  project-wide defaults, so it is not rewritten as a header-only substitute.
  Source restoration does not add audio/Bluetooth services or tests to recovery
  packages, and does not prove a full native build or hardware compatibility.

- Retained `icu4j-tests` needs `junit-params`. Restore the complete
  `external/junit-params` project from `android-12.1.0_r4`, pinned to
  `fa8720eb57ec6d8fe8fdfd7c74e581f094fd9219`, keeping the original host/target
  definitions, license, Android fixes/ignores, test sources, CSV resources and
  test-only AssertJ 1.7.1 JAR (SHA256 checked). It uses the already restored JUnit;
  no ICU declarations are changed and no test libraries are added to recovery.
  Standalone compilation covers all 45 library and 39 test Java sources. Of 206
  original test executions, one exact-message assertion expects pre-4.13 JUnit
  text; retained JUnit adds an `InvalidTestClassError` prefix. That difference
  and valid/invalid rule handling are checked separately without editing source
  or adding ignores. These checks do not prove a full Soong/ICU build or boot.

- Retained headtracking, bsdiff, AV audio and signapk also need real native and
  signing libraries. Restore complete projects at `android-12.1.0_r4`:

  | Project | Verified commit |
  | --- | --- |
  | `external/eigen` | `c5a628e442d5a093b9f9d7179ac090738f4e093d` |
  | `external/libdivsufsort` | `83ef56609ee34fcddb21571d377f58af34c14f64` |
  | `tools/apksig` | `c2b69bcc45dfac3a745e5f2fefcec42594dddb6c` |
  | `external/speex` | `6af04891263cf41d54b47121d604c168a0846c86` |
  | `external/google-benchmark` | `770b190cd0052a180fe161abad59b4cbdfd99d46` |

  Keep Eigen's original BLAS declarations and both divsufsort index widths.
  Expand the same pinned `system/media` checkout with complete `audio_utils`,
  including its tests/fuzzers/benchmarks. `libsndfile` here is its original
  `tinysndfile.c`, not a separate external project. Speex supplies the Android
  resampler dependency; Soong's `cc_benchmark` linker implicitly needs
  `libgoogle-benchmark`. Original Conscrypt host/JNI/generator and audio
  core/log/base/gtest dependencies remain retained, not replaced by stubs.
  No test/benchmark packages are added to recovery and no missing-dependency
  bypasses or upstream Blueprint edits are used.

  Standalone apksig compilation/tests exercise the original signing/verifying
  fixtures: 340 runs, two upstream assumptions and one documented Java 17
  provider issue-code mismatch. The corrupt RSA APK is still rejected (provider
  returns false instead of throwing); all three DSA/RSA/ECDSA bad-signature
  fixtures are checked independently. No test edits or added ignores. Modern
  host compilers also diagnose an old uninstantiated Eigen template; local
  native smoke uses delayed template parsing, without changing Android build
  flags/source. These host checks do not prove full Soong/ARM variants, the
  apksigner Conscrypt JNI build, image boot or hardware compatibility.

- Retained Bluetooth Rust/native declarations and host tools require another
  52 complete source projects from `android-12.1.0_r4`: 43 Rust crate projects
  and the nine projects below. Every commit is checked by the workflow's
  `RUST_NATIVE_PROJECTS` table. Keep original nested Blueprints, licenses,
  proc macros, generator inputs, tests, fuzzers and benchmarks; do not substitute
  Cargo/Maven downloads or trim upstream declarations to hide missing modules.

  | Project | Verified commit |
  | --- | --- |
  | `external/opencensus-java` | `19de7b296c7c1b6c4563fab8f22b5c6f15d86498` |
  | `external/libusb` | `b103c6be096fc0f1b0114188430e3ff5d39fdc35` |
  | `external/flatbuffers` | `04d4e06804470e451b7f67d1c07c614a66f5e03b` |
  | `external/python/pybind11` | `960c6f3b4ca0b7ac3d6178bd76cbcb7687ad5173` |
  | `external/nanopb-c` | `2bbb09319b1aa6bd55791ccb19caf822b75de0c2` |
  | `external/rust/cxx` | `e21664011d153978e59171e636aa8520a4153440` |
  | `system/testing/gtest_extras` | `95cc749048a53521688b68ee1d0b34c5db8be4c3` |
  | `tools/dexter` | `093604d5f4ac95f1e63296014483325e8cf063a7` |
  | `external/escapevelocity` | `b76828a75424a8cc000192440488f4f26966dd59` |

  The crate set covers bytes, numeric derives, paste, serde/JSON, futures,
  Tokio, parking_lot, protobuf, grpcio and their explicit transitive crates,
  macros and CXX diagnostic dependencies. Original CXX bridge generator/demo,
  grpc bindgen/native wrapper and generated `OUT_DIR` inputs are preserved.
  Libusb/FlatBuffers retain their **upstream** empty root `Android.mk` sentinels
  that prevent recursive discovery of NDK sample Makefiles; these are not local
  placeholder modules. Nanopb is the actual `external/nanopb-c` project.

  The same pinned CTS checkout also includes complete `libs/json/` for
  `jsonlib`, without dropping install/shim/staged-install or harness scopes.
  OpenCensus uses the original AutoValue processor and EscapeVelocity sources;
  retained grpc Context, native gRPC and Python protobuf declarations are
  checked rather than replaced. No host tools/tests are added to recovery.

  Local input auditing checks 9,540 selected tracked files and 74 unchanged
  Blueprints across these restores and the expanded CTS/Auto scopes. Standalone
  Java compilation runs the real AutoValue processor to generate OpenCensus
  classes and exercises CTS JSON streaming. Slicer/Dexter matches 102 original
  golden outputs under ASAN; nanopb compiles four configurations and libusb's
  ten Linux sources compile **without running USB APIs**. Nanopb's Python 2
  generator/example runtime and full Android/native linking remain untested.

  Host incompatibilities are recorded, not patched away: modern Clang rejects
  FlatBuffers' original deleted copy assignment at `flatbuffers.h:1875`;
  stable Rust 1.99 cannot compile the retained proc-macro2's old nightly API,
  and slab's original deny-warnings catches a newer lifetime lint. Thirty-three
  selected Rust modules compile locally with literal Blueprint flags/features;
  this is not a full Rust/Soong build, grpc bindgen or CXX final-link result.
  None of these standalone checks proves Soong closure, ARM variants or boot.

- Retained ART disassembly, USB accessory host tests, installd flag tests and
  MIDI wrappers also need these four **complete**, pinned source projects from
  `android-12.1.0_r4` (the `ART_MIDI_PROJECTS` workflow table):

  | Project | Verified commit |
  | --- | --- |
  | `external/vixl` | `eea8abec9ea365f30ac09461a6133077d34f5ca2` |
  | `external/tinyalsa` | `5638a6e1d1a5775c9d064948e68ac40722814b31` |
  | `external/sonivox` | `39d4c3efe8f0c379c77305d0cf83a1ae480f2930` |
  | `system/server_configurable_flags` | `cf0231f8f5c03f9c83a5a972cfbaa410782a63f4` |

  VIXL keeps original ART-only visibility, ARM/T32/A64 codegen, simulator,
  debug/release defaults, test runner and nonempty root `Android.mk` test target.
  The retained ART plugin implements `art_cc_defaults`/`art_cc_library`, and its
  `dex2oat-pgo-defaults` explicitly allows `external/vixl`; these are checked,
  not recreated or widened. Tinyalsa is `external/tinyalsa`, not `tinyalsa_new`:
  its seven library sources and five CLI declarations remain unchanged.
  Sonivox keeps nested license/Blueprints, without-JET and JET libraries,
  ARM assembly and original tests/configuration. Server flags keep their library,
  tests and `flags_health_check` binary/init RC. Nothing here adds host tools or
  tests to recovery packages, runs device hooks or relaxes missing dependencies.

  Local input auditing checks all 3,419 tracked files, eight unchanged Blueprints
  and 26 declarations, including licenses, source/include/test/RC inputs and
  direct retained `libbase`/`libcutils`/`liblog`/license/ART defaults declarations.
  Standalone Clang 23 checks are **partial, not passes**: 14/25 selected VIXL
  library sources compile; old `std::iterator`, boolean-bitwise and constant
  conversion diagnostics stop the rest under original `-Werror`. Ten of twelve
  tinyalsa library/CLI sources compile; `pcm.c` hits a newer one-bit bit-field
  diagnostic and `tinycap.c` lacks the Android `__unused` macro on this host.
  No VIXL runner, disassembler example or tinyalsa helper/CLI runtime was run.
  Sonivox standalone compilation stops at its original external framework
  `media/MediaPlayerInterface.h` include; no synthetic header is supplied.
  Server flags receive input/declaration auditing only: no native build/tests,
  property writes, boot-failure/reset hooks or audio device operations are run.
  Sources and diagnostic flags are unchanged; none of these local checks proves
  Android compiler compatibility, Soong/ARM variants, final linking or boot.

- Retained `libsimpleperf_etm_decoder` requires the complete case-sensitive
  `external/OpenCSD` project at `bec745a24a3c9657ae5726e7b307760e69bdc288`
  from `android-12.1.0_r4`. Keep the upstream private/default and explicit
  CTS/simpleperf consumer visibility, exception/RTTI flags, source globs,
  BSD/GPL license metadata, C API, offline snapshots/tests and `TEST_MAPPING`.
  The workflow checks the pin, library/license/consumer declarations and
  representative inputs; no new tests/tools are installed into recovery and
  no perf or device trace collection is run.

  Local auditing checks all 737 tracked files and the unchanged Blueprint;
  36 actual workflow guard cases reject wrong pins/URLs/branches/modules or
  missing source/header/license/test/snapshot/consumer inputs. All 42 original
  Blueprint-selected C++ sources compile on Clang 23, but a whole-archive link
  **fails**: the original Blueprint omits `decoder/source/ete/trc_cmp_cfg_ete.cpp`,
  leaving `ETEConfig::ETEConfig(const ocsd_ete_cfg*)` unresolved. The upstream
  Linux Makefile does include ETE; the Android Blueprint is not patched here.
  This is a recorded original input/link limitation, not a passing library
  build or a proven host-only incompatibility. No C API/offline test, CTS,
  simpleperf integration, Soong/ARM final link or boot result is claimed.

- Retained Bionic `libc_jemalloc_wrapper` and `hwbinder.stubs` need two more
  **complete**, pinned projects from `android-12.1.0_r4`:

  | Project | Verified commit |
  | --- | --- |
  | `external/jemalloc_new` | `6d4d27fd2651ed114386b89c2d251b816a849460` |
  | `frameworks/libs/modules-utils` | `0a8bde0eb27a5de62e73faf9de06a498a4ccec69` |

  In this AOSP version, `framework-annotations-lib` is declared in
  `frameworks/libs/modules-utils/java/Android.bp`, **not** `frameworks/base`.
  The minimal manifest removes that project. Restore its original annotation
  filegroups/library, `core_current` API level and visibility, native SDK header,
  Java/AIDL helpers, test/coverage/build-helper modules and instrumentation
  manifest unchanged; do not manufacture an annotation module in framework.
  Their direct AndroidX/platform/Tradefed/base/license dependencies are retained.

  Jemalloc keeps its original variable-based flags, 30 library sources, JET,
  unit/integration/stress lists, checked-in Bionic/host configuration and headers,
  licenses, recovery/ramdisk variants, `linux_bionic_supported` defaults and
  `libc_headers`. No allocator replacement, tcache/arena tuning, diagnostic
  suppression, upstream edits or recovery test packages are introduced.

  Local audits check all 429 tracked files, ten unchanged Blueprints and 23
  declarations. Explicit expansion of jemalloc's nine original variables and
  list/map/concatenation inputs is limited to this file, **not** a Soong evaluator.
  All 185 selected base/JET/test-library/test-source compilations succeed on
  Clang 23/glibc with the checked-in host configuration; the base library also
  passes a whole-archive host link. No allocator executables/tests are run or
  preloaded. All 76 original annotation-filegroup sources compile with Java 8
  APIs, and ten custom metadata/default/consumer assertions pass. The other
  modules-utils helpers/native header/instrumentation tests receive input and
  declaration checks only. The 93 actual workflow guard cases reject wrong
  pins/URLs/branches/modules or missing inputs/retained declarations. None of
  these checks proves Android global compiler flags, Bionic/ARM/Soong variants,
  complete helper/test builds, final image linking or hardware boot.

- Before building this profile, an advisory read-only scan reports literal
  defaults references without literal definitions, capped at 200 candidate names.
  A separate scan reports library/tool reference candidates, with the same cap.
  `source-defaults-report.json` and `source-libraries-report.json` are retained
  with build diagnostics. These scans are **not
  Soong evaluation**: namespaces, generated modules, variants, types and dynamic
  Blueprint expressions are not resolved. It never suppresses modules, edits
  sources or enables missing-dependency bypasses; the strict build is authoritative.
- Safety variables are sourced before lunch, when OrangeFox snapshots its build
  environment. Do not upload that environment snapshot: it may contain CI secrets.
- The workflow validates the encoded boot ramdisk and the published image, rejects
  ZIP installers, and publishes a **prerelease** with `SHA256SUMS` and boot-test notes.
- Build logs are retained as a diagnostics artifact even on failure.

This is for temporary `fastboot boot` testing, **not flashing/installing**. Build
and image checks do not prove hardware boot, touch, USB, reboot or FBE compatibility.

 # Note
* This action will now only support manifest 12.1 and 11.0, since all orangefox manifest below 11.0 are considered obsolete.
* Make sure your tree uses right variable (updated vars) from OrangeFox; [fox_11.0](https://gitlab.com/OrangeFox/vendor/recovery/-/blob/fox_11.0/orangefox_build_vars.txt) and [fox_12.1](https://gitlab.com/OrangeFox/vendor/recovery/-/blob/fox_12.1/orangefox_build_vars.txt), to avoid build erros.
