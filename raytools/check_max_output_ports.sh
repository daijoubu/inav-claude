#!/bin/sh

check_count() {
  pincount=`grep 'TIM_USE_OUTPUT_AUTO' target.c | wc -l`
  max=`awk '/MAX_PWM_OUTPUT_PORTS/ {print $3}' target.h`

  if [ "$pincount" -ne "$max" ]
  then
    pwd
    echo "pincount $pincount ne $max"
  fi
}


OLDPWD=`pwd`
for dir in src/main/target/*/
do
  cd $OLDPWD
  cd "$dir"
  check_count()
  cd $OLDPWD
done


