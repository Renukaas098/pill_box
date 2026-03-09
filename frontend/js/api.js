async function getDevices(){

const res = await fetch("/device/list")

return await res.json()

}

async function scanWifi(ip){

const res = await fetch(`/device/wifi-scan?ip=${ip}`)

return await res.json()

}

async function setupWifi(data){

const res = await fetch("/device/wifi-setup",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify(data)
})

return await res.json()

}

async function getRecognitionLogs(){

const res = await fetch("/detection_log")

return await res.json()

}