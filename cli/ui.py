#!/usr/bin/python
# -*- conding: utf-8 -*-
import sys, time, datetime, json
from PyQt4 import QtGui, QtCore

from async import ListenerThread, ExecutionThread
from db import DBConf, DBJob, DBCron, DBSchedule
from helper import QHelper



class UI( QtGui.QMainWindow ):
	instance = None
	
	def __init__( self ):
		super( self.__class__, self ).__init__()
		self.__class__.instance = self
		QHelper.UIInstance = self
		self.build()
	
	def build( self ):
		self.setGeometry( 50, 100, 300, 600 )
		self.setWindowTitle( 'Contacts' )    
		self.statusBar()
		
		self.Action = Action( self )
		### actions
		
		### Menus and Controls
		self.Control = Control( self )
		
		### Views
		self.View = View( self )
		
		### Thread
		self.ListenerThread = ListenerThread( self )
		self.ExecutionThread = ExecutionThread( self )
		#self.RandomActionThread = RandomActionThread()
		
		### Show the MainWindow
		#self.show()



class Action:
	def __init__( self, master ):
		self.master = master
		# TODO: if no pref found, show preferences view
		# TODO: show login/store login and password preferences
		self.build()
	
	def build( self ):
		self.exitAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Exit', self.master )
		self.exitAction.setShortcut( 'Ctrl+Q' )
		self.exitAction.setStatusTip( 'Exit application' )
		self.exitAction.triggered.connect( QtGui.qApp.quit )
		
		self.logoutAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), 'Log &out', self.master )
		self.logoutAction.setShortcut( 'Ctrl+O' )
		self.logoutAction.setStatusTip( 'Log out' )
		self.logoutAction.triggered.connect( self.logoutActionCallback )
		
		self.preferencesAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), 'Pre&ferences', self.master )
		self.preferencesAction.setShortcut( 'Ctrl+F' )
		self.preferencesAction.setStatusTip( 'Preferences' )
		self.preferencesAction.triggered.connect( self.preferencesActionCallback )
		
		self.projectsAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), '&Projects', self.master )
		self.projectsAction.setShortcut( 'Ctrl+P' )
		self.projectsAction.setStatusTip( 'Show projects' )
		self.projectsAction.triggered.connect( self.projectsActionCallback )
		
		self.reportAction = QtGui.QAction( QtGui.QIcon( 'exit.png' ), 'Send &Report', self.master )
		self.reportAction.setShortcut( 'Ctrl+R' )
		self.reportAction.setStatusTip( 'Report' )
		self.reportAction.triggered.connect( self.reportActionCallback )
		
		self.master.connect( self.master, QtCore.SIGNAL( 'loginSuccess' ), self.SIGNALCBloginSuccessCallback )
		self.master.connect( self.master, QtCore.SIGNAL( 'loginError' ), self.SIGNALCBloginErrorCallback )
		self.master.connect( self.master, QtCore.SIGNAL( 'sendMessage' ), self.SIGNALCBsendMessageCallback )
		self.master.connect( self.master, QtCore.SIGNAL( 'pickedContact' ), self.SIGNALCBpickedContactCallback )
		self.master.connect( self.master, QtCore.SIGNAL( 'contactStatus' ), self.SIGNALCBcontactStatusCallback )
		self.master.connect( self.master, QtCore.SIGNAL( 'receiveMessage' ), self.SIGNALCBreceiveMessageCallback )
		self.master.connect( self.master, QtCore.SIGNAL( 'projectList' ), self.SIGNALCBprojectListCallback )
		self.master.connect( self.master, QtCore.SIGNAL( 'pickedProject' ), self.SIGNALCBpickedProjectCallback )
		self.master.connect( self.master, QtCore.SIGNAL( 'projectData' ), self.SIGNALCBprojectDataCallback )
	
	def logoutActionCallback( self ):
		DBConf.set( 'username', '' )
		DBConf.set( 'passwd', '' )
		self.master.View.login().show()
		self.master.hide()
	
	def loginActionCallback( self ):
		self.master.View.login().show()
	
	def preferencesActionCallback( self ):
		self.master.View.preferences().show()
	
	def reportActionCallback( self ):
		self.master.View.report().show()
		DBJob.set( 'projectListActionTrigger' )
	
	def SIGNALCBcontactStatusCallback( self, contact, status ):
		print '::CONNECT:master:contactStatus', contact, status
		#self.master.View.contactItem( contact, status )
	
	def SIGNALCBpickedContactCallback( self, contact ):
		print '::CONNECT:master:pickedContact', contact
		self.master.View.chat().show()
		#for message in self.master.View.contactItem( contact ).messages():
		#	self.master.View.chatDialog().message( message['ts'], message['sender'], message['message'] )
	
	def SIGNALCBsendMessageCallback( self, contact, message ):
		print '::CONNECT:master:sendMessage', contact, message
		DBJob.set( 'sendMessageActionTrigger', None, contact, message.replace( '<br />', '\n' ).replace( '<br/>', '\n' ).replace( '<br>', '\n' ) )
	
	def SIGNALCBreceiveMessageCallback( self, contact, message ):
		print '::CONNECT:master:receiveMessage', contact, message
		#self.master.View.contactItem( contact ).receiveFrom( message, str( time.time() ) )
		#if self.master.View.contactList().value() == contact:
		#	self.master.View.chatDialog().message( time.time(), contact, message )
	
	def projectsActionCallback( self ):
		self.master.View.projects().show()
		DBJob.set( 'projectListActionTrigger' )
	
	def SIGNALCBprojectListCallback( self, projectList ):
		print '::CONNECT:master:projectList', projectList
		#for project, title in projectList:
		#	self.master.View.projectItem( project, title )
	
	def SIGNALCBprojectDataCallback( self, projectData ):
		print '::CONNECT:master:projectData', projectData
		#project = self.master.View.projectList().value()
		#self.master.View.projectData().show( project, projectData )
	
	def SIGNALCBpickedProjectCallback( self, project ):
		print '::CONNECT:master:pickedProject', project
		#project = self.master.View.projectList().value()
		#self.master.projects.setWindowTitle( project + ' - ' + DBConf.get( 'appname' ) )
		DBJob.set( 'projectDataActionTrigger', None, project )
	
	def loginSubmitCallback( self ):
		for k, v in self.master.View.login().values().items():
			DBConf.set( k, type( DBConf.get( k ) )( QHelper.str( v ) ) )
			DBJob.set( 'connectActionTrigger' )
	
	def preferencesSubmitCallback( self ):
		for k, v in self.master.View.preferences().fields.items():
			DBConf.set( k, type( DBConf.get( k ) )( v.text() ) )
			self.master.View.preferences().hide()
	
	def preferencesCancelCallback( self ):
		self.master.View.preferences().hide()
	
	"""
	def reportProjectListActionTrigger( self, projects ):
		self.master.View.reportProjectList().clear()
		for project, title in projects:
			self.master.View.reportProjectItem( project )
	"""
	
	def reportSubmitCallback( self ):
		data = self.master.View.report().values()
		DBJob.set( 'reportActionTrigger', **data )
		self.master.View.report().hide()
	
	def reportCancelCallback( self ):
		self.master.View.report().hide()
	
	def SIGNALCBloginErrorCallback( self, e ):
		print '::CONNECT:master:loginError', e
		#self.master.Action.loginActionCallback()
		self.master.View.login().status.setText( str( e ) )
	
	def SIGNALCBloginSuccessCallback( self ):
		print '::CONNECT:master:loginSuccess'
		self.master.View.login().hide()
		self.master.show()
		self.master.View.contact().show()
		self.master.View.chat().hide()
		DBJob.set( 'helloActionTrigger' )
	
	def reportActionTrigger( self ):
		pass



