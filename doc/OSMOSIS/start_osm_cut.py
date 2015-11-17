#!/usr/bin/env python
#coding=utf-8
# скрипт для разбиения файла OSM (.osm OR .pbf) на меньшие части
# с требуемой глубиной
# при глубине 1 заданная область делится на 4 равные части 
# при глубине 2 каждая из частей также делится на 4 части и т.д.

import os
import sys
import getopt

count = 0
depth = 0

help1="""
		Скрипт разбиения OSM или PBF файла нак части с требуемой глубиной
		Принимает имя файла вернюю, нижнюю, левую и правые границы и глубину
		разбиения. при глубине 1 заданная область делится на 4 равные части, 
		при глубине 2 каждая из частей также делится на 4 части и т.д.
"""

try:
	optlist, args = getopt.getopt(sys.argv[1:],'sf:t:l:b:r:d:')
	print optlist
	infile = filter(lambda item: item[0]=='-f',optlist)[0][1]
	top = float(filter(lambda item: item[0]=='-t',optlist)[0][1])
	left = float(filter(lambda item: item[0]=='-l',optlist)[0][1])
	bottom = float(filter(lambda item: item[0]=='-b',optlist)[0][1])
	right = float(filter(lambda item: item[0]=='-r',optlist)[0][1])
	depth = float(filter(lambda item: item[0]=='-d',optlist)[0][1])

except:
	print 'Usage %s [-s] -f <osm_file> -t <top> -l <left> -b <bottom> -r <right> -d <depth>' % sys.argv[0]
	exit(1)

if '-s' not in map(lambda item: item[0],optlist):
	print help1
				   
				   
#формируем словарь описания области карты
def get_area():
	global depth,top,left,bottom,right,infile
	area = {}
	area['top'] = top
	area['left'] = left
	area['bottom'] = bottom
	area['right'] = right
	area['depth'] = depth
	area['infile'] = infile
	return area

#делим область на 4 части и каждую часть еще на 4 и т.д. 
# пока не достигнем нужной глубины разбиения 
def split_four(area):
	print area
	if area['depth'] == 0:
		return
	delta_width = (area['right'] - area['left'])/2
	delta_height = (area['top'] - area['bottom'])/2
	area1 = area.copy()
	area1['bottom'] = area['bottom'] + delta_height
	area1['right'] = area['left'] + delta_width
	area1['depth'] -= 1
	area2 = area1.copy()
	area2['left'] += delta_width
	area2['right'] += delta_width
	area3 = area2.copy()
	area3['top'] -= delta_height
	area3['bottom'] -= delta_height
	area4 = area1.copy()
	area4['top'] -= delta_height
	area4['bottom'] -= delta_height
	for area_curr in [area1,area2,area3,area4]:
		osm_cut_area(area_curr)
	for area_curr in [area1,area2,area3,area4]:
		split_four(area_curr)

#разбиваем OSM файл на множество мелких в соответствии с заданной глубиной
def osm_cut_area(area):
	global count, depth
	count += 1
	
	infile = area['infile']
	top = area['top']
	left = area['left']
	bottom = area['bottom']
	right = area['right']
	
	command = ' '.join(['./osm_cut_box.py', '-f',infile, '-t',str(top), '-l',str(left), '-b',str(bottom), '-r',str(right), '-s'])
	print 'Prosessing %d / %d: %s' % (count, reduce(lambda n1,n2: (n1+n2),map(lambda x: 2**(2*x),range(1, int(depth)+1))), command)
	os.system(command)
	#print command
				   
split_four(get_area())
