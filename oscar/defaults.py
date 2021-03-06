# Basket settings
OSCAR_BASKET_COOKIE_LIFETIME = 7*24*60*60
OSCAR_BASKET_COOKIE_OPEN = 'oscar_open_basket'
OSCAR_BASKET_COOKIE_SAVED = 'oscar_saved_basket'

# Currency
OSCAR_DEFAULT_CURRENCY = 'GBP'

# Max number of products to keep on the user's history
OSCAR_RECENTLY_VIEWED_PRODUCTS = 4

# Image paths
OSCAR_IMAGE_FOLDER = 'images/products/%Y/%m/'
OSCAR_BANNER_FOLDER = 'images/promotions/banners'
OSCAR_POD_FOLDER = 'images/promotions/pods'

# Search settings
OSCAR_SEARCH_SUGGEST_LIMIT = 10

OSCAR_PARTNER_WRAPPERS = {}

# Promotions
COUNTDOWN, LIST, SINGLE_PRODUCT = ('Countdown', 'List', 'SingleProduct')
OSCAR_PROMOTION_MERCHANDISING_BLOCK_TYPES = (
    (COUNTDOWN, "Countdown"),
    (LIST, "List"),
    (SINGLE_PRODUCT, "Single product"),
)



PRICE_RANGES = (
    (0, 'FREE'),
    (10, '0.01-10'),
    (20, '10-20'),
    (30, '20-30'),
    (40, '30-40'),
    (50, '40-50'),
)

PRICE_RANGE_MAX = '50+'