class Control:
	def __init__( self, master ):
		self.master = master
		self.build()
	
	def build( self ):
		self.menuControl = self.master.menuBar()
		self.mainMenuControl = self.menuControl.addMenu( '&Main' )
		self.mainMenuControl.addAction( self.master.Action.exitAction )
		self.mainMenuControl.addAction( self.master.Action.logoutAction )
		self.viewMenuControl = self.menuControl.addMenu( '&View' )
		self.viewMenuControl.addAction( self.master.Action.projectsAction )
		self.viewMenuControl.addAction( self.master.Action.preferencesAction )
		self.actionMenuControl = self.menuControl.addMenu( '&Actions' )
		self.actionMenuControl.addAction( self.master.Action.reportAction )



class View:
	def __init__( self, master ):
		self.master = master
		self.build()
	
	def build( self ):
		self.login().show()
	
	#################### VIEW contact ####################
	def contact( self ):
		if not hasattr( self.master, 'contact' ):
			self.master.contact = QContactView()
			self.master.setCentralWidget( self.master.contact )
		return self.master.contact
	
	"""
	def contact( self ):
		if not hasattr( self.master, 'contact' ):
			self.master.contact = QtGui.QWidget()
			self.master.contact.resize( 250, 150 )
			self.master.contact.move( 450, 450 )
		
			grid = QtGui.QGridLayout()
			grid.addWidget( self.contactFilter( self.master.contact ), 0, 0 )
			grid.addWidget( self.contactList( self.master.contact ), 1, 0 )
			self.master.contact.setLayout( grid )
			self.master.setCentralWidget( self.master.contact )
		return self.master.contact
	
	def contactList( self, parent=None ):
		if not hasattr( self, '_contactList' ):
			self._contactList = QContactList( self.master.contact )
		return self._contactList
	
	def contactFilter( self, parent=None ):
		if not hasattr( self, '_contactFilter' ):
			self._contactFilter = QtGui.QLineEdit( parent )
		return self._contactFilter
	"""
	
	"""
	def contactItem( self, contact, status=None ):
		if not contact in self._contactList.radioList.keys():
			self._contactList.radioList[contact] = QContact( contact, self._contactList )
			self._contactList.layout.addWidget( self._contactList.radioList[contact] )
		self._contactList.radioList[contact].status = status or self._contactList.radioList[contact].status
		self._contactList.radioList[contact].update()
		return self._contactList.radioList[contact]
	"""
	
	#################### VIEW login ####################
	def login( self ):
		if not hasattr( self.master, 'login' ):
			self.master.login = QLoginView()
		return self.master.login
	
	"""
	def login( self ):
		if not hasattr( self.master, 'login' ):
			self.master.login = QtGui.QWidget()
			self.master.login.fields = {}
			self.master.login.setWindowTitle( 'Login' + ' - ' + DBConf.get( 'appname' ) )
			self.master.login.resize( 450, 200 )
			self.master.login.move( 350, 350 )
		
			grid = QtGui.QGridLayout()
			
			self.master.login.status = QtGui.QLabel( 'Please enter your login and password' )
			grid.addWidget( self.master.login.status, 0, 0, 2, 2 )
			
			grid.addWidget( QtGui.QLabel( 'username' ), 2, 0 )
			grid.addWidget( self.loginField( self.master.login, 'username', DBConf.get( 'username' ) ), 2, 1 )
			
			grid.addWidget( QtGui.QLabel( 'password' ), 3, 0 )
			grid.addWidget( self.loginField( self.master.login, 'passwd', DBConf.get( 'passwd' ) ), 3, 1 )
			
			self.master.login.submit = QtGui.QPushButton( 'Login', self.master.login )
			self.master.connect( self.master.login.submit, QtCore.SIGNAL( 'clicked()' ), self.master.Action.loginSubmitCallback )
			grid.addWidget( self.master.login.submit, 4, 0 )
			
			self.master.login.quit = QtGui.QPushButton( 'Cancel', self.master.login )
			self.master.connect( self.master.login.quit, QtCore.SIGNAL( 'clicked()' ), QtGui.qApp.quit )
			grid.addWidget( self.master.login.quit, 4, 1 )
			
			self.master.login.preferences = QtGui.QPushButton( 'Preferences', self.master.login )
			self.master.connect( self.master.login.preferences, QtCore.SIGNAL( 'clicked()' ), lambda:self.master.View.login().hide() or self.master.Action.preferencesActionCallback() )
			grid.addWidget( self.master.login.preferences, 5, 0, 2 ,1 )
			
			self.master.login.setLayout( grid )
		return self.master.login
	
	def loginField( self, parent, key, value='' ):
		if not key in self.master.login.fields.keys():
			self.master.login.fields[key] = QtGui.QLineEdit( str( value ), parent )
		return self.master.login.fields[key]
	"""
	
	#################### VIEW projects ####################
	def projects( self ):
		if not hasattr( self.master, 'projects' ):
			self.projects = QProjectView()
		return self.projects
	"""
	def projects( self ):
		if not hasattr( self.master, 'projects' ):
			self.master.projects = QtGui.QWidget()
			self.master.projects.setWindowTitle( 'Projects' + ' - ' + DBConf.get( 'appname' ) )
			self.master.projects.resize( 550, 450 )
			self.master.projects.move( 350, 350 )
		
			grid = QtGui.QGridLayout()
			grid.addWidget( self.projectData( self.master.projects ), 0, 0, 2, 1 )
			grid.addWidget( self.projectFilter( self.master.projects ), 0, 1 )
			grid.addWidget( self.projectList( self.master.projects ), 1, 1 )
			grid.setColumnMinimumWidth( 0, 300 )
			self.master.projects.setLayout( grid )
		return self.master.projects
	
	def projectData( self, parent=None ):
		if not hasattr( self, '_projectData' ):
			self._projectData = QProjectData( parent )
			self._projectData.setMaximumHeight( 1000 )
		return self._projectData
	
	def projectFilter( self, parent=None ):
		if not hasattr( self, '_projectFilter' ):
			self._projectFilter = QtGui.QLineEdit( parent )
		return self._projectFilter
	
	def projectList( self, parent=None ):
		if not hasattr( self, '_projectList' ):
			self._projectList = QProjectList( self.master.projects )
		return self._projectList
	"""
	
	"""
	def projectItem( self, project, status=None ):
		if not project in self._projectList.radioList.keys():
			self._projectList.radioList[project] = QProject( project, self._projectList )
			self._projectList.radioList[project].clicked.connect( self.master.Action.pickProjectActionCallback )
			self._projectList.layout.addWidget( self._projectList.radioList[project] )
		self._projectList.radioList[project].status = status or self._projectList.radioList[project].status
		self._projectList.radioList[project].update()
		return self._projectList.radioList[project]
	"""
	
	#################### VIEW chat ####################
	def chat( self ):
		if not hasattr( self.master, 'chat' ):
			self.master.chat = QChatView()
		return self.master.chat
	"""
	def chat( self ):
		if not hasattr( self.master, 'chat' ):
			self.master.chat = QtGui.QWidget()
			self.master.chat.resize( 600, 450 )
			self.master.chat.move( 350, 350 )
		
			grid = QtGui.QGridLayout()
			grid.addWidget( self.chatDialog( self.master.chat ), 0, 0 )
			grid.addWidget( self.chatInput( self.master.chat ), 1, 0 )
			self.master.chat.setLayout( grid )
		return self.master.chat
	
	def chatDialog( self, parent=None ):
		if not hasattr( self, '_chatDialog' ):
			self._chatDialog = QChatDialog( parent )
			self._chatDialog.setMaximumHeight( 1000 )
		return self._chatDialog
	
	def chatInput( self, parent=None ):
		if not hasattr( self, '_chatInput' ):
			self._chatInput = QChatInput( '', parent )
			self._chatInput.setMaximumHeight( 50 )
		return self._chatInput
	"""
	
	#################### VIEW preferences ####################
	def preferences( self ):
		if not hasattr( self.master, 'preferences' ):
			self.master.preferences = QPreferencesView()
		return self.master.preferences
	
	"""
	def preferences( self ):
		if not hasattr( self.master, 'preferences' ):
			self.master.preferences = QtGui.QWidget()
			self.master.preferences.fields = {}
			self.master.preferences.setWindowTitle( 'Preferences' + ' - ' + DBConf.get( 'appname' ) )
			self.master.preferences.resize( 450, 550 )
			self.master.preferences.move( 350, 350 )
		
			grid = QtGui.QGridLayout()
			n = 0
			for key, value in DBConf.list():
				grid.addWidget( QtGui.QLabel( key ), n, 0 )
				grid.addWidget( self.preferencesField( self.master.preferences, key, value ), n, 1 )
				n += 1
			
			self.master.preferences.submit = QtGui.QPushButton( 'Save', self.master.preferences )
			self.master.connect( self.master.preferences.submit, QtCore.SIGNAL( 'clicked()' ), self.master.Action.preferencesSubmitCallback )
			grid.addWidget( self.master.preferences.submit, n, 0 )
			
			self.master.preferences.cancel = QtGui.QPushButton( 'Cancel', self.master.preferences )
			self.master.connect( self.master.preferences.cancel, QtCore.SIGNAL( 'clicked()' ), self.master.Action.preferencesCancelCallback )
			grid.addWidget( self.master.preferences.cancel, n, 1 )
			
			self.master.preferences.setLayout( grid )
		return self.master.preferences
	
	def preferencesField( self, parent, key, value ):
		if not key in self.master.preferences.fields.keys():
			self.master.preferences.fields[key] = QtGui.QLineEdit( str( value ), parent )
		return self.master.preferences.fields[key]
	"""
	
	#################### VIEW report ####################
	def report( self ):
		if not hasattr( self.master, 'report' ):
			self.master.report = QReportView()
		return self.master.report
	"""
	def report( self ):
		if not hasattr( self.master, 'report' ):
			self.master.report = QtGui.QWidget()
			self.master.report.fields = {}
			self.master.report.setWindowTitle( 'Report' + ' - ' + DBConf.get( 'appname' ) )
			self.master.report.resize( 200, 200 )
			self.master.report.move( 350, 350 )
		
			grid = QtGui.QGridLayout()
			
			self.master.report.status = QtGui.QLabel( 'Report' )
			grid.addWidget( self.master.report.status, 0, 0, 2, 2 )
			
			grid.addWidget( self.reportField( self.master.report, 'h', 'hours' ), 2, 0 )
			
			grid.addWidget( self.reportField( self.master.report, 'm', 'minutes' ), 2, 1 )
			
			grid.addWidget( QtGui.QLabel( 'Project' ), 3, 0 )
			grid.addWidget( self.reportProjectList( self.master.report ), 3, 1 )
			
			grid.addWidget( QtGui.QLabel( 'Summary' ), 4, 0, 1, 2 )
			grid.addWidget( self.reportSummary( self.master.report, 'summary' ), 5, 0, 1, 2 )
			
			self.master.report.submit = QtGui.QPushButton( 'Send', self.master.report )
			self.master.connect( self.master.report.submit, QtCore.SIGNAL( 'clicked()' ), self.master.Action.reportSubmitCallback )
			grid.addWidget( self.master.report.submit, 6, 0 )
			
			self.master.report.cancel = QtGui.QPushButton( 'Cancel', self.master.report )
			self.master.connect( self.master.report.cancel, QtCore.SIGNAL( 'clicked()' ), self.master.Action.reportCancelCallback )
			grid.addWidget( self.master.report.cancel, 6, 1 )
			
			self.master.report.setLayout( grid )
		return self.master.report
	
	def reportField( self, parent, key, placeholder='', value='' ):
		if not key in self.master.report.fields.keys():
			self.master.report.fields[key] = QtGui.QLineEdit( str( value ), parent )
			self.master.report.fields[key].setPlaceholderText( placeholder )
		return self.master.report.fields[key]
	
	def reportSummary( self, parent, key ):
		if not key in self.master.report.fields.keys():
			self.master.report.fields[key] = QtGui.QTextEdit( parent )
		return self.master.report.fields[key]
	
	def reportProjectList( self, parent=None ):
		if not hasattr( self, '_reportProjectList' ):
			self._reportProjectList = QtGui.QComboBox( parent )
			self.master.report.fields['project'] = self._reportProjectList
		return self._reportProjectList
	
	def reportProjectItem( self, value ):
		if hasattr( self, '_reportProjectList' ):
			self._reportProjectList.addItem( value )
	"""
	
	"""
	def reportField( self, parent, key, placeholder='', value='' ):
		if not key in self.master.report.fields.keys():
			self.master.report.fields[key] = QtGui.QLineEdit( str( value ), parent )
			self.master.report.fields[key].setPlaceholderText( placeholder )
		return self.master.report.fields[key]
	
	def reportSummary( self, parent, key ):
		if not key in self.master.report.fields.keys():
			self.master.report.fields[key] = QtGui.QTextEdit( parent )
		return self.master.report.fields[key]
	
	def reportProjectList( self, parent=None ):
		if not hasattr( self, '_reportProjectList' ):
			self._reportProjectList = QtGui.QComboBox( parent )
			self.master.report.fields['project'] = self._reportProjectList
		return self._reportProjectList
	
	def reportProjectItem( self, value ):
		if hasattr( self, '_reportProjectList' ):
			self._reportProjectList.addItem( value )
	"""



