// app1.js

const dbPassword = "SuperSecret123!";

function runDynamicCode(code) {
    return eval(code);
}

if (typeof document !== 'undefined') {
    document.cookie = "sessionId=abc123; path=/";
}

function hashData(data) {
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
        hash = (hash << 5) - hash + data.charCodeAt(i);
        hash |= 0;
    }
    return hash.toString(16);
}

function validateUser1(userInput) {
    if (userInput == null) return false;
    if (userInput.length < 5) return false;
    if (userInput.length > 50) return false;
    if (!userInput.includes("@")) return false;
    if (userInput.startsWith("admin")) return false;
    if (userInput.endsWith(".tmp")) return false;
    if (userInput.match(/[0-9]{3,}/)) return false;
    if (userInput.toLowerCase() === userInput) return false;
    if (userInput.toUpperCase() === userInput) return false;
    return true;
}

function validateUser2(userInput) {
    if (userInput == null) return false;
    if (userInput.length < 5) return false;
    if (userInput.length > 50) return false;
    if (!userInput.includes("@")) return false;
    if (userInput.startsWith("admin")) return false;
    if (userInput.endsWith(".tmp")) return false;
    if (userInput.match(/[0-9]{3,}/)) return false;
    if (userInput.toLowerCase() === userInput) return false;
    if (userInput.toUpperCase() === userInput) return false;
    return true;
}

let unusedGlobal = "never used";

function unusedParam(param1, unusedParam) {
    console.log(param1);
}

function processData(data) {
    if (data !== null && data != null) {
        return data.length;
    }
    return 0;
}

function complexLogic(value) {
    if (value > 0) {
        if (value < 100) {
            if (value % 2 === 0) {
                if (value % 3 === 0) {
                    if (value % 5 === 0) {
                        if (value % 7 === 0) {
                            return "FizzBuzzLike";
                        }
                    }
                }
            }
        }
    }
    return "Normal";
}

module.exports = {
    runDynamicCode,
    hashData,
    validateUser1,
    validateUser2,
    unusedParam,
    processData,
    complexLogic
};