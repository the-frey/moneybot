from collections import namedtuple

Purchase = namedtuple('Purchase', [
	'from_coin', 'from_amount', 'to_coin', 'to_amount'
])