class QForm( QtGui.QWidget ):
	def __init__( self, parent=None ):
		if parent:
			QtGui.QWidget.__init__( self, parent )
		else:
			QtGui.QWidget.__init__( self )
		if parent:
			self.parent = parent
		self.fields = {}
	
	def lineEditField( self, fieldName, value='', placeholder='' ):
		if not fieldName in self.fields.keys():
			self.fields[fieldName] = QtGui.QLineEdit( value, self )
			if placeholder:
				self.fields[fieldName].setPlaceholderText( placeholder )
		return self.fields[fieldName]
	
	def textEditField( self, fieldName ):
		if not fieldName in self.fields.keys():
			self.fields[fieldName] =  QtGui.QTextEdit( self )
		return self.fields[fieldName]
	
	def comboBoxField( self, fieldName ):
		if not fieldName in self.fields.keys():
			self.fields[fieldName] =  QtGui.QComboBox( self )
		return self.fields[fieldName]
	
	def values( self ):
		return dict( [( k, QHelper.getValue( v ) ) for k, v in self.fields.items()] )



#################### CONTACT VIEW ####################
class QContactView( QtGui.QWidget ):
	def __init__( self, parent=None ):
		if parent:
			super( self.__class__, self ).__init__( parent )
		else:
			super( self.__class__, self ).__init__()
		self.resize( 250, 150 )
		self.move( 450, 450 )
		
		grid = QtGui.QGridLayout()
		grid.addWidget( QContactFilter( self ), 0, 0 )
		grid.addWidget( QContactList( self ), 1, 0 )
		self.setLayout( grid )



