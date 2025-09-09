console.log("Hello from Script.js");
const number = 7
console.log(number)
function fun(){
    console.log("Hello from function..");
}
fun();
function add(a,b){
    let c = a+b
    console.log("Sum of "+a+" and "+b+" = "+c)
}
let a = 5
let b = 6
add(a,b);

let arr = [1,23,4,5,5,4,7,4]
console.log("Array content...")
for(let i = 0;i<arr.length;i++){
    let value = arr[i];
    console.log("arr["+i+"]="+value)
}