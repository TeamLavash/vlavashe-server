import json
from enum import Enum
import os.path
import shawarma


class MessageType(Enum):
	UNDEFINED = 0,
	SHOW_MAP = 1,
	SHOW_PROFILE = 2,
	SHOW_FAVOURITE = 3,
	SHOW_ADD_NEW = 4,
	SHOW_SIGN_UP_SIGN_IN = 5,
	SHOW_SIGN_UP = 6,
	SHOW_SIGN_IN = 7,
	SHOW_COMMENTS = 8,

	SIGN_IN = 9,
	SIGN_UP = 10,
	LOGOUT = 11,

	ADD_NEW_SHAWA = 12,
	SEARCH = 13,
	MORE = 14,
	FAVOURITE_ADD = 15,
	FAVOURITE_REMOVE = 16,
	COMMENT_ADD = 17
	

class UserType(Enum):
	UNREGISTERED = 0,
	USER = 1,
	ADMIN = 2


USER_DIR = './users'
FAVOURITE_DIR = '{}/favourite'.format(USER_DIR)
NAMES_FILE = '{}/users.txt'.format(USER_DIR)
EMAILS_FILE = '{}/emails.txt'.format(USER_DIR)
LAST_ID = '{}/last_id.txt'.format(USER_DIR)


def get_message(message_type, data, error=False):
	return { 'type': message_type.value[0], 'data': json.dumps(data), 'error': error }


def get_result_message(message_type, result_str, error=True):
	return { 'type': int(message_type.value[0]), 'data': json.dumps({ 'result': result_str }), 'error': error }


def check_name_is_available(name):
	res = True
	names = open(NAMES_FILE, 'r')
	name = '{}\n'.format(name)
	for entry in names:
		if name == entry:
			res = False
			break
	names.close()
	return res


def check_email_is_available(email):
	res = True
	emails = open(EMAILS_FILE, 'r')
	email = '{}\n'.format(email)
	for entry in emails:
		if email == entry:
			res = False
			break
	emails.close()
	return res


def append_name(name):
	names = open(NAMES_FILE, 'a')
	names.write('{}\n'.format(name))
	names.close()


def append_email(email):
	emails = open(EMAILS_FILE, 'a')
	emails.write('{}\n'.format(email))
	emails.close()


def get_last_id():
	file = open(LAST_ID, 'r')
	last_id = file.read()
	print(last_id)
	file.close()
	return int(last_id)


def set_last_id(new_id):
	file = open(LAST_ID, 'w')
	file.write('{}'.format(new_id))
	file.close()


def get_user_id(name):
	user_id = 0
	users = open(NAMES_FILE, 'r')
	name = '{}\n'.format(name)
	for entry in users:
		if entry == name:
			return user_id 
		user_id += 1
	return -1


def is_favourite(user_id, shawa_id):
	if not os.path.isfile('{}/{}.json'.format(FAVOURITE_DIR, user_id)):
		return False

	fav_file = open('{}/{}.json'.format(FAVOURITE_DIR, user_id), 'r')
	fav = json.loads(fav_file.read())
	fav_file.close()

	return shawa_id in fav



def sign_up(json_obj):
	if (json_obj['password'] != json_obj['checkPassword']):
		return get_result_message(MessageType.SIGN_UP, 'Пароли не совпадают.')
	elif (not check_name_is_available(json_obj['name'])):
		return get_result_message(MessageType.SIGN_UP, 'Пользователь с таким именем уже зарегистрирован.')
	elif (not check_email_is_available(json_obj['email'])):
		return get_result_message(MessageType.SIGN_UP, 'Пользователь с таким email уже зарегистрирован.')
	else:
		append_name(json_obj['name'])
		append_email(json_obj['email'])

		user_id = get_last_id() + 1
		set_last_id(user_id)
		new_user = { 'id': user_id, 'name': json_obj['name'], 'email': json_obj['email'], 'password': json_obj['password'], 'status': UserType.USER.value[0] }

		info = open('{}/{}.json'.format(USER_DIR, user_id), 'w')
		info.write(json.dumps(new_user))
		info.close()

		favourite = open('{}/{}.json'.format(FAVOURITE_DIR, user_id), 'w')
		favourite.write('[]')
		favourite.close()

		return get_result_message(MessageType.SIGN_UP, 'Пользователь успешно зарегистрирован.', False)


def sign_in(json_obj):
	user_id = get_user_id(json_obj['name'])
	if user_id == -1:
		return get_result_message(MessageType.SIGN_IN, 'Пользователь не найден.')

	if (os.path.isfile('{}/{}.json'.format(USER_DIR, user_id))):
		info_file = open('{}/{}.json'.format(USER_DIR, user_id), 'r')
		info_str = info_file.read()
		info_file.close()

		info = json.loads(info_str)

		if info['password'] == json_obj['password']:
			return get_message(MessageType.SIGN_IN, info)
		else:
			return get_result_message(MessageType.SIGN_IN, 'Неверный логин/пароль.')
	else:
		return get_result_message(MessageType.SIGN_IN, 'Неверный логин/пароль.')


def get_favourite(json_obj):
	print('{}/{}.json'.format(FAVOURITE_DIR, json_obj['id']))
	if (os.path.isfile('{}/{}.json'.format(FAVOURITE_DIR, json_obj['id']))):
		fav_file = open('{}/{}.json'.format(FAVOURITE_DIR, json_obj['id']), 'r')
		fav = json.loads(fav_file.read())
		fav_file.close()

		res = []
		for it in fav:
			res.append(shawarma.get_info(it))

		return get_message(MessageType.SHOW_FAVOURITE, res)
	else:
		return get_result_message(MessageType.SHOW_FAVOURITE, 'Пользователь не найден.')


def add_favourite(json_obj):
	if (os.path.isfile('{}/{}.json'.format(FAVOURITE_DIR, json_obj['userId']))):
		fav_file = open('{}/{}.json'.format(FAVOURITE_DIR, json_obj['userId']), 'r')
		fav = json.loads(fav_file.read())
		fav_file.close()
		fav.append(json_obj['shawaId'])

		fav_file = open('{}/{}.json'.format(FAVOURITE_DIR, json_obj['userId']), 'w')
		fav_file.write(json.dumps(fav))
		fav_file.close()

		return get_result_message(MessageType.FAVOURITE_ADD, '', False)
	else:
		return get_result_message(MessageType.FAVOURITE_ADD, 'Пользователь не найден.')


def remove_favourite(json_obj):
	if (os.path.isfile('{}/{}.json'.format(FAVOURITE_DIR, json_obj['userId']))):
		fav_file = open('{}/{}.json'.format(FAVOURITE_DIR, json_obj['userId']), 'r')
		fav = json.loads(fav_file.read())
		fav_file.close()
		if json_obj['shawaId'] in fav:
			fav.remove(json_obj['shawaId'])

		fav_file = open('{}/{}.json'.format(FAVOURITE_DIR, json_obj['userId']), 'w')
		fav_file.write(json.dumps(fav))
		fav_file.close()

		return get_result_message(MessageType.FAVOURITE_REMOVE, '', False)
	else:
		return get_result_message(MessageType.FAVOURITE_REMOVE, 'Пользователь не найден.')