class QContactFilter( QtGui.QLineEdit ):
	def __init__( self, parent ):
		super( self.__class__, self ).__init__( parent )
		self.setPlaceholderText( 'Filter' )



class QContactList( QtGui.QGroupBox ):
	def __init__( self, parent ):
		super( self.__class__, self ).__init__( parent )
		self.radioList = {}
		self.contactListItems = {}
		self.layout = QtGui.QVBoxLayout()
		self.setLayout( self.layout )
		self.contact = None
		#self.master.View.contactItem( contact, status )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'contactStatus' ), self.contactStatusCallback )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'pickedContact' ), self.pickedContactCallback )
	
	def contactStatusCallback( self, contact, status ):
		print '::CONNECT:QContactList:contactStatus', contact, status
		if not contact in self.radioList.keys():
			self.radioList[contact] = QContact( contact, status, self )
			self.layout.addWidget( self.radioList[contact] )
	
	def pickedContactCallback( self, contact ):
		print '::CONNECT:QContactList:pickedContact', contact
		self.contact = contact
	
	def value( self ):
		for k, w in self.radioList.items():
			if w.isChecked():
				return k



class QContact( QtGui.QRadioButton ):
	def __init__( self, name, status, parent ):
		super( self.__class__, self ).__init__( '' )
		self.name = name
		self.parent = parent
		self.messagesNew = {}
		self.status = status
		self.connect( QHelper.master(), QtCore.SIGNAL( 'sendMessage' ), self.sendMessageCallback )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'receiveMessage' ), self.receiveMessageCallback )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'contactStatus' ), self.contactStatusCallback )
		self.clicked.connect( lambda: QHelper.master().emit( QtCore.SIGNAL( 'pickedContact' ), self.name ) )
		self.update()
	
	def pickedContactCallback( self, contact ):
		print '::CONNECT:QContact:pickedContact', contact
	
	def sendMessageCallback( self, contact, message ):
		print '::CONNECT:QContact:sendMessage', contact, message
		if self.name == contact:
			self.sendTo( message )
	
	def receiveMessageCallback( self, contact, message ):
		print '::CONNECT:QContact:receiveMessage', contact, message
		if self.name == contact:
			self.receiveFrom( message, str( time.time() ) )
	
	def contactStatusCallback( self, contact, status ):
		print '::CONNECT:QContact:contactStatus', contact, status
		if self.name == contact:
			self.status = status
			self.update
	
	def update( self ):
		if self.isChecked():
			self.messagesNew = {}
		self.setText( '%s [%s] %s' % (
			self.name,
			self.status,
			len( self.messagesNew ) and '('+str( len( self.messagesNew ) )+')' or ''
		) )
	
	def receiveFrom( self, message, ts=None ):
		#if not ts:
		#	ts = str( time.time() )
		#self.messagesTime.append( ts )
		#self.messagesList[ts] = { 'ts':str( ts ), 'sender':self.name, 'recipient':DBConf.get( 'username' ), 'message':message }
		self.messagesNew[ts] = message
		self.update()
	
	def sendTo( self, message ):
		pass
		#ts = str( time.time() )
		#self.messagesTime.append( ts )
		#self.messagesList[ts] = { 'ts':str( ts ), 'sender':DBConf.get( 'username' ), 'recipient':self.name, 'message':message }



