# Thyme / PixelOS 17 — local review

Reviewed on 2026-11-16. This document records local findings, not a successful
Android build or a hardware boot result. The original paused-review findings
below are historical. The owner subsequently authorized fixes, pushes and CI.

## Authorized follow-up

- The device tree now prepares a guarded fix for a reproduced null-CRTC crash
  in OrangeFox DRM initialization. Host tests do not establish hardware boot.
- Deploy the already-reviewed eight-project restoration and sanitized diagnostics.
- Run the real `m nothing` graph check before `mka adbd bootimage`; retain both
  stages in the sanitized build log. No missing-dependency bypass is enabled.
- Inspect actual CI errors before selecting further source changes. The full
  non-pruned checkout remains an alternative, not an already completed sync.

## What is established

### 1. The repeated CI failures and black screen are different problems

CI #37 (`43802473224`, builder commit
`bc0304a422d03f934601a813db607c05e82667ea`) passed its source restoration step
but failed during Soong dependency resolution, before creating an image. Its
eight undefined modules belong to seven AOSP projects:

| Undefined module | Missing project |
| --- | --- |
| `libphonenumber-platform` | `external/libphonenumber` |
| `java_api_finder` | `tools/apifinder` |
| `libwebp-decode`, `libwebp-encode` | `external/webp` |
| `libsfntly` | `external/sfntly` |
| `libdng_sdk` | `external/dng_sdk` |
| `libjpeg` | `external/libjpeg-turbo` |
| `libpiex` | `external/piex` |

The `twrp-12.1` manifest uses AOSP `android-12.1.0_r4` and includes
`remove-minimal.xml`. That file explicitly removes all seven providers, while
retaining their consumers in `frameworks/base`, `external/conscrypt` and
`external/skia`. Apifinder's lint prebuilt project is removed too. All 116
destinations in the current local restoration inventory were explicitly removed
by that minimal manifest; CI #37 contained the earlier 108-destination version.

The OrangeFox 12.1 sync patch exports `ALLOW_MISSING_DEPENDENCIES=true` in
`build/envsetup.sh`. This profile deliberately unsets both missing-dependency
bypasses. Blueprint's `ResolveDependencies()` validates dependencies of **all
parsed modules**, not just the modules copied into the boot ramdisk. This
explains why even retained test/documentation/framework declarations cause
successive strict-graph failures. Removing packages from this device product
alone does not establish that the global graph will resolve.

The mistake was repeatedly restoring the next reported provider and dispatching
CI without first resolving this manifest/strict-graph mismatch. The existing
local eight-project restoration is retained for review, not selected as the
next CI plan. A literal-reference scan and host compilation are not substitutes
for the real Soong graph or Android compile/link stages.

### 2. Tree/runtime review does not establish a black-screen fix

The reported black-screen image is CI #6, SHA256
`e653ea4fff224dee5a885df2b402fd91dc4f2c5ae361d68771824ab56b46f9f9`.
It contains the stock 4.19.157 kernel, not the kernel from the specified PixelOS
ROM. It already has `twrpfastboot=1`; adding that marker is **not** a new fix.
Its `/init` symlink and the tree's Qualcomm/USB startup files were checked.

The `fox_12.1-aosp` tree selects the unchanged PixelOS kernel
`4.19.325-perf-g526b147b5def`, source commit
`526b147b5defadc91d52c464c7dc473a013a4e76`. Boot remains header v3;
the installed matching `vendor_boot`/DTB and DTBO must remain unchanged.
Temporary boot mode disables ZIP generation and current-recovery reflashing.
No device flash, data format, vbmeta change or encryption/VINTF bypass is part
of this review.

One apparent display issue was checked rather than patched: the embedded
IKCONFIG says `CONFIG_DRM_MSM` is unset, but this kernel's
`techpack/display/Makefile` includes `config/konadisp.conf` for
`CONFIG_ARCH_KONA=y`. That file explicitly exports `CONFIG_DRM_MSM=y`,
`CONFIG_DRM_MSM_SDE=y` and `CONFIG_DRM_MSM_DSI=y`. The prebuilt image also
contains the associated MSM/SDE/DSI strings. Therefore the IKCONFIG line alone
does **not** establish that Qualcomm display support is missing or that a
display module needs to be copied into recovery. This is a source/static
finding, not proof of successful driver initialization on PixelOS.

The old hardware log showing OrangeFox DRM at 1080×2340 belongs to RyuOS using
its retained ROM kernel. It cannot be used as PixelOS boot evidence. The
ramdisk overlay model, startup ELF/symbol checks and 73 host regression tests
pass within their documented scope, but do not identify the runtime hang.
There is still no recovery/pstore log from the PixelOS black-screen attempt.

