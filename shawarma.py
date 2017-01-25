import json
from enum import Enum
import os
import os.path
import user


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


SHAWARMA_DIR = './shawarmas'
COMMENTS_DIR = '{}/comments'.format(SHAWARMA_DIR)
LAST_ID = '{}/last_id.txt'.format(SHAWARMA_DIR)


def get_message(message_type, data, error=False):
	return { 'type': message_type.value[0], 'data': json.dumps(data), 'error': error }


def get_result_message(message_type, result_str, error=True):
	return { 'type': int(message_type.value[0]), 'data': json.dumps({ 'result': result_str }), 'error': error }


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


def get_info(shawa_id):
	if os.path.isfile('{}/{}.json'.format(SHAWARMA_DIR, shawa_id)):
		info_file = open('{}/{}.json'.format(SHAWARMA_DIR, shawa_id))
		info = json.loads(info_file.read())
		info_file.close()
		return info
	else:
		return {}


def add_shawarma(json_obj):
	shawa_id = get_last_id() + 1
	set_last_id(shawa_id)
	new_shawa = { 'id': shawa_id, 'name': json_obj['name'], 'road': json_obj['road'], \
		'house': json_obj['house'], 'x': json_obj['x'], 'y': json_obj['y'], \
		'rating': 0.0, 'rateCount': 0, 'rates': 0, 'price': json_obj['price'] }

	info = open('{}/{}.json'.format(SHAWARMA_DIR, shawa_id), 'w')
	info.write(json.dumps(new_shawa))
	info.close()

	comments = open('{}/{}.json'.format(COMMENTS_DIR, shawa_id), 'w')
	comments.write('[]')
	comments.close()

	return get_result_message(MessageType.ADD_NEW_SHAWA, 'Шаверма добавлена.', False)


def get_comments(json_obj):
	if os.path.isfile('{}/{}.json'.format(COMMENTS_DIR, json_obj['id'])):
		comments_file = open('{}/{}.json'.format(COMMENTS_DIR, json_obj['id']))
		com_str = comments_file.read()
		comments_file.close()

		res = { 'id': json_obj['id'], 'comments': json.loads(com_str) }

		return get_message(MessageType.SHOW_COMMENTS, res)
	else:
		return get_result_message(MessageType.SHOW_COMMENTS, 'Шаверма не найдена.')


def add_comment(json_obj):
	if not os.path.isfile('{}/{}.json'.format('./users', json_obj['userId'])):
		return get_result_message(MessageType.COMMENT_ADD, 'Пользователь не найден.')

	if not os.path.isfile('{}/{}.json'.format(SHAWARMA_DIR, json_obj['shawaId'])):
		return get_result_message(MessageType.COMMENT_ADD, 'Шаверма не найдена.')

	if not os.path.isfile('{}/{}.json'.format(COMMENTS_DIR, json_obj['shawaId'])):
		return get_result_message(MessageType.COMMENT_ADD, 'Шаверма не найдена.')

	user = open('{}/{}.json'.format('./users', json_obj['userId']), 'r')
	user_obj = json.loads(user.read())
	user.close()
	user_name = user_obj['name']

	com_file = open('{}/{}.json'.format(COMMENTS_DIR, json_obj['shawaId']), 'r')
	comments = json.loads(com_file.read())
	com_file.close()

	new_comment = { 'user': user_name, 'comment': json_obj['comment'], 'rating': json_obj['rating'] }
	comments.append(new_comment)

	com_file = open('{}/{}.json'.format(COMMENTS_DIR, json_obj['shawaId']), 'w')
	com_file.write(json.dumps(comments))
	com_file.close()

	info_file = open('{}/{}.json'.format(SHAWARMA_DIR, json_obj['shawaId']), 'r')
	info = json.loads(info_file.read())
	info_file.close()

	info['rateCount'] = info['rateCount'] + json_obj['rating']
	info['rates'] = info['rates'] + 1
	info['rating'] = round(info['rateCount'] / info['rates'], 2)

	info_file = open('{}/{}.json'.format(SHAWARMA_DIR, json_obj['shawaId']), 'w')
	info_file.write(json.dumps(info))

	req = { 'id': json_obj['shawaId'] }
	return get_comments(req)


def more(json_obj):
	if os.path.isfile('{}/{}.json'.format(SHAWARMA_DIR, json_obj['shawaId'])):
		info_file = open('{}/{}.json'.format(SHAWARMA_DIR, json_obj['shawaId']))
		info_str = info_file.read()
		info_file.close()

		info = json.loads(info_str)
		info['favourite'] = user.is_favourite(json_obj['userId'], json_obj['shawaId'])

		return get_message(MessageType.MORE, info)
	else:
		return get_result_message(MessageType.MORE, 'Шаверма не найдена.')


def search(json_obj):
	tokens = json_obj['text'].split(' ')
	ftokens = list()
	for t in tokens:
		if t != '':
			ftokens.append(t)
	tokens = ftokens

	print(tokens)

	if len(tokens) == 2:
		road = tokens[0].lower()
		house = tokens[1].lower()
	elif len(tokens) == 1:
		road = tokens[0].lower()
	# else:
	# 	return get_message(MessageType.SEARCH, '[]')

	result = []
	if len(tokens) == 2:
		print(os.listdir(SHAWARMA_DIR))
		for file in os.listdir(SHAWARMA_DIR):
			if file.endswith('.json'):
				f = open('{}/{}'.format(SHAWARMA_DIR, file), 'r')
				info = json.loads(f.read())
				f.close()

				if info['road'].lower().find(tokens[0]) != -1 and info['house'].lower().find(tokens[1]) != -1:
					result.append(info)
	elif len(tokens) == 1:
		print(os.listdir(SHAWARMA_DIR))
		for file in os.listdir(SHAWARMA_DIR):
			if file.endswith('.json'):
				f = open('{}/{}'.format(SHAWARMA_DIR, file), 'r')
				info = json.loads(f.read())
				f.close()

				if info['road'].lower().find(tokens[0]) != -1:
					result.append(info)
	else:
		for file in os.listdir(SHAWARMA_DIR):
			if file.endswith('.json'):
				f = open('{}/{}'.format(SHAWARMA_DIR, file), 'r')
				info = json.loads(f.read())
				f.close()
				result.append(info)

	return get_message(MessageType.SEARCH, result)


