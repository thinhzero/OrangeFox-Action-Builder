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
