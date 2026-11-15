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
  metadata and complete `common`/`service` subtrees. The unrelated AutoValue and
  AutoFactory declarations are not selected; no upstream Blueprint is edited.
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