## Diagnostics credential exposure and local mitigation

Raw Soong logs record exported environment values. The five retained, extracted
diagnostic sets that were examined each contain an unmasked **job token** in
`out/soong.log`. No match to the two owner-provided credentials was found in
those examined files. This is not a scan of every remote artifact or a general
secret audit. Values are not reproduced here. According to GitHub, the job token
expires when its job finishes; that does not make publishing it acceptable.

The local workflow changes:

- remove the job-level token environment variable and disable checkout credential
  persistence;
- unset `GITHUB_TOKEN` and `GH_TOKEN` before building;
- pass the token directly to the two release actions instead;
- stage only bounded allowlisted diagnostic files, omit Soong environment dumps
  and redact recognized credentials;
- reject symlink/oversized inputs and stale staging; skip upload if preparation
  fails, including after partial staging.

Seventeen synthetic regressions and a replay on real CI #37 diagnostics pass.
The replay preserves all eight original error messages, excludes raw Soong logs
and contains none of the five observed job-token values or the two known owner
credentials. All nine embedded shell steps pass `bash -n`; YAML and Python
syntax checks pass. The sixteen existing literal-scanner tests also pass.

These changes are **not deployed**: no commit, push or CI dispatch is implied.
The job still has `contents: write`; this patch is not an isolation boundary
against arbitrary actions or malicious build code. No remote artifact was
deleted and no repository/account permission was changed.

## GitHub account concern

The final read-only repository check still shows no active runs, CI #37 as the
latest completed failure, and remote `main` unchanged at `bc0304a`. No CI #38 was
started. The repository is public; GitHub documents standard hosted-runner
compute for public repositories as free. Its limits documentation says hitting
a limit normally cancels the workflow/job, not that a particular number of
build attempts automatically bans an account. These facts do **not** verify
account-wide enforcement, abuse review or billing status, and are not a
guarantee against future restriction. Further hosted builds remain paused.

## Proposed build direction — requires a separate decision

Do not continue the loop of “one missing module, one CI run.” Keep strict
dependency checks and all current boot-test safety restrictions.

The preferred investigation is a separate, revision-pinned **non-pruned 12.1
source checkout** preserving the same TeamWin/OrangeFox replacements, recovery
branch and device tree. Resolve the source inventory and actual Soong graph
locally before requesting a hosted build. Start with the real graph-generation
check (`m nothing`), then the exact `mka adbd bootimage` target only after that
passes. Neither check has been run against such a checkout yet.

This is a proposal, not an instruction to remove `remove-minimal.xml` from the
existing checkout or sync hundreds of projects immediately. A full source tree
needs a disk/RAM/network budget; local `/tmp` is almost full and the data disk
has about 100 GiB free at review time. A new full checkout has not been approved
or shown to fit, and the hosted runner's capacity must be checked separately.

An exact dependency-closed subset could be smaller, but it must be established
using the actual Soong graph, including generated/variant dependencies. The
current literal scanner cannot certify that closure. No stub modules, deleted
upstream declarations, relaxed validator or missing-dependency bypass should be
used to claim success.

Even after a build succeeds, validate the actual final image and checksum before
any separately authorized hardware test. Until that test produces logs, do not
claim that the kernel change fixes the black screen or assign a boot percentage.

## References

- [CI #37](https://github.com/thinhzero/OrangeFox-Action-Builder/actions/runs/43802473224)
- [12.1 minimal-manifest removals](https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp/blob/twrp-12.1/remove-minimal.xml)
- [OrangeFox 12.1 build patch](https://gitlab.com/OrangeFox/sync/-/blob/master/patches/patch-manifest-fox_12.1.diff)
- [Blueprint dependency resolution](https://android.googlesource.com/platform/build/blueprint/+/refs/tags/android-12.1.0_r4/context.go)
- [Pinned kernel display Makefile](https://github.com/Flicker-Android-Devices/kernel_xiaomi_sm8250/blob/526b147b5defadc91d52c464c7dc473a013a4e76/techpack/display/Makefile)
- [Pinned Kona display configuration](https://github.com/Flicker-Android-Devices/kernel_xiaomi_sm8250/blob/526b147b5defadc91d52c464c7dc473a013a4e76/techpack/display/config/konadisp.conf)
- [GitHub job token lifetime](https://docs.github.com/en/actions/concepts/security/github_token)
- [GitHub Actions limits](https://docs.github.com/en/actions/reference/limits)
- [GitHub Actions billing](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions)
