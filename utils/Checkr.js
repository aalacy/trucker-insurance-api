let request = require('request')
let config = require('../config.js').get()
module.exports = {
    createCandidate: (data) => {
        return new Promise ((resolve, reject) => {
            request.post({
                url: 'https://api.checkr.com/v1/candidates',
                headers : {
                    "Authorization" : 'Basic ' + new Buffer(config.checkrApiKey + ":").toString("base64")
                },
                form: data
            }, (error, response, body) => {
                if (error != null) {
                    reject (error)
                    return
                }
                console.log(body)
                resolve (JSON.parse(body))
            })
        })

    }
}

