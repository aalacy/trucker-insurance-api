module.exports = (app) => {
    let express = require('express')
    let router = express.Router()
    let fs = require('fs')
    let mime = require('mime-types')

    router.get('/:id', (req, res, next) => {
        let filePath = '/var/www/html/tmp/' + req.params.id
        fs.exists(filePath, function(exists){
            if (exists) {
                console.log(mime.lookup(filePath))
                // res.writeHead(200, {
                //     "Content-Type": "image/png",
                //     "Content-Disposition": "attachment; filename=" + req.params.id
                // });
                res.sendFile(filePath);
            } else {
                res.writeHead(400, {"Content-Type": "text/plain"})
                res.end("ERROR File does not exist")
            }
        });
    })

    app.use('/tmp', router)
}