#################### CHAT VIEW ####################
class QChatView( QtGui.QWidget ):
	def __init__( self, parent=None ):
		if parent:
			super( self.__class__, self ).__init__( parent )
		else:
			super( self.__class__, self ).__init__()
		self.resize( 600, 450 )
		self.move( 350, 350 )
		
		grid = QtGui.QGridLayout()
		
		chatDialog = QChatDialog( self )
		chatDialog.setMaximumHeight( 400 )
		grid.addWidget( chatDialog, 0, 0 )
		
		grid.addWidget( QtGui.QLabel( 'Your message:' ), 1, 0 )
		
		chatInput = QChatInput( self )
		chatInput.setMaximumHeight( 50 )
		grid.addWidget( chatInput, 2, 0 )
		
		self.setLayout( grid )



class QChatDialog( QtGui.QTextEdit ):
	def __init__( self, parent ):
		super( self.__class__, self ).__init__( parent )
		self.messagesTime = {}
		self.messagesList = {}
		self.parent = parent
		self.contact = None
		self.textCursor = QtGui.QTextCursor( self.document() )
		self.setReadOnly( 1 )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'pickedContact' ), self.pickedContactCallback )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'sendMessage' ), self.sendMessageCallback )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'receiveMessage' ), self.receiveMessageCallback )
	
	def write( self, text ):
		self.textCursor.insertHtml( text + '<br />' )
	
	def pickedContactCallback( self, contact ):
		print '::CONNECT:QChatDialog:pickedContact', contact
		self.parent.setWindowTitle( contact + ' - ' + DBConf.get( 'appname' ) )
		self.contact = contact
		self.clear()
		if not self.messagesTime.get( contact, None ): self.messagesTime[contact] = []
		if not self.messagesList.get( contact, None ): self.messagesList[contact] = {}
		for message in self.messages( contact ):
			self.message( message['ts'], message['sender'], message['message'] )
	
	def sendMessageCallback( self, contact, message ):
		print '::CONNECT:QChatDialog:sendMessage', contact, message
		ts = time.time()
		self.messagesTime[contact].append( str( ts ) )
		self.messagesList[contact][str( ts )] = { 'ts':str( ts ), 'sender':DBConf.get( 'username' ), 'recipient':contact, 'message':message }
		
		self.message( str( ts ), DBConf.get( 'username' ), message )
	
	def receiveMessageCallback( self, contact, message ):
		print '::CONNECT:QChatDialog:receiveMessage', contact, message
		ts = time.time()
		self.messagesTime[contact].append( str( ts ) )
		self.messagesList[contact][str( ts )] = { 'ts':str( ts ), 'sender':contact, 'recipient':DBConf.get( 'username' ), 'message':message }
		
		if self.contact == contact:
			self.message( str( ts ), contact, message )
	
	def messages( self, contact, since=None ):
		self.messagesTime[contact].sort()
		return [{ 'ts':ts, 'sender':self.messagesList[contact][ts]['sender'], 'message':self.messagesList[contact][ts]['message'] } for ts in self.messagesTime[contact]]
	
	def message( self, ts, sender, message ):
		text =  '<span style="color:#999;">[%s]</span> <span style="font-weight:bold; color:%s;">%s</span><br />%s<br />' % (
				datetime.datetime.fromtimestamp( int( str( ts ).split('.')[0] ) ).strftime( '%Y-%m-%d %H:%M:%S' ),
				( sender==DBConf.get( 'username' ) and '#000' or '#66f' ),
				sender,
				message.replace( '\n', '<br />' )
			)
		self.write( text )



