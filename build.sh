BLUE_BOLD='\033[1;34m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo -e "${BLUE_BOLD} > Emptying 'dist' dir${CYAN}"
rm -rf dist/*

echo -e "${BLUE_BOLD} > Generating MCMEL Binary${CYAN}"
pyinstaller main.py --onefile --windowed --name=mcmel

echo -e "${BLUE_BOLD} > Copying required folders and files${CYAN}"
mkdir -p dist/assets/images && cp -r assets/images/* dist/assets/images/
mkdir -p dist/assets/ui && cp -r assets/ui/* dist/assets/ui/
#mkdir -p dist/assets/icons && cp -r assets/icons/* dist/assets/icons/
cp games_config_example.json dist/games_config.json

# echo -e "${BLUE_BOLD} > Generating MCMEL Flatpak${CYAN}"
# flatpak run org.flatpak.Builder --force-clean --sandbox --user --install --install-deps-from=flathub --ccache --mirror-screenshots-url=https://dl.flathub.org/media/ --repo=repo builddir manifest.yml
echo -e "${BLUE_BOLD} > Build finished!${RESET}"