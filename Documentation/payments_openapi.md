# Payment service endpoints

## __POST /wallet__

Parameters: None

Request Body: 
    { email: string }

Responses:

* success => {"status":"ok", "message":"Wallet created succesfully"}

* error => {"status":"error", "message":"User already has a wallet"}

* error => {"status":"error", "message":"Unexpected error"}

## __GET /wallet/:email__

Parameters: email

Request Body: None
Responses:

* success => {"address":string, "balance":string}

* error => {"status":"error", "message":"This user does not have a wallet"}

* error => {"status":"error", "message":"could not get wallet balance"}

## __POST /deposit__

Parameters: None

Request Body: 

{email: string
amountInEthers: string
newSubscription: string
}


Responses:

* success => {"status":"ok", "message":"transaction is beign processed"}

* error => {"status":"error", "message":"Amount to deposit should be positive"}

* error => {"status":"error", "message":"User does not have a wallet"}

* error => {"status":"error", "message":"Insufficient Funds"}

* error => {"status":"error", "message":"Unexpected error in deposit"}


## __POST /pay_creator__

Parameters: None

Request Body: 

{creatorEmail: string
amountInEthers: string
courseSubscription: string
}

Responses:

* success => {"status":"ok", "message":"transaction is beign processed"}

* error => {"status":"error", "message":"Amount to pay should be positive"}

* error => {"status":"error", "message":"Creator does not have a wallet"}

* error => {"status":"error", "message":"Insufficient Funds"}

* error => {"status":"error", "message":"Unexpected error in pay creator"}


## __GET /last_deposit/:email__

Parameters: email

Request Body: None

Responses:

* success => {"status":"ok", "message":"Last deposit found", "last_deposit_date":string}

* success => {"status":"error", "message":"User does not have deposits"}

* error => {"status":"error", "message":"Could not get last deposit"}

## __GET /deposits/:email__

Parameters: email

Request Body: None

Responses:

* success => {"status":"ok", "message":"No deposits found"}

* success => {"status":"ok", "message":"Deposits found", "deposits":deposits}

* error => {"status":"error", "message":"Could not get deposits"}