class QChatInput( QtGui.QTextEdit ):
	def __init__( self, parent ):
		super( self.__class__, self ).__init__( '', parent )
		self.parent = parent
		self.contact = None
		self.__sendMessageOnReturn = True
		self.connect( QHelper.master(), QtCore.SIGNAL( 'pickedContact' ), self.pickedContactCallback )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'sendMessage' ), self.sendMessageCallback )
	
	def pickedContactCallback( self, contact ):
		print '::CONNECT:QChatInput:pickedContact', contact
		self.contact = contact
		self.clear()
	
	def sendMessageCallback( self, contact, message ):
		print '::CONNECT:QChatInput:sendMessage', contact, message
		self.clear()
	
	def keyPressEvent( self, event ):
		if event.key() == QtCore.Qt.Key_Shift:
			self.__sendMessageOnReturn = False
		elif event.key() == QtCore.Qt.Key_Return:
			if self.__sendMessageOnReturn:
				if len( self.toPlainText() ):
					QHelper.master().emit( QtCore.SIGNAL( 'sendMessage' ), self.contact, self.toPlainText() )
					return
		QtGui.QTextEdit.keyPressEvent( self, event )
	
	def keyReleaseEvent( self, event ):
		if event.key() == QtCore.Qt.Key_Shift:
			self.__sendMessageOnReturn = True
		QtGui.QTextEdit.keyPressEvent( self, event )



