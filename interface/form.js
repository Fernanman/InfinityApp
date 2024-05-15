const pub = document.getElementById('pub')
const priv = document.getElementById('priv')
const form = document.getElementById('form')
const submit_button = document.getElementById('submit')
var modal = document.getElementById("myModal");
var span = document.getElementsByClassName("close")[0];
const error = document.getElementById('error')

span.onclick = function() {
    modal.style.display = "none";
}

if (submit_button.textContent == "Login") {
    form.addEventListener('submit', (e) => {
        e.preventDefault()
    
        const data = new URLSearchParams();
        data.append('public_signature', pub.value.trim());
        data.append('private_signature', priv.value.trim())
    
        fetch('http://127.0.0.1:5000/login?' + data, {
                method : "GET",
                headers : {
                    "Content-Type" : "application/json"
                }
            })
                .then(res => {
                    return res.json()
                })
                .then(data => {    
                    if (data["status"])  {
                        sessionStorage.setItem('token', String(data["token"]))
                        console.log(data["token"])
                        console.log(sessionStorage.getItem('token'))

                        window.location.href = "./home.html";
                    }
                    else {
                        modal.style.display = "block";
                    }
                    
                })
    })
}

else {
    form.addEventListener('submit', (e) => {
        e.preventDefault()
    
        const data = new URLSearchParams();
        data.append('public_signature', pub.value.trim());
        data.append('private_signature', priv.value.trim())
    
        fetch('http://127.0.0.1:5000/register?' + data, {
                method : "GET",
                headers : {
                    "Content-Type" : "application/json"
                }
            })
                .then(res => {
                    return res.json()
                })
                .then(data => {
                    // NEED TO FINISH THIS
                    console.log(data["success"])

                    if (data["success"]) {
                        window.location.href = "./index.html";
                    }
                    else {
                        modal.style.display = "block";
                    }
                })
    })
}

