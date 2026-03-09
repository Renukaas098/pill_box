let video
let canvas
let ctx
let stream
let detectInterval

let capturedImages=[]

const REQUIRED_IMAGES = 20

const lastDetected={}

function showStatus(msg){

const bar=document.getElementById("status-bar")

if(bar) bar.innerText=msg

}

// CAMERA STREAM

async function startStream(){

video=document.getElementById("video")
canvas=document.getElementById("overlay")

ctx=canvas.getContext("2d")

try{

stream=await navigator.mediaDevices.getUserMedia({video:true})

video.srcObject=stream

video.onloadedmetadata=()=>{

canvas.width=video.videoWidth
canvas.height=video.videoHeight

}

detectInterval=setInterval(sendFrame,300)

showStatus("Camera started")

}catch(err){

console.error(err)
showStatus("Camera permission denied")

}

}

function stopStream(){

if(stream){
stream.getTracks().forEach(t=>t.stop())
}

clearInterval(detectInterval)

if(ctx){
ctx.clearRect(0,0,canvas.width,canvas.height)
}

showStatus("Camera stopped")

}

// FRAME SEND

async function sendFrame(){

if(!video || video.videoWidth===0) return

const temp=document.createElement("canvas")

temp.width=video.videoWidth
temp.height=video.videoHeight

const tctx=temp.getContext("2d")

tctx.drawImage(video,0,0)

temp.toBlob(async blob=>{

const formData=new FormData()
formData.append("image",blob)

try{

const res=await fetch("/upload",{
method:"POST",
body:formData
})

const data=await res.json()

if(data.success){

drawFaces(data.result.faces)
updateDetectionList(data.result.faces)

}

}catch(err){

console.error("Upload error:",err)

}

},"image/jpeg")

}

// DRAW BOX

function drawFaces(faces){

ctx.clearRect(0,0,canvas.width,canvas.height)

const scaleX=canvas.width/video.videoWidth
const scaleY=canvas.height/video.videoHeight

faces.forEach(face=>{

const b=face.box

const x=b.x1*scaleX
const y=b.y1*scaleY
const w=(b.x2-b.x1)*scaleX
const h=(b.y2-b.y1)*scaleY

ctx.strokeStyle="lime"
ctx.lineWidth=2
ctx.strokeRect(x,y,w,h)

ctx.fillStyle="lime"
ctx.font="16px Arial"
ctx.fillText(face.label,x,y-5)

})

}

// DETECTION TABLE

function updateDetectionList(faces){

const table=document.getElementById("recognition-table")

if(!table) return

table.innerHTML=""

faces.forEach(face=>{

const row=document.createElement("tr")

row.innerHTML=`
<td>${face.label}</td>
<td>${face.score.toFixed(2)}</td>
`

table.appendChild(row)

})

}

// CAPTURE FACE

function captureFace(){

if(!video) return

if(capturedImages.length >= REQUIRED_IMAGES){

showStatus("Maximum "+REQUIRED_IMAGES+" images reached")

return

}

const temp=document.createElement("canvas")

temp.width=video.videoWidth
temp.height=video.videoHeight

const ctx2=temp.getContext("2d")

ctx2.drawImage(video,0,0)

temp.toBlob(blob=>{

capturedImages.push(blob)

const img=document.createElement("img")
img.src=URL.createObjectURL(blob)
img.className="captured-face"

document.getElementById("captured-faces").appendChild(img)

document.getElementById("capture-number").innerText=capturedImages.length

if(capturedImages.length >= REQUIRED_IMAGES){

document.getElementById("upload-btn").disabled=false

}

showStatus("Face captured")

},"image/jpeg")

}

// REGISTER USER

async function uploadCapturedFaces(){

const name=document.getElementById("person-name").value

if(!name){

showStatus("Enter name first")
return

}

if(capturedImages.length < REQUIRED_IMAGES){

showStatus("Capture "+REQUIRED_IMAGES+" images")
return

}

const formData=new FormData()

formData.append("name",name)

capturedImages.forEach(img=>{
formData.append("images",img)
})

showStatus("Uploading faces...")

try{

const res=await fetch("/register-user",{
method:"POST",
body:formData
})

const data=await res.json()

if(!data.success){

showStatus("Upload failed")
return

}

showStatus("User registered")

// IMPORTANT: reload embeddings
await fetch("/reload_embeddings",{method:"POST"})

capturedImages=[]

document.getElementById("captured-faces").innerHTML=""
document.getElementById("capture-number").innerText="0"
document.getElementById("upload-btn").disabled=true

loadUsers()

}catch(err){

console.error(err)
showStatus("Upload error")

}

}

// LOAD USERS

async function loadUsers(){

try{

const res=await fetch("/user_list")

const data=await res.json()

if(!data.success) return

const list=document.getElementById("user-list")

if(!list) return

list.innerHTML=""

data.users.forEach(name=>{

const row=document.createElement("div")

row.className="user-item"

row.innerHTML=`
<span>${name}</span>
<button onclick="deleteUser('${name}')">Delete</button>
`

list.appendChild(row)

})

}catch(err){

console.error(err)
showStatus("Failed to load users")

}

}

// DELETE USER

async function deleteUser(name){

showStatus("Deleting "+name)

try{

const res=await fetch("/user/"+encodeURIComponent(name),{
method:"DELETE"
})

const data=await res.json()

if(!data.success){

showStatus("Delete failed")
return

}

showStatus("User removed")

// IMPORTANT: reload embeddings
await fetch("/reload_embeddings",{method:"POST"})

loadUsers()

}catch(err){

console.error(err)
showStatus("Delete error")

}

}