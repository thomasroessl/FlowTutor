NEW_FLOWTUTOR_VERSION=$(grep -Po '^version = "\K\d+\.\d+\.\d+(?=")' pyproject.toml)

git tag -a "v"$NEW_FLOWTUTOR_VERSION -m "Version "$NEW_FLOWTUTOR_VERSION | echo