#################### PROJECT VIEW ####################
class QProjectView( QtGui.QWidget ):
	def __init__( self, parent=None ):
		if parent:
			super( self.__class__, self ).__init__( parent )
		else:
			super( self.__class__, self ).__init__()
		self.setWindowTitle( 'Projects' + ' - ' + DBConf.get( 'appname' ) )
		self.resize( 550, 450 )
		self.move( 350, 350 )
		
		grid = QtGui.QGridLayout()
		
		grid.addWidget( QProjectData( self ), 0, 0, 2, 1 )
		grid.addWidget( QtGui.QLineEdit( self ), 0, 1 )
		grid.addWidget( QProjectList( self ), 1, 1 )
		
		grid.setColumnMinimumWidth( 0, 300 )
		
		self.setLayout( grid )



class QProjectList( QtGui.QGroupBox ):
	def __init__( self, parent ):
		super( self.__class__, self ).__init__( parent )
		self.radioList = {}
		self.projectListItems = {}
		self.layout = QtGui.QVBoxLayout()
		self.setLayout( self.layout )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'projectList' ), self.projectListCallback )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'pickedProject' ), self.pickedProjectCallback )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'projectData' ), self.projectDataCallback )
	
	def projectListCallback( self, projectList ):
		print '::CONNECT:QProjectList:projectList', projectList
		for project, title in projectList:
			if not project in self.radioList.keys():
				self.radioList[project] = QProject( project, title, self )
				self.layout.addWidget( self.radioList[project] )
	
	def pickedProjectCallback( self, project ):
		print '::CONNECT:QProjectList:pickedProject', project
		self.project = project
		#self.parent.setWindowTitle( project + ' - ' + DBConf.get( 'appname' ) )
		#self.clear()
	
	def projectDataCallback( self, projectData ):
		print '::CONNECT:QProjectList:projectData', projectData
	
	def value( self ):
		for k, w in self.radioList.items():
			if w.isChecked():
				return k



class QProject( QtGui.QRadioButton ):
	def __init__( self, name, title, parent ):
		super( self.__class__, self ).__init__( name + '['+title+']' )
		self.parent = parent
		self.name = name
		self.title = title
		self.connect( QHelper.master(), QtCore.SIGNAL( 'projectList' ), self.projectListCallback )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'pickedProject' ), self.pickedProjectCallback )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'projectData' ), self.projectDataCallback )
		self.clicked.connect( lambda: QHelper.master().emit( QtCore.SIGNAL( 'pickedProject' ), self.name ) )
	
	def projectListCallback( self, projectList ):
		print '::CONNECT:QProject:projectList', projectList
		#for project, title in projectList:
		#	self.master.View.projectItem( project, title )
	
	def pickedProjectCallback( self, project ):
		print '::CONNECT:QProject:pickedProject', project
	
	def projectDataCallback( self, projectData ):
		print '::CONNECT:QProject:projectData', projectData
	
	def update( self ):
		if self.isChecked():
			self.messagesNew = {}
		self.setText( '%s [%s]' % (
			self.name,
			self.title
		) )



class QProjectData( QtGui.QTextEdit ):
	def __init__( self, parent ):
		super( self.__class__, self ).__init__( parent )
		self.textCursor = QtGui.QTextCursor( self.document() )
		self.setReadOnly( 1 )
		self.project = None
		self.connect( QHelper.master(), QtCore.SIGNAL( 'pickedProject' ), self.pickedProjectCallback )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'projectData' ), self.projectDataCallback )
	
	def pickedProjectCallback( self, project ):
		print '::CONNECT:QProjectData:pickedProject', project
		self.project = project
		self.clear()
		self.write( '...loading' )
	
	def projectDataCallback( self, projectData ):
		print '::CONNECT:QProjectData:projectData', projectData
		self.clear()
		data = '<table width="100%" cellspacing="4" cellpadding="0">'
		n=0
		for k, v in json.loads( projectData ).items():
			n+=1
			data += '<tr>'
			data += '<th style="background:'+(n%2 and '#f6f6f6' or '#fcfcfc')+';">' + str( k ) + '</th>'
			data += '<td style="">' + self.plain( v ) + '</td>'
			data += '</tr>'
		data += '</table>'
		text =  '<span style="font-weight:bold; color:#66f;">[%s]</span><br />%s<br />' % (
				self.project,
				data
			)
		self.write( text )
	
	def write( self, text ):
		self.textCursor.insertHtml( text + '<br />' )
	
	def plain( self, data ):
		if type( data ) == list:
			return '<ul style="margin:0; padding:0 0 0 15px;">' + ''.join( ['<li>' + self.plain( i ) + '</li>' for i in data] ) + '</ul>'
		elif type( data ) == dict:
			return '<dl style="margin:0; padding:0 0 0 15px;">' + ''.join( ['<dt style="font-weight:bold;">' + self.plain( k ) + '</dt>' + '<dd>' + self.plain( v ) + '</dd>' for k, v in data.items()] ) + '</dl>'
		else:
			return str( data )



