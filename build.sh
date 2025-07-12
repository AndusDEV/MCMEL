echo "Emptying 'dist' dir"
rm -rf dist/*

echo "Generating MCMEL Binary"
pyinstaller main.py --onefile --windowed --name=mcmel

echo "Copying required folders and files"
mkdir -p dist/assets/images && cp -r assets/images/* dist/assets/images/
mkdir -p dist/assets/ui && cp -r assets/ui/* dist/assets/ui/
mkdir -p dist/assets/icons && cp -r assets/icons/* dist/assets/icons/
cp games_config_example.json dist/games_config.json

echo "Generating MCMEL Flatpak"
flatpak run org.flatpak.Builder --force-clean --sandbox --user --install --install-deps-from=flathub --ccache --mirror-screenshots-url=https://dl.flathub.org/media/ --repo=repo builddir manifest.yml