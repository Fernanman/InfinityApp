const token = sessionStorage.getItem('token')
const token_url = new URLSearchParams();
token_url.append('token', token);

const logout_button = document.getElementById('logout_button')

var modal = document.getElementById("myModal");
var span = document.getElementsByClassName("close")[0];
const error = document.getElementById('error')
span.onclick = function() {
    modal.style.display = "none";
}

const usd_balance = document.getElementById('usd_balance')
const inf_balance = document.getElementById('inf_balance')

function update_balance(usd_balance, inf_balance) {
    fetch('http://127.0.0.1:5000/balance?' + token_url, {
        method : "GET",
        headers : {
            "Content-Type" : "application/json"
        }
    })
        .then(res => {
            return res.json()
        })
        .then(data => {                    
            console.log(data["acc_name"])

            usd_balance.innerText = data["usd_bal"]
            inf_balance.innerText = data["inf_bal"]
    })
}

update_balance(usd_balance, inf_balance)

// https://www.w3schools.com/jsref/met_element_addeventlistener.asp
logout_button.addEventListener('click', (e) => {
    e.preventDefault()

    fetch('http://127.0.0.1:5000/logout?' + token_url, {
                method : "GET",
                headers : {
                    "Content-Type" : "application/json"
                }
            })
                .then(res => {
                    return res.json()
                })
                .then(data => {                    
                    console.log(data["success"])
                })

    sessionStorage.removeItem('token');
    window.location.href = "./index.html";

})

const username = document.getElementById('username')
fetch('http://127.0.0.1:5000/get_name?' + token_url, {
                method : "GET",
                headers : {
                    "Content-Type" : "application/json"
                }
            })
                .then(res => {
                    return res.json()
                })
                .then(data => {                    
                    console.log(data["acc_name"])

                    username.innerText = data["acc_name"]
})


const conversion_rate = document.getElementById('conv_rate')
const image_tag = document.getElementById('market_plot')

function update_conversion() {
    fetch('http://127.0.0.1:5000/conversion', {
        method : "GET",
        headers : {
            "Content-Type" : "application/json"
        }
    })
        .then(res => {
            return res.json()
        })
        .then(data => {                    
            console.log(data["conversion_rate"])

            conversion_rate.innerText = data["conversion_rate"]
    })
}

function fetch_market(img) {
    fetch('http://127.0.0.1:5000/market', {
        method : "GET",
        headers : {
            "Content-Type" : "image/png"
        }
    })
        .then(res => {
            return res.blob()
        })
        .then(image_data => {       
            console.log("Updated image")             
            const imageUrl = URL.createObjectURL(image_data);
            img.src = imageUrl  
    })

}


fetch_market(image_tag)
update_conversion()



setInterval(update_conversion, 1000);
setInterval(fetch_market, 1200, image_tag);



const buy_form = document.getElementById('buy')
const buy_amount = document.getElementById('buy_amount')

buy_form.addEventListener('submit', (e) => {
    e.preventDefault()

    const data = new URLSearchParams();
    data.append('token', token)
    data.append('amount', buy_amount.value.trim());

    fetch('http://127.0.0.1:5000/buy?' + data, {
            method : "GET",
            headers : {
                "Content-Type" : "application/json"
            }
        })
            .then(res => {
                return res.json()
            })
            .then(data => {                    
                if (!data["success"]) {
                    console.log("Was false")
                    error.innerText = "You do not have sufficient funds to perform that transaction."
                    modal.style.display = "block";
                }
                else {
                    buy_amount.value = ""
                    update_balance(usd_balance, inf_balance)
                }
            })
})

const sell_form = document.getElementById('sell')
const sell_amount = document.getElementById('sell_amount')

sell_form.addEventListener('submit', (e) => {
    e.preventDefault()

    const data = new URLSearchParams();
    data.append('token', token)
    data.append('amount', sell_amount.value.trim());

    fetch('http://127.0.0.1:5000/sell?' + data, {
            method : "GET",
            headers : {
                "Content-Type" : "application/json"
            }
        })
            .then(res => {
                return res.json()
            })
            .then(data => {                    
                if (!data["success"]) {
                    console.log("Was false")
                    error.innerText = "You do not have sufficient funds to perform that transaction."
                    modal.style.display = "block";
                    
                }
                else {
                    sell_amount.value = ""
                    update_balance(usd_balance, inf_balance)
                }
            })
})

const transfer_form = document.getElementById('transfer')
const transfer_amount = document.getElementById('transfer_amount')
const recipient = document.getElementById('receiver_sig')

transfer_form.addEventListener('submit', (e) => {
    e.preventDefault()

    const data = new URLSearchParams();
    data.append('sender_token', token)
    data.append('amount', transfer_amount.value.trim());
    data.append('recipient_pub', recipient.value.trim())

    fetch('http://127.0.0.1:5000/transfer?' + data, {
            method : "GET",
            headers : {
                "Content-Type" : "application/json"
            }
        })
            .then(res => {
                return res.json()
            })
            .then(data => {                    
                if (!data["success"]) {
                    console.log("Was false")
                    error.innerText = "That public signature does not exist or you do not have the proper funds."
                    modal.style.display = "block";
                    
                }
                else {
                    transfer_amount.value = ""
                    recipient.value = ""
                    update_balance(usd_balance, inf_balance)
                }
            })
})
