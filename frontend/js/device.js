let selectedDeviceIP = null

async function loadDevices(){

const data = await getDevices()

const container = document.getElementById("device-list")

container.innerHTML=""

data.devices.forEach(d=>{

const card=document.createElement("div")

card.className="device-card"

card.innerHTML=`
<strong>${d.device_id}</strong><br>
IP: ${d.ip}
`

card.onclick=()=>selectDevice(d.ip,card)

container.appendChild(card)

})

}

function selectDevice(ip,card){

selectedDeviceIP=ip

document.getElementById("device-ip").value=ip

document.querySelectorAll(".device-card").forEach(c=>{
c.classList.remove("selected")
})

card.classList.add("selected")

}

async function scanWifiNetworks(){

if(!selectedDeviceIP) return alert("Select device first")

const data = await scanWifi(selectedDeviceIP)

const wifiList=document.getElementById("wifi-list")

wifiList.innerHTML=""

data.wifi.forEach(w=>{

const opt=document.createElement("option")

opt.value=w
opt.text=w

wifiList.appendChild(opt)

})

}

async function connectDevice(){

const ssid=document.getElementById("wifi-list").value
const password=document.getElementById("wifi-pass").value

await setupWifi({
ip:selectedDeviceIP,
ssid,
password
})

alert("Device connected")

}