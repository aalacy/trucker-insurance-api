
module.exports = {
    sequelizeValidationErrorsToArray : (errors) => {
        let messages = []
        errors.forEach(error => {
            let errorRow = {}
            errorRow[error.path] = error.message.replace('Error: ', '')
            messages.push(errorRow)
        })
        return messages
    },
    createErrorResponse : (data, message) => {

        let messages = []
        console.log(data)
        if (Object.keys(data).length > 0) {
            data.forEach(error => {
                Object.values(error).forEach(err => {
                    messages.push(err)
                })
            })
        }

        if (!message && messages.length > 0) {
            message = messages.join('. ')
        }

        return {
            status : "error",
            data : data,
            message : message || ''
        }
    },
    createSuccessResponse : (data, message) => {
        return {
            status : "ok",
            data : data,
            message : message || ''
        }
    },
    postToLower: (data, fields) => {
        fields.forEach(key => {
            if (data[key]) {
                data[key] = data[key].toLowerCase()
            }
        })
        return data
    },
    checkInput : (post, structure) => {
        let errors = []
        Object.keys(structure).forEach(key => {
            if (structure[key].required == true) {
                if (! (key in post) ) {
                    let error = {}
                    error[key] = 'Required key ' + key + ' not found'
                    errors.push(error)
                }
            }
        })
        return errors
    },
    transformInput : (post) => {
        if (post.json) {
            let json = post.json
            if (typeof json == 'string') {
                json = JSON.parse(json)
            }
            // let json = post.json
            Object.keys(json).forEach(key => {
                post[key] = json[key]
            })
        }
        return post
    }
}