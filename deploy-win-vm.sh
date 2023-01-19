VM_USER=Thomas
VM_TYPE=fusion
VM_PATH="/Users/thomas/Documents/Virtual Machines.localized/Windows 10 x64.vmwarevm"
VM_DEV_DIR=C:\\Users\\Thomas\\Documents\\dev\\

if [ -z $VM_WARE_ENCRYPTION_KEY ]
then
    echo "\033[0;31mThe VM_WARE_ENCRYPTION_KEY environment variable is not set\033[0m"
    exit 1
fi

echo "\033[0;33mPlease enter password for $VM_USER on the VM:\033[0m"
read -s PASSWORD

echo "\033[0;32mBuilding installer...\033[0m"
source venv/bin/activate

pynsist win_installer.cfg

DIR_EXISTS=$(vmrun -vp $VM_WARE_ENCRYPTION_KEY -gu $VM_USER -gp $PASSWORD -T $VM_TYPE directoryExistsInGuest "$VM_PATH" ${VM_DEV_DIR}nsis)

if [[ $DIR_EXISTS == "The directory exists." ]]
then
    echo "\033[0;33mThe directory exists in the VM. Deleting...\033[0m"
    vmrun -vp $VM_WARE_ENCRYPTION_KEY -gu $VM_USER -gp $PASSWORD -T $VM_TYPE deleteDirectoryInGuest "$VM_PATH" ${VM_DEV_DIR}nsis
fi
echo "\033[0;32mCopying files...\033[0m"
vmrun -vp $VM_WARE_ENCRYPTION_KEY -gu $VM_USER -gp $PASSWORD -T $VM_TYPE copyFileFromHostToGuest "$VM_PATH" ./build/nsis ${VM_DEV_DIR}nsis