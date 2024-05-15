from infinity_bank import InfinityBank
from flask import Flask, request, send_file
from flask_cors import CORS, cross_origin


# Pre-reqs
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
infinity_bank = InfinityBank(update_rate=2)

# ------------------------------------------------------ Endpoints ------------------------------------------------------ 

@app.route('/login', methods=['GET'])
def login():
    """
    Endpoint for loggging in.
    """
    pub_sig = request.args.get('public_signature')
    priv_sig = request.args.get('private_signature')

    token = infinity_bank.login(pub_sig, priv_sig)
    if token is None:
        status = False
    else:
        status = True

    return {"status" : status,
            "token" : token}

@app.route('/get_name', methods=['GET'])
def get_name():
    """
    Endpoint for getting the user's public signature.
    """
    token = request.args.get('token')

    acc_name = infinity_bank.get_acc_name(token)

    return {"acc_name" : acc_name}

@app.route('/register', methods=['GET'])
def register():
    """
    Endpoint for registering a new user.
    """
    pub_sig = request.args.get('public_signature')
    priv_sig = request.args.get('private_signature')

    success = infinity_bank.create_account(pub_sig, priv_sig)

    return {"success" : success}

@app.route('/balance', methods=['GET'])
def get_balance():
    """
    Endpoint for getting a user's balance.
    """
    token = request.args.get('token')
    balance = infinity_bank.get_account_balance(token)

    if balance is not None:
        return {"inf_bal" : "%.4f" % round(balance[1], 4),
                "usd_bal" : "%.2f" % round(balance[0], 2)}
    else:
        return {"inf_bal" : None,
                "usd_bal" : None}

@app.route('/logout', methods=['GET'])
def logout():
    """
    Endpoint for logging out a user.
    """
    token = request.args.get('token')
    success = infinity_bank.logout(token)

    return {"success" : success}

@app.route('/transfer', methods=['GET'])
def transfer():
    """
    Endpoint for transferring Infinity from one user to another.
    """
    sender_token = request.args.get('sender_token')
    token_receiver = request.args.get('recipient_pub')
    amount = float(request.args.get('amount'))

    success = infinity_bank.transfer(sender_token, token_receiver, True, amount)

    return {"success" : success}


@app.route('/buy', methods=['GET'])
def buy():
    """
    Endpoint for buying Infinity.
    """
    token = request.args.get('token')
    amount = float(request.args.get('amount'))
    
    success = infinity_bank.buy(token, amount)

    return {"success" : success}

@app.route('/sell', methods=['GET'])
def sell():
    """
    Endpoint for selling Infinity.
    """
    token = request.args.get('token')
    amount = float(request.args.get('amount'))
    
    success = infinity_bank.sell(token, amount)

    return {"success" : success}

@app.route('/conversion', methods=['GET'])
def get_conversion():
    """
    Endpoint for getting the conversion rate of Infinity.
    """
    return {"conversion_rate" : "%.4f" % round(infinity_bank.get_conv_rate(), 4)}

@app.route('/market', methods=['GET'])
def get_market():
    """
    Endpoint for getting the market plot.
    """
    return send_file("./market.png", mimetype='image/png')


# ------------------------------------------------------ Endpoints ------------------------------------------------------ 


if __name__ == "__main__":
    app.run()