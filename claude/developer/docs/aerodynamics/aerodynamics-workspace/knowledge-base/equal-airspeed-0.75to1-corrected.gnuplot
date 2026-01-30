#!/usr/bin/gnuplot

set term pngcairo size 1000,1000 font "Arial,18"
set output 'equal-airspeed-0.75to1-corrected.png'

set title "Equal Airspeeds - 0.75:1 T/W Aircraft" font "Arial,28"
set xlabel ""
set ylabel ""

unset border
unset xtics
unset ytics
set key off

set xrange [-2:6]
set yrange [-2:8]

set size ratio -1

# Origin point
ox = 0
oy = 0

# Arrow length
len = 5

# 0% throttle - -5.7 degrees (glide angle)
ang0 = -5.7
set arrow from ox,oy to ox+len*cos(ang0*pi/180),oy+len*sin(ang0*pi/180) lw 6 lc rgb "blue" head filled
set label "0% Throttle" at ox+len*cos(ang0*pi/180)+0.3,oy+len*sin(ang0*pi/180)-0.5 font "Arial,16" tc rgb "blue"
set label "-5.7° glide" at ox+len*cos(ang0*pi/180)+0.3,oy+len*sin(ang0*pi/180)-0.9 font "Arial,14" tc rgb "blue"

# 50% throttle - 16.0 degrees (symmetry point)
ang50 = 16.0
set arrow from ox,oy to ox+len*cos(ang50*pi/180),oy+len*sin(ang50*pi/180) lw 6 lc rgb "green" head filled
set label "50% Throttle" at ox+len*cos(ang50*pi/180)+0.3,oy+len*sin(ang50*pi/180) font "Arial,16" tc rgb "green"
set label "16.0° (symmetry)" at ox+len*cos(ang50*pi/180)+0.3,oy+len*sin(ang50*pi/180)-0.4 font "Arial,14" tc rgb "green"

# 100% throttle - 40.5 degrees
ang100 = 40.5
set arrow from ox,oy to ox+len*cos(ang100*pi/180),oy+len*sin(ang100*pi/180) lw 6 lc rgb "red" head filled
set label "100% Throttle" at ox+len*cos(ang100*pi/180)-1.5,oy+len*sin(ang100*pi/180)+0.3 font "Arial,16" tc rgb "red"
set label "40.5° climb" at ox+len*cos(ang100*pi/180)-1.5,oy+len*sin(ang100*pi/180)-0.1 font "Arial,14" tc rgb "red"

# Horizontal reference line
set arrow from -1,0 to 6,0 nohead dt 2 lw 2 lc rgb "gray"
set label "Level (0°)" at 5.2,-0.3 font "Arial,14" tc rgb "gray"

# Caption
set label "All maintaining same airspeed V" at -1.5,-1.5 font "Arial,20" tc rgb "black"
set label "Envelope width: 46.3°" at -1.5,-1.9 font "Arial,16" tc rgb "black"

plot NaN notitle
