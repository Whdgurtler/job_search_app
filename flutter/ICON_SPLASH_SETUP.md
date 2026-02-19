# App Icon and Splash Screen Setup

## Required Assets

### 1. App Icon
Create a square PNG image with the following specifications:
- **Size**: 1024x1024 pixels (will be scaled down automatically)
- **Format**: PNG with transparency
- **Location**: `assets/icons/app_icon.png`

For Android Adaptive Icons, also create:
- **Foreground**: `assets/icons/app_icon_foreground.png` (1024x1024)
  - Contains the main icon elements (center 768x768 safe zone)
  - Transparent background

### 2. Splash Screen
Create splash screen images:
- **Logo**: `assets/splash/splash_logo.png` (1024x1024 recommended)
  - Your app logo/branding centered
- **Dark Mode**: `assets/splash/splash_logo_dark.png` (1024x1024)
  - Same logo optimized for dark backgrounds

## Design Guidelines

### App Icon Best Practices:
- Use simple, recognizable design
- Avoid text (hard to read at small sizes)
- Ensure it looks good at all sizes (16px to 512px)
- Use branded colors
- Test on both light and dark backgrounds

### Splash Screen Best Practices:
- Keep it simple and fast to load
- Use your brand colors
- Center the logo
- Don't overcrowd with information

## Quick Start with Placeholder Icon

For testing, you can use a simple placeholder. Run this PowerShell script to create a basic icon:

```powershell
.\create_placeholder_icon.ps1
```

Or design your own in:
- **Figma** (recommended): https://www.figma.com/
- **Canva**: https://www.canva.com/
- **Adobe Illustrator**
- **Inkscape** (free)

## Generate App Icons and Splash Screens

Once you have your assets in place:

### Step 1: Install dependencies
```bash
flutter pub get
```

### Step 2: Generate launcher icons
```bash
flutter pub run flutter_launcher_icons
```

This will create:
- Android: `android/app/src/main/res/mipmap-*/ic_launcher.png`
- iOS: `ios/Runner/Assets.xcassets/AppIcon.appiconset/`

### Step 3: Generate splash screens
```bash
flutter pub run flutter_native_splash:create
```

This will create:
- Android: `android/app/src/main/res/drawable*/launch_background.xml`
- iOS: `ios/Runner/Base.lproj/LaunchScreen.storyboard`

## Verification

After generation:
1. Check the generated files exist
2. Run the app: `flutter run`
3. Verify the icon appears correctly on home screen
4. Verify splash screen shows during app startup

## Color Customization

Edit the configuration files to change colors:
- **Launcher Icons**: `flutter_launcher_icons.yaml`
- **Splash Screen**: `flutter_native_splash.yaml`

## Icon Templates

Download icon templates:
- **Android**: https://developer.android.com/develop/ui/views/launch/icon_design_adaptive
- **iOS**: https://developer.apple.com/design/resources/

## Common Issues

### Icons not updating
- Uninstall the app completely
- Clean build: `flutter clean && flutter pub get`
- Rebuild: `flutter run`

### Wrong colors
- Check configuration files
- Regenerate: `flutter pub run flutter_launcher_icons`

### Splash screen shows too long
- This is normal in debug mode
- Test in release mode: `flutter run --release`
