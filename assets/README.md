# App icon

- `icon.icns` — compiled macOS icon, ready to install
- `icon.iconset/` — source PNGs at all required sizes (10 files)

## Regenerate from source

    python scripts/generate_icon.py assets/icon.iconset
    iconutil -c icns assets/icon.iconset -o assets/icon.icns

## Install into /Applications/MD Converter.app

    cp assets/icon.icns "/Applications/MD Converter.app/Contents/Resources/icon.icns"
    /usr/libexec/PlistBuddy -c "Set :CFBundleIconFile icon" "/Applications/MD Converter.app/Contents/Info.plist" 2>/dev/null || \
        /usr/libexec/PlistBuddy -c "Add :CFBundleIconFile string icon" "/Applications/MD Converter.app/Contents/Info.plist"
    xattr -cr "/Applications/MD Converter.app"
    codesign --force --deep --sign - "/Applications/MD Converter.app"
    touch "/Applications/MD Converter.app"; killall Dock; killall Finder
