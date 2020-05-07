
git clone --depth 1 ${GIT_CLONE_URL} /mnt/repo > /mnt/log.txt 2>&1

if [ $? -eq 0 ]
then
    echo "CLONE_OK"
else
    echo "CLONE_FAIL"
fi