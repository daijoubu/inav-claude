#!/bin/sh


# Fri Dec 25 14:09:29 2020 +0100

start_date="2020-11-01"
end_date="2021-02-01"
needle_ref="ad5215920dc2a7cf5ff0704efb90961766649e9d"

echo "" > /tmp/script.out;
shas=$(git log --oneline --all --after="$start_date" --until="$end_date" | cut -d' ' -f 1)
for sha in $shas
do
    wc=$(git diff --name-only "$needle_ref" "$sha" | wc -l)
    wc=$(printf %04d $wc);
    echo "$wc $sha" >> /tmp/script.out
done
cat /tmp/script.out | grep -v ^$ | sort | head -5

