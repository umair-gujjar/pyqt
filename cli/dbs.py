#!/usr/bin/python
# -*-coding: utf-8 -*-
import shelve, time, os
from helper import QHelper

class DBBase:
	filepath = [ 'data' ]
	filename = ''
	fileext = ''
	
	@classmethod
	def path( cls ):
		path = os.path.join( *cls.filepath )
		path = os.path.join( path, '.'.join( [ cls.filename, cls.fileext ] ) )
		return path
	
	@classmethod
	def handle( cls ):
		if not hasattr( cls, '__handle' ):
			for i in range( 10 ):
				try:
					cls.__handle = shelve.open( cls.path() )
					break
				except Exception as e:
					print '::DB EXCEPTION', e
		return cls.__handle
	
	@classmethod
	def sync( cls ):
		for i in range( 10 ):
			try:
				if hasattr( cls, '__handle' ):
					cls.__handle.sync()
					cls.__handle.close()
					delattr( cls, '__handle' )
				break
			except Exception as e:
				print '::DB EXCEPTION', e
	
	@classmethod
	def keys( cls ):
		for i in range( 10 ):
			try:
				return cls.handle().keys()
			except Exception as e:
				print '::DB EXCEPTION', e
	
	@classmethod
	def list( cls ):
		return cls.handle().items()
	
	@classmethod
	def get( cls, key, default=None ):
		return cls.handle().get( key, default )
	
	@classmethod
	def set( cls, key, value ):
		cls.handle()[key] = value
		cls.sync()



class DBConf( DBBase ):
	filepath = [ 'data' ]
	filename = 'conf'
	fileext = 'db'



class DBHistory( DBBase ):
	filepath = [ 'data', 'history' ]
	filename = ''
	fileext = 'history'
	
	@classmethod
	def setPath( cls, sender, recipient ):
		filename = [ sender, recipient ]
		filename.sort()
		filename = '_'.join( filename )
		cls.sync()
		cls.filename = os.path.join( filename )
	
	@classmethod
	def set( cls, sender, recipient, message, ts=None ):
		cls.setPath( sender, recipient )
		if not ts:
			ts = time.time()
		cls.handle()[str( ts )] = {
			'ts':str( int( ts ) ),
			'sender':QHelper.str( sender ),
			'recipient':QHelper.str( recipient ),
			'message':QHelper.str( message )
		}
		cls.handle().sync()
	
	@classmethod
	def get( cls, user, contact ):
		cls.setPath( user, contact )
		keys = cls.keys()
		keys.sort()
		return [cls.handle()[key] for key in keys]



class DB:
	filepath = [ 'data', 'db' ]
	filename = 'account'
	fileext = 'db'
	_conn = None
	_cur = None
	
	"""
sqlite> CREATE TABLE `contact_group`( `id` INTEGER PRIMARY KEY, `name` TEXT );
sqlite> INSERT INTO `contact_group` ( `name` ) VALUES ( 'general' );
sqlite> INSERT INTO `contact_group` ( `name` ) VALUES ( 'friends' );
sqlite> INSERT INTO `contact_group` ( `name` ) VALUES ( 'work' );
sqlite> INSERT INTO `contact_group` ( `name` ) VALUES ( 'family' );
sqlite> CREATE TABLE `contact` ( `id` INTEGER PRIMARY KEY, `name` TEXT, `contact_group_id` INTEGER, FOREIGN KEY ( `contact_group_id` ) REFERENCES contact_group( `id` ) );

last_id = cls._cur.lastrowid
	"""
	
	@classmethod
	def path( cls ):
		path = os.path.join( *cls.filepath )
		path = os.path.join( path, '.'.join( [ cls.filename, cls.fileext ] ) )
		return ( cls.filename and path or ':memory:' )
	
	@classmethod
	def _connect( cls ):
		import sqlite3
		cls._conn = sqlite3.connect( cls.path() )
		cls._conn.row_factory = sqlite3.Row
		cls._cur = cls._conn.cursor()
		
	@classmethod
	def conn( cls ):
		if not cls._conn:
			cls._connect()
		return cls._conn
	
	@classmethod
	def cur( cls ):
		if not cls._cur:
			cls._connect()
		return cls._cur
	
	@classmethod
	def execute( cls, queryString, *arg ):
		QHelper.log( '::DB:execute', queryString, arg )
		cls.cur().execute( queryString, arg )
		
		if queryString.strip().lower().startswith( 'select' ):
			# SELECT: return result
			result = cls.cur().fetchall()
			QHelper.log( '::DB:select:fetchall', result )
			return result
		else:
			# write-query: commit after execution 
			cls.conn().commit()
			
			rowcount = cls.cur().rowcount
			lastrowid = cls.cur().lastrowid
			
			if queryString.strip().lower().startswith( 'insert' ):
				# INSERT: return last inserted id
				QHelper.log( '::DB:insert:rowcount', rowcount )
				QHelper.log( '::DB:insert:lastrowid', lastrowid )
				return lastrowid
			else:
				QHelper.log( '::DB:update:rowcount', rowcount )
				QHelper.log( '::DB:update:lastrowid', lastrowid )
				return rowcount
