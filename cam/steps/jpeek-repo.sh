#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2021-2025 Yegor Bugayenko
# SPDX-License-Identifier: MIT
set -e
set -o pipefail

repo=$1
pos=$2
total=$3

start=$(date +%s%N)

project=${TARGET}/github/${repo}

logs=${TARGET}/temp/jpeek-logs/${repo}

if [ -e "${logs}" ]; then
    echo "Repo ${repo} already analyzed by jPeek"
    exit
fi

mkdir -p "${logs}"

build() {
    failure_log="${TARGET}/temp/jpeek_failure.log"
    success_log="${TARGET}/temp/jpeek_success.log"
    if [ -e "${project}/gradlew" ]; then
        echo "Building ${repo} (${pos}/${total}) with Gradlew..."
        if ! timeout 1h "${project}/gradlew" classes -q -p "${project}" > "${logs}/gradlew.log" 2>&1; then
            echo "Failed to compile ${repo} using Gradlew$("${LOCAL}/help/tdiff.sh" "${start}")"
            echo "Failure ${repo} Gradlew" >> "${failure_log}"
            exit
        fi
        echo "Compiled ${repo} using Gradlew$("${LOCAL}/help/tdiff.sh" "${start}")"
        echo "Success ${repo} Gradlew" >> "${success_log}"
    elif [ -e "${project}/build.gradle" ]; then
        echo "Building ${repo} (${pos}/${total}) with Gradle..."
        echo "apply plugin: 'java'" >> "${project}/build.gradle"
        if ! timeout 1h gradle classes -q -p "${project}" > "${logs}/gradle.log" 2>&1; then
            echo "Failed to compile ${repo} using Gradle$("${LOCAL}/help/tdiff.sh" "${start}")"
            echo "Failure ${repo} Gradle" >> "${failure_log}"
            exit
        fi
        echo "Compiled ${repo} using Gradle$("${LOCAL}/help/tdiff.sh" "${start}")"
        echo "Success ${repo} Gradle" >> "${success_log}"
    elif [ -e "${project}/pom.xml" ]; then
        echo "Building ${repo} (${pos}/${total}) with Maven..."
        if ! timeout 1h mvn compile -quiet -DskipTests -f "${project}" -U > "${logs}/maven.log" 2>&1; then
            echo "Failed to compile ${repo} using Maven$("${LOCAL}/help/tdiff.sh" "${start}")"
            echo "Failure ${repo} Maven" >> "${failure_log}"
            exit
        fi
        echo "Compiled ${repo} using Maven$("${LOCAL}/help/tdiff.sh" "${start}")"
        echo "Success ${repo} Maven" >> "${success_log}"
    else
        echo "Could not build classes in ${repo} (${pos}/${total}) (neither Maven nor Gradle project)"
        echo "Failure ${repo} Non-build" >> "${failure_log}"
        exit
    fi
}

collect() {
    timeout 1h java -jar "${JPEEK}" --overwrite --include-ctors --include-static-methods \
        --include-private-methods --sources "${project}" \
        --target "${TARGET}/temp/jpeek/all/${repo}" > "${logs}/jpeek-all.log" 2>&1
    timeout 1h java -jar "${JPEEK}" --overwrite --sources "${project}" \
        --target "${TARGET}/temp/jpeek/cvc/${repo}" > "${logs}/jpeek-cvc.log" 2>&1
}

declare -i re=0
until build; do
    re=$((re+1))
    echo "Retry #${re} for ${repo} (${pos}/${total})..."
done

start=$(date +%s%N)

if ! collect; then
    echo "Failed to calculate jPeek metrics in ${repo} (${pos}/${total}) due to jpeek.jar error$("${LOCAL}/help/tdiff.sh" "${start}")"
    exit
fi

accept="^(?!.*(index|matrix|skeleton)).*\.xml$"

values=${TARGET}/temp/jpeek-values/${repo}.txt
mkdir -p "$(dirname "${values}")"
echo > "${values}"
files=${TARGET}/temp/jpeek-files/${repo}.txt
mkdir -p "$(dirname "${files}")"
printf '' > "${files}"

skeleton="${TARGET}/temp/jpeek/all/${repo}/skeleton.xml"

xmlstarlet sel -t -m "//class" -v "@id" -n "$skeleton" | while read -r class; do
    static_count=$(xmlstarlet sel -t -v "count(//class[@id='$class']/methods/method[@static='true'])" "$skeleton")
        total_count=$(xmlstarlet sel -t -v "count(//class[@id='$class']/methods/method)" "$skeleton")
        if [ "$total_count" -gt 0 ]; then
        staticity=$(echo "scale=3; $static_count / $total_count" | bc)
    else
        staticity=0
    fi
    staticity=$(printf "%0.3f" "$staticity")
    package=$(xmlstarlet sel -t -v "//class[@id='$class']/ancestor::package/@id" "$skeleton" | tr '.' '/')
    jfile=$(find "${project}" -type f -path "*${package}/${class}.java" -exec bash -c 'realpath --relative-to="${1}" "$2"' _ "${project}" {} \;)
    if [ -n "$jfile" ]; then
        echo "${jfile}" >> "${files}"
        mfile=${TARGET}/measurements/${repo}/${jfile}.m.STAT
        mkdir -p "$(dirname "${mfile}")"
        echo "$staticity" > "${mfile}"
    fi
    echo "Class: $class, Staticity: $staticity"
done


echo "Analyzed ${repo} through jPeek (${pos}/${total}), \
$(sort "${files}" | uniq | wc -l | xargs) classes, \
sum is $(awk '{ sum += $1 } END { print sum }' "${values}" | xargs)$("${LOCAL}/help/tdiff.sh" "${start}")"
