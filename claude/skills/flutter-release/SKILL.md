---
name: flutter-release
description: Flutter release checklist — version bump, signing, build, and distribution for Android and iOS
---

Use this skill when the user is preparing a Flutter app release.

## Step 0 — Check for Flutter MCP

Check if the Dart MCP server is available (requires Dart 3.9+):

```bash
dart --version
```

**If Dart 3.9+ is available and MCP not yet added:**
```bash
claude mcp add --transport stdio dart -- dart mcp-server
```

**If Flutter MCP is active**, use its tools throughout this skill:
- `Code analysis & fixes` — run before building to catch all errors and warnings
- `Run tests` — execute the test suite and review results
- `Package search` — verify any new dependencies on pub.dev before adding
- `Code formatting` — ensure code is clean before release

---

## Step 1 — Version bump

In `pubspec.yaml`, bump `version: x.y.z+build`:
- Patch (`z`) for bug fixes
- Minor (`y`) for new features
- Major (`x`) for breaking changes
- Build number (`+build`) must increment on every release — Play Store and App Store both reject a re-used build number

```yaml
version: 1.4.2+18
```

## Step 2 — Environment / flavors check

Confirm the correct flavor/environment is targeted:
- Is the right `.env` / `config.dart` / `flavor` active?
- Are API endpoints pointing to production, not staging?
- Check `AndroidManifest.xml` and `Info.plist` for any debug flags or test configs left in.

## Step 3 — Analysis and tests

If Flutter MCP is active, use `Code analysis & fixes` and `Run tests` tools.

Otherwise, run manually:
```bash
flutter analyze
flutter test
```

Zero errors and zero warnings required before proceeding.

## Step 4 — Build

### Android APK / AAB
```bash
# AAB for Play Store (preferred)
flutter build appbundle --release --obfuscate --split-debug-info=build/debug-info/android

# APK for direct distribution
flutter build apk --release --obfuscate --split-debug-info=build/debug-info/android
```

Verify signing config in `android/app/build.gradle` — `signingConfigs.release` must reference the keystore, not `signingConfigs.debug`.

### iOS IPA
```bash
flutter build ipa --release --obfuscate --split-debug-info=build/debug-info/ios
```

Verify in Xcode: Signing & Capabilities → correct provisioning profile and certificate for distribution, not development.

## Step 5 — Pre-release checks

- [ ] `flutter analyze` — zero errors, zero warnings
- [ ] `flutter test` — all tests pass
- [ ] Tested on a physical device (not just simulator)
- [ ] Tested on both Android and iOS if cross-platform
- [ ] No `debugPrint`, `print`, or `TODO` left in release-path code
- [ ] App icon and splash screen correct for this flavor
- [ ] Permissions in `AndroidManifest.xml` / `Info.plist` match what the app actually uses
- [ ] `--obfuscate` and `--split-debug-info` flags used (store the debug-info artifacts for crash symbolication)

## Step 6 — Distribution

**Play Store:**
1. Upload AAB to Google Play Console → Internal Testing first
2. Promote to Production after internal sign-off
3. Staged rollout recommended for major releases

**App Store:**
1. Upload IPA via Xcode Organizer or `xcrun altool`
2. Submit via App Store Connect → TestFlight first
3. App Review typically 1-3 days

## Common release failures

| Symptom | Cause | Fix |
|---|---|---|
| "Version code already used" | Build number not incremented | Bump `+build` in pubspec.yaml |
| Crash only in release build | Obfuscation removed a name relied on via reflection | Add `@pragma('vm:entry-point')` or check Proguard rules |
| Missing assets in release | `flutter clean` needed | Run `flutter clean && flutter pub get` before build |
| iOS signing error | Wrong profile type | Check Distribution vs Development in Xcode |
| Play Store rejects AAB | Min SDK too low | Check `minSdkVersion` in `build.gradle` |
