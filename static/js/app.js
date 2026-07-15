async function sendMessage(){

    const message=document.getElementById("message").value;

    const response=await fetch("/chat",{

        method:"POST",

        headers:{
            "Content-Type":"application/x-www-form-urlencoded"
        },

        body:`message=${encodeURIComponent(message)}`
    });

    const data=await response.json();

    document.getElementById("chat-box").innerHTML+=`

        <p>

        <b>You:</b>

        ${message}

        </p>

        <p>

        <b>CareerGPT:</b>

        ${data.reply}

        </p>

        <hr>

    `;

    document.getElementById("message").value="";
}