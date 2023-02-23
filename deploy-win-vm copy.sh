VM_SHARED_DIR="/Users/thomas/Shared/flowtutor"

echo "\033[0;32mBuilding installer...\033[0m"
source venv/bin/activate

envsubst < nsis/win_installer_light.cfg > win_installer.cfg
pynsist win_installer.cfg

rm -rf $VM_SHARED_DIR

echo "\033[0;32mCopying files...\033[0m"
cp -r ./build/nsis $VM_SHARED_DIR


echo "\033[0;32mCopied files to $VM_SHARED_DIR\033[0m"