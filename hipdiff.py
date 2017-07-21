from hypchat import HypChat
from hypchat.restobject import Linker

import difflib
import os
import sys

HIPCHAT_AUTH_KEY = 'YOUR_HIPCHAT_API_KEY'

class UserGetter(HypChat):
	"""
	Extends HypChat class so I can use the max-results parameter on the /v2/users URL.
	"""

	def users(self, **ops):
		"""
		Adds the "max" parameter.
		"""
		params = {}
		if ops.get('guests', False):
			params['include-guests'] = 'true'
		if ops.get('deleted', False):
			params['include-deleted'] = 'true'
		if ops.get('max', False):
			params['max-results'] = str(ops.get('max'))
		resp = self._requests.get(self.users_url, params=params)
		return Linker._obj_from_text(resp.text, self._requests)

def touchopen(filename, *args, **kwargs):
	# Open the file in R and create if it doesn't exist. *Don't* pass O_TRUNC
	fd = os.open(filename, os.O_RDONLY | os.O_CREAT)
	# Encapsulate the low-level file descriptor in a python file object
	return os.fdopen(fd, *args, **kwargs)

def get_user_list_from_file():
	# Gets the user list from the file stored on disk (as opposed to the API)
	print 'Getting stored user list...'
	with touchopen('hipchat-users.txt') as old_file:
		lines = [line.rstrip('\n') for line in old_file]
	return lines

def get_current_hipchat_users():
	print 'Getting current user list...'
	hc = UserGetter(HIPCHAT_AUTH_KEY)
	response = hc.users(max=500)
	user_list = response['items']
	names_list = []
	output_file = open('hipchat-users-new.txt', 'w')
	for i, name in enumerate(d['name'] for d in user_list):
		output_file.write(name.encode('utf-8').strip())
		names_list.append(name.encode('utf-8').strip())
		output_file.write('\n')
	output_file.close()
	return names_list

def compare_lists(old_list, new_list):
	# ADDED = in new_list but not in old_list
	# REMOVED = in old_list but not in new_list
	new_list_copy = new_list
	added = [x for x in new_list if x not in old_list]
	old_list_copy = old_list
	removed = [x for x in old_list if x not in new_list]
	return added, removed

def move_new_file_to_stored():
	try:
		os.rename('hipchat-users-new.txt', 'hipchat-users.txt')
	except:
		print 'File not renamed, please check.'

if __name__ == '__main__':
	print 'hipdiff: Your definitive tool for transparent company evacuation management'
	new_list = get_current_hipchat_users()
	old_list = get_user_list_from_file()
	added, removed = compare_lists(old_list, new_list)
	print 'Added: '
	print added
	print 'Removed: '
	print removed
	move_new_file_to_stored()