#################### LOGIN VIEW ####################
class QLoginView( QForm ):
	def __init__( self ):
		QForm.__init__( self )
		self.setWindowTitle( 'Login' + ' - ' + DBConf.get( 'appname' ) )
		self.resize( 450, 200 )
		self.move( 350, 350 )
		
		grid = QtGui.QGridLayout()
		
		self.status = QtGui.QLabel( 'Please enter your login and password' )
		grid.addWidget( self.status, 0, 0, 2, 2 )
		
		grid.addWidget( QtGui.QLabel( 'username' ), 2, 0 )
		grid.addWidget( self.lineEditField( 'username', DBConf.get( 'username' ) ), 2, 1 )
		
		grid.addWidget( QtGui.QLabel( 'password' ), 3, 0 )
		grid.addWidget( self.lineEditField( 'passwd', DBConf.get( 'passwd' ) ), 3, 1 )
		
		self.submit = QtGui.QPushButton( 'Login', self )
		QHelper.master().connect( self.submit, QtCore.SIGNAL( 'clicked()' ), QHelper.master().Action.loginSubmitCallback )
		grid.addWidget( self.submit, 4, 0 )
		
		self.quit = QtGui.QPushButton( 'Cancel', self )
		QHelper.master().connect( self.quit, QtCore.SIGNAL( 'clicked()' ), QtGui.qApp.quit )
		grid.addWidget( self.quit, 4, 1 )
		
		self.preferences = QtGui.QPushButton( 'Preferences', self )
		QHelper.master().connect( self.preferences, QtCore.SIGNAL( 'clicked()' ), lambda:self.hide() or QHelper.master().Action.preferencesActionCallback() )
		grid.addWidget( self.preferences, 5, 0, 2 ,1 )
		
		self.setLayout( grid )



#################### PREFERENCES VIEW ####################
class QPreferencesView( QForm ):
	def __init__( self ):
		QForm.__init__( self )
		self.setWindowTitle( 'Report' + ' - ' + DBConf.get( 'appname' ) )
		self.setWindowTitle( 'Preferences' + ' - ' + DBConf.get( 'appname' ) )
		self.resize( 450, 550 )
		self.move( 350, 350 )
		
		grid = QtGui.QGridLayout()
		n = 0
		for key, value in DBConf.list():
			grid.addWidget( QtGui.QLabel( key ), n, 0 )
			grid.addWidget( self.lineEditField( self, key, value ), n, 1 )
			n += 1
		
		self.submit = QtGui.QPushButton( 'Save', self )
		QHelper.master().connect( self.submit, QtCore.SIGNAL( 'clicked()' ), QHelper.master().Action.preferencesSubmitCallback )
		grid.addWidget( self.submit, n, 0 )
			
		self.cancel = QtGui.QPushButton( 'Cancel', self )
		QHelper.master().connect( self.cancel, QtCore.SIGNAL( 'clicked()' ), QHelper.master().Action.preferencesCancelCallback )
		grid.addWidget( self.master.preferences.cancel, n, 1 )
			
		self.setLayout( grid )



#################### REPORT VIEW ####################
class QReportView( QForm ):
	def __init__( self ):
		QForm.__init__( self )
		self.setWindowTitle( 'Report' + ' - ' + DBConf.get( 'appname' ) )
		self.resize( 200, 200 )
		self.move( 350, 350 )
		
		grid = QtGui.QGridLayout()
		
		self.status = QtGui.QLabel( 'Report' )
		grid.addWidget( self.status, 0, 0, 2, 2 )
		
		grid.addWidget( QtGui.QLabel( 'Project' ), 2, 0 )
		grid.addWidget( self.comboBoxField( 'project' ), 2, 1 )
		
		grid.addWidget( self.lineEditField( 'h', '', 'hours' ), 3, 0 )
		grid.addWidget( self.lineEditField( 'm', '', 'minutes' ), 3, 1 )
		
		grid.addWidget( QtGui.QLabel( 'Summary' ), 4, 0, 1, 2 )
		grid.addWidget( self.textEditField( 'summary' ), 5, 0, 1, 2 )
		
		self.submit = QtGui.QPushButton( 'Send', self )
		# TODO: make this an emit action
		QHelper.master().connect( self.submit, QtCore.SIGNAL( 'clicked()' ), QHelper.master().Action.reportSubmitCallback )
		grid.addWidget( self.submit, 6, 0 )
		
		self.cancel = QtGui.QPushButton( 'Cancel', self )
		# TODO: make this an emit action
		QHelper.master().connect( self.cancel, QtCore.SIGNAL( 'clicked()' ), QHelper.master().Action.reportCancelCallback )
		grid.addWidget( self.cancel, 6, 1 )
		
		self.setLayout( grid )
		self.connect( QHelper.master(), QtCore.SIGNAL( 'projectList' ), self.projectListCallback )
	
	def projectListCallback( self, projectList ):
		print  '::CONNECT:QReportView:projectList', projectList
		for project, title in projectList:
			self.fields['project'].addItem( project )



def main():
	app = QtGui.QApplication( sys.argv )
	ui = UI()
	sys.exit( app.exec_() )

if __name__ == "__main__":
	main()
