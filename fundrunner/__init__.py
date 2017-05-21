from collections import namedtuple

Trade = namedtuple('Trade', ['coin', 'investment_fiat'])
Purchase = namedtuple('Purchase', ['coin', 'amount', 'investment_fiat'])
