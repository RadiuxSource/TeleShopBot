from Modules import StoreDB


async def add_group_listing(group_data: dict):
    """
    Add a new group listing to StoreDB.
    """
    await StoreDB.insert_one(group_data)

async def fetch_group_listings():
    """
    Fetch all active group listings from StoreDB.
    """
    listings = StoreDB.find({})
    return await listings.to_list(length=30)