#!/bin/bash
set -x

TMP_PATH_1=$(mktemp -d)
TMP_PATH_2=$(mktemp -d)

mkdir -p "${TMP_PATH_1}"/bar
mkdir -p "${TMP_PATH_1}"/buzz
echo "hello" > "${TMP_PATH_1}"/test.txt
echo "world" > "${TMP_PATH_1}"/bar/doo
echo "mundo" > "${TMP_PATH_1}"/bar/moo
echo "buddie" > "${TMP_PATH_1}"/buzz/woop 

K1="inl"
V1="pica"
K2="bar/moo"
V2="shoo"

sharik --command foo --add "${TMP_PATH_1}" --inline "${K1}=${V1}" "${K2}=${V2}" > "${TMP_PATH_2}"/sharik.sh
cat "${TMP_PATH_2}"/sharik.sh

pushd "${TMP_PATH_2}"
bash sharik.sh
rm -f sharik.sh
popd

if [ $(cat "${TMP_PATH_2}/${K1}") != "$V1" ]; then
    exit -1
fi


if [ $(cat "${TMP_PATH_2}/${K2}") != "$V2" ]; then
    exit -2
fi

rm -rf "${TMP_PATH_2}/${K1}" "${TMP_PATH_2}/${K2}"

if  ! diff -r "${TMP_PATH_1}" "${TMP_PATH_2}"; then
    exit -3
fi

rm -rf "${TMP_PATH_1}" "${TMP_PATH_2}"