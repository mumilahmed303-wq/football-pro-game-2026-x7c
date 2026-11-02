# FOOTBALL PRO — Android starter project

## What is included
- `main.py`: playable offline football prototype using Kivy.
- `buildozer.spec`: Android package settings.
- `.github/workflows/build-apk.yml`: GitHub Actions workflow that builds a debug APK.

## Build from your phone (no computer)
1. Create/sign in to a GitHub account in your phone browser.
2. Create a new **public** repository named `football-pro` (public repositories allow GitHub Actions on the free plan).
3. Upload the contents of this ZIP to the repository root. Make sure `.github/workflows/build-apk.yml` keeps its folders.
4. Open the repository's **Actions** tab and enable workflows if GitHub asks.
5. Run **Build Android APK** using **Run workflow**, or push a commit.
6. Wait for the green check mark. Open the completed workflow run, scroll to **Artifacts**, and download `FOOTBALL-PRO-debug-apk`.
7. Extract the downloaded artifact ZIP. Install the `.apk` on your HONOR phone. Android may ask you to allow installation from that browser/file manager.

## Notes
- This is an early 2D prototype, not an eFootball-level game yet.
- The first build can take several minutes because Android build tools are downloaded.
- Debug APK is for testing/sharing. A release APK should be signed before public distribution.
- If the build fails, open the failed Actions run and share the last error lines so the workflow can be corrected.
