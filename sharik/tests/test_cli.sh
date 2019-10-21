#!/bin/bash
set -x

TMP_PATH_1=$(mktemp -d)
TMP_PATH_2=$(mktemp -d)

ls -la "${TMP_PATH_1}" "${TMP_PATH_2}"

UNIQUE="this is a long string that's supposed to be unique"

mkdir -p "${TMP_PATH_1}"/bar
mkdir -p "${TMP_PATH_1}"/buzz
mkdir -p "${TMP_PATH_2}"
echo "${UNIQUE}" > "${TMP_PATH_1}"/test.txt
echo "world" > "${TMP_PATH_1}"/bar/doo
echo "mundo" > "${TMP_PATH_1}"/bar/moon
echo "buddie" > "${TMP_PATH_1}"/buzz/woop 

K1="inl"
V1="pica"
K2="bar/moo"
V2="shoo"

sharik -x --command foo --add "${TMP_PATH_1}" \
    --inline "${K1}=${V1}" --inline "${K2}=${V2}" --clear-glob 'test.txt' \
    -o "${TMP_PATH_2}"/sharik.sh

cat "${TMP_PATH_2}"/sharik.sh

if ! grep "${UNIQUE}" "${TMP_PATH_2}"/sharik.sh; then
    echo "Not encoded clearly"
    exit -1
fi

pushd "${TMP_PATH_2}"
bash sharik.sh
rm -f sharik.sh
popd

if [ $(cat "${TMP_PATH_2}/${K1}") != "$V1" ]; then
    exit -2
fi


if [ $(cat "${TMP_PATH_2}/${K2}") != "$V2" ]; then
    exit -3
fi

rm -rf "${TMP_PATH_2}/${K1}" "${TMP_PATH_2}/${K2}"

if  diff -r "${TMP_PATH_1}" "${TMP_PATH_2}"; then
    exit -4
fi


rm -rf "${TMP_PATH_1}" "${TMP_PATH_2}"