def getUserOrders(accountId):
    orders = Session.query(Order).\
                        join(User).\
                        filter(Order.user_id == User.id).\
                        filter(User.account_number == accountId).\
                        all()
    Session.commit()
    return orders