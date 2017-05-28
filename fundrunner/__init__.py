from collections import namedtuple

Trade = namedtuple('Trade', [
	'from_coin', 'from_amount', 'to_coin'
])

Purchase = namedtuple('Purchase', [
	'from_coin', 'from_amount', 'to_coin', 'to_amount'
])
