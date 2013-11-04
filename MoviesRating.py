#!/usr/bin/env python

"""Get the rating of a movie on RottenTomatoes.com and imdb.com"""

# Forked from 
# RottenTomatoesRating
# Laszlo Szathmary, 2011 (jabba.laci@gmail.com)
#
# Project's home page: 
# https://pythonadventures.wordpress.com/2011/03/26/get-the-rottentomatoes-rating-of-a-movie/
#
# Version: 0.2 
# Date:	2011-03-29 (yyyy-mm-dd)
#
# This free software is copyleft licensed under the same terms as Python, or,
# at your option, under version 2 of the GPL license.

import sys
import re
import urllib
import urlparse
import os
from mechanize import Browser
from BeautifulSoup import BeautifulSoup

#Movie Directory Path
moviesDirectory="H:\\"

class MyOpener(urllib.FancyURLopener):
	"""Tricking web servers."""
	version = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'
	
class RottenTomatoesRating:
	"""Get the rating of a movie."""
	# title of the movie
	title = None
	# RT URL of the movie
	url = None
	# RT tomatometer rating of the movie
	tomatometer = None
	# RT audience rating of the movie
	audience = None
	# Did we find a result?
	found = False
	
	# for fetching webpages
	myopener = MyOpener()
	# Should we search and take the first hit?
	search = True
	
	# constant
	BASE_URL = 'http://www.rottentomatoes.com'
	SEARCH_URL = '%s/search/full_search.php?search=' % BASE_URL
	
	def __init__(self, title, search=True):
		self.title = title
		self.search = search
		self._process()
		
	def _search_movie(self):
		"""Use RT's own search and return the first hit."""
		movie_url = ""
		
		url = self.SEARCH_URL + self.title
		page = self.myopener.open(url)
		result = re.search(r'(/m/.*)', page.geturl())
		if result:
			# if we are redirected
			movie_url = result.group(1)
		else:
			# if we get a search list
			soup = BeautifulSoup(page.read())
			ul = soup.find('ul', {'id' : 'movie_results_ul'})
			if ul:
				div = ul.find('div', {'class' : 'media_block_content'})
				if div:
					movie_url = div.find('a', href=True)['href']
				
		return urlparse.urljoin( self.BASE_URL, movie_url )
		
	def _process(self):
		"""Start the work."""
		
		# if search option is off, i.e. try to locate the movie directly 
		if not self.search:
			movie = '_'.join(self.title.split())
			
			url = "%s/m/%s" % (self.BASE_URL, movie)
			soup = BeautifulSoup(self.myopener.open(url).read())
			if soup.find('title').contents[0] == "Page Not Found":
				url = self._search_movie()				
		else:
			# if search option is on => use RT's own search
			url = self._search_movie()

		try:
			self.url = url
			soup = BeautifulSoup( self.myopener.open(url).read() )
			self.title = soup.find('meta', {'property' : 'og:title'})['content']
			if self.title:
				self.found = True
			
			self.tomatometer = soup.find('span', {'id' : 'all-critics-meter'}).contents[0]
			self.audience = soup.find('span', {'class' : 'meter popcorn numeric '}).contents[0]
			
			if self.tomatometer.isdigit():
				self.tomatometer += "%"
			if self.audience.isdigit():
				self.audience += "%"
		except:
			pass

class ImdbRating:
	"""Get the rating of a movie."""
	# title of the movie
	title = None
	# IMDB URL of the movie
	url = None
	# IMDB rating of the movie
	rating = None
	# Did we find a result?
	found = False
	
	# constant
	BASE_URL = 'http://www.imdb.com'
	
	def __init__(self, title):
		self.title = title
		self._process()
		
	def _process(self):
		"""Start the work."""
		movie = '+'.join(self.title.split())
		br = Browser()
		url = "%s/find?s=tt&q=%s" % (self.BASE_URL, movie)
		br.open(url)

		if re.search(r'/title/tt.*', br.geturl()):
			self.url = "%s://%s%s" % urlparse.urlparse(br.geturl())[:3]
			soup = BeautifulSoup( MyOpener().open(url).read() )
		else:
			link = br.find_link(url_regex = re.compile(r'/title/tt.*'))
			res = br.follow_link(link)
			self.url = urlparse.urljoin(self.BASE_URL, link.url)
			soup = BeautifulSoup(res.read())

		try:
			self.title = soup.find('h1').contents[0].strip()
			for span in soup.findAll('span'):
				if span.has_key('itemprop') and span['itemprop'] == 'ratingValue':
					self.rating = span.contents[0]
					break
			self.found = True
		except:
			pass


if __name__ == "__main__":
	for root, dirs, files in os.walk(moviesDirectory):
		for name in files:
			fullpath=os.path.join(root, name)
			filename,ext = os.path.splitext(fullpath)
			if ext=='.avi' or ext == '.mkv':
				try:
				   name=name[:-4]
				   name=name.replace("."," ")
				   name= name.split()
				   try:
						name=name[0]+" "+name[1]+" "+name[2]
				   except:
						try:
							name=name[0]+" "+name[1]
						except:
							try:
								name=name[0]
							except:
								pass
				   print name
				   if "Rotten Rating" not in filename:
					   rt = RottenTomatoesRating(name)
					   if rt.found:
							print rt.url
							print rt.title
							print rt.tomatometer
							print rt.audience
							os.rename(filename+ext,filename+" Rotten Rating-"+rt.tomatometer+ext)
							filename=filename+" Rotten Rating-"+rt.tomatometer
							
				   if "IMDB Rating" not in filename:
					   imdb = ImdbRating(name)
					   if imdb.found:
							print imdb.url
							print imdb.title
							print imdb.rating
							os.rename(filename+ext,filename+" IMDB Rating-"+imdb.rating+ext)
				except:
					pass
					