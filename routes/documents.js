module.exports = (app) => {
    let express = require('express')
    let multer  = require('multer')
    let router = express.Router()
    let upload = multer({ dest: 'public/tmp/' })
    let document = require('../models/Document')
    const vision = require('@google-cloud/vision')
    const client = new vision.ImageAnnotatorClient()
    let visionUtil = require('../utils/Vision')
    let companySnapshot = require('../utils/company-snapshot')
    let checkr = require('../utils/Checkr')

    router.get('/admin/list', (req, res, next) => {
        res.send({})
    })
    router.post('/admin/list', async (req, res, next) => {
        let list = await document.find()
        res.send({
            status: "OK",
            data: list,
            messages: []
        })
    })

    router.get('/admin/item', (req, res, next) => {
        res.send({'_id': 'required'})
    })
    router.post('/admin/item', upload.none(), async (req, res, next) => {

        let item = await document.findById(req.body._id)
        res.send({
            status: "OK",
            data: item,
            messages: []
        })
    })

    router.get('/upload', (req, res, next) => {
        console.log(document.schema.obj)
        res.send(document.schema.obj)
    })
    router.post('/upload', upload.fields([
        {name: 'imageIdFront', maxCount: 5},
        {name: 'imageIdBack', maxCount: 5},
        {name: 'imageDOT', maxCount: 5},
        {name: 'imageRegistration', maxCount: 5}
        ]), async (req, res, next) => {
        let doc = new document()
        Object.keys(req.files).forEach(file => {
            doc[file] = req.files[file]
        })
        Object.keys(req.body).forEach(key => {
            doc[key] = req.body[key]
        })

        console.log("doc=======>",doc);

        await doc.save(async error => {
            if (error !== null) {
                console.log('error=============>');
                console.log(error);
                return res.send({
                    status: "ERROR",
                    data: {},
                    messages: error
                })
            } else {
                console.log('else');
                doc.checkrCandidate = {}
                doc.checkrCandidate.first_name = doc.ownerFirstName
                doc.checkrCandidate.last_name = doc.ownerLastName
                doc.checkrCandidate.email = doc.email
                doc.checkrCandidate.phone = doc.phone
                doc.checkrCandidate.dob = doc.ownerDOB
                doc.checkrCandidate.zipcode = doc.ownerZip

                doc.imageIdFront.forEach(async id => {
                    let [result] = await client.textDetection(id.path)
                    let labels = result.textAnnotations
                    let dln = visionUtil.extractDLId(labels[0])
                    if (dln) {
                        doc.checkrCandidate.driver_license_number = dln
                    }
                    let dlstate = visionUtil.extractDLState(labels[0])
                    if (dlstate) {
                        doc.checkrCandidate.driver_license_state = dlstate
                    }
                    await doc.save( async error => {
                        doc.imageDOT.forEach(async dot => {
                            let [result] = await client.textDetection(dot.path)
                            let labels = result.textAnnotations
                            doc.dataDOT = result.textAnnotations
                            doc.resultDOT = visionUtil.extractDOT(labels[0])

                            await doc.save(async error => {
                                let re = /([0-9]+)/i;
                                let dotNumber = re.exec(doc.resultDOT)
                                if (dotNumber != null && parseInt(dotNumber[0]) > 0) {
                                    let snapshot = await companySnapshot.get(dotNumber[0])
                                    // console.log(snapshot)
                                    doc.resultDOTSaferData = snapshot
                                    await doc.save(async error => {
                                        let candidate = await checkr.createCandidate(doc.checkrCandidate)
                                        doc.checkrCandidateResponse = candidate
                                        await doc.save()
                                    })


                                }
                            })
                        })
                    })
                })

                res.send({
                    status: "OK",
                    data: doc,
                    messages: []
                })
            }


        })


    })

    app.use('/api/documents', router)
